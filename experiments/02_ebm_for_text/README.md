# Experiment 02: EBM for Text (Residual Energy Critic)

## What

Residual energy-based model (EBM) that acts as a **critic over structured search states** for code generation and Lean 4 theorem proving. Instead of replacing the base LM, the EBM scores candidates produced by a strong proposal model:

```
p_θ(τ | x) ∝ q_φ(τ | x) · exp(-E_θ(x, τ))
```

Architecture (Version 1 / prototype):
- **Proposal model** (`q_φ`): Pretrained causal LM (e.g. CodeGen, StarCoder)
- **Energy model** (`E_θ`): Bidirectional cross-encoder (e.g. CodeBERT) with 3 heads:
  - Ranking head — scalar energy for contrastive ranking
  - Value head — cost-to-go (estimated remaining work)
  - Feedback head — error-type classification (teaches *why* code is wrong)
- **Tool adapters**: Python compiler/tests, Lean 4 verifier (scaffold)
- **Retrieval**: BM25 context retrieval
- **Inference**: Best-first search over structured states

## Why

Pure token-level EBM sampling is unlikely to beat a strong LM for discrete text. The more plausible architecture is proposer + critic: the LM generates candidates, the EBM ranks them and guides search. This matches residual text EBM results (Deng et al. 2020), code EBM compilability constraints (Chen et al. 2021), and modern verifier-in-the-loop theorem proving.

## Directory Structure

```
experiments/02_ebm_for_text/
├── gpt5pro_proposal.md        # Full design doc / proposal
├── README.md                  # This file
├── config/
│   └── ebm_text.yaml          # Hydra config
├── scripts/
│   ├── train.sh               # Launch training
│   └── search.sh              # Launch search
└── ebm_for_text/              # Python package
    ├── __init__.py
    ├── main.py                # Entry point (train / search)
    ├── data_types.py          # Core dataclasses (SearchState, Action, etc.)
    ├── energy_model.py        # Cross-encoder with 3 heads + loss functions
    ├── proposal.py            # Causal LM wrapper for candidate generation
    ├── tools.py               # Tool adapters (Python exec, Lean scaffold)
    ├── retrieval.py           # BM25 context retrieval
    ├── search.py              # Best-first search loop
    ├── trainer.py             # Contrastive ranking training loop
    └── dataset.py             # Training data loading + synthetic negatives
```

## How to Run

### Training (demo data)

```bash
cd experiments/02_ebm_for_text
bash scripts/train.sh
```

### Training (custom JSONL data)

```bash
bash scripts/train.sh training.data_path=path/to/data.jsonl training.epochs=20
```

JSONL format — each line:
```json
{
  "problem": "Write a function ...",
  "positive": {"code": "def foo(): ...", "value_target": 0.0, "error_category": null},
  "negatives": [
    {"code": "def foo( ...", "diagnostics": ["SyntaxError"], "value_target": 5.0, "error_category": "syntax"},
    ...
  ]
}
```

### Search (inference)

```bash
bash scripts/search.sh checkpoint=checkpoints/step_500.pt
```

### Override any config from CLI (Hydra)

```bash
bash scripts/train.sh energy_model.encoder_name=roberta-base training.learning_rate=3e-5 device=cpu
```

## Key Design Decisions

1. **Hard constraints as masks, not soft energy** (§3): Syntax errors and type errors are pruned immediately by the tool adapter. The energy model only ranks valid candidates.
2. **Contrastive / listwise ranking loss** (§4): InfoNCE over (positive, hard negatives). No attempt at exact EBM likelihood.
3. **Three heads** (§8): Ranking tells *which* candidate is best; value estimates remaining work for search guidance; feedback predicts error type as an auxiliary signal.
4. **Best-first search** (§5): Priority queue over states, expanding by lowest cumulative energy. Natural fit for both code repair and tactic-level theorem proving.

## Metrics

- **Ranking accuracy**: How often the positive has lowest energy in a contrastive set
- **Search solve rate**: Fraction of problems solved within budget
- **Nodes-to-solution**: Average expansions needed for solved problems
- **Value head correlation**: Spearman correlation between predicted and actual remaining steps
