# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Energy-Based Models (EBM) and Diffusion Models trained on MNIST/CIFAR-10. The project implements multiple training paradigms including EBT (Energy-Based Training), Contrastive Learning, IRED, and Diffusion models.

## Setup & Commands

Uses **uv** as the package manager (Python 3.12).
uv is installed at `~/uv_envs/bin/uv` — add to PATH before use:
```bash
export PATH="$HOME/uv_envs/bin:$PATH"
uv sync                                # Install dependencies from uv.lock
cd py_src                              # Working directory for all commands
```

Run EBM training (MNIST):
```bash
python train_mnist.py                  # Default: IRED training with Hydra config from config/conf.yaml
```

Run Diffusion training (CIFAR-10):
```bash
python train_diffusion.py              # Uses config/diffusion.yaml
```

Override Hydra config values from CLI:
```bash
python train_mnist.py training.epochs=5 ebt.steps=3 training.batch_size=16
python train_diffusion.py training.epochs=20 diffusion.sigma_max=0.5
```

Hydra writes run logs to `outputs/<date>/<time>/`.

## Project Structure

```
py_src/                 # Main source directory (cd here for all commands)
├── config/             # Hydra configs
│   ├── conf.yaml       # Main EBM config (EBT, Contrastive, IRED settings)
│   └── diffusion.yaml  # Diffusion model config
├── models/             # Model architectures
│   ├── cnn.py          # CNN for EBM (scalar energy output)
│   ├── unet.py         # UNet for Diffusion (noise prediction)
│   ├── ired.py         # IRED models (energy + denoiser)
│   └── swish.py        # Swish activation
├── ebm/                # EBM training methods
│   ├── ebt.py          # EBTTrainer (MSE between real and Langevin-generated)
│   ├── contrastive.py  # ContrastiveLearning (contrastive divergence)
│   └── ired.py         # IREDTrainer (multi-energy landscape)
├── diffusion/          # Diffusion training
│   └── diff.py         # DiffusionTrainer (DDIM/DDPM)
├── utils/              # Utilities
│   ├── trainer.py      # Generic Trainer (Accelerate + WandB wrapper)
│   └── langevin.py     # Langevin dynamics base class
├── train_mnist.py      # Entry point for EBM training
└── train_diffusion.py  # Entry point for Diffusion training
pyproject.toml          # Package config (hatchling build, uv manages deps)
```

## Architecture

### Entry Points

- **`train_mnist.py`** — EBM training on MNIST. Loads dataset, creates trainer (EBT/Contrastive/IRED), wraps in generic `Trainer`, trains via `trainer.train()`.
- **`train_diffusion.py`** — Diffusion training on CIFAR-10. Uses `DiffusionTrainer` with `UNet`.

### Models

- **`CNN`** (`models/cnn.py`) — Conv2d feature extractor with Swish activations. Takes (image, one-hot class) → outputs scalar energy.
- **`UNet`** (`models/unet.py`) — U-Net for diffusion with time embedding and class conditioning. Outputs noise prediction.
- **`IREDEnergy`** (`models/ired.py`) — Energy model with landscape index conditioning. Uses squared L2 norm for E ≥ 0.

### Training Methods

- **`LangevinTrainer`** (`utils/langevin.py`) — Base class implementing `sample_langevin()`. Generates images via gradient descent on energy with configurable gradient methods (`NONE`, `LAST_STEP`, `ALL_STEPS`) and stop conditions.
- **`EBTTrainer`** (`ebm/ebt.py`) — Energy-Based Training. Generates fake via Langevin, computes MSE loss between generated and real images.
- **`ContrastiveLearning`** (`ebm/contrastive.py`) — Contrastive divergence. Minimizes energy of real images, maximizes energy of fake (Langevin-sampled), plus L2 regularization.
- **`IREDTrainer`** (`ebm/ired.py`) — Multi-energy landscape training with score-function supervision.
- **`DiffusionTrainer`** (`diffusion/diff.py`) — DDIM/DDPM training with continuous cosine schedule. Predicts noise at random timestep.

### Generic Trainer

- **`Trainer`** (`utils/trainer.py`) — Wraps HuggingFace Accelerate for multi-GPU/mixed-precision + WandB. Handles optimizer (AdamW), gradient clipping, checkpointing, and evaluation. Calls `model.forward()` which should return `(loss, logs_dict)`.

## Key Dependencies

- **Hydra** (`hydra-core`) — Config management via `@hydra.main` decorator
- **Accelerate** — Multi-GPU/mixed-precision training wrapper
- **WandB** — Experiment tracking via Accelerate's `init_trackers`
- **PyTorch + torchvision** — Models and MNIST/CIFAR-10 datasets
- **OpenCV** — Saving debug images during training

## Config Parameters

### `config/conf.yaml` (EBM)

- `ebt.steps` / `ebt.alpha` / `ebt.clamp_grad` — EBT Langevin sampling: steps, step size, gradient clamping
- `contrastive.steps` / `contrastive.alpha` / `contrastive.reg_coef` — Contrastive training parameters
- `ired.num_landscapes` / `ired.sigma_min/max` — IRED energy landscape count and noise schedule
- `training.epochs` / `training.batch_size` / `training.learning_rate` — Standard training params
- `training.save_steps` / `training.print_every` — Checkpoint and logging frequency

### `config/diffusion.yaml` (Diffusion)

- `diffusion.sigma_min` / `diffusion.sigma_max` — Cosine schedule boundaries for noise scale
- `model.steps` / `model.alpha` — Diffusion sampling parameters

## Running Experiments

The entry point scripts directly instantiate trainers with models. To switch between training methods, modify the trainer instantiation in `train_mnist.py`:

```python
# EBT
trainer = Trainer(model=EBTTrainer(CNN(conf), conf), config=conf)

# Contrastive
trainer = Trainer(model=ContrastiveLearning(CNN(conf), conf), config=conf)

# IRED
trainer = Trainer(model=IREDTrainer(IREDEnergy(conf), conf), config=conf)
```
