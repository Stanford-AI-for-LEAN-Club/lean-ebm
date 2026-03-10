import torch
import torch.nn.functional as F
import math
from torch import nn

class DiffusionTrainer(nn.Module):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs) # pass the device
        self.model = model
        self.device = conf.training.device

        # We only need the boundaries for a continuous schedule
        self.sigma_min = conf.diffusion.sigma_min
        self.sigma_max = conf.diffusion.sigma_max       

        self.model.to(self.device)
    
    def get_continuous_beta(self, t):
        """
        Maps continuous t in [0, 1] to a noise scale β_t using a cosine schedule.
        """
        angles = (1.0 - t) * (math.pi / 2)
        beta_t = self.sigma_min + (self.sigma_max - self.sigma_min) * (torch.cos(angles) ** 2)
        return beta_t
    
    # score matching procedure
    # pretty simple :)
    def forward(self, x, condition=None):
        batch_size = x.shape[0]
        t = torch.rand(batch_size, device=self.device)
        
        # 1. Get noise scale beta_t and alpha_t
        beta_t = self.get_continuous_beta(t)
        beta_t_reshaped = beta_t.view(batch_size, *([1] * (x.ndim - 1))) 
        alpha_t = torch.sqrt(1 - beta_t_reshaped**2) # variance preserving

        epsilon = torch.randn_like(x)
        x_t = alpha_t * x + beta_t_reshaped * epsilon
        predicted_noise = self.model(x_t, t, condition=condition)
            
        loss = F.mse_loss(predicted_noise, epsilon, reduction='mean')
        return loss, {}
    
    @torch.no_grad()
    def sample(self, x_init, sigma_t=0.0, num_steps=1000, condition=None):
        """
        Stable DDIM simulation from t=1 down to t=0.
        sigma_t acts as 'eta' in [0, 1]. 0.0 is deterministic DDIM, 1.0 is standard DDPM.
        """
        self.model.eval()
        xt = x_init.to(self.device)
        batch_size = xt.shape[0]
        
        for i in range(num_steps):
            t_current = 1.0 - (i / num_steps)
            t_next = 1.0 - ((i + 1) / num_steps)
            
            t_tensor = torch.full((batch_size,), t_current, device=self.device)
            t_next_tensor = torch.full((batch_size,), max(t_next, 0.0), device=self.device)
            
            beta_curr = self.get_continuous_beta(t_tensor).view(batch_size, *([1] * (xt.ndim - 1)))
            alpha_curr = torch.clamp(torch.sqrt(1 - beta_curr**2), min=1e-5)
            
            beta_next = self.get_continuous_beta(t_next_tensor).view(batch_size, *([1] * (xt.ndim - 1)))
            alpha_next = torch.sqrt(1 - beta_next**2)
            
            predicted_noise = self.model(xt, t_tensor, condition=condition)
            
            x0_pred = (xt - beta_curr * predicted_noise) / alpha_curr
            x0_pred = torch.clamp(x0_pred, -1.0, 1.0)
            
            # --- FIXED STOCHASTIC STEP ---
            eta = sigma_t # Treat the hyperparameter as eta
            
            if eta > 0.0:
                # 1. Calculate dynamic DDIM variance (sigma_actual)
                # This ensures the noise injected decays to 0 as t approaches 0
                variance_ratio = torch.clamp(1.0 - (alpha_curr**2 / alpha_next**2), min=0.0)
                sigma_actual = eta * (beta_next / beta_curr) * torch.sqrt(variance_ratio)
                
                # 2. Adjust the direction pointing back to x_t
                noise_scale = torch.sqrt(torch.clamp(beta_next**2 - sigma_actual**2, min=0.0))
                
                # 3. Inject noise ONLY if we are not at the final step (t_next > 0)
                noise = torch.randn_like(xt) if t_next > 0 else 0.0
                
                xt = alpha_next * x0_pred + noise_scale * predicted_noise + sigma_actual * noise
            else:
                # Pure Probability Flow ODE (Deterministic)
                xt = alpha_next * x0_pred + beta_next * predicted_noise
                
        self.model.train()
        return xt