# EBT Training paradigm 
import torch.nn.functional as F
from random import randint
from utils.langevin import StopStep, LangevinTrainer, GradientMethod

class System2Trainer(LangevinTrainer):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        self.model = model
        self.device = conf.training.device

        self.min_steps = conf.ebt.step_min
        self.min_alpha = conf.ebt.alpha_min
        self.clamp_grad = conf.ebt.clamp_grad
        self.model.to(self.device) # put model to device
        self.max_steps = conf.ebt.step_max
        self.max_alpha = conf.ebt.alpha_max
    
    """
    Improvements: 

    System 1 vs. System 2 Learning <-- find out what this means
    * Gradient method all steps doesn't work
    * Gradient methods last step does work
    * what is the difference thet wo

    Why is there an averaging effect
    * Model architecture (implement DiT?)
    * Or is this within training (maybe because we are doing MSE)

    Random MCMC steps
    * Implemented random steps 
    
    Random Alpha
    * implemented annealed alpha 
    * + alpha is a nn.Parameter
    
    You might need to alter the parameters better for the EBT
    """
    
    def forward(self, x, condition=None): # x is the "actual" or "desired input"; the 8 digit
        x = x.to(self.device)
        num_steps = randint(self.min_steps, self.max_steps)
        alpha = randint(self.min_alpha, self.max_alpha)
        x_fake, extra = self.sample_langevin(
            num_samples=x.size(0),
            condition=condition,
            step_size=alpha,
            device=self.device,
            gradient_method=GradientMethod.PER_RUN,  
            stop_method=StopStep(max_steps=num_steps),
            noise_scale=0.,
            clamp_grad=self.clamp_grad,
            ret_extra=True
        )
        energy_h = extra["energy_history"]
        grad_h = extra["grad_norm_history"]

        if randint(1, 10) == 1:
            self.save_imgs(x, x_fake)

        total_loss = F.mse_loss(x_fake, x)
        
        return total_loss, {
            "last_energy": energy_h[-1], 
            "last_grad": grad_h[-1],
        }

class System1Trainer(LangevinTrainer):
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

    System 1 vs. System 2 Learning <-- find out what this means
    * Gradient method all steps doesn't work
    * Gradient methods last step does work
    * what is the difference thet wo

    Why is there an averaging effect
    * Model architecture (implement DiT?)
    * Or is this within training (maybe because we are doing MSE)

    Random MCMC steps
    * Implemented random steps 
    
    Random Alpha
    * implemented annealed alpha 
    * + alpha is a nn.Parameter
    
    You might need to alter the parameters better for the EBT
    """
    
    def forward(self, x, condition=None): # x is the "actual" or "desired input"; the 8 digit
        x = x.to(self.device)

        x_fake, extra = self.sample_langevin(
            num_samples=x.size(0),
            condition=condition,
            step_size=self.alpha,
            device=self.device,
            gradient_method=GradientMethod.PER_STEP,  # ALL Steps doesn't work
            stop_method=StopStep(max_steps=self.steps),
            noise_scale=0.,
            clamp_grad=self.clamp_grad,
            ret_extra=True
        )
        energy_h = extra["energy_history"]
        grad_h = extra["grad_norm_history"]

        if randint(1, 10) == 1:
            self.save_imgs(x, x_fake)

        total_loss = F.mse_loss(x_fake, x)
        
        return total_loss, {
            "last_energy": energy_h[-1], 
            "last_grad": grad_h[-1],
        }
