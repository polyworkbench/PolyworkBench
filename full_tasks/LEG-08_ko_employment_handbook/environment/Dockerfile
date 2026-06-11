FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl jq && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pandas openpyxl jsonschema pyyaml requests

WORKDIR /workspace
COPY inputs/ /workspace/inputs/

RUN mkdir -p /workspace/output
