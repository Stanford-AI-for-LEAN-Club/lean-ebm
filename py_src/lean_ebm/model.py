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
        )
        
        self.linear_layers = nn.Sequential(
            nn.Linear(c_hid3*4 + 10, c_hid3),
            Swish(),
            nn.Linear(c_hid3, 1)
        )
       
        # MSE Loss
        self.mse_loss = nn.MSELoss()

    def forward (self, x, condition):
        condition = F.one_hot(condition, num_classes=10)        
        x = self.cnn_layers(x)
        x = self.linear_layers(torch.cat([x, condition], dim=1))
        x = x.squeeze(dim=-1)
        return x
