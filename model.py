# model
import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint

class Swish(nn.Module):
    def forward(self, x):
        return x * torch.sigmoid(x)

class CNN(nn.Module):
    def __init__(self, conf):
        super().__init__()

        # We increase the hidden dimension over layers. Here pre-calculated for simplicity.
        hidden_features = 32
        c_hid1 = hidden_features//2
        c_hid2 = hidden_features
        c_hid3 = hidden_features*2

        # Series of convolutions and Swish activation functions
        self.cnn_layers = nn.Sequential(
            nn.Conv2d(1, c_hid1, kernel_size=5, stride=2, padding=4), # [16x16] - Larger padding to get 32x32 image
            Swish(),
            nn.Conv2d(c_hid1, c_hid2, kernel_size=3, stride=2, padding=1), #  [8x8]
            Swish(),
            nn.Conv2d(c_hid2, c_hid3, kernel_size=3, stride=2, padding=1), # [4x4]
            Swish(),
            nn.Conv2d(c_hid3, c_hid3, kernel_size=3, stride=2, padding=1), # [2x2]
            Swish(),
            nn.Flatten(),
            nn.Linear(c_hid3*4, c_hid3),
            Swish(),
            nn.Linear(c_hid3, 1)
        )
       
        # MSE Loss
        self.mse_loss = nn.MSELoss()
        
        # self the step number
        self.steps = conf.model.steps
        self.batch_size = conf.training.batch_size 
        self.alpha = conf.model.alpha

        # inference
        self.samples = conf.inference.samples

    def model_forward (self, x):
        x = x.to("mps") # ensure x is on device
        x = self.cnn_layers(x).squeeze(dim=-1)
        return x

    #def forward(self, x):
    #    device = "mps"
        
    def forward(self, x):
        """
        Calculates the EBM loss using Contrastive Divergence and L2 regularization.
        """
        device = "mps"
        x = x.to(device)
        x_fake = self.sample_langevin(
            steps=self.steps, 
            step_size=self.alpha 
        )
        energy_real = self.model_forward(x)      # E(x_real)
        energy_fake = self.model_forward(x_fake) # E(x_fake)

        cd_loss = energy_real.mean() - energy_fake.mean()
        reg_loss = 0.01 * (energy_real**2 + energy_fake**2).mean()
        total_loss = cd_loss + reg_loss
        
        # create sample
        if randint(1, 50) == 1:
            import cv2
            print(x.shape)
            cv2.imwrite(
                "test.png",
                (x_fake[0][0].cpu().detach().numpy() + 1)/2*255
            ) 
            cv2.imwrite(
                "real.png",
                (x[0][0].cpu().detach().numpy() + 1)/2*255
            ) 
        
        return total_loss, {
            "energy_fake": energy_fake.mean().cpu().item(),
            "eneryg_real": energy_real.mean().cpu().item(),
        }
    
    def sample_langevin(self, steps, step_size, noise_scale=0.005):
        """
        Performs Stochastic Gradient Langevin Dynamics (SGLD).
        
        Args:
            steps: Number of MCMC iterations.
            step_size: Learning rate for the image updates.
            noise_scale: Standard deviation of the noise added at each step.
        """
        # We need to calculate gradients with respect to the input image 'x'
        x_init = torch.randn(16, 1, 28, 28)
        x_sample = x_init.detach().requires_grad_(True)
        

        for _ in range(steps):
            # 1. Forward pass to get energy
            energy = self.model_forward(x_sample)
            grads = torch.autograd.grad(energy.sum(), x_sample)[0]
            noise = torch.randn_like(x_sample) * noise_scale
            x_sample.data = x_sample.data - (0.5 * step_size * grads) + noise
            x_sample.data.clamp_(-1, 1)
            
        # clear all gradients with the model
        for param in self.cnn_layers.parameters():
            if param.grad is not None:
                param.grad.zero_()
            
        return x_sample.detach()

    def sample_with_energy_track(self, steps, step_size, noise_scale):
        x_init = torch.randn(16, 1, 28, 28)
        x_sample = x_init.detach().requires_grad_(True)
        
        energy_history = []
        
        for _ in range(steps):
            # 1. Forward pass to get energy
            energy = self.model_forward(x_sample)
            
            # Record mean energy for plotting
            energy_history.append(energy.mean().item())
            
            # Calculate gradients w.r.t. the input image
            grads = torch.autograd.grad(energy.sum(), x_sample)[0]
            
            # Langevin update: x = x - (dt/2 * grad) + noise
            noise = torch.randn_like(x_sample) * noise_scale
            x_sample.data = x_sample.data - (0.5 * step_size * grads) + noise
            x_sample.data.clamp_(-1, 1)
            
        # Zero out gradients for the model parameters
        self.cnn_layers.zero_grad()
            
        return x_sample.detach(), energy_history  
