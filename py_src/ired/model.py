# model
import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint

class Swish(nn.Module):
    def forward(self, x):
        return x * torch.sigmoid(x)


class CNN(nn.Module):
    def __init__(self, conf):
        super().__init__()

        # We increase the hidden dimension over layers. Here pre-calculated for simplicity.
        hidden_features = 32
        c_hid1 = hidden_features//2
        c_hid2 = hidden_features
        c_hid3 = hidden_features*2

        # Series of convolutions and Swish activation functions
        self.cnn_layers = nn.Sequential(
            nn.Conv2d(1, c_hid1, kernel_size=5, stride=2, padding=4), # [16x16] - Larger padding to get 32x32 image
            Swish(),
            nn.Conv2d(c_hid1, c_hid2, kernel_size=3, stride=2, padding=1), #  [8x8]
            Swish(),
            nn.Conv2d(c_hid2, c_hid3, kernel_size=3, stride=2, padding=1), # [4x4]
            Swish(),
            nn.Conv2d(c_hid3, c_hid3, kernel_size=3, stride=2, padding=1), # [2x2]
            Swish(),
            nn.Flatten(),
            nn.Linear(c_hid3*4, c_hid3),
            Swish(),
            nn.Linear(c_hid3, 1)
        )
       
        # MSE Loss
        self.mse_loss = nn.MSELoss()

    def forward (self, x):
        x = self.cnn_layers(x).squeeze(dim=-1)
        return x


class IREDEnergy(nn.Module):
    """
    Energy model for IRED training.

    Accepts (y, k_idx) where:
      - y      : (B, 1, 28, 28) image tensor (the candidate solution)
      - k_idx  : (B,)           landscape index in [0, num_landscapes)

    Energy is computed as the squared L2 norm of a learned projection:
        E(y, k) = ||f_theta(y, k)||^2

    This guarantees E >= 0 with a natural minimum at zero, eliminating
    the need for explicit energy regularization while keeping gradients
    dE/dy expressive (they are a weighted sum of `energy_dim` gradient fields).
    """
    def __init__(self, conf):
        super().__init__()

        hidden_features = 32
        c_hid1 = hidden_features // 2
        c_hid2 = hidden_features
        c_hid3 = hidden_features * 2
        k_embed_dim = c_hid3  # match feature dimension for clean additive injection

        num_landscapes = int(conf.get("ired", {}).get("num_landscapes", 10))
        energy_dim = int(conf.get("ired", {}).get("energy_dim", 128))

        # Shared conv trunk — identical structure to CNN but stops before scalar head
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
            nn.Linear(c_hid3 * 4, c_hid3),
            Swish(),
        )

        # Landscape embedding: maps integer k -> vector of same width as trunk output
        self.k_embedding = nn.Embedding(num_landscapes, k_embed_dim)

        # Projects fused features to energy_dim so E = ||f||^2 is always >= 0
        self.energy_head = nn.Sequential(
            Swish(),
            nn.Linear(c_hid3, energy_dim),
        )

    def forward(self, y, k_idx):
        # y: (B, 1, 28, 28), k_idx: (B,)
        feat = self.conv_trunk(y)               # (B, c_hid3)
        k_feat = self.k_embedding(k_idx)        # (B, c_hid3)
        f = self.energy_head(feat + k_feat)     # (B, energy_dim)
        return (f ** 2).sum(dim=-1)             # (B,) — E = ||f||^2 >= 0
