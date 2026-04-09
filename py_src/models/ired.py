import torch.nn as nn
import torch
import torch.nn.functional as F
from random import randint
from models.swish import Swish

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
        )

        # Landscape embedding: maps integer k -> vector of same width as trunk output
        self.k_embedding = nn.Embedding(num_landscapes, 10)

        # Projects fused features to energy_dim so E = ||f||^2 is always >= 0
        # Note: conv trunk outputs 256 features (tested)
        self.energy_head = nn.Sequential(
            nn.Linear(256 + 10 + 10, c_hid3*2),
            Swish(),
            nn.Linear(c_hid3*2, c_hid3),
            Swish(),
            nn.Linear(c_hid3, energy_dim),
        )

    def forward(self, x, k_idx, condition):
        # x: (B, 1, 28, 28), k_idx: (B,)
        condition = F.one_hot(condition, num_classes=10)
        feat = self.conv_trunk(x)               # (B, c_hid3)
        k_feat = self.k_embedding(k_idx)        # (B, c_hid3)
        f = self.energy_head(torch.cat([feat,k_feat,condition], dim=-1))     # (B, energy_dim)

        # Return squared L2 norm as energy: E = ||f||^2 >= 0
        return (f ** 2).sum(dim=-1)             # (B,) — E = ||f||^2 >= 0

import torch
import torch.nn as nn
import torch.nn.functional as F

class IREDUnet(nn.Module):
    def __init__(self, conf):
        super().__init__()
        
        num_landscapes = int(conf.get("ired", {}).get("num_landscapes", 10))
        num_classes = 10 
        self.time_emb_dim = 64 
        
        # 1. Conditioning Embeddings
        self.k_embedding = nn.Embedding(num_landscapes, self.time_emb_dim)
        self.cond_embedding = nn.Embedding(num_classes, self.time_emb_dim)
        
        # Combined embedding MLP (outputs dimension 256)
        cond_out_dim = self.time_emb_dim * 4
        self.mlp_cond = nn.Sequential(
            nn.Linear(self.time_emb_dim * 2, cond_out_dim),
            nn.SiLU(),
            nn.Linear(cond_out_dim, cond_out_dim),
        )

        # 2. U-Net Architecture
        self.inc = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.down1 = self._make_down_block(32, 64)   
        self.down2 = self._make_down_block(64, 128)  
        
        # 3. Bottleneck with conditioning projection
        self.bottleneck_conv = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.bottleneck_emb = nn.Linear(cond_out_dim, 128) # Project emb to 128 channels
        
        # 4. Decoder with conditioning projections
        self.up1_up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.up1_emb = nn.Linear(cond_out_dim, 128 + 64)  # Project to match concat channels
        self.up1_conv = nn.Sequential(
            nn.Conv2d(128 + 64, 64, kernel_size=3, padding=1),
            nn.SiLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.SiLU()
        )
        
        self.up2_up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.up2_conv = nn.Sequential(
            nn.Conv2d(64 + 32, 32, kernel_size=3, padding=1),
            nn.SiLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.SiLU()
        )
        
        self.outc = nn.Conv2d(32, 1, kernel_size=1)

    def _make_down_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.MaxPool2d(2),
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.SiLU(),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1),
            nn.SiLU()
        )

    def forward(self, x, k_idx, condition):
        # --- 1. Compute Global Conditioning ---
        k_emb = self.k_embedding(k_idx)              
        c_emb = self.cond_embedding(condition)      
        emb = self.mlp_cond(torch.cat([k_emb, c_emb], dim=-1)) # (B, 256)
        
        # --- 2. Encoder ---
        x1 = self.inc(x)             # (B, 32, 28, 28)
        x2 = self.down1(x1)          # (B, 64, 14, 14)
        x3 = self.down2(x2)          # (B, 128, 7, 7)
        
        # --- 3. Bottleneck + Condition ---
        # Project emb and add to spatial features
        emb_bottleneck = self.bottleneck_emb(emb).unsqueeze(-1).unsqueeze(-1) 
        b = self.bottleneck_conv(x3) + emb_bottleneck 
        b = F.silu(b)
        
        # --- 4. Decoder + Condition ---
        # Up 1
        u1 = self.up1_up(b)          # (B, 128, 14, 14)
        u1 = torch.cat([u1, x2], dim=1) 
        
        # Inject condition into decoder block
        emb_u1 = self.up1_emb(emb).unsqueeze(-1).unsqueeze(-1)
        u1 = self.up1_conv(u1 + emb_u1)
        
        # Up 2
        u2 = self.up2_up(u1)         # (B, 64, 28, 28)
        u2 = torch.cat([u2, x1], dim=1)
        u2 = self.up2_conv(u2)
        
        return self.outc(u2)