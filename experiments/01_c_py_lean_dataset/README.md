# Experiment 01: Synthetic C-to-Lean4 Dataset Generation

## What

Generate a dataset containing C and Python functions, their translations into Lean4, test cases that verify faithful representation, theorems about the Lean algorithms that prove correctness, and proofs of those theorems.

## Why

To create training data (`StanfordAILean/c-py-dataset` on HuggingFace) for learning Lean4 translations and proofs from imperative code. This supports the broader goal of using EBMs and MCTS for automated theorem proving in Lean4.

## Pipeline

1. **Source**: Scrape C/Python functions from [bigcode/the-stack](https://huggingface.co/datasets/bigcode/the-stack)
2. **Filter**: Skip functions with OS-level deps, inline asm, global mutable state, etc.
3. **Call-graph ordering**: Topologically sort functions, process leaves first
4. **Translation**: For each function generate Lean4 translation + test cases + theorems + proofs
5. **Validation**: Run Lean compiler checks, cross-check C/Py vs Lean test results, verify proofs
6. **Upload**: Push to HuggingFace `StanfordAILean/c-py-dataset`

## Output Schema

Each record is a JSON object with keys:
- `language`, `source`, `lean_translation`, `tests`, `lean_tests`
- `theorems` (list of `{name, statement, proof}`)
- `deps_fully_translated`, `axiomatized_deps`, `skip_reason`

## Key Decisions

- Use axiomatization for dependencies outside the dataset or that were skipped
- Model C arrays as `Array α` or `Fin n → α`, structs as Lean `structure`
- Use `UInt32`/`UInt64` for wrapping integer semantics, not `Nat`
- Use `Float` for doubles, `Float.isNaN`/`Float.isInf` for special values
- Floating-point equality in theorems uses epsilon bounds, not `=`

## Metrics

- Number of functions translated
- Proof completion rate (vs `sorry` fallbacks)
- Test case pass rate (C/Py vs Lean agreement)

## Directory Structure

```
experiments/01_c_py_lean_dataset/
├── README.md                  # This file
├── PROMPT.md                  # Full generation prompt
└── scripts/                   # Runbooks (to be added)
```
