# Next Task: Test LoRA Fine-Tuning Run

## Status
- Script written and committed: `py_src/lean_ebm/train_lora_lean4.py`
- Dependencies installed: transformers, peft, datasets, trl, bitsandbytes
- Model download started but slow (~6/65 GB) — needs HF_TOKEN for faster download

## To resume

### 1. Set HF token (speeds up download dramatically)
```bash
export HF_TOKEN=hf_...
```

### 2. Run training on GPU 6
```bash
export PATH="$HOME/uv_envs/bin:$PATH"
CUDA_VISIBLE_DEVICES=6 uv run python -m lean_ebm.train_lora_lean4
```

### 3. What to look for
- **Baseline eval loss** printed before training starts
- **Train loss** should decrease each step (logged every step)
- **Eval loss** (test split) printed after each epoch — compare to baseline
- VRAM usage: check with `nvidia-smi` that it fits on 1 B200 (~80 GB expected)

### 4. If it OOMs
- Reduce `--max_seq_length 1024`
- Reduce `--lora_r 8 --lora_alpha 16`
- Add QLoRA (load model in 4-bit) — would need a small code change

### 5. After training succeeds
- Record baseline vs final eval loss
- Check if test loss also decreased (generalization) or only train loss (overfitting)
- LoRA adapter saved to `experiments/00_lm_mini_f2f/checkpoints/final/`
- Commit results and update `open_source_lean4_models.md` with findings

## Key files
- Training script: `py_src/lean_ebm/train_lora_lean4.py`
- Model survey: `experiments/00_lm_mini_f2f/open_source_lean4_models.md`
- Config: all CLI args, defaults in script (see `parse_args()`)
- Model: `Goedel-LM/Goedel-Prover-V2-32B` (cached at `~/.cache/huggingface/hub/`)
- Dataset: `brando/minif2f-lean4` (244 val / 244 test)
