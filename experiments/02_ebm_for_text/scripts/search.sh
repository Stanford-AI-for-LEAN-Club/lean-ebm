#!/usr/bin/env bash
# Run best-first search with the trained energy model + proposal LM.
set -euo pipefail

export PATH="$HOME/uv_envs/bin:$PATH"

cd "$(dirname "$0")/.."

uv run python -m ebm_for_text.main \
    mode=search \
    device=mps \
    "$@"
