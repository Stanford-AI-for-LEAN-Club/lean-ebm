import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
import cv2

class ContrastiveLearning (nn.Module):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.model = model
        self.device = conf.training.device
        self.steps = conf.contrastive.steps
        self.reg_coef = conf.contrastive.reg_coef 
        self.alpha = conf.contrastive.alpha

        
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

    #Currently no conditioning so 
    def forward(self, y):

        y = y.to(self.device)
        batch_size = y.size(0)
        
        # Sample k uniformly from {1, ..., K}
        k = torch.randint(0, self.num_landscapes, (batch_size,), device=self.device)
        sigma_k = self.sigmas[k].view(-1, 1, 1, 1)

        # Generate perturbed sample: y_k = y + sigma_k * epsilon
        # TODO: make this general
        noise = torch.randn_like(y)
        y_noisy = y + sigma_k * noise
        y_noisy.requires_grad_(True) 

        # Compute energy values
        energy_noisy = self.model(x_noisy, k) 
        energy_real = self.model(y, k)

        # 4. Score Function Supervision (Equation 5)
        # Target is (y - y_k) / sigma_k^2
        target_grad = (y - y_noisy).detach() / (sigma_k**2)
        
        energy_grad = torch.autograd.grad(
            outputs=energy_noisy.sum(),
            inputs=x_noisy,
            create_graph=True,
            retain_graph=True
        )[0]

        # Literal interpretation of Eq 5: || grad - target ||^2
        # We use mean() to reduce the batch, but the inner norm is squared
        score_loss = torch.mean(torch.sum((energy_grad - target_grad)**2, dim=[1, 2, 3]))

        # 5. Energy Landscape Supervision (Equation 6)
        # Literal interpretation: E_real - E_noisy
        energy_loss = (energy_real - energy_noisy).mean()

        # 6. Total Loss (Eq 4)
        total_loss = self.lambda_score * score_loss + self.lambda_energy * energy_loss
        
        return total_loss, {
            "score_loss": score_loss.item(),
            "energy_loss": energy_loss.item()
        }


    def _____forward(self, x): #TODO: delete this reference function
        # Generate fake and real data samples; 
        # perform loss to decrease energy of the real images and increase energy of the fake images 
        # Fake images generated via the model (acts like GANs in this sense)
        x = x.to(self.device)
        x_fake = self.sample_langevin(
            num_samples=x.size(0),
            steps=self.steps, 
            step_size=self.alpha,
            record_energy=False
        )
        energy_real = self.model(x)      # E(x_real)
        energy_fake = self.model(x_fake) # E(x_fake)

        # cd = Contrastive Learning loss
        cd_loss = energy_real.mean() - energy_fake.mean()
        reg_loss = self.reg_coef * (energy_real**2 + energy_fake**2).mean() # regularize the energy
        total_loss = cd_loss + reg_loss
        
        ############# Optional; Write fake and real images as training goes on #############
        #if randint(1, 50) == 1:
        #    self._save_fake_real_imgs(x, x_fake)
        
        return total_loss, {
            "energy_fake": energy_fake.mean().cpu().item(), # for debugging
            "energy_real": energy_real.mean().cpu().item(), # for debugging
        }
    
    def sample_langevin (
        self, 
        num_samples,            # number of samples to generate
        steps,                  # langevin # of steps
        step_size,              # step size
        noise_scale=0.005,      # we add a small noise scale
        record_energy=False     # whehter to record the energy over time
    ):
        x_sample = torch.randn(num_samples, 1, 28, 28, requires_grad=True).to(self.device)
        energy_history = []
        
        for _ in range(steps):
            # 1. Forward pass to get energy
            energy = self.model(x_sample)
            grads = torch.autograd.grad(energy.sum(), x_sample)[0]
            noise = torch.randn_like(x_sample) * noise_scale

            x_sample.data = x_sample.data - (0.5 * step_size * grads) + noise
            x_sample.data.clamp_(-1, 1) # clamp from -1 to 1; could depend on the generation however 

            # append energy history
            if record_energy:
                energy_history.append(energy.mean().cpu().item())
            
        # clear all gradients with the model; this is just for sampling
        for param in self.model.parameters():
            if param.grad is not None:
                param.grad.zero_()
            
        if record_energy:
            return x_sample.detach(), energy_history
        else:
            return x_sample.detach()