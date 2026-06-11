#!/bin/bash
set -e
cd "$(dirname "$0")"
pytest test_outputs.py -v --tb=short 2>&1
