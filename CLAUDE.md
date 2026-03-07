# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Energy-Based Model (EBM) trained on MNIST. The model learns a scalar energy function over images, then generates samples by gradient descent in input space (Langevin dynamics).

## Setup & Commands

Uses **uv** as the package manager (Python 3.12).
uv is installed at `~/uv_envs/bin/uv` — add to PATH before use:
```bash
export PATH="$HOME/uv_envs/bin:$PATH"
uv sync                                # Install dependencies from uv.lock
uv run python -m lean_ebm.main         # Run training (uses Hydra, config from config.yaml)
```

Override Hydra config values from CLI:
```bash
uv run python -m lean_ebm.main training.epochs=5 ebt.steps=3 training.batch_size=16
```

Hydra writes run logs to `outputs/<date>/<time>/`.

## Project Structure

```
py_src/lean_ebm/     # Python package (all source code lives here)
config.yaml          # Hydra config (project root)
pyproject.toml       # Package config (hatchling build, uv manages deps)
```

## Architecture

All Python modules live under `py_src/lean_ebm/` and use relative imports.

- **`main.py`** — Entry point. Loads MNIST, creates `EBTTrainer(CNN(...))` wrapped in a generic `Trainer`, builds a single DataLoader, and loops over `num_episodes` calling `trainer.train()`.
- **`model.py`** — `CNN` class. Conv2d feature extractor (with Swish activations) that takes an image + one-hot class condition and outputs a scalar energy value.
- **`langevin.py`** — `LangevinTrainer` base class (extends `nn.Module`). Implements `sample_langevin()` which generates images by iterative gradient descent on the energy, with configurable gradient methods (`NONE`, `LAST_STEP`, `ALL_STEPS`) and stop conditions (`StopStep`, `StopEnergyGradient`).
- **`ebt.py`** — `EBTTrainer` (extends `LangevinTrainer`). The active training method. Generates fake images via Langevin sampling, computes MSE loss between generated and real images.
- **`contrastive.py`** — `ContrastiveLearning` (extends `LangevinTrainer`). Alternative training method using contrastive divergence: minimizes energy of real images, maximizes energy of fake (Langevin-sampled) images, plus L2 regularization.
- **`ired.py`** — Alternative `ContrastiveLearning` implementation with score-function supervision and energy landscape loss (standalone, does not use `LangevinTrainer`).
- **`trainer.py`** — Generic `Trainer` wrapping HuggingFace Accelerate for multi-GPU/mixed-precision and WandB logging. Handles optimizer, gradient clipping, checkpointing, and evaluation. Has both `train()` (full dataloader) and `train_single()` (single sample, for RL/online learning).
- **`config.yaml`** — Hydra config (at project root) with model, ebt, contrastive, training, inference, memory, and wandb sections.
- **`dataset.py`** / **`energy.py`** — Currently empty.

## Key Dependencies

- **Hydra** (`hydra-core`) for config management — `@hydra.main` decorator in `main.py`
- **Accelerate** for distributed training — wraps model/optimizer in `trainer.py`
- **WandB** for experiment tracking — initialized through Accelerate's `init_trackers`
- **PyTorch + torchvision** for the model and MNIST dataset
- **OpenCV** (`opencv-python`) for saving debug images during training

## Config Parameters (config.yaml)

- `ebt.steps` / `ebt.alpha` / `ebt.clamp_grad` — EBT Langevin sampling: number of steps, step size, gradient clamping
- `contrastive.steps` / `contrastive.alpha` / `contrastive.reg_coef` — Contrastive training: sampling steps, step size, regularization coefficient
- `training.num_episodes` — Outer loop count (each episode iterates the full dataset)
- `training.save_steps` / `training.print_every` — Checkpoint and logging frequency (in optimizer steps)
