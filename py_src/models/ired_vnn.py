"""
VNN-based Energy model for IRED training.
Uses VNNv11 (multi-head attention-style VNN) for the energy head.
"""

import sys
sys.path.append("/lfs/mercury1/0/eshaanb/VNN")

import torch
import torch.nn as nn
import torch.nn.functional as F
from models.swish import Swish
from VNNv11 import VNNv11

class IREDEnergyVNN(nn.Module):
    """
    Compact VNNv11-based Energy model for IRED training.
    Designed to match Dense IRED parameter count (~112K).

    Uses VNNv11 (multi-head VNN) instead of dense Linear layers.
    VNNv11 provides dynamic feature interaction through position-encoded heads.

    Accepts (y, k_idx, condition) where:
      - y        : (B, 1, 28, 28) image tensor
      - k_idx    : (B,)           landscape index
      - condition: (B,)           class label (0-9)

    Energy is computed as the squared L2 norm:
        E(y, k) = ||VNN_theta(y, k, condition)||^2
    """

    def __init__(self, conf):
        super().__init__()

        hidden_features = 32
        c_hid1 = hidden_features // 2
        c_hid2 = hidden_features
        c_hid3 = hidden_features * 2

        num_landscapes = int(conf.get("ired", {}).get("num_landscapes", 10))
        energy_dim = int(conf.get("ired", {}).get("energy_dim", 64))  # Reduced: 128->64

        device = conf.training.device

        # Shared conv trunk (same as original IREDEnergy)
        self.conv_trunk = nn.Sequential(
            nn.Conv2d(1, c_hid1, kernel_size=5, stride=2, padding=4),
            Swish(),
            nn.Conv2d(c_hid1, c_hid2, kernel_size=3, stride=2, padding=1),
            Swish(),
            nn.Conv2d(c_hid2, c_hid3, kernel_size=3, stride=2, padding=1),
            Swish(),
            nn.Conv2d(c_hid3, c_hid3, kernel_size=3, stride=2, padding=1),
            Swish(),
            nn.Flatten(),
        )

        # Landscape embedding
        self.k_embedding = nn.Embedding(num_landscapes, 10)

        # After conv: the actual output dimension is 256 (tested)
        trunk_dim = 256  # Actual conv trunk output
        total_input_dim = trunk_dim + 10 + 10  # trunk + k_emb + condition

        # Compact VNNv11-based energy head
        # Reduced dimensions to match ~112K parameters
        num_heads = 2  # Reduced: 4->2
        hid_dim = 64   # Reduced: 128->64
        num_layers = 2 # Unchanged

        self.input_proj = nn.Linear(total_input_dim, hid_dim)

        self.vnn = VNNv11(
            num_heads=num_heads,
            hid_dim=hid_dim,
            num_layers=num_layers,
            device=device,
            sum_last=False
        )

        self.output_proj = nn.Sequential(
            nn.Linear(hid_dim, energy_dim),
        )

    def forward(self, x, k_idx, condition):
        # x: (B, 1, 28, 28), k_idx: (B,), condition: (B,)
        condition = F.one_hot(condition, num_classes=10).float()

        feat = self.conv_trunk(x)               # (B, trunk_dim)
        k_feat = self.k_embedding(k_idx)        # (B, 10)

        # Concatenate all features
        combined = torch.cat([feat, k_feat, condition], dim=-1)  # (B, total_input_dim)

        # Project to VNN hidden dimension and add sequence dimension
        h = self.input_proj(combined).unsqueeze(1)  # (B, 1, hid_dim)

        # Pass through VNN
        h = self.vnn(h)  # (B, 1, hid_dim)

        # Output projection
        f = self.output_proj(h.squeeze(1))  # (B, energy_dim)

        # Return squared L2 norm as energy: E = ||f||^2 >= 0
        return (f ** 2).sum(dim=-1)  # (B,) — E = ||f||^2 >= 0
