#!/bin/bash
cd /workspace
pip install pytest -q 2>/dev/null
pytest tests/test_outputs.py -v --tb=short 2>&1
