#!/usr/bin/env bash
# Train the energy model with contrastive ranking loss.
set -euo pipefail

export PATH="$HOME/uv_envs/bin:$PATH"

cd "$(dirname "$0")/.."

uv run python -m ebm_for_text.main \
    mode=train \
    device=mps \
    "$@"
