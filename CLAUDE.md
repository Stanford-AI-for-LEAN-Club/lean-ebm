# Claude Code: read `~/agents-config/INDEX_RULES.md` for all agent documentation and routing.
# If `~/agents-config/` is not present, clone it: `git clone https://github.com/brando90/agents-config.git ~/agents-config`

@/dfs/scratch0/brando9/CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Energy-Based Model (EBM) trained on MNIST — a prototype toward using EBMs for Lean 4 theorem proving. The long-term goal is to replace the separate policy + value heads in MCTS-based theorem provers (e.g. DeepSeek Prover) with a single EBM that unifies both: lower energy = more promising proof tactic. The MNIST experiment is the current working prototype: the model learns a scalar energy function over images, then generates samples by gradient descent in input space (Langevin dynamics).

## Research Context (`experiments/`)

- `experiments/00_lm_mini_f2f/` — Planned experiment: LoRA fine-tune an 8B open-weight model on miniF2F
- `experiments/research_journal/` — Slide notes and journal from the Stanford AI for LEAN Club (March 2026). Key ideas: use EBM + Langevin to sample tactic chunks; use energy score as the value function to guide MCTS; benchmark on miniF2F and Veribench; interface with Lean via PyPantograph.

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

- **`main.py`** — Entry point. Loads MNIST from `../4D-Dyn/flow-matching-mnist/data/` (hardcoded path), creates `EBTTrainer(CNN(...))` wrapped in `Trainer`, and runs `num_episodes` outer loops each calling `trainer.train()` (which itself loops `epochs` times over the full DataLoader).
- **`model.py`** — `CNN` class. Four Conv2d layers with Swish activations, then two linear layers. Takes `(image, condition_label)` and outputs a scalar energy. Condition is one-hot encoded from class index inside `forward`.
- **`langevin.py`** — `LangevinTrainer` base class (`nn.Module`). Core method is `sample_langevin()`: starts from random noise, iteratively calls `self.model` to get energy, computes `∂E/∂x`, and steps `x -= 0.5 * step_size * grad + noise`. `GradientMethod` controls whether `create_graph=True` (for backprop through sampling): `NONE`=no graph, `LAST_STEP`=graph only on final step, `ALL_STEPS`=graph through all steps. Also saves debug images via OpenCV.
- **`ebt.py`** — `EBTTrainer` (extends `LangevinTrainer`). Uses `GradientMethod.LAST_STEP` so the loss (`MSE(x_fake, x_real)`) backprops through only the last Langevin step into the model weights.
- **`contrastive.py`** — `ContrastiveLearning` (extends `LangevinTrainer`). Uses `GradientMethod.NONE` (no graph through sampling). Loss = `E(real).mean() - E(fake).mean() + reg_coef * (E(real)² + E(fake)²).mean()`.
- **`ired.py`** — Standalone alternative; score-function supervision and energy landscape loss. Does not use `LangevinTrainer`.
- **`trainer.py`** — Generic `Trainer` wrapping HuggingFace Accelerate (AdamW optimizer, gradient clipping, WandB logging via `init_trackers`). `train(dl, unpack)` iterates `epochs` over a DataLoader; `train_single(sample)` trains on one sample (for RL/online use). Checkpoints saved to `training.checkpoint_dir`.
- **`dataset.py`** / **`energy.py`** — Currently empty stubs.

## Key Notes

- **Training loop structure**: outer `num_episodes` loop (in `main.py`) × inner `epochs` loop (in `Trainer.train`) × batches. Total optimizer steps = `num_episodes × epochs × (dataset_size / batch_size)`.
- **Device**: `config.yaml` defaults to `device: "cuda"`. Change to `"mps"` on Apple Silicon or `"cpu"` for CPU-only.
- **MNIST data path** is hardcoded in `main.py` as `../4D-Dyn/flow-matching-mnist/data/` relative to the Hydra working directory (which may differ from the project root). Set `download=True` to auto-fetch if missing.
- **WandB**: configured in `config.yaml` under `wandb:`. The API key in `config.yaml` is a comment — set it via `wandb login` or the `WANDB_API_KEY` env var instead.
- **Debug images**: `test.png` (fake) and `real.png` (real) are written periodically during training by `LangevinTrainer.save_imgs()` to the current working directory.

## Config Parameters (config.yaml)

- `ebt.steps` / `ebt.alpha` / `ebt.clamp_grad` — EBT Langevin: number of steps, step size, gradient clamping
- `contrastive.steps` / `contrastive.alpha` / `contrastive.reg_coef` — Contrastive: steps, step size, L2 regularization weight
- `training.num_episodes` / `training.epochs` — Outer episode count and inner epoch count per episode
- `training.save_steps` / `training.print_every` — Checkpoint and console logging frequency (in optimizer steps)

## API Keys

Keys live at `~/keys/` (DFS-backed, shared across all servers):
```bash
export ANTHROPIC_API_KEY=$(cat ~/keys/anthropic_bm_key_koyejolab.txt)
export OPENAI_API_KEY=$(cat ~/keys/openai_api_brandos_personal_key.txt)
export HF_TOKEN=$(cat ~/keys/master_hf_token.txt)
export WANDB_API_KEY=$(cat ~/keys/brandos_wandb_key.txt)
```

WandB is configured in `config.yaml` — set the key via env var (above) rather than hardcoding it.

## GPU Usage

Check free GPUs before launching training:
```bash
nvidia-smi --query-gpu=index,memory.used,memory.free,utilization.gpu --format=csv,noheader
# Free = memory.used < 1000 MiB
```

`config.yaml` defaults to `device: "cuda"`. Change to `"mps"` (Apple Silicon) or `"cpu"` as needed.

## File Documentation

Always include a single-sentence TLDR comment at the top of each file describing what it does.

## Experiment Conventions

**Keep this file fresh.** When you move files, rename scripts, or refactor an experiment, update `CLAUDE.md` in the same commit.

**README = design doc, scripts/ = runbooks.** Each experiment dir has a `README.md` (what/why/metrics/decisions) and a `scripts/` dir (how to run). Keep them in sync whenever files move.

**When you refactor or move files:**
1. Update the `Directory Structure` block in the experiment's `README.md`
2. Update any path references in `README.md` and `CLAUDE.md`
3. Archive superseded scripts to `scripts/archive/` — don't leave both copies active in `scripts/`
