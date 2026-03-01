# EBT Training paradigm 
import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
import cv2
from langevin import StopStep, LangevinTrainer, GradientMethod

class EBTTrainer (LangevinTrainer):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.model = model
        self.device = conf.training.device

        self.steps = conf.ebt.steps
        self.alpha = conf.ebt.alpha
        self.reg_coef = conf.ebt.reg_coef
        
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

    def forward(self, x): # x is the "actual" or "desired input"; the 8 digit
        x = x.to(self.device)
        x_fake, extra = self.sample_langevin(
            num_samples=x.size(0),
            step_size=self.alpha,
            device=self.device,
            gradient_method=GradientMethod.LAST_STEP,
            stop_method=StopStep(max_steps=self.steps),
            noise_scale=0,
            ret_extra=True
        )
        energy_h = extra["energy_history"]

        if randint(1, 10) == 1:
            self.save_imgs(x, x_fake)

        total_loss = F.mse_loss(x_fake, x)
        
        return total_loss, {
            "last_energy": energy_h[-1].mean()
        }