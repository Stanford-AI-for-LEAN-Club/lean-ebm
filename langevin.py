# General Langevin Trainer + Helper Functions 
# Ex: Langevin Dynamics
import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
from enum import Enum
import cv2
from typing import Union
from dataclasses import dataclass

# Gradeint method
class GradientMethod: 
    NONE=0      # Don't keep the gradients of the class at all
    LAST_STEP=1 # only keep the gradient of the very last step
    ALL_STEPS=2 # keep the gradients through all steps

# stops when we reach a certain number of steps
@dataclass
class StopStep: 
    max_steps:int

# stops when the energy - last energy <= threshold
# max_steps is also declared if it never reaches the threshold
@dataclass
class StopEnergyGradient:
    max_steps:int
    threshold:float
   
StopMethod = Union[StopStep, GradientMethod] 

class LangevinTrainer (nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # helper function to save images
    def save_imgs (self, x, x_fake):
        cv2.imwrite(
            "test.png",
            (x_fake[0][0].cpu().detach().numpy() + 1)/2*255
        ) 
        cv2.imwrite(
            "real.png",
            (x[0][0].cpu().detach().numpy() + 1)/2*255
        )

    def sample_langevin (
        self, 
        num_samples,                    # number of samples to generate
        step_size,                      # step size
        device,                         # what device to run on
        gradient_method:GradientMethod, # what Gradient method to use
        stop_method:StopMethod,         # what Stop Method to use
        noise_scale=0.005,              # we add a small noise scale
        ret_extra=False,                # returns extra information like energy and num steps
    ):
        # prepare x sample
        x_sample = torch.randn(num_samples, 1, 28, 28, requires_grad=True).to(device)
        x_sample.retain_grad() 
        
        # other variables
        num_steps = 0
        energy_history = []
        last_energy = None
        
        while True:
            num_steps += 1 # incr steps

            # 1. Forward pass to get energy
            energy = self.model(x_sample)
            current_energy = energy.mean().cpu().item()
            
            # determine variables for gradient calculation
            should_stop = False
            match stop_method:
                case StopStep(max_steps):
                    if num_steps >= max_steps:
                        should_stop = True
                case StopEnergyGradient(max_steps, threshold):
                    if num_steps >= max_steps:
                        should_stop = True
                    if last_energy is not None and abs(last_energy - current_energy) <= threshold:
                        should_stop = True
            last_energy = current_energy

            should_create_graph = True if (
                gradient_method == GradientMethod.ALL_STEPS or \
                (gradient_method == GradientMethod.LAST_STEP and should_stop)
            ) else False
            
            # calculate gradient
            grads = torch.autograd.grad(
                energy.sum(), 
                x_sample, 
                create_graph=should_create_graph,
                retain_graph=False
            )[0]
            
            # Update x_sample
            noise = torch.randn_like(x_sample) * noise_scale
            x_sample = torch.clamp(
                x_sample - (0.5 * step_size * grads) + noise,
                -1, 1
            )
            
            # store other values; debug
            if ret_extra:
                energy_history.append(energy.detach().unsqueeze(0)) 
                # note that we always detach the energy!
            
            if should_stop:
                break
            
        if ret_extra:
            return x_sample, {
                "energy_history": torch.cat(energy_history, dim=0).to(device),
                "num_steps": num_steps
            }
        else:
            return x_sample