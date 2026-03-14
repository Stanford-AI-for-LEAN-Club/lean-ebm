# lean-ebm

Energy-Based Models (EBMs) for Lean 4 formal theorem proving — a Stanford AI for LEAN Club project.

## Motivation

Current SOTA theorem provers (DeepSeek Prover, Aristotle) use MCTS with two separate heads:
- **Policy**: a fine-tuned LLM that generates tactic candidates
- **Value**: another LLM that estimates the probability of proof success

We want to **unify both into a single EBM**: the energy score replaces the value function (lower energy = more promising tactic), and Langevin dynamics replaces the policy (gradient descent in tactic space generates candidates). This mirrors the "bitter lesson" intuition — more computation at inference time via search should yield better generalization.

## De-risking Strategy

The project runs two parallel tracks:

1. **Data-centric / synthetic data track** *(primary bet)*: Generate high-quality Lean 4 proof data using scalable oversight and automated theorem writing. Train a strong LLM baseline on this data. If the synthetic data approach works well, the LLM alone may be sufficient.

2. **EBM track** *(baseline / fallback)*: If we cannot beat the LLM with standard approaches, the EBM serves as a structured alternative — it can model uncertainty, dynamically allocate compute (harder problems = more Langevin steps), and is trained on verification rather than generation.

The MNIST experiment in this repo is the current EBM prototype, validating the training pipeline before scaling to language.

## Long-Term Vision

- Take a pretrained math-finetuned model (e.g. DeepSeek Math-7B), finetune a projection head to output a scalar energy
- Use Langevin dynamics to sample tactic chunks in embedding space
- Use the energy score as the value signal to guide MCTS proof search
- Interface with Lean 4 via [PyPantograph](https://github.com/stanford-centaur/PyPantograph)
- Benchmark on miniF2F and Veribench

## Current Implementation (MNIST Prototype)

The model learns `E(image, class) → scalar` using a CNN, then generates samples by minimizing energy via Langevin dynamics.

### Setup

```bash
uv sync
uv run python -m lean_ebm.main
```

Override config values:
```bash
uv run python -m lean_ebm.main training.epochs=5 ebt.steps=3 training.device=mps
```

### Training Methods

| Method | File | Loss |
|--------|------|------|
| EBT (active) | `ebt.py` | MSE between Langevin sample and real image; backprops through last Langevin step |
| Contrastive Divergence | `contrastive.py` | `E(real) - E(fake) + reg * (E(real)² + E(fake)²)` |
| IRED | `ired.py` | Score-function supervision (standalone, no Langevin base class) |

### Key Config (`config.yaml`)

```yaml
training:
  device: "cuda"       # change to "mps" (Apple Silicon) or "cpu"
  num_episodes: 100    # outer loops over full dataset
  epochs: 3            # inner epochs per episode

ebt:
  steps: 50            # Langevin steps
  alpha: 10            # step size
  clamp_grad: 0.03     # gradient clipping during sampling
```

## Team

William Peng, Holger Molin, Eshaan Barkataki, Matt Chen, Brando Miranda, Sanmi Koyejo

[Stanford AI for LEAN Club](https://aiforlean.org/)
