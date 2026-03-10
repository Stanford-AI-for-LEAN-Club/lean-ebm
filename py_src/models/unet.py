import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from models.swish import Swish

class TimeEmbedding(nn.Module):
    """
    Maps continuous time t to a high-dimensional embedding.
    """
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
        self.mlp = nn.Sequential(
            nn.Linear(dim, dim * 4),
            Swish(),
            nn.Linear(dim * 4, dim)
        )

    def forward(self, t):
        # Sinusoidal embedding
        device = t.device
        half_dim = self.dim // 2
        embeddings = math.log(10000) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=device) * -embeddings)
        embeddings = t[:, None] * embeddings[None, :]
        embeddings = torch.cat((embeddings.sin(), embeddings.cos()), dim=-1)
        
        # MLP projection
        return self.mlp(embeddings)

class UNetBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.GroupNorm(8, out_ch),
            Swish(),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1),
            nn.GroupNorm(8, out_ch),
            Swish()
        )

    def forward(self, x):
        return self.conv(x)

class UNet(nn.Module):
    def __init__(self, conf):
        super().__init__()
        in_channels = 3  
        num_classes = 10
        base_ch = 64
        time_dim = base_ch * 8 # 512

        # 1. Conditioning modules
        self.time_mlp = TimeEmbedding(time_dim)
        self.label_emb = nn.Embedding(num_classes, time_dim)
        
        # Projection to merge time and label info
        self.cond_proj = nn.Sequential(
            nn.Linear(time_dim, time_dim),
            Swish(),
            nn.Linear(time_dim, time_dim)
        )

        # 2. Encoder (Downsampling)
        self.enc1 = UNetBlock(in_channels, base_ch)      # 32x32
        self.enc2 = UNetBlock(base_ch, base_ch * 2)      # 16x16
        self.enc3 = UNetBlock(base_ch * 2, base_ch * 4)  # 8x8
        self.pool = nn.MaxPool2d(2)

        # 3. Bottleneck
        self.bottleneck = UNetBlock(base_ch * 4, base_ch * 8) # 4x4

        # 4. Decoder (Upsampling)
        self.up3 = nn.ConvTranspose2d(base_ch * 8, base_ch * 4, kernel_size=2, stride=2)
        self.dec3 = UNetBlock(base_ch * 8, base_ch * 4) 

        self.up2 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, kernel_size=2, stride=2)
        self.dec2 = UNetBlock(base_ch * 4, base_ch * 2)

        self.up1 = nn.ConvTranspose2d(base_ch * 2, base_ch, kernel_size=2, stride=2)
        self.dec1 = UNetBlock(base_ch * 2, base_ch) 

        self.final_conv = nn.Conv2d(base_ch, in_channels, kernel_size=3, padding=1)

    def forward(self, x, t, condition):
        """
        x: [B, 3, 32, 32]
        t: [B] (Continuous values 0-1)
        condition: [B] (Class labels)
        """
        # --- Conditioning Integration ---
        t_emb = self.time_mlp(t)                # [B, 512]
        c_emb = self.label_emb(condition)       # [B, 512]
        
        # Combine and project: [B, 512, 1, 1] for spatial broadcasting
        combined_cond = self.cond_proj(t_emb + c_emb).view(-1, 512, 1, 1)

        # --- Forward Pass ---
        e1 = self.enc1(x)                        # 32x32
        e2 = self.enc2(self.pool(e1))            # 16x16
        e3 = self.enc3(self.pool(e2))            # 8x8

        # Bottleneck + Conditioning
        b = self.bottleneck(self.pool(e3))       # 4x4
        b = b + combined_cond                    # Add time + class info

        # Decoder
        d3 = self.up3(b)
        d3 = self.dec3(torch.cat([d3, e3], dim=1))

        d2 = self.up2(d3)
        d2 = self.dec2(torch.cat([d2, e2], dim=1))

        d1 = self.up1(d2)
        d1 = self.dec1(torch.cat([d1, e1], dim=1))

        return self.final_conv(d1)