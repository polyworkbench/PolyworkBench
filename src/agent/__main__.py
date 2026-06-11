"""Allow running as: python -m src.agent"""

import sys
from pathlib import Path

# Ensure project root is on path
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.agent.run_batch import main

if __name__ == "__main__":
    main()
