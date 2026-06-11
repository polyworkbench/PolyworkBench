"""LongHorizon Agent Module.

Provides agent evaluation infrastructure for the LongHorizon benchmark.
Unlike Terminal_Bench which pulls docker images by task name, LongHorizon
pulls images by harness name — each harness corresponds to a mature agent
framework (OpenClaw, ClaudeCode, etc.) that is deployed directly.
"""

import os
import sys

# Ensure the agent module's parent directory is on sys.path
# so that `from src.agent...` style imports work even without pip install.
_AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_AGENT_DIR)
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
