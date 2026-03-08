# IRED Training paradigm
import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class IREDTrainer(nn.Module):
    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.device = conf.training.device

        # IRED-specific config (with safe defaults if block is missing)
        ired_conf = conf.get("ired", {})
        self.num_landscapes = int(ired_conf.get("num_landscapes", 10))
        self.sigma_max = float(ired_conf.get("sigma_max", 0.95))
        self.sigma_min = float(ired_conf.get("sigma_min", 0.01))
        self.neg_corruption_scale = float(ired_conf.get("neg_corruption_scale", 0.25))
        self.neg_refine_steps = int(ired_conf.get("neg_refine_steps", 0))
        self.neg_refine_step_size = float(ired_conf.get("neg_refine_step_size", 0.2))
        self.mse_weight = float(ired_conf.get("mse_weight", 1.0))
        self.contrastive_weight = float(ired_conf.get("contrastive_weight", 1.0))
        self.reg_coef = float(ired_conf.get("reg_coef", 0.005))

        # Optional per-landscape inference optimization settings (Algorithm 2 style)
        self.inference_steps_per_landscape = int(
            ired_conf.get("inference_steps_per_landscape", 10)
        )
        self.inference_step_size = float(ired_conf.get("inference_step_size", 0.1))

        # Descending sigmas: smooth -> sharp landscapes
        self.register_buffer("sigmas", self._build_sigma_schedule())
        self.model.to(self.device)

    def _build_sigma_schedule(self):
        # Cosine schedule from 0 to 1, then map to sigma_min to sigma_max   
        K = self.num_landscapes
        t = torch.arange(K, dtype=torch.float32) / (K - 1)
        angles = (1.0 - t) * (math.pi / 2)
        sigmas = self.sigma_min + (self.sigma_max - self.sigma_min) * torch.cos(angles) ** 2
        return sigmas.flip(0) # Reverse so index 0 is the smoothest (highest sigma) landscape

    def _energy(self, y, k_idx, condition):
        # make sure to be careful with the clamping here
        return self.model(y, k_idx, condition)

    def _sample_k_and_sigma(self, batch_size):
        k_idx = torch.randint(
            low=0,
            high=self.num_landscapes,
            size=(batch_size,),
            device=self.device,
        )
        sigma = self.sigmas[k_idx].view(batch_size, *([1] * 3))
        return k_idx, sigma

    def _make_negative(self, y_true, k_idx, condition=None):
        # Paper's c(y): corrupt the ground-truth label with Gaussian noise,
        # then optionally refine via gradient ascent on the energy to push the
        # negative toward a harder local maximum (paper appendix, continuous tasks).
        y_neg = (y_true + self.neg_corruption_scale * torch.randn_like(y_true))

        if self.neg_refine_steps > 0:
            for _ in range(self.neg_refine_steps):
                y_neg = y_neg.detach().requires_grad_(True)
                e = self._energy(y_neg, k_idx, condition)
                grad = torch.autograd.grad(e.sum(), y_neg)[0]
                y_neg = (y_neg - self.neg_refine_step_size * grad)

        return y_neg.detach()

    def forward(self, x, condition):
        """
        Input `y` is treated as the supervision target y*.
        Returns combined loss and logs.
        
        You can make this faster by batching both the positive and negative samples
        """
        y_true = x.to(self.device)
        batch_size = y_true.size(0)

        # Sample landscape k and its noise level sigma_k
        k_idx, sigma = self._sample_k_and_sigma(batch_size)
        eps = torch.randn_like(y_true)
        sqrt_term = torch.sqrt(torch.clamp(1.0 - sigma * sigma, min=1e-8))

        # Positive noisy sample: y_hat = sqrt(1-sigma^2) * y* + sigma * eps
        y_hat_pos = (sqrt_term * y_true + sigma * eps).detach().requires_grad_(True)
    
        # Score supervision: || grad_y E(x, y_hat, k) - eps ||^2
        e_pos = self._energy(y_hat_pos, k_idx, condition)
        score_pred = torch.autograd.grad(
            e_pos.sum(),
            y_hat_pos,
            create_graph=True,
        )[0]
        mse_loss = F.mse_loss(score_pred, eps)

        # Contrastive shaping between positive and negative energies
        y_neg = self._make_negative(y_true, condition)
        y_hat_neg = (sqrt_term * y_neg + sigma * eps).detach()
        e_neg = self._energy(y_hat_neg, k_idx, condition)

        energy_stack = torch.stack([e_pos, e_neg], dim=1)
        target = torch.zeros(e_pos.size(0)).to(energy_stack.device)
        contrastive_loss = F.cross_entropy(-energy_stack, target.long(), reduction='mean')

        #contrastive_loss = (e_pos - e_neg).mean() # <--  

        # Total l
        total_loss = \
                self.mse_weight * mse_loss + \
                self.contrastive_weight * contrastive_loss + \
                self.reg_coef * (e_pos + e_neg).mean()

        logs = {
            "loss": total_loss.detach().cpu().item(),
            "mse_loss": mse_loss.detach().cpu().item(),
            "contrastive_loss": contrastive_loss.detach().cpu().item(),
            "mean_energy_pos": e_pos.detach().mean().cpu().item(),
            "mean_energy_neg": e_neg.detach().mean().cpu().item(),
            "mean_k": k_idx.float().mean().detach().cpu().item(),
        }
        return total_loss, logs

    def sample_annealed(
        self, 
        shape, 
        steps_per_landscape=None,
        step_size=None,
        condition=None
    ):
        """
        IRED inference-style optimizer (Algorithm 2 style):
        start from Gaussian and optimize over landscapes from smooth->sharp.
        """
        y_hat = torch.randn(shape, device=self.device, requires_grad=True)
        condition = torch.randint(0, 10, (shape[0], ), device=self.device) if condition is None else condition
        steps_per_landscape = self.inference_steps_per_landscape if steps_per_landscape is None else steps_per_landscape
        step_size = self.inference_step_size if step_size is None else step_size

        y_hat = y_hat.to(self.device)
        condition = condition.to(self.device)

        for k in range(self.num_landscapes):
            sigma_k = self.sigmas[k]
            sigma_prev = self.sigmas[k - 1] if k > 0 else self.sigmas[k]
            k_idx = torch.full((shape[0],), k, device=self.device, dtype=torch.long)

            for _ in range(steps_per_landscape):
                y_hat = y_hat.detach().requires_grad_(True)
                energy = self._energy(y_hat, k_idx, condition)
                grad = torch.autograd.grad(energy.sum(), [y_hat], create_graph=False)[0]
                y_hat = (y_hat - step_size * grad).detach()

                #e_next = self._energy(y_next, k_idx, condition)
                #accept = (e_next < energy).view(-1, *([1] * (y_hat.dim() - 1)))
                #y_hat = torch.where(accept, y_next, y_hat.detach())

            #scale = torch.sqrt(torch.clamp(1.0 - sigma_k * sigma_k, min=1e-8))
            #scale_prev = torch.sqrt(torch.clamp(1.0 - sigma_prev * sigma_prev, min=1e-8))
            #y_hat = y_hat * (scale / torch.clamp(scale_prev, min=1e-8))

        return y_hat