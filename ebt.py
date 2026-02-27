# EBT Training paradigm 
import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
import cv2

# create a general energy trainer

class ContrastiveLearning (nn.Module):
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
        return x
    
    def sample_langevin (
        self, 
        num_samples,            # number of samples to generate
        steps,                  # langevin # of steps
        step_size,              # step size
        noise_scale=0.005,      # we add a small noise scale
        record_energy=False     # whehter to record the energy over time
    ):
        x_init = torch.randn(num_samples, 1, 28, 28).to(self.device)
        x_sample = x_init.detach().requires_grad_(True)
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