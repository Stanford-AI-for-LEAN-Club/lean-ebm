"""
Comparison Experiment: IRED with Dense Layers vs IRED with VNN
Task: Energy-based model training on MNIST
"""

import os
import sys
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from omegaconf import OmegaConf
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import time

# Add paths
sys.path.append("/lfs/mercury1/0/eshaanb/VNN")

# Import models and trainers
from models.ired import IREDEnergy
from models.ired_vnn import IREDEnergyVNN
from ebm.ired import IREDTrainer
from utils.trainer import Trainer

# Set seeds
torch.manual_seed(42)
np.random.seed(42)

# Device
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# ============= Config =============
class ConfigDict(dict):
    """Dict subclass that allows dot notation access"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = ConfigDict(v)

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return super().get(key, default)


def create_config(use_vnn=False):
    return ConfigDict({
        'training': {
            'device': str(device),
            'batch_size': 128,
            'epochs': 20,
            'learning_rate': 0.001,
            'mixed_precision': False,
            'log_every': 10,
            'save_every': 1000,
            'num_workers': 0,
        },
        'ired': {
            'num_landscapes': 5,
            'sigma_max': 0.95,
            'sigma_min': 0.01,
            'neg_corruption_scale': 0.25,
            'neg_refine_steps': 0,
            'mse_weight': 1.0,
            'contrastive_weight': 1.0,
            'reg_coef': 0.005,
            'energy_dim': 128,
            'inference_steps_per_landscape': 5,
            'inference_step_size': 0.1,
        },
        'wandb': {
            'enable': False,
        },
        'use_vnn': use_vnn
    })

# ============= Custom Tracker =============
class ComparisonTracker:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.epoch_times = []

    def update(self, epoch, train_loss, mse_loss, contrastive_loss):
        self.metrics['epoch'].append(epoch)
        self.metrics['train_loss'].append(train_loss)
        self.metrics['mse_loss'].append(mse_loss)
        self.metrics['contrastive_loss'].append(contrastive_loss)

    def save_logs(self, name):
        os.makedirs("comparison_results", exist_ok=True)
        with open(f"comparison_results/{name}_metrics.txt", 'w') as f:
            for key in self.metrics:
                f.write(f"{key}: {self.metrics[key]}\n")

# ============= Custom Trainer Wrapper =============
class ComparisonTrainer(Trainer):
    def __init__(self, model, config, tracker, model_name):
        # Minimal initialization
        self.model = model.to(config.training.device)
        self.config = config
        self.device = config.training.device
        self.tracker = tracker

        # Setup optimizer
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=config.training.learning_rate
        )

        # Count parameters
        self.num_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"{model_name} Parameters: {self.num_params:,}")

    def train(self, dl, unpack=lambda x: {"x": x[0], "condition": x[1]}):
        print(f"Training {self.model.__class__.__name__}...")
        self.model.train()

        num_epochs = self.config.training.epochs
        global_step = 0

        for epoch in range(num_epochs):
            epoch_start = time.time()
            epoch_losses = []
            epoch_mse = []
            epoch_contrastive = []

            for batch_idx, batch in enumerate(dl):
                unpacked = unpack(batch)
                x = unpacked["x"].to(self.device)
                condition = unpacked["condition"].to(self.device)

                # Forward pass
                loss, logs = self.model(x, condition)

                # Backward
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()

                epoch_losses.append(logs["loss"])
                epoch_mse.append(logs["mse_loss"])
                epoch_contrastive.append(logs["contrastive_loss"])

                global_step += 1

            # Epoch metrics
            avg_loss = np.mean(epoch_losses)
            avg_mse = np.mean(epoch_mse)
            avg_contrastive = np.mean(epoch_contrastive)
            epoch_time = time.time() - epoch_start

            self.tracker.update(epoch + 1, avg_loss, avg_mse, avg_contrastive)
            self.tracker.epoch_times.append(epoch_time)

            if (epoch + 1) % 5 == 0 or epoch == 0:
                print(f"Epoch [{epoch+1}/{num_epochs}] "
                      f"Loss: {avg_loss:.6f} | MSE: {avg_mse:.6f} | "
                      f"Contrastive: {avg_contrastive:.6f} | Time: {epoch_time:.2f}s")

# ============= Data Loading =============
def get_dataloaders(batch_size):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=0.5, std=0.5)  # -1 to 1
    ])

    train_dataset = datasets.MNIST(
        root='../data/',
        train=True,
        transform=transform,
        download=True
    )

    val_dataset = datasets.MNIST(
        root='../data/',
        train=False,
        transform=transform,
        download=True
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    return train_loader, val_loader

# ============= Run Experiment =============
def run_experiment():
    print("\n" + "="*70)
    print("IRED Comparison: Dense vs VNN")
    print("="*70)

    # Get data
    batch_size = 128
    train_loader, val_loader = get_dataloaders(batch_size)
    print(f"Train samples: {len(train_loader.dataset)} | Val samples: {len(val_loader.dataset)}")

    results = {}

    # ============= Train IRED with Dense =============
    print("\n" + "-"*70)
    print("Training IRED with Dense Layers")
    print("-"*70)

    config_dense = create_config(use_vnn=False)
    dense_tracker = ComparisonTracker()

    dense_model = IREDTrainer(IREDEnergy(config_dense), config_dense)

    dense_trainer = ComparisonTrainer(
        dense_model, config_dense, dense_tracker, "Dense IRED"
    )

    dense_trainer.train(train_loader)
    dense_tracker.save_logs("dense_ired")

    results['dense'] = {
        'metrics': dense_tracker.metrics,
        'params': dense_trainer.num_params,
        'avg_time': np.mean(dense_tracker.epoch_times)
    }

    # Clean up
    del dense_model, dense_trainer
    torch.cuda.empty_cache()

    # ============= Train IRED with VNN =============
    print("\n" + "-"*70)
    print("Training IRED with VNN")
    print("-"*70)

    config_vnn = create_config(use_vnn=True)
    vnn_tracker = ComparisonTracker()

    vnn_model = IREDTrainer(IREDEnergyVNN(config_vnn), config_vnn)

    vnn_trainer = ComparisonTrainer(
        vnn_model, config_vnn, vnn_tracker, "VNN IRED"
    )

    vnn_trainer.train(train_loader)
    vnn_tracker.save_logs("vnn_ired")

    results['vnn'] = {
        'metrics': vnn_tracker.metrics,
        'params': vnn_trainer.num_params,
        'avg_time': np.mean(vnn_tracker.epoch_times)
    }

    return results

# ============= Plot Results =============
def plot_results(results):
    os.makedirs("comparison_results", exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('IRED Dense vs VNN: Training Comparison', fontsize=16, fontweight='bold')

    epochs = results['dense']['metrics']['epoch']

    # 1. Total Loss
    ax1 = axes[0]
    ax1.plot(epochs, results['dense']['metrics']['train_loss'], 'b-', label='Dense IRED', linewidth=2)
    ax1.plot(epochs, results['vnn']['metrics']['train_loss'], 'r-', label='VNN IRED', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Total Loss')
    ax1.set_title('Total Training Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')

    # 2. MSE Loss (Score Matching)
    ax2 = axes[1]
    ax2.plot(epochs, results['dense']['metrics']['mse_loss'], 'b-', label='Dense IRED', linewidth=2)
    ax2.plot(epochs, results['vnn']['metrics']['mse_loss'], 'r-', label='VNN IRED', linewidth=2)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('MSE Loss')
    ax2.set_title('Score Matching Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')

    # 3. Contrastive Loss
    ax3 = axes[2]
    ax3.plot(epochs, results['dense']['metrics']['contrastive_loss'], 'b-', label='Dense IRED', linewidth=2)
    ax3.plot(epochs, results['vnn']['metrics']['contrastive_loss'], 'r-', label='VNN IRED', linewidth=2)
    ax3.set_xlabel('Epoch')
    ax3.set_ylabel('Contrastive Loss')
    ax3.set_title('Contrastive Loss')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('comparison_results/training_curves.png', dpi=300, bbox_inches='tight')
    print(f"\nPlots saved to comparison_results/training_curves.png")

    # Final comparison bar chart
    fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))
    fig2.suptitle('Final Performance Comparison', fontsize=16, fontweight='bold')

    models = ['Dense IRED', 'VNN IRED']
    final_losses = [
        results['dense']['metrics']['train_loss'][-1],
        results['vnn']['metrics']['train_loss'][-1]
    ]
    params = [results['dense']['params'], results['vnn']['params']]
    times = [results['dense']['avg_time'], results['vnn']['avg_time']]

    colors = ['#3498db', '#e74c3c']

    axes2[0].bar(models, final_losses, color=colors, alpha=0.7)
    axes2[0].set_ylabel('Final Loss')
    axes2[0].set_title('Final Training Loss')
    axes2[0].grid(True, alpha=0.3, axis='y')
    axes2[0].set_yscale('log')

    axes2[1].bar(models, params, color=colors, alpha=0.7)
    axes2[1].set_ylabel('Parameters')
    axes2[1].set_title('Model Parameters')
    axes2[1].grid(True, alpha=0.3, axis='y')

    axes2[2].bar(models, times, color=colors, alpha=0.7)
    axes2[2].set_ylabel('Avg Epoch Time (s)')
    axes2[2].set_title('Training Speed')
    axes2[2].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('comparison_results/final_comparison.png', dpi=300, bbox_inches='tight')
    print(f"Final comparison saved to comparison_results/final_comparison.png")

def print_summary(results):
    print("\n" + "="*70)
    print("EXPERIMENT SUMMARY")
    print("="*70)

    print(f"\n{'Metric':<25} {'Dense IRED':<20} {'VNN IRED':<20} {'Difference':<15}")
    print("-"*70)

    dense_params = results['dense']['params']
    vnn_params = results['vnn']['params']
    param_diff = ((vnn_params - dense_params) / dense_params) * 100
    print(f"{'Parameters':<25} {dense_params:>18,} {vnn_params:>18,} {param_diff:>+13.1f}%")

    dense_time = results['dense']['avg_time']
    vnn_time = results['vnn']['avg_time']
    time_diff = ((vnn_time - dense_time) / dense_time) * 100
    print(f"{'Avg Epoch Time (s)':<25} {dense_time:>18.4f} {vnn_time:>18.4f} {time_diff:>+13.1f}%")

    print("-"*70)

    dense_final = results['dense']['metrics']['train_loss'][-1]
    vnn_final = results['vnn']['metrics']['train_loss'][-1]
    loss_diff = ((dense_final - vnn_final) / dense_final) * 100

    print(f"{'Final Loss':<25} {dense_final:>18.6f} {vnn_final:>18.6f} {loss_diff:>+13.1f}%")

    print("-"*70)

    if results['vnn']['metrics']['train_loss'][-1] < results['dense']['metrics']['train_loss'][-1]:
        print("\n🏆 VNN IRED achieved lower final loss!")
    elif results['dense']['metrics']['train_loss'][-1] < results['vnn']['metrics']['train_loss'][-1]:
        print("\n🏆 Dense IRED achieved lower final loss!")
    else:
        print("\n⚖️ Both models performed similarly!")

    print("="*70)

if __name__ == "__main__":
    # Change to py_src directory
    os.chdir("/lfs/mercury1/0/eshaanb/lean-ebm/py_src")

    # Run experiment
    results = run_experiment()

    # Plot results
    plot_results(results)

    # Print summary
    print_summary(results)

    print("\n✅ Experiment completed! Check the 'comparison_results' folder for outputs.")
