
<div align="center">
<img src="polyworkbench.png" width="160" alt="PolyWorkBench Logo">

<h1 align="center">PolyWorkBench</h1>

<p align="center">
  <strong>A Cross-Lingual Long-Horizon Agent Benchmark</strong>
</p>

<p align="center">
  <em>67 multilingual tasks | 10 languages | 5 domains | Ground-truth grading</em>
</p>

<p align="center">
  <a href="#-leaderboard"><img alt="Tasks" src="https://img.shields.io/badge/tasks-67-blue"></a>
  <a href="#-leaderboard"><img alt="Languages" src="https://img.shields.io/badge/languages-10-green"></a>
  <a href="#-leaderboard"><img alt="Domains" src="https://img.shields.io/badge/domains-5-purple"></a>
  <a href="#-leaderboard"><img alt="Models" src="https://img.shields.io/badge/models-8-orange"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-yellow"></a>
  <a href="https://polyworkbench.github.io/"><img alt="Leaderboard" src="https://img.shields.io/badge/🏆_Leaderboard-PolyWorkBench-8c2416"></a>
</p>

> [README.zh-CN.md](README.zh-CN.md)
</div>

---

## Table of Contents

- [Why PolyWorkBench?](#why-polyworkbench)
- [Leaderboard](#leaderboard)
- [Tasks](#tasks)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Task Structure](#task-structure)
- [Supported Harnesses](#supported-harnesses)
- [Scripts & Tools](#scripts--tools)
- [Adding Your Own Tasks](#adding-your-own-tasks)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)
- [License](#license)

---

> **Cross-lingual long-horizon agent evaluation.** PolyWorkBench tests AI agents in real-world multilingual scenarios — parsing Japanese receipts, auditing German contracts, correlating Korean incident logs with Chinese sensor data — and measures whether they can deliver correct, verifiable results across language barriers.
>
> **Three-track scoring.** Every task is graded by pytest structural tests, weighted dimensional `grade()`, and LLM-as-Judge quality evaluation.

---

## Why PolyWorkBench?

Most agent benchmarks test single-language, single-step capabilities. Real enterprise work is different:

| | What We Test | Why It's Hard |
|:---:|---|---|
| **Cross-Lingual** | Process sources in 3-5 languages simultaneously | Must parse Chinese CSVs, Korean alerts, Russian logs — not just translate, but *extract and compute* |
| **Long-Horizon** | Multi-step pipelines with dependencies | Step N output feeds Step N+1; can't skip or shortcut |
| **Precise Verification** | Ground-truth numerical assertions | Not "does it look right" but "is the total exactly 47,250?" |
| **Domain Diversity** | Commerce, Legal, Manufacturing, Knowledge, Localization | Each domain has its own multilingual challenges |

### What Sets Us Apart

- **10 languages, real content.** Not machine-translated — native-language source documents with domain terminology (Japanese keigenzeiritsu, Korean jeokap/bujeokap, German Rahmenvertrag).
- **Three-track scoring.** Each task is graded independently by: (1) pytest structural tests, (2) weighted dimensional `grade()` with ground-truth assertions, (3) LLM-as-Judge quality evaluation.
- **Seeded ground truth.** Input files contain specific verifiable facts (amounts, dates, IDs) that grading scripts check precisely.
- **Harness-agnostic.** Same tasks run on OpenClaw, Claude Code, Codex CLI, or any agent framework via Docker containers.
- **Reproducible & isolated.** Each task runs in its own Docker container with injected inputs. Grading scripts are never visible to the agent.

---

## Leaderboard

Full interactive leaderboard at [polyworkbench.github.io](https://polyworkbench.github.io/).

> All scores are **n=1** (single run) on the full 67-task suite (v4). Pass@3 / Pass^3 robustness results coming soon.

| Rank | Model | Org | Avg Grade | COM | KNW | LEG | LOC | MFG | Tasks |
|:----:|-------|-----|:---------:|:---:|:---:|:---:|:---:|:---:|:-----:|
| 🥇 | **GPT-5.5** | OpenAI | 0.786 | 0.811 | 0.773 | 0.745 | 0.815 | 0.808 | 67 |
| 🥈 | **Minimax-M2.7** | MiniMax | 0.739 | 0.779 | 0.691 | 0.623 | 0.813 | 0.797 | 67 |
| 🥉 | **Minimax-M3** | MiniMax | 0.734 | 0.703 | 0.745 | 0.646 | 0.742 | 0.847 | 67 |
| 4 | **Claude Opus 4.8** | Anthropic | 0.722 | 0.661 | 0.751 | 0.618 | 0.811 | 0.808 | 67 |
| 5 | **Claude Opus 4.7** | Anthropic | 0.719 | 0.656 | 0.737 | 0.613 | 0.804 | 0.814 | 67 |
| 6 | **Qwen3.6-27B** | Alibaba Cloud | 0.669 | 0.584 | 0.536 | 0.662 | 0.832 | 0.750 | 67 |
| 7 | **Qwen3.6-35B-A3B** | Alibaba Cloud | 0.660 | 0.464 | 0.684 | 0.650 | 0.757 | 0.800 | 67 |
| 8 | **DeepSeek-v4-Flash** | DeepSeek | 0.485 | 0.386 | 0.432 | 0.565 | 0.613 | 0.452 | 67 |

---

## Tasks

67 tasks across 5 domains, difficulty L3-L6, covering 10 instruction/source languages.

### Domain Distribution

| Domain | Tasks | Description | Example |
|--------|:-----:|-------------|---------|
| **COM** (Commerce) | 16 | Cross-border trade, pricing, fraud, compliance | Multi-currency reconciliation detecting 3 seeded discrepancies |
| **KNW** (Knowledge) | 11 | Research synthesis, fact verification, contradiction detection | Cross-lingual fact-check requiring ALL 4 language sources |
| **LEG** (Legal) | 15 | Contract review, evidence chains, patent analysis | German contract conflict detection (6 seeded clause conflicts) |
| **LOC** (Localization) | 11 | App strings, game dialogue, code docs, UI consistency | Cross-platform UI string inconsistency detection (8 seeded) |
| **MFG** (Manufacturing) | 14 | SRE root cause, quality analysis, shift handover | Timestamp correlation across KO/ZH/EN logs to find root cause |

### Language Coverage

| Language | Tasks | Roles |
|----------|:-----:|-------|
| Korean (ko) | 12 | Instruction + source |
| English (en) | 12 | Instruction + source |
| French (fr) | 8 | Instruction + source |
| Russian (ru) | 8 | Source |
| Japanese (ja) | 7 | Instruction + source |
| Vietnamese (vi) | 7 | Instruction + source |
| Chinese (zh) | 7 | Instruction + source |
| Spanish (es) | 4 | Instruction + source |
| German (de) | 3 | Instruction + source |
| Arabic (ar) | 1 | Instruction (RTL) |

### Difficulty Distribution

| Level | Tasks | Avg Grade (M2.7) | Description |
|:-----:|:-----:|:-----------------:|-------------|
| L3 | 8 | 0.75 | Baseline: 2-3 source files, structured output |
| L4 | 26 | 0.82 | Multi-source cross-reference, precise calculations |
| L5 | 23 | 0.65 | Deep pipeline: 4+ sources, iterative verification |
| L6 | 10 | 0.45 | Stress: 5+ languages, anomaly detection, decision trees |

---

## Quick Start

### Prerequisites

- Python 3.9+
- Docker (for containerized agent execution)
- API keys for your target model (OpenRouter, Anthropic, or other supported provider)

### 1. Install

```bash
git clone https://github.com/polyworkbench/PolyWorkBench.git
cd PolyWorkBench
pip install -r src/agent/requirements.txt
```

### 2. Download & Load Docker Images

Images are hosted on HuggingFace. Download and load the harness(es) you want to use:

```bash
pip install -U "huggingface_hub[cli]"

# Download OpenClaw image (recommended for first-time use)
huggingface-cli download polyworkbench/PolyWorkBench \
    Images/polyworkbench-openclaw.tar \
    --repo-type dataset --local-dir .

# Load into Docker
docker load -i Images/polyworkbench-openclaw.tar
```

> See [Supported Harnesses](#supported-harnesses) for the full list of available images.

### 3. Configure API Keys

```bash
cp src/agent/.env.example src/agent/.env
```

Edit `src/agent/.env` with one of the following configurations:

**Option A: OpenRouter (supports many models)**
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
```

**Option B: Anthropic Direct**
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
ANTHROPIC_BASE_URL=https://api.anthropic.com
DEFAULT_MODEL=claude-sonnet-4-20250514
```

**Option C: DeepSeek**
```env
OPENROUTER_API_KEY=sk-xxxxxxxxxxxx
OPENROUTER_BASE_URL=https://api.deepseek.com
DEFAULT_MODEL=deepseek-chat
```

**Option D: MiniMax**
```env
OPENROUTER_API_KEY=sk-xxxxxxxxxxxx
OPENROUTER_BASE_URL=https://api.minimaxi.com/v1
DEFAULT_MODEL=minimax/MiniMax-M2.7
```

For LLM-as-Judge scoring (optional, defaults to same key):
```env
JUDGE_API_KEY=sk-ant-xxxxxxxxxxxx
JUDGE_BASE_URL=https://api.anthropic.com
JUDGE_MODEL=claude-sonnet-4-20250514
```

### 4. Quick Run (Demo)

```bash
bash run.sh
```

This runs a single demo task to verify your setup.

### 5. Run a Specific Task

```bash
python3 -m src.agent \
    --task COM-09_ko_compliance_check \
    --harness openclaw \
    --model "your-model-name" \
    --tasks-dir full_tasks \
    --grade-on-error
```

### 6. Run All Tasks

```bash
python3 -m src.agent \
    --all \
    --harness openclaw \
    --model "your-model-name" \
    --tasks-dir full_tasks \
    --output-dir output/ \
    --grade-on-error \
    --parallel 3
```

### 7. View Results

Results are saved per-task in `output/<harness>/<task_id>/<model>_<timestamp>_<run_id>/`:
- `result.json` — overall_score, dimensions, error info, token/cost stats
- `agent.log` / `gateway.log` — agent execution trace
- `task_output/` — all files the agent produced

Example `result.json`:
```json
{
  "task_id": "COM-09_ko_compliance_check",
  "scores": {
    "overall_score": 0.82,
    "pytest_score": 1.0,
    "judge_score": 0.72,
    "dimensions": {"structure": 0.9, "accuracy": 0.8, "coverage": 0.75}
  },
  "usage": {
    "input_tokens": 5234,
    "output_tokens": 1823,
    "cost_usd": 0.0234,
    "elapsed_time": 45.2
  }
}
```

---

## Project Structure

```
PolyWorkBench/
├── run.sh                       # Quick-start entry script
├── scripts/
│   ├── run_smoke.sh             # Smoke test (few tasks, fast)
│   └── run_full_eval.sh         # Full evaluation (67 tasks x 3 runs)
├── config/
│   └── task.example.toml        # Annotated task config example
├── full_tasks/                  # All 67 evaluation tasks
│   ├── COM-00_ja_receipt.../
│   ├── COM-01_ru_marketplace.../
│   ├── KNW-02_ko_tech.../
│   ├── LEG-00_es_privacy.../
│   ├── LOC-01_ko_game.../
│   └── MFG-01_ko_sre.../
├── src/
│   └── agent/                   # Evaluation framework
│       ├── __main__.py          # Entry: python -m src.agent
│       ├── run_batch.py         # Main orchestrator
│       ├── run_full_eval.py     # Full eval (Pass@3 metrics)
│       ├── run_judge_rescore.py # Re-run LLM judge on existing outputs
│       ├── harness_registry.py  # Harness -> Docker image mapping
│       ├── base.py              # BaseAgent interface
│       ├── .env.example         # Environment config template
│       ├── requirements.txt     # Python dependencies
│       ├── agents/              # Harness runner implementations
│       │   ├── openclaw/
│       │   ├── claudecode/
│       │   ├── codex/
│       │   └── hermesagent/
│       └── utils/               # Shared utilities
│           ├── cli_args.py      # CLI argument parsing
│           ├── docker_utils.py  # Container management
│           ├── grading.py       # Three-track scoring
│           ├── judge.py         # LLM-as-Judge implementation
│           └── task_parser.py   # task.toml + instruction.md parsing
├── output/                      # Evaluation results (git-ignored)
├── CONTRIBUTING.md              # How to contribute
├── LICENSE                      # Apache 2.0
└── README.md                    # This file
```

---

## Task Structure

Each task is a self-contained directory:

```
full_tasks/COM-09_ko_compliance_check/
├── task.toml              # Metadata: id, difficulty, timeout, tags
├── instruction.md         # Full task instruction (in target language)
├── environment/
│   ├── Dockerfile         # Container environment spec
│   └── inputs/            # Source files (multilingual, mounted read-only)
│       ├── fda_requirements_en.json
│       ├── gb_standards_zh.txt
│       └── jis_standards_ja.txt
└── tests/
    ├── test.sh            # Grading entry point
    ├── test_outputs.py    # grade() + pytest assertions
    ├── expected_output_schema.json
    └── rubric.md          # LLM judge dimensions
```

### Scoring Architecture

```
+---------------------------------------------------------+
|  Track 1: pytest        -> pass/fail gate (structural)   |
|  Track 2: grade()       -> 0-1.0 weighted dimensions     |
|  Track 3: LLM Judge     -> 0-1.0 quality assessment      |
+---------------------------------------------------------+
Primary metric: grade() (Track 2)
- Weighted dimensions with non-linear scaling
- Ground-truth numerical assertions (weight 2x)
- Cap at 0.85 for all-pass; 1.0 reserved for perfect ground-truth
```

### System Architecture

```
+-------------------+     +--------------------+     +-------------------+
|  run_batch.py     |---->|  Docker Container  |---->|  Grading Script   |
|  (orchestrator)   |     |  (agent runs here) |     |  (isolated)       |
+-------------------+     +--------------------+     +-------------------+
        |                          |                          |
        |                          v                          v
        |                 +----------------+         +----------------+
        +---------------->|  API / Model   |         |  result.json   |
                          +----------------+         +----------------+
```

---

## Supported Harnesses

PolyWorkBench ships **four** Docker images, one per harness. They are hosted on [HuggingFace](https://huggingface.co/datasets/polyworkbench/PolyWorkBench).

| Harness | Image Tarball | Loaded Tag |
|---------|--------------|------------|
| **openclaw** | `polyworkbench-openclaw.tar` | `polyworkbench-openclaw:v1` |
| **claudecode** | `polyworkbench-claudecode.tar` | `polyworkbench-claudecode:v1` |
| **codex** | `polyworkbench-codex.tar` | `polyworkbench-codex:v1` |
| **hermesagent** | `polyworkbench-hermes.tar` | `polyworkbench-hermes:v1` |

### Download & Load Images

```bash
pip install -U "huggingface_hub[cli]"

# Download images (pick the harness(es) you need, or all four)
huggingface-cli download polyworkbench/PolyWorkBench \
    Images/polyworkbench-openclaw.tar \
    Images/polyworkbench-claudecode.tar \
    Images/polyworkbench-codex.tar \
    Images/polyworkbench-hermes.tar \
    --repo-type dataset --local-dir .

# Load into Docker
docker load -i Images/polyworkbench-openclaw.tar
docker load -i Images/polyworkbench-claudecode.tar
docker load -i Images/polyworkbench-codex.tar
docker load -i Images/polyworkbench-hermes.tar
```

### Override Images

If you want to use a custom image (e.g., built locally or from a private registry), override via environment variables:

```bash
# Per-harness override
export LONGHORIZON_OPENCLAW_IMAGE=my-registry/custom-openclaw:v2
export LONGHORIZON_CLAUDECODE_IMAGE=my-registry/custom-claudecode:v2
export LONGHORIZON_CODEX_IMAGE=my-registry/custom-codex:v2
export LONGHORIZON_HERMES_IMAGE=my-registry/custom-hermes:v2

# Global override (applies to ALL harnesses)
export LONGHORIZON_DOCKER_IMAGE=my-universal-image:latest
```

Or via CLI:
```bash
python3 -m src.agent --task ... --image my-registry/custom:v2
```

---

## Scripts & Tools

### `run.sh` - Quick Start

```bash
bash run.sh                                  # Run demo task
bash run.sh --task COM-09_ko_compliance_check  # Specific task
bash run.sh --all --parallel 3               # All tasks
bash run.sh --collection smoke               # Smoke test
```

### `scripts/run_smoke.sh` - Smoke Test

Quick verification that your setup works:
```bash
bash scripts/run_smoke.sh
bash scripts/run_smoke.sh --harness claudecode
PARALLEL=4 bash scripts/run_smoke.sh
```

### `scripts/run_full_eval.sh` - Full Evaluation

Runs all 67 tasks x 3 repetitions with Pass@3/Pass^3 metrics:
```bash
bash scripts/run_full_eval.sh
```

### Common CLI Options

```
--task TASK_ID                        Run a specific task
--all                                 Run all tasks
--collection {smoke|baseline|stress}  Filter by collection

--harness {openclaw|claudecode|codex|hermesagent}
--model MODEL_NAME                    Model to use
--parallel N                          Parallel task count

--max-difficulty N                    Only tasks with difficulty <= N
--tags TAG1 TAG2                      Tasks must have ALL tags

--skip-grading                        Skip tests (debug mode)
--grade-on-error                      Grade even if agent errors
--timeout-override SECONDS            Override task timeout

--tasks-dir PATH                      Tasks directory
--output-dir PATH                     Results directory
--image DOCKER_IMAGE                  Override docker image
```

---

## Adding Your Own Tasks

1. Create a directory under `full_tasks/` following the naming convention: `{DOMAIN}-{NUM}_{lang}_{description}`
2. Write `task.toml` with metadata (see [`config/task.example.toml`](config/task.example.toml))
3. Write `instruction.md` in the target language
4. Add multilingual source files to `environment/inputs/`
5. Write `tests/test_outputs.py` with `grade()` function and pytest assertions
6. Write `tests/rubric.md` for LLM judge

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## Troubleshooting

### "Docker daemon not running"
Make sure Docker Desktop is open, or start the daemon:
```bash
# Linux
sudo systemctl start docker

# macOS - open Docker Desktop app
open -a Docker
```

### "Image not found"
Re-download and load the image:
```bash
huggingface-cli download polyworkbench/PolyWorkBench \
    Images/polyworkbench-openclaw.tar \
    --repo-type dataset --local-dir .
docker load -i Images/polyworkbench-openclaw.tar

# Or set a custom image in .env:
# LONGHORIZON_OPENCLAW_IMAGE=your-registry/your-image:tag
```

### "API key not set"
Edit `src/agent/.env` with your API key. See [Configure API Keys](#2-configure-api-keys) above.

### "Connection refused" / proxy issues
Unset proxy variables:
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
python3 -m src.agent --task ...
```

### "Task timeout exceeded"
Override the timeout:
```bash
python3 -m src.agent --task ... --timeout-override 3600
```

### "No tasks found matching criteria"
Check that `--tasks-dir` points to the correct directory:
```bash
python3 -m src.agent --task COM-09_ko_compliance_check --tasks-dir full_tasks
```

---

## FAQ

### Can I run tasks without Docker?
Docker is required for full isolation and grading. For development, you can inspect task instructions and inputs directly, but the agent execution and grading pipeline requires Docker.

### How do I add a new harness?
Create a new directory under `src/agent/agents/{harness_name}/` with a `runner.py` implementing `BaseAgent`, then register it in `src/agent/harness_registry.py`. See existing implementations as reference.

### What models are supported?
Any model accessible via OpenRouter, Anthropic API, or OpenAI-compatible API. Set the API base URL and key in `.env`.

---

## Citation

```bibtex
@misc{polyworkbench2026,
  title={PolyWorkBench: A Cross-Lingual Long-Horizon Agent Benchmark},
  author={PolyWorkBench Team},
  year={2026},
  url={https://github.com/polyworkbench/PolyWorkBench}
}
```

---

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.

Task content (instructions, inputs) may contain excerpts from public domain or CC-licensed sources. Individual task attributions are noted in their respective `task.toml` files.

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

<p align="center">
  <em>PolyWorkBench — Evaluating agents where language meets work.</em>
</p>
