import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
import cv2
from .langevin import LangevinTrainer, GradientMethod, StopStep

class ContrastiveLearning (LangevinTrainer):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs) # pass the device
        self.model = model
        self.device = conf.training.device
        self.steps = conf.contrastive.steps
        self.reg_coef = conf.contrastive.reg_coef 
        self.alpha = conf.contrastive.alpha
        
        self.model.to(self.device) # put model to device
    
    def forward(self, x, condition=None):
        # Generate fake and real data samples; 
        # perform loss to decrease energy of the real images and increase energy of the fake images 
        # Fake images generated via the model (acts like GANs in this sense)
        x = x.to(self.device)
        x_fake = self.sample_langevin(
            num_samples=x.size(0),
            condition=condition,
            step_size=self.alpha,
            device=self.device,
            gradient_method=GradientMethod.NONE,
            stop_method=StopStep(max_steps=self.steps),
            noise_scale=0.005,
            ret_extra=False
        )
        energy_real = self.model(x, condition=condition)      # E(x_real)
        energy_fake = self.model(x_fake, condition=condition) # E(x_fake)

        # cd = Contrastive Learning loss
        cd_loss = energy_real.mean() - energy_fake.mean()
        reg_loss = self.reg_coef * (energy_real**2 + energy_fake**2).mean() # regularize the energy
        total_loss = cd_loss + reg_loss
        
        ############# Optional; Write fake and real images as training goes on #############
        if randint(1, 10) == 1:
            self.save_imgs(x, x_fake)
        
        return total_loss, {
            "energy_fake": energy_fake.mean().cpu().item(), # for debugging
            "energy_real": energy_real.mean().cpu().item(), # for debugging
        }