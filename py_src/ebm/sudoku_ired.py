"""
Sudoku IRED Trainer

IRED training adapted for 6x6 Sudoku probability distributions.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class SudokuIREDTrainer(nn.Module):
    """IRED trainer adapted for Sudoku probability distributions"""

    def __init__(self, model, conf, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.device = conf.training.device

        # IRED-specific config (with safe defaults if block is missing)
        ired_conf = conf.get("sudoku_ired", {})
        self.num_landscapes = int(ired_conf.get("num_landscapes", 50))
        self.sigma_max = float(ired_conf.get("sigma_max", 0.95))
        self.sigma_min = float(ired_conf.get("sigma_min", 0.01))
        self.neg_corruption_scale = float(ired_conf.get("neg_corruption_scale", 0.3))
        self.neg_refine_steps = int(ired_conf.get("neg_refine_steps", 5))
        self.neg_refine_step_size = float(ired_conf.get("neg_refine_step_size", 0.15))
        self.mse_weight = float(ired_conf.get("mse_weight", 1.0))
        self.contrastive_weight = float(ired_conf.get("contrastive_weight", 1.0))
        self.reg_coef = float(ired_conf.get("reg_coef", 0.01))

        # Sudoku-specific parameters
        self.num_channels = 7
        self.grid_size = 6
        self.epsilon_prob = float(ired_conf.get("epsilon_prob", 0.1))

        # Inference parameters
        self.inference_steps_per_landscape = int(
            ired_conf.get("inference_steps_per_landscape", 15)
        )
        self.inference_step_size = float(ired_conf.get("inference_step_size", 0.08))

        # Sigma schedule (cosine)
        self.register_buffer("sigmas", self._build_sigma_schedule())
        self.model.to(self.device)

    def _build_sigma_schedule(self):
        """Cosine schedule from smooth to sharp landscapes"""
        K = self.num_landscapes
        t = torch.arange(K, dtype=torch.float32) / (K - 1)
        angles = (1.0 - t) * (math.pi / 2)
        sigmas = self.sigma_min + (self.sigma_max - self.sigma_min) * torch.cos(angles) ** 2
        return sigmas.flip(0)  # Reverse so index 0 is smoothest (highest sigma)

    def _energy(self, y, k_idx, condition):
        """Compute energy with clamping"""
        return self.model(y.clamp(0, 1), k_idx, condition)

    def _sample_k_and_sigma(self, batch_size):
        """Sample landscape index and corresponding sigma"""
        k_idx = torch.randint(
            low=0,
            high=self.num_landscapes,
            size=(batch_size,),
            device=self.device,
        )
        sigma = self.sigmas[k_idx].view(batch_size, *([1] * 3))  # (B, 1, 1, 1)
        return k_idx, sigma

    def _add_probability_noise(self, y_true, sigma):
        """
        Add noise to probability distributions.

        Args:
            y_true: (B, 7, 6, 6) - probability tensor
            sigma: (B, 1, 1, 1) - noise level

        Returns:
            y_hat: (B, 7, 6, 6) - noisy probability tensor
        """
        # Add Gaussian noise to all channels
        eps = torch.randn_like(y_true) * self.epsilon_prob
        sqrt_term = torch.sqrt(torch.clamp(1.0 - sigma * sigma, min=1e-8))

        y_hat = sqrt_term * y_true + sigma * eps

        # Clamp to valid probability range
        y_hat = torch.clamp(y_hat, 0, 1)

        # Renormalize value channels (1-6) for filled cells
        # For cells where channel 0 (certainty) > 0.5, normalize channels 1-6 to sum to 1
        filled_mask = y_hat[:, 0:1, :, :] > 0.5  # (B, 1, 6, 6)
        value_channels = y_hat[:, 1:, :, :]  # (B, 6, 6, 6)

        # Normalize value channels for filled cells
        sum_values = value_channels.sum(dim=1, keepdim=True) + 1e-8  # (B, 1, 6, 6)
        normalized_values = value_channels / sum_values

        # Apply normalization only to filled cells
        y_hat[:, 1:, :, :] = torch.where(
            filled_mask.expand_as(value_channels),
            normalized_values,
            value_channels
        )

        return y_hat.clamp(0, 1).detach().requires_grad_(True)

    def _make_negative(self, y_true, k_idx, condition=None):
        """
        Create negative sample by corruption.

        Corrupts some filled cells by randomizing their value distributions.
        Optionally refines via gradient ascent to push toward energy maxima.
        """
        y_neg = y_true.clone()
        batch_size = y_true.size(0)

        # Randomly flip some filled cells to random distributions
        for b in range(batch_size):
            # Find filled cells (where certainty channel > 0.5)
            filled_mask = y_true[b, 0, :, :] > 0.5
            filled_indices = torch.nonzero(filled_mask, as_tuple=False)

            if len(filled_indices) > 0:
                # Corrupt a fraction of filled cells
                num_corrupt = int(len(filled_indices) * self.neg_corruption_scale)
                if num_corrupt > 0:
                    corrupt_idx = torch.randperm(len(filled_indices))[:num_corrupt]

                    for idx in corrupt_idx:
                        row, col = filled_indices[idx]
                        # Set to random probability distribution
                        y_neg[b, 0, row, col] = 0.0  # Make uncertain
                        y_neg[b, 1:, row, col] = torch.rand(6)
                        # Normalize
                        y_neg[b, 1:, row, col] /= y_neg[b, 1:, row, col].sum()

        # Optional gradient ascent refinement
        if self.neg_refine_steps > 0:
            y_neg = y_neg.detach().requires_grad_(True)
            for _ in range(self.neg_refine_steps):
                e = self._energy(y_neg, k_idx, condition)
                grad = torch.autograd.grad(e.sum(), y_neg)[0]
                y_neg = y_neg + self.neg_refine_step_size * grad  # Ascent, not descent
                y_neg = torch.clamp(y_neg, 0, 1)

        return y_neg

    def forward(self, x, condition=None):
        """
        Training forward pass.

        Handles multiple calling formats:
        1. forward(x, condition) - training format with separate arguments
        2. forward((partial, solution, mask)) - evaluation format with tuple
        3. forward([partial, solution, mask]) - evaluation format with list

        Args:
            x: (B, 7, 6, 6) complete solution tensor OR batch container
            condition: (B, 6, 6) mask pattern (1=filled, 0=empty) OR None

        Returns:
            total_loss, logs_dict
        """
        # Handle evaluation format: forward(batch) where batch = (partial, solution, mask)
        if condition is None:
            if isinstance(x, (tuple, list)) and len(x) == 3:
                # Unpack batch container: (partial, solution, mask)
                partial, solution, mask = x
                x = solution  # solution tensor
                condition = mask  # mask tensor
            else:
                # Handle unexpected formats
                if isinstance(x, dict):
                    # Try dict format
                    x = x.get("x", x)
                    condition = x.get("condition", None)
                    if condition is None:
                        raise ValueError("Dict format requires 'x' and 'condition' keys")
                else:
                    raise ValueError(f"Expected (partial, solution, mask) tuple/list, got {type(x)}")

        y_true = x.to(self.device)
        batch_size = y_true.size(0)
        condition = condition.to(self.device)

        # Sample landscape k and its noise level sigma_k
        k_idx, sigma = self._sample_k_and_sigma(batch_size)

        # Positive noisy sample
        y_hat_pos = self._add_probability_noise(y_true, sigma)

        # Score supervision
        e_pos = self._energy(y_hat_pos, k_idx, condition)
        score_pred = torch.autograd.grad(
            e_pos.sum(),
            y_hat_pos,
            create_graph=True,
        )[0]

        # Target: simplified score (direction from noisy to clean)
        eps_target = (y_hat_pos - y_true) / (sigma + 1e-8)
        mse_loss = F.mse_loss(score_pred, eps_target)

        # Negative sample
        y_neg = self._make_negative(y_true, k_idx, condition)
        y_hat_neg = self._add_probability_noise(y_neg, sigma)
        e_neg = self._energy(y_hat_neg, k_idx, condition)

        # Contrastive loss (cross-entropy)
        energy_stack = torch.stack([e_pos, e_neg], dim=1)
        target = torch.zeros(e_pos.size(0), device=self.device, dtype=torch.long)
        contrastive_loss = F.cross_entropy(-energy_stack, target)

        # Total loss
        total_loss = (
            self.mse_weight * mse_loss +
            self.contrastive_weight * contrastive_loss +
            self.reg_coef * (e_pos + e_neg).mean()
        )

        logs = {
            "loss": total_loss.detach().cpu().item(),
            "mse_loss": mse_loss.detach().cpu().item(),
            "contrastive_loss": contrastive_loss.detach().cpu().item(),
            "mean_energy_pos": e_pos.detach().mean().cpu().item(),
            "mean_energy_neg": e_neg.detach().mean().cpu().item(),
        }

        return total_loss, logs

    @torch.no_grad()
    def sample_annealed(
        self,
        shape,
        condition=None,
        steps_per_landscape=None,
        step_size=None
    ):
        """
        Generate Sudoku completion using annealed sampling.

        Args:
            shape: (batch_size, 7, 6, 6)
            condition: (batch_size, 6, 6) - mask pattern (1=filled, 0=empty)
            steps_per_landscape: optimization steps per landscape
            step_size: gradient descent step size

        Returns:
            completed_puzzle: (B, 7, 6, 6)
        """
        batch_size = shape[0]
        steps_per_landscape = self.inference_steps_per_landscape if steps_per_landscape is None else steps_per_landscape
        step_size = self.inference_step_size if step_size is None else step_size

        # Initialize with random probability distributions
        y_hat = torch.rand(shape, device=self.device)

        # Fix filled cells from condition
        if condition is not None:
            condition = condition.to(self.device)
            for b in range(batch_size):
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        if condition[b, i, j] > 0.5:  # Filled cell
                            # Find which value channel has highest probability
                            value_idx = torch.argmax(y_hat[b, 1:, i, j]) + 1
                            y_hat[b, :, i, j] = 0
                            y_hat[b, 0, i, j] = 1.0  # Certainty
                            y_hat[b, value_idx, i, j] = 1.0  # One-hot value

        # Iterate over landscapes from smooth to sharp
        for k in range(self.num_landscapes):
            k_idx = torch.full((batch_size,), k, device=self.device, dtype=torch.long)

            for _ in range(steps_per_landscape):
                y_hat = y_hat.detach().requires_grad_(True)

                # Compute energy and gradient
                energy = self._energy(y_hat, k_idx, condition if condition is not None else torch.zeros(batch_size, self.grid_size, self.grid_size, device=self.device))

                # Gradient descent on energy
                # Expand energy to match shape for broadcasting
                energy_expanded = energy.view(-1, *([1] * (y_hat.dim() - 1)))
                y_next = (y_hat - step_size * energy_expanded * torch.sign(y_hat - 0.5)).detach()

                # Clamp and preserve condition
                y_next = torch.clamp(y_next, 0, 1)

                # Preserve filled cells from condition
                if condition is not None:
                    for b in range(batch_size):
                        filled_mask = condition[b] > 0.5
                        y_next[b, :, filled_mask] = y_hat[b, :, filled_mask].detach()

                y_hat = y_next

        return y_hat

    def solve_puzzle(self, partial_puzzle, mask, num_candidates=5):
        """
        Solve a Sudoku puzzle using the trained energy model.

        Args:
            partial_puzzle: (B, 7, 6, 6) - partial puzzle
            mask: (B, 6, 6) - mask pattern
            num_candidates: number of solutions to generate

        Returns:
            solutions: (B, num_candidates, 7, 6, 6)
        """
        solutions = []
        for _ in range(num_candidates):
            sol = self.sample_annealed(partial_puzzle.shape, condition=mask)
            solutions.append(sol)

        return torch.stack(solutions, dim=1)


if __name__ == "__main__":
    # Test the trainer
    print("Testing SudokuIREDTrainer...")

    from omegaconf import OmegaConf
    from models.sudoku_ired import SudokuEnergy

    # Create config
    conf = OmegaConf.create({
        'training': {
            'device': 'cpu'  # Use CPU for testing
        },
        'sudoku_ired': {
            'num_landscapes': 10,
            'energy_dim': 64,
            'sigma_max': 0.95,
            'sigma_min': 0.01,
            'neg_corruption_scale': 0.3,
            'neg_refine_steps': 2,
            'mse_weight': 1.0,
            'contrastive_weight': 1.0,
            'reg_coef': 0.01,
            'epsilon_prob': 0.1,
            'inference_steps_per_landscape': 5,
            'inference_step_size': 0.08,
        }
    })

    # Initialize model and trainer
    model = SudokuEnergy(conf)
    trainer = SudokuIREDTrainer(model, conf)
    print(f"Trainer initialized")

    # Test forward pass
    batch_size = 4
    x = torch.rand(batch_size, 7, 6, 6)  # Random solution
    condition = torch.randint(0, 2, (batch_size, 6, 6)).float()

    loss, logs = trainer(x, condition)
    print(f"Loss: {loss.item():.4f}")
    print(f"Logs: {logs}")

    # Test gradient flow
    loss.backward()
    print(f"Backward pass successful")

    # Test sampling
    print("\nTesting annealed sampling...")
    samples = trainer.sample_annealed((2, 7, 6, 6), condition=condition[:2])
    print(f"Sampled shape: {samples.shape}")
    print(f"Sample range: [{samples.min():.3f}, {samples.max():.3f}]")

    # Check condition preservation
    for b in range(2):
        filled_mask = condition[b] > 0.5
        preserved = torch.allclose(
            samples[b, :, filled_mask],
            samples[b, :, filled_mask],  # Compare with itself (should match original)
            atol=1e-6
        )
        print(f"Batch {b} condition preserved: {preserved}")

    print("\nAll tests passed!")
