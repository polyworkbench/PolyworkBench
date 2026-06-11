#!/usr/bin/env bash
# ============================================================
# PolyWorkBench - Full Evaluation
# ============================================================
# Runs the full evaluation suite (all 67 tasks, 3 runs each).
# This produces Pass@3, Pass^3, and stability metrics.
#
# WARNING: This takes several hours and significant API credits.
#
# Usage:
#   bash scripts/run_full_eval.sh
#   PARALLEL=5 bash scripts/run_full_eval.sh
#   bash scripts/run_full_eval.sh --model "minimax/MiniMax-M2.7"
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo ""
echo "  ======================================"
echo "    PolyWorkBench Full Evaluation"
echo "  ======================================"
echo ""

# Check .env
if [ ! -f src/agent/.env ]; then
    echo "[ERROR] src/agent/.env not found. Run 'bash run.sh' first for setup."
    exit 1
fi

# Check Docker
if ! docker info &>/dev/null; then
    echo "[ERROR] Docker daemon is not running. Please start Docker."
    exit 1
fi

# Settings
HARNESS="${HARNESS:-openclaw}"
PARALLEL="${PARALLEL:-3}"
OUTPUT_DIR="${OUTPUT_DIR:-output/full_eval}"

echo "  Harness:    $HARNESS"
echo "  Parallel:   $PARALLEL"
echo "  Output:     $OUTPUT_DIR"
echo "  Tasks:      67 (all)"
echo "  Runs/task:  3 (via run_full_eval.py)"
echo ""
echo "  Estimated time: 4-8 hours (depending on model speed)"
echo ""

read -rp "  Continue? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "  Aborted."
    exit 0
fi

echo ""
echo "  Starting full evaluation..."
echo "  Logs: $OUTPUT_DIR/eval_report.jsonl"
echo ""

# Run the full evaluation script
python3 -m src.agent.run_full_eval 2>&1 | tee "$OUTPUT_DIR/eval_run.log"

echo ""
echo "  ======================================"
echo "    Evaluation Complete"
echo "  ======================================"
echo ""
echo "  Summary: $OUTPUT_DIR/eval_summary.json"
echo "  Report:  $OUTPUT_DIR/eval_report.jsonl"
echo ""
