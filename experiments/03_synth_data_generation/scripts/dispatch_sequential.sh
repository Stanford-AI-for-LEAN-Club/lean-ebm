#!/usr/bin/env bash
# Sequential dispatch: one agent at a time to avoid rate limits and ensure completion.
# Usage: bash dispatch_sequential.sh [batch_number] [agent_type]
# Example: bash dispatch_sequential.sh 1 codex
#          bash dispatch_sequential.sh 5 gemini

set -euo pipefail

WORKDIR="/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation"
TEMPLATE="$WORKDIR/scripts/focused_prompt.md"
OUTPUT_DIR="$WORKDIR/output"
LOG_DIR="$WORKDIR/logs"

mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

BATCH_NUM="${1:?Usage: dispatch_sequential.sh <batch_num> <codex|gemini>}"
AGENT="${2:-codex}"

# Map batch number to files
case "$BATCH_NUM" in
    1) C_FILE="c_src/batch01_arithmetic.c"; PY_FILE="py_src/batch01_arithmetic.py"; NAME="batch01_arithmetic" ;;
    2) C_FILE="c_src/batch02_gcd_math.c";   PY_FILE="py_src/batch02_gcd_math.py";   NAME="batch02_gcd_math" ;;
    3) C_FILE="c_src/batch03_array_ops.c";  PY_FILE="py_src/batch03_array_ops.py";  NAME="batch03_array_ops" ;;
    4) C_FILE="c_src/batch04_search.c";     PY_FILE="py_src/batch04_search.py";     NAME="batch04_search" ;;
    5) C_FILE="c_src/batch05_sort.c";       PY_FILE="py_src/batch05_sort.py";       NAME="batch05_sort" ;;
    6) C_FILE="c_src/batch06_bits.c";       PY_FILE="py_src/batch06_bits.py";       NAME="batch06_bits" ;;
    7) C_FILE="c_src/batch07_string_ops.c"; PY_FILE="py_src/batch07_string_ops.py"; NAME="batch07_string_ops" ;;
    8) C_FILE="c_src/batch08_math2.c";      PY_FILE="py_src/batch08_math2.py";      NAME="batch08_math2" ;;
    *) echo "Invalid batch number: $BATCH_NUM (must be 1-8)"; exit 1 ;;
esac

# Generate prompt
PROMPT=$(sed \
    -e "s|C_FILE_PLACEHOLDER|$WORKDIR/$C_FILE|g" \
    -e "s|PY_FILE_PLACEHOLDER|$WORKDIR/$PY_FILE|g" \
    -e "s|OUTPUT_PLACEHOLDER|$WORKDIR/output/${NAME}.jsonl|g" \
    "$TEMPLATE")

LOG_FILE="$LOG_DIR/${NAME}_${AGENT}_v2.log"

echo "[$(date)] Launching $AGENT for $NAME..."
echo "[$(date)] Log: $LOG_FILE"

if [[ "$AGENT" == "codex" ]]; then
    echo "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -C "$WORKDIR" - \
        > "$LOG_FILE" 2>&1
elif [[ "$AGENT" == "gemini" ]]; then
    gemini -p "$PROMPT" -y --approval-mode yolo \
        > "$LOG_FILE" 2>&1
else
    echo "Unknown agent: $AGENT (must be codex or gemini)"
    exit 1
fi

echo "[$(date)] $AGENT for $NAME completed (exit $?)"
echo "Output: $OUTPUT_DIR/${NAME}.jsonl"
ls -la "$OUTPUT_DIR/${NAME}.jsonl" 2>/dev/null || echo "  (no output file created)"
