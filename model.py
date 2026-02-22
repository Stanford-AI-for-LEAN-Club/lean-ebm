# model
import torch.nn as nn
import torch
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self, conf):
        super().__init__()

        # feature extractor
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)  # halves spatial dims
        self.loss_fn = nn.CrossEntropyLoss()

        # classifier
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, 1)
       
        # MSE Loss
        self.mse_loss = nn.MSELoss() 
        
        # self the step number
        self.steps = conf.model.steps
        self.batch_size = conf.training.batch_size 
        self.alpha = conf.model.alpha

        # inference
        self.samples = conf.inference.samples

    def model_forward (self, x):
        x = x.unsqueeze(1) # add one channel 
        x = self.pool(F.relu(self.conv1(x)))  # b, 1, 28, 28 -> b, 32, 14, 14
        x = self.pool(F.relu(self.conv2(x)))  # -> b, 64, 7, 7
        x = x.flatten(start_dim=1)
        x = F.relu(self.fc1(x))  # -> b, 128
        x = self.fc2(x)  # -> b, 10 (logits)
        return x

    def forward(self, x):
        y_hat = torch.randn((self.batch_size, 28, 28), requires_grad=True) # deal with shapes later

        # forward steps
        for i in range(self.steps):
            energy = self.model_forward(y_hat)
            predicted = torch.autograd.grad([energy.sum()], [y_hat], retain_graph=True)[0]
            y_hat = y_hat - self.alpha * predicted

        # calculate loss
        loss = self.mse_loss(y_hat, x)

        return loss, {
            "loss": loss.cpu().item()
        }
        
    def sampling (self, x):
        total = []
        for j in range(self.samples):
            y_hat = torch.randn((self.batch_size, 28, 28))
            min_sample_energy = None
            min_sample = None 
            for _ in range(self.steps):
                energy = self.model_forward(y_hat)
                predicted = torch.autograd.grad([energy.sum()], [y_hat], retain_graph=False)[0]
                y_hat -= self.alpha * predicted
                if min_sample_energy is None or energy < min_sample_energy:
                    min_sample = y_hat
            total.append(min_sample)
        return total 
