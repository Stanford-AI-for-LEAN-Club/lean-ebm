# EBT Training paradigm 
import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
import cv2
from .langevin import StopStep, LangevinTrainer, GradientMethod

class EBTTrainer (LangevinTrainer):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.model = model
        self.device = conf.training.device

        self.steps = conf.ebt.steps
        self.alpha = conf.ebt.alpha
        self.clamp_grad = conf.ebt.clamp_grad
        
        self.model.to(self.device) # put model to device
    
    """
    Improvements: 
    
    Random MCMC steps
    Random Alpha
    TruncateMCMC? 
    You might need to alter the parameters better for the EBT
    Check more!!
    """
    
    def forward(self, x, condition=None): # x is the "actual" or "desired input"; the 8 digit
        x = x.to(self.device)

        x_fake, extra = self.sample_langevin(
            num_samples=x.size(0),
            condition=condition,
            step_size=self.alpha,
            device=self.device,
            gradient_method=GradientMethod.LAST_STEP,
            stop_method=StopStep(max_steps=self.steps),
            noise_scale=0,
            clamp_grad=self.clamp_grad,
            ret_extra=True
        )
        energy_h = extra["energy_history"]

        if randint(1, 10) == 1:
            self.save_imgs(x, x_fake)

        total_loss = F.mse_loss(x_fake, x)
        
        return total_loss, {
            "last_energy": energy_h[-1].mean()
        }