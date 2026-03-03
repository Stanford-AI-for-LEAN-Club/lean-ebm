import torch
from torch import nn
from torch.nn import functional as F
import pytorch_lightning as L
import torch.optim as optim
from torchmetrics import Accuracy
import traceback
from torchvision.transforms import functional as TF
import torchvision.models as models
import math
import random
from diffusers import AutoencoderKL

from model.model_utils import *
from model.diffusion import create_diffusion
from model.diffusion.gaussian_diffusion import mean_flat
# from model.replay_buffer import CausalReplayBuffer # fix

class EBT_IMG_Denoise(L.LightningModule):
    def __init__(self, hparams):
        super().__init__()
        if isinstance(hparams, dict):#passed in from model ckpt
            self.hparams.update(hparams)
        else:
            self.hparams.update(vars(hparams))

        self.alpha = nn.Parameter(torch.tensor(float(self.hparams.mcmc_step_size)), requires_grad=self.hparams.mcmc_step_size_learnable)
        self.langevin_dynamics_noise_std = nn.Parameter(torch.tensor(float(self.hparams.langevin_dynamics_noise)), requires_grad=False) # if using self.hparams.langevin_dynamics_noise_learnable this will be turned on in warm_up_finished func
        self.finished_warming_up = False

        self.transformer = setup_bidirectional_ebt(self.hparams)
        self.learned_adaln_condition = nn.Embedding(1, self.hparams.embedding_dim)

        self.diffusion = create_diffusion(timestep_respacing="", diffusion_steps=int(self.hparams.diffusion_steps / self.hparams.denoise_images_noise_level)) # only for adding noise to real samples

        self.smooth_l1 = nn.SmoothL1Loss(beta=1.0)
        self.l1 = nn.L1Loss()
        self.mse = nn.MSELoss()

        self.mcmc_replay_buffer = 'mcmc_replay_buffer' in self.hparams and self.hparams.mcmc_replay_buffer and self.hparams.execution_mode != "inference"
        if self.mcmc_replay_buffer:
            replay_buffer_max_size = self.hparams.mcmc_replay_buffer_size
            self.replay_buffer_samples = self.hparams.batch_size_per_device * self.hparams.mcmc_replay_buffer_sample_bs_percent
            raise NotImplementedError("need to implement bidirectional replay buffer")
            # self.replay_buffer = CausalReplayBuffer(max_size=replay_buffer_max_size, sample_size=self.replay_buffer_samples)

    def forward(self, noised_x, learning = True, no_randomness = True): # y here is caption_embeddings since is just text conditional; a lot of the logic here is just for S2 params, see pseudocode in paper for a more concise view of how this works. it can be < 10 LOC
        predicted_x_list = []
        predicted_energies_list = []
        batch_size = noised_x.shape[0]

        predicted_x = noised_x.clone().detach()

        # Calculate the alpha parameter
        # Randomizes alpha for training (pretty interesting paradigm)
        alpha = torch.clamp(self.alpha, min=0.0001)
        if not no_randomness and self.hparams.randomize_mcmc_step_size_scale != 1:
            expanded_alpha = alpha.expand(batch_size, 1, 1, 1)

            scale = self.hparams.randomize_mcmc_step_size_scale
            low = alpha / scale
            high = alpha * scale
            alpha = low + torch.rand_like(expanded_alpha) * (high - low)

        # noise std randomization
        langevin_dynamics_noise_std = torch.clamp(self.langevin_dynamics_noise_std, min=0.000001)
        
        # MCMC Steps -- randomization of MCMC steps
        mcmc_steps = [] # in the general case of no randomize_mcmc_num_steps then this has len == self.hparams.randomize_mcmc_num_steps
        for step in range(self.hparams.mcmc_num_steps):
            # whether we randomize the number of steps
            if not no_randomness and hasattr(self.hparams, 'randomize_mcmc_num_steps') and self.hparams.randomize_mcmc_num_steps > 0:
                if self.hparams.randomize_mcmc_num_steps_final_landscape: # makes so only applies rand steps to final landscape
                    if step == (self.hparams.mcmc_num_steps - 1):
                        min_steps = 1 if self.hparams.randomize_mcmc_num_steps_min == 0 else self.hparams.randomize_mcmc_num_steps_min
                        repeats = torch.randint(min_steps, self.hparams.randomize_mcmc_num_steps + 2, (1,)).item()
                        mcmc_steps.extend([step] * repeats)
                    else:
                        mcmc_steps.append(step)
                else:
                    min_steps = 1 if self.hparams.randomize_mcmc_num_steps_min == 0 else self.hparams.randomize_mcmc_num_steps_min
                    repeats = torch.randint(min_steps, self.hparams.randomize_mcmc_num_steps + 2, (1,)).item()
                    mcmc_steps.extend([step] * repeats)
            elif no_randomness and hasattr(self.hparams, 'randomize_mcmc_num_steps') and self.hparams.randomize_mcmc_num_steps > 0: # use max steps
                if step == (self.hparams.mcmc_num_steps - 1): # i found this was a better pretraining metric and was more stable, only do several steps on final energy landscape instead of over all energy landscapes
                    mcmc_steps.extend([step] * (self.hparams.randomize_mcmc_num_steps + 1))
                else:
                    mcmc_steps.append(step)
            else:
                mcmc_steps.append(step)

        with torch.set_grad_enabled(True): # set to true for validation since grad would be off
            for i, mcmc_step in enumerate(mcmc_steps): # mcmc steps is randomized!!

                # On system **2** learning --> LAST STEP
                if self.hparams.no_mcmc_detach: 
                    predicted_x = predicted_x.requires_grad_() # B, C, W, H

                # on System **1** leraning, detach!
                else:  
                    predicted_x = predicted_x.detach().requires_grad_() # B, C, W, H
                
                if self.hparams.langevin_dynamics_noise != 0 and not (no_randomness and self.hparams.no_langevin_during_eval):
                    ld_noise = torch.randn_like(predicted_x.detach(), device=predicted_x.device) * langevin_dynamics_noise_std # langevin dynamics
                    predicted_x = predicted_x + ld_noise
                                
                # Model forward
                condition = self.learned_adaln_condition(torch.tensor([0], device=predicted_x.device))
                condition = condition.expand(batch_size, -1)  # Expand to match batch size
                energy_preds = self.transformer(predicted_x, condition).squeeze()
                energy_preds = energy_preds.mean(dim=[1]).reshape(-1) # B
                predicted_energies_list.append(energy_preds)
                
                # On system **2** Learning --> truncuate MCMC | LAST STEP
                if self.hparams.truncate_mcmc:  #retain_graph defaults to create_graph value here; if learning is true then create_graph else dont (inference)
                    if i == (len(mcmc_steps) - 1):
                        predicted_embeds_grad = torch.autograd.grad([energy_preds.sum()], [predicted_x], create_graph=learning)[0]
                    else:
                        predicted_embeds_grad = torch.autograd.grad([energy_preds.sum()], [predicted_x], create_graph=False)[0]
                
                # On system **1** learning, don't truncate MCMC
                else:
                    predicted_embeds_grad = torch.autograd.grad([energy_preds.sum()], [predicted_x], create_graph=learning)[0]
                
                if self.hparams.clamp_futures_grad:
                    min_and_max = self.hparams.clamp_futures_grad_max_change / (self.alpha)
                    # predicted_embeds_grad = scale_clamp(predicted_embeds_grad, -min_and_max, min_and_max)
                    predicted_embeds_grad = torch.clamp(predicted_embeds_grad, min = -min_and_max, max = min_and_max)

                if torch.isnan(predicted_embeds_grad).any() or torch.isinf(predicted_embeds_grad).any():
                    raise ValueError("NaN or Inf gradients detected during MCMC.")
                    
                predicted_x = predicted_x - alpha * predicted_embeds_grad
                
                predicted_x_list.append(predicted_x)

        return predicted_x_list, predicted_energies_list
        
    
    def forward_loss_wrapper(self, x, phase="train"):
        no_randomness = False if phase == "train" else True
        learning = (phase == "train")

        real_images = x['image']
        if self.hparams.randomize_denoise_images_noise_level:
            t = torch.randint(0, self.hparams.diffusion_steps, (real_images.shape[0],), device=self.device)
        else:
            t = torch.tensor(self.hparams.diffusion_steps-1, device=self.device).expand(real_images.shape[0])
        noised_images = self.diffusion.q_sample(real_images, t)
        # noised_images = real_images + torch.randn_like(real_images.detach(), device=real_images.device) * self.hparams.denoise_images_noise_level

        if not no_randomness and self.mcmc_replay_buffer: # dont do this when doing val/testing
            raise NotImplementedError("not yet implemented, please add functionality for bidirectional replay buffer")
            noised_images, real_images = self.replay_buffer.get_batch(noised_images, real_images) 
            denoised_images_list, predicted_energies_list = self(noised_images, learning=learning, no_randomness = no_randomness)
            self.replay_buffer.update(real_images, denoised_images_list[-1].detach()) # update using the final predicted embeddings
        else:
            denoised_images_list, predicted_energies_list = self(noised_images, learning=learning, no_randomness = no_randomness)

        reconstruction_loss = 0
        total_mcmc_steps = len(predicted_energies_list)
        for mcmc_step, (denoised_images, predicted_energy) in enumerate(zip(denoised_images_list, predicted_energies_list)):
            #loss calculations
            if self.hparams.truncate_mcmc:
                if mcmc_step == (total_mcmc_steps - 1):
                    reconstruction_loss = self.smooth_l1(denoised_images, real_images)
                    final_reconstruction_loss = reconstruction_loss.detach()
            else:
                reconstruction_loss += self.smooth_l1(denoised_images, real_images)
                if mcmc_step == (total_mcmc_steps - 1):
                    final_reconstruction_loss = self.smooth_l1(denoised_images, real_images).detach()
                    reconstruction_loss = reconstruction_loss / total_mcmc_steps # normalize so is indifferent to number of mcmc steps
            
            #pure logging things (no function for training)
            if mcmc_step == 0:
                initial_loss = self.smooth_l1(denoised_images, real_images).detach()
                initial_pred_energies = predicted_energy.squeeze().mean().detach()
            if mcmc_step == (total_mcmc_steps - 1):
                final_pred_energies = predicted_energy.squeeze().mean().detach()
                l1_loss = self.l1(denoised_images, real_images).detach()

        initial_final_pred_energies_gap = initial_pred_energies - final_pred_energies
        total_loss = self.hparams.reconstruction_coeff * reconstruction_loss

        log_dict = {
            'loss': total_loss,
            'initial_loss' : initial_loss,
            'final_step_loss': final_reconstruction_loss,
            'initial_final_pred_energies_gap': initial_final_pred_energies_gap,
            'l1_loss': l1_loss,
        }

        is_update_step = (self.trainer.fit_loop.epoch_loop.batch_progress.current.completed + 1) % self.trainer.accumulate_grad_batches == 0 # so dont have issues with gradient accumulation
        if self.trainer.global_step % self.hparams.log_image_every_n_steps == 0 and is_update_step and phase == "train":
            t = torch.tensor(self.hparams.diffusion_steps-1, device=self.device).expand(real_images.shape[0])
            noised_images = self.diffusion.q_sample(real_images, t)
            denoised_images_list, predicted_energies_list = self(noised_images, no_randomness = True, learning=False) # dont do randomness when getting samples and disable higher order grad

            with torch.no_grad():
                denoised_images = denoised_images_list[-1].detach()
                predicted_samples = torch.cat((denoised_images[0].unsqueeze(0), real_images[0].unsqueeze(0), noised_images[0].unsqueeze(0)), dim = 0) # only use first index of generated samples for loss calc
                decoded_images = denormalize(predicted_samples.unsqueeze(0), self.hparams.dataset_name, self.device, self.hparams.custom_image_normalization, True).squeeze(0)

                log_dict['denoised_image'] = decoded_images[0]
                log_dict['original_image'] = decoded_images[1]
                log_dict['noised_image'] = decoded_images[2]
                log_dict['mse_raw_loss'] = torch.mean(mean_flat((real_images - denoised_images) ** 2)).detach()
        
        return log_dict

    
    def ebt_advanced_inference(self, noised_x, learning = True, no_randomness = True): #NOTE should eventually add more features from NLP and VID, for now is same as forward but with more steps
        predicted_x_list = []
        predicted_energies_list = []
        batch_size = noised_x.shape[0]

        predicted_x = noised_x.clone().detach()

        alpha = torch.clamp(self.alpha, min=0.0001)
        if not no_randomness and self.hparams.randomize_mcmc_step_size_scale != 1:
            expanded_alpha = alpha.expand(batch_size, 1, 1, 1)

            scale = self.hparams.randomize_mcmc_step_size_scale
            low = alpha / scale
            high = alpha * scale
            alpha = low + torch.rand_like(expanded_alpha) * (high - low)

        langevin_dynamics_noise_std = torch.clamp(self.langevin_dynamics_noise_std, min=0.000001)

        mcmc_steps = [] # in the general case of no randomize_mcmc_num_steps then this has len == self.hparams.randomize_mcmc_num_steps
        for step in range(self.hparams.infer_ebt_num_steps):
            if not no_randomness and hasattr(self.hparams, 'randomize_mcmc_num_steps') and self.hparams.randomize_mcmc_num_steps > 0:
                if self.hparams.randomize_mcmc_num_steps_final_landscape: # makes so only applies rand steps to final landscape
                    if step == (self.hparams.infer_ebt_num_steps - 1):
                        min_steps = 1 if self.hparams.randomize_mcmc_num_steps_min == 0 else self.hparams.randomize_mcmc_num_steps_min
                        repeats = torch.randint(min_steps, self.hparams.randomize_mcmc_num_steps + 2, (1,)).item()
                        mcmc_steps.extend([step] * repeats)
                    else:
                        mcmc_steps.append(step)
                else:
                    min_steps = 1 if self.hparams.randomize_mcmc_num_steps_min == 0 else self.hparams.randomize_mcmc_num_steps_min
                    repeats = torch.randint(min_steps, self.hparams.randomize_mcmc_num_steps + 2, (1,)).item()
                    mcmc_steps.extend([step] * repeats)
            elif no_randomness and hasattr(self.hparams, 'randomize_mcmc_num_steps') and self.hparams.randomize_mcmc_num_steps > 0: # use max steps
                if step == (self.hparams.infer_ebt_num_steps - 1): # i found this was a better pretraining metric and was more stable, only do several steps on final energy landscape instead of over all energy landscapes
                    mcmc_steps.extend([step] * (self.hparams.randomize_mcmc_num_steps + 1))
                else:
                    mcmc_steps.append(step)
            else:
                mcmc_steps.append(step)

        with torch.set_grad_enabled(True): # set to true for validation since grad would be off
            for i, mcmc_step in enumerate(mcmc_steps):
                if self.hparams.no_mcmc_detach:
                    predicted_x = predicted_x.requires_grad_() # B, C, W, H
                else: # default, do detach
                    predicted_x = predicted_x.detach().requires_grad_() # B, C, W, H
                
                if self.hparams.langevin_dynamics_noise != 0 and not (no_randomness and self.hparams.no_langevin_during_eval):
                    ld_noise = torch.randn_like(predicted_x.detach(), device=predicted_x.device) * langevin_dynamics_noise_std # langevin dynamics
                    predicted_x = predicted_x + ld_noise
                                
                condition = self.learned_adaln_condition(torch.tensor([0], device=predicted_x.device))
                condition = condition.expand(batch_size, -1)  # Expand to match batch size
                energy_preds = self.transformer(predicted_x, condition).squeeze()
                energy_preds = energy_preds.mean(dim=[1]).reshape(-1) # B
                predicted_energies_list.append(energy_preds)

                if self.hparams.truncate_mcmc:  #retain_graph defaults to create_graph value here; if learning is true then create_graph else dont (inference)
                    if i == (len(mcmc_steps) - 1):
                        predicted_embeds_grad = torch.autograd.grad([energy_preds.sum()], [predicted_x], create_graph=learning)[0]
                    else:
                        predicted_embeds_grad = torch.autograd.grad([energy_preds.sum()], [predicted_x], create_graph=False)[0]
                else:
                    predicted_embeds_grad = torch.autograd.grad([energy_preds.sum()], [predicted_x], create_graph=learning)[0]
                
                if self.hparams.clamp_futures_grad:
                    min_and_max = self.hparams.clamp_futures_grad_max_change / (self.alpha)
                    # predicted_embeds_grad = scale_clamp(predicted_embeds_grad, -min_and_max, min_and_max)
                    predicted_embeds_grad = torch.clamp(predicted_embeds_grad, min = -min_and_max, max = min_and_max)

                if torch.isnan(predicted_embeds_grad).any() or torch.isinf(predicted_embeds_grad).any():
                    raise ValueError("NaN or Inf gradients detected during MCMC.")
                    
                predicted_x = predicted_x - alpha * predicted_embeds_grad
                
                predicted_x_list.append(predicted_x)

        return predicted_x_list, predicted_energies_list