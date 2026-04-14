#!/usr/bin/env bash
# Dispatch C/Python-to-Lean4 formalization agents to Codex and Gemini CLIs.
# Usage: bash dispatch.sh [--dry-run]

set -euo pipefail

WORKDIR="/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation"
PROMPT_TEMPLATE="$WORKDIR/scripts/prompt_template.md"
OUTPUT_DIR="$WORKDIR/output"
PROMPT_DIR="$WORKDIR/scripts/prompts"
LOG_DIR="$WORKDIR/logs"

mkdir -p "$OUTPUT_DIR" "$PROMPT_DIR" "$LOG_DIR"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "[DRY RUN] Will generate prompts but not launch agents."
fi

# Batch definitions: batch_name c_file py_file agent_type
BATCHES=(
    "batch01_arithmetic:batch01_arithmetic.c:batch01_arithmetic.py:codex"
    "batch02_gcd_math:batch02_gcd_math.c:batch02_gcd_math.py:codex"
    "batch03_array_ops:batch03_array_ops.c:batch03_array_ops.py:codex"
    "batch04_search:batch04_search.c:batch04_search.py:codex"
    "batch05_sort:batch05_sort.c:batch05_sort.py:gemini"
    "batch06_bits:batch06_bits.c:batch06_bits.py:gemini"
    "batch07_string_ops:batch07_string_ops.c:batch07_string_ops.py:gemini"
    "batch08_math2:batch08_math2.c:batch08_math2.py:gemini"
)

PIDS=()
NAMES=()

for entry in "${BATCHES[@]}"; do
    IFS=':' read -r batch_name c_file py_file agent <<< "$entry"

    prompt_file="$PROMPT_DIR/${batch_name}_prompt.md"

    # Generate batch-specific prompt from template
    sed \
        -e "s|WORKDIR_PLACEHOLDER|$WORKDIR|g" \
        -e "s|BATCH_C_FILE|$c_file|g" \
        -e "s|BATCH_PY_FILE|$py_file|g" \
        -e "s|BATCH_NAME|$batch_name|g" \
        "$PROMPT_TEMPLATE" > "$prompt_file"

    echo "[$(date +%H:%M:%S)] Generated prompt: $prompt_file"

    if $DRY_RUN; then
        continue
    fi

    log_file="$LOG_DIR/${batch_name}_${agent}.log"

    if [[ "$agent" == "codex" ]]; then
        echo "[$(date +%H:%M:%S)] Launching codex for $batch_name..."
        codex exec --full-auto -C "$WORKDIR" "$(cat "$prompt_file")" \
            > "$log_file" 2>&1 &
    else
        echo "[$(date +%H:%M:%S)] Launching gemini for $batch_name..."
        gemini -p "$(cat "$prompt_file")" -y \
            > "$log_file" 2>&1 &
    fi

    PIDS+=($!)
    NAMES+=("$batch_name ($agent)")

    # Small stagger to avoid rate limits
    sleep 2
done

if $DRY_RUN; then
    echo "[DRY RUN] Done generating prompts. Check $PROMPT_DIR/"
    exit 0
fi

echo ""
echo "=== All agents launched ==="
echo "PIDs: ${PIDS[*]}"
echo "Logs: $LOG_DIR/"
echo ""
echo "Waiting for agents to finish..."

FAILED=0
for i in "${!PIDS[@]}"; do
    pid=${PIDS[$i]}
    name=${NAMES[$i]}
    if wait "$pid"; then
        echo "[DONE] $name (PID $pid) - SUCCESS"
    else
        echo "[DONE] $name (PID $pid) - FAILED (exit $?)"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "=== Results ==="
echo "Total batches: ${#BATCHES[@]}"
echo "Failed: $FAILED"
echo "Output files:"
ls -la "$OUTPUT_DIR/"*.jsonl 2>/dev/null || echo "  (no output files yet)"
