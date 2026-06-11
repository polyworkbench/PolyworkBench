#!/usr/bin/env bash
# ============================================================
# PolyWorkBench - Quick Start Run Script
# ============================================================
# Usage:
#   bash run.sh                         # Run demo task (COM-00)
#   bash run.sh --task COM-09_ko_compliance_check
#   bash run.sh --all --parallel 3
#   bash run.sh --collection smoke
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---- Color helpers ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }

# ---- Pre-flight checks ----
echo ""
echo "  =============================="
echo "    PolyWorkBench Runner"
echo "  =============================="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    error "Python 3 not found. Please install Python 3.9+."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python version: $PYTHON_VERSION"

# Check Docker
if ! command -v docker &>/dev/null; then
    warn "Docker not found. Tasks require Docker for containerized execution."
    warn "Install Docker: https://docs.docker.com/get-docker/"
fi

# Check .env file
ENV_FILE="$SCRIPT_DIR/src/agent/.env"
ENV_EXAMPLE="$SCRIPT_DIR/src/agent/.env.example"

if [ ! -f "$ENV_FILE" ]; then
    warn ".env file not found at: $ENV_FILE"
    if [ -f "$ENV_EXAMPLE" ]; then
        info "Copying .env.example to .env ..."
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        warn "Please edit $ENV_FILE with your API keys before running."
        echo ""
        echo "  Example configurations:"
        echo ""
        echo "  # OpenRouter (recommended for most models)"
        echo "  OPENROUTER_API_KEY=sk-or-..."
        echo "  DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514"
        echo ""
        echo "  # Anthropic direct"
        echo "  ANTHROPIC_API_KEY=sk-ant-..."
        echo "  DEFAULT_MODEL=claude-sonnet-4-20250514"
        echo ""
        exit 1
    else
        error ".env.example also not found. Please check your installation."
        exit 1
    fi
fi

# Check if API key is configured
if grep -q "your_.*_key_here" "$ENV_FILE" 2>/dev/null; then
    warn "API keys in .env appear to be placeholder values."
    warn "Please edit $ENV_FILE with your actual API keys."
    exit 1
fi

# Check dependencies
if ! python3 -c "import dotenv" 2>/dev/null; then
    info "Installing dependencies..."
    pip install -r "$SCRIPT_DIR/src/agent/requirements.txt"
fi

ok "Pre-flight checks passed."
echo ""

# ---- Default arguments ----
DEFAULT_TASK="COM-00_ja_receipt_to_en_excel"
DEFAULT_HARNESS="openclaw"

# If no arguments provided, run a demo task
if [ $# -eq 0 ]; then
    info "No arguments provided. Running demo task: $DEFAULT_TASK"
    info "Harness: $DEFAULT_HARNESS"
    echo ""
    info "Command:"
    echo "  python3 -m src.agent --task $DEFAULT_TASK --harness $DEFAULT_HARNESS --grade-on-error"
    echo ""
    exec python3 -m src.agent --task "$DEFAULT_TASK" --harness "$DEFAULT_HARNESS" --grade-on-error
else
    # Pass all arguments through
    info "Running: python3 -m src.agent $*"
    echo ""
    exec python3 -m src.agent "$@"
fi
