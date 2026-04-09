"""
Sudoku Energy Model for IRED Training

CNN-based energy function adapted for 6x6 Sudoku probability distributions.
"""

import torch
import torch.nn as nn
import math
from models.swish import Swish


class SudokuEnergy(nn.Module):
    """
    Energy model for 6x6 Sudoku IRED training.

    Input: (B, 7, 6, 6) - 7 channels for probability distribution
        - Channel 0: Certainty (1=filled, 0=empty)
        - Channels 1-6: One-hot encoding of values 1-6

    Output: (B,) - energy per puzzle configuration
    """

    def __init__(self, conf):
        super().__init__()

        # Architecture parameters
        hidden_features = 32
        c_hid1 = hidden_features // 2   # 16
        c_hid2 = hidden_features         # 32
        c_hid3 = hidden_features * 2     # 64

        # Get config with safe defaults
        sudoku_ired_conf = conf.get("sudoku_ired", {})
        self.num_landscapes = int(sudoku_ired_conf.get("num_landscapes", 50))
        energy_dim = int(sudoku_ired_conf.get("energy_dim", 128))

        # Convolutional trunk adapted for 6x6 input with 7 channels
        self.conv_trunk = nn.Sequential(
            nn.Conv2d(7, c_hid1, kernel_size=3, stride=1, padding=1),  # (6, 6)
            Swish(),
            nn.Conv2d(c_hid1, c_hid2, kernel_size=3, stride=2, padding=1),  # (3, 3)
            Swish(),
            nn.Conv2d(c_hid2, c_hid3, kernel_size=3, stride=1, padding=1),  # (3, 3)
            Swish(),
            nn.AdaptiveAvgPool2d(1),  # Global pooling -> (B, c_hid3, 1, 1)
            nn.Flatten(),  # (B, c_hid3)
        )

        # Landscape embedding (maintain multi-landscape approach)
        self.k_embedding = nn.Embedding(self.num_landscapes, 16)

        # Condition embedding (encodes mask pattern)
        self.condition_embedding = nn.Sequential(
            nn.Linear(36, 32),  # 6x6 = 36
            Swish(),
            nn.Linear(32, 16),
        )

        # Energy head
        trunk_dim = c_hid3  # 64
        self.energy_head = nn.Sequential(
            nn.Linear(trunk_dim + 16 + 16, c_hid2),
            Swish(),
            nn.Linear(c_hid2, c_hid1),
            Swish(),
            nn.Linear(c_hid1, energy_dim),
        )

    def forward(self, x, k_idx, condition):
        """
        Args:
            x: (B, 7, 6, 6) - probability distribution tensor
            k_idx: (B,) - landscape index
            condition: (B, 6, 6) - mask pattern (1=filled, 0=empty)

        Returns:
            energy: (B,) - energy per sample
        """
        feat = self.conv_trunk(x)  # (B, c_hid3)
        k_feat = self.k_embedding(k_idx)  # (B, 16)

        # Flatten condition and embed
        condition_flat = condition.view(condition.size(0), -1)  # (B, 36)
        cond_feat = self.condition_embedding(condition_flat)  # (B, 16)

        # Combine features
        combined = torch.cat([feat, k_feat, cond_feat], dim=-1)
        f = self.energy_head(combined)  # (B, energy_dim)

        # Return squared L2 norm as energy (guarantees E >= 0)
        energy = (f ** 2).sum(dim=-1)  # (B,)

        return energy


if __name__ == "__main__":
    # Test the model
    print("Testing SudokuEnergy model...")

    from omegaconf import OmegaConf

    # Create config
    conf = OmegaConf.create({
        'sudoku_ired': {
            'num_landscapes': 50,
            'energy_dim': 128
        }
    })

    # Initialize model
    model = SudokuEnergy(conf)
    print(f"Model initialized with {sum(p.numel() for p in model.parameters())} parameters")

    # Test forward pass
    batch_size = 4
    x = torch.randn(batch_size, 7, 6, 6)
    k_idx = torch.randint(0, 50, (batch_size,))
    condition = torch.randint(0, 2, (batch_size, 6, 6)).float()

    energy = model(x, k_idx, condition)
    print(f"Energy shape: {energy.shape}")
    print(f"Energy values: {energy}")

    # Test gradient flow
    loss = energy.sum()
    loss.backward()
    print(f"Backward pass successful")

    # Check that gradients exist
    for name, param in model.named_parameters():
        if param.grad is not None:
            print(f"  {name}: grad norm = {param.grad.norm().item():.6f}")

    print("\nAll tests passed!")
