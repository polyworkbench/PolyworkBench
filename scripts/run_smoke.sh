#!/usr/bin/env bash
# ============================================================
# PolyWorkBench - Smoke Test
# ============================================================
# Runs a small subset of tasks to verify your setup is working.
# Ideal for first-time setup or CI integration.
#
# Usage:
#   bash scripts/run_smoke.sh
#   bash scripts/run_smoke.sh --harness claudecode
#   bash scripts/run_smoke.sh --model "deepseek-chat"
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo ""
echo "  =============================="
echo "    PolyWorkBench Smoke Test"
echo "  =============================="
echo ""

# Default settings
HARNESS="${HARNESS:-openclaw}"
MODEL="${MODEL:-}"
PARALLEL="${PARALLEL:-2}"

# Parse extra arguments
EXTRA_ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --harness)
            HARNESS="$2"; shift 2 ;;
        --model)
            MODEL="$2"; shift 2 ;;
        --parallel)
            PARALLEL="$2"; shift 2 ;;
        *)
            EXTRA_ARGS+=("$1"); shift ;;
    esac
done

# Build command
CMD=(python3 -m src.agent
    --collection smoke
    --harness "$HARNESS"
    --parallel "$PARALLEL"
    --grade-on-error
    --output-dir output/smoke
)

if [ -n "$MODEL" ]; then
    CMD+=(--model "$MODEL")
fi

CMD+=("${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}")

echo "  Harness:  $HARNESS"
echo "  Model:    ${MODEL:-<from .env>}"
echo "  Parallel: $PARALLEL"
echo ""
echo "  Command: ${CMD[*]}"
echo ""

exec "${CMD[@]}"
