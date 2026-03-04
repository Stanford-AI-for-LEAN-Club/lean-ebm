# Open-Source LLMs for Lean 4 Theorem Proving

**Date:** 2026-03-03
**Goal:** Find the best model we can *train* on 1x NVIDIA B200 (~183 GB VRAM, GPU 6 is free).

---

## Available Models (sorted by MiniF2F-test performance)

| Model | Params | MiniF2F-test | Base Model | HuggingFace |
|-------|--------|-------------|------------|-------------|
| Goedel-Prover-V2-32B | 32B | **90.4%** (pass@32, self-correction) | Qwen | [link](https://huggingface.co/Goedel-LM/Goedel-Prover-V2-32B) |
| DeepSeek-Prover-V2-671B | 671B | 88.9% (pass@32) | DeepSeek-V3 | [link](https://huggingface.co/deepseek-ai/DeepSeek-Prover-V2-671B) |
| Goedel-Prover-V2-8B | 8B | **84.6%** (pass@32) | Qwen | [link](https://huggingface.co/Goedel-LM/Goedel-Prover-V2-8B) |
| Kimina-Prover-72B | 72B | 84.0% (pass@32) | Qwen2.5-72B | [link](https://huggingface.co/AI-MO/Kimina-Prover-72B) |
| Leanabell-Prover-V2 | 7B | 78.2% (pass@128) | DSP-V1.5 | [GitHub](https://github.com/Leanabell-LM/Leanabell-Prover-V2) |
| DeepSeek-Prover-V2-7B | 7B | ~75% (pass@32) | DSP-V1.5 | [link](https://huggingface.co/deepseek-ai/DeepSeek-Prover-V2-7B) |
| Kimina-Prover-Distill-1.7B | 1.7B | — | Qwen2.5 | [link](https://huggingface.co/AI-MO/Kimina-Prover-Distill-1.7B) |
| Goedel-Prover-V1 (SFT) | 7B | 57.6% (pass@32) | DSP-V1.5 | [link](https://huggingface.co/Goedel-LM/Goedel-Prover-SFT) |
| InternLM2-Math-Plus-7B | 7B | N/A (math-general) | InternLM2 | [link](https://huggingface.co/internlm/internlm2-math-plus-7b) |

---

## VRAM Budget Analysis (1x B200, 183 GB)

Rule of thumb (BF16 mixed-precision, AdamW):
- **Full fine-tuning:** ~16 bytes/param (weights + optimizer + grads) + activations
- **LoRA fine-tuning:** ~2 bytes/param (frozen weights) + small LoRA overhead + activations

| Model | Full FT (est.) | LoRA FT (est.) | Fits for Full FT? | Fits for LoRA? |
|-------|---------------|----------------|-------------------|----------------|
| Kimina-Distill-1.7B | ~27 GB | ~5 GB | YES | YES |
| DSP-V2-7B / Leanabell-V2 | ~112 GB | ~20 GB | YES (w/ grad ckpt) | YES |
| Goedel-V2-8B | ~128 GB | ~22 GB | YES (w/ grad ckpt) | YES |
| Goedel-V2-32B | ~512 GB | ~80 GB | NO | YES |
| Kimina-72B | ~1.1 TB | ~160 GB | NO | TIGHT |
| DSP-V2-671B | ~10 TB | ~1.3 TB | NO | NO |

---

## Recommendations

### Best overall: Goedel-Prover-V2-32B with LoRA
- **90.4%** MiniF2F (SOTA among open models)
- LoRA needs ~80 GB -- fits comfortably on 183 GB B200
- Full FT does NOT fit, but LoRA + QLoRA would work well

### Best for full fine-tuning: Goedel-Prover-V2-8B
- **84.6%** MiniF2F -- matches the 671B DeepSeek-Prover-V2 (100x smaller!)
- Full FT needs ~128 GB + activations -- fits on B200 with gradient checkpointing
- Best performance/compute ratio of any model

### Budget option: DeepSeek-Prover-V2-7B or Leanabell-Prover-V2
- 7B params, full FT ~112 GB, very comfortable on B200
- Leanabell-V2 adds RL-based self-correction on top of DSP-V2-7B
- Good starting point for experimentation

### Tiny/fast iteration: Kimina-Prover-Distill-1.7B
- Only ~27 GB for full FT -- can run multiple experiments fast
- Good for prototyping pipelines before scaling up

---

## Summary: What to train

| Priority | Model | Method | Est. VRAM | Why |
|----------|-------|--------|-----------|-----|
| 1st | **Goedel-Prover-V2-8B** | Full FT | ~140 GB | Best perf/size ratio, full FT fits |
| 2nd | **Goedel-Prover-V2-32B** | LoRA | ~80 GB | Highest MiniF2F score, LoRA fits |
| 3rd | **Kimina-Distill-1.7B** | Full FT | ~27 GB | Fast prototyping |

---

## Decision (2026-03-03)

**Selected model: Goedel-Prover-V2-32B with LoRA on 1x B200 (GPU 6, 183 GB)**

- 90.4% MiniF2F-test (SOTA among open models)
- LoRA est. ~80 GB VRAM -- leaves ~100 GB headroom for activations, batch size, etc.
- HuggingFace: https://huggingface.co/Goedel-LM/Goedel-Prover-V2-32B
- TODO: test actual VRAM usage with a trial run

---

## Key Tools

- [Lean Copilot](https://github.com/lean-dojo/LeanCopilot) -- integrates LLMs directly into Lean 4 editor for tactic suggestions and proof search
- [LeanDojo](https://leandojo.org/) -- open-source framework for training/evaluating Lean 4 provers

## Sources

- [DeepSeek-Prover-V2 paper](https://arxiv.org/abs/2504.21801)
- [Goedel-Prover-V2 paper](https://arxiv.org/pdf/2508.03613)
- [Kimina-Prover paper](https://arxiv.org/abs/2504.11354)
- [Leanabell-Prover-V2](https://github.com/Leanabell-LM/Leanabell-Prover-V2)
- [Lean Copilot paper](https://arxiv.org/abs/2404.12534)
