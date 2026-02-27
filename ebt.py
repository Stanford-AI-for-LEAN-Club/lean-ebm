# EBT Training paradigm 
import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
import cv2

class EBTTrainer (nn.Module):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.model = model
        self.device = conf.training.device

        self.steps = conf.ebt.steps
        self.alpha = conf.ebt.alpha
        
        self.model.to(self.device) # put model to device
    
    def _save_fake_real_imgs (self, x, x_fake):
        cv2.imwrite(
            "test.png",
            (x_fake[0][0].cpu().detach().numpy() + 1)/2*255
        ) 
        cv2.imwrite(
            "real.png",
            (x[0][0].cpu().detach().numpy() + 1)/2*255
        )

    def forward(self, x):
        x = x.to(self.device)
        x_fake, en = self.sample_langevin(
            num_samples=x.size(0),
            steps=self.steps, 
            step_size=self.alpha,
            record_energy=True,
            full_gradient=True, # only include the gradient for the last step
            noise_scale=0
        )

        if randint(1, 10) == 1:
            self._save_fake_real_imgs(x, x_fake)

        reconstruction_loss = F.mse_loss(x_fake, x)
        return reconstruction_loss, {
            "last_energy": en[-1]
        }
    
    # different parameters 
    # includes gradient at the end.
    def sample_langevin (
        self, 
        num_samples,            # number of samples to generate
        steps,                  # langevin # of steps
        step_size,              # step size
        noise_scale=0.005,      # we add a small noise scale
        record_energy=False,    # whehter to record the energy over time
        full_gradient=True # True if we only include parameter gradeints for the last step; False if we include it for all
    ):
        x_sample = torch.randn(num_samples, 1, 28, 28, requires_grad=True).to(self.device)
        x_sample.retain_grad()
        energy_history = []
        
        for i in range(steps):
            # clear all gradients with the model; this is just for sampling
            # 1. Forward pass to get energy
            energy = self.model(x_sample)
            
            if i == steps-1 or full_gradient:
                grads = torch.autograd.grad(energy.sum(), x_sample, create_graph=True)[0]
                noise = torch.randn_like(x_sample) * noise_scale
                x_sample = torch.clamp(
                    x_sample - (0.5 * step_size * grads) + noise,
                    -1, 1
                )
            else:
                grads = torch.autograd.grad(energy.sum(), x_sample)[0]
                noise = torch.randn_like(x_sample) * noise_scale
                x_sample.data = x_sample.data - (0.5 * step_size * grads) + noise
                x_sample.data.clamp_(-1, 1) # clamp from -1 to 1; could depend on the generation however 

            # append energy history
            if record_energy:
                energy_history.append(energy.mean().cpu().item())
            
        if record_energy:
            return x_sample, energy_history
        else:
            return x_sample