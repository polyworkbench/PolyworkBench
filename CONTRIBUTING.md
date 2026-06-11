# Contributing to PolyWorkBench

Thank you for your interest in contributing to PolyWorkBench! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Getting Started](#getting-started)
- [Adding New Tasks](#adding-new-tasks)
- [Code Contributions](#code-contributions)
- [Reporting Issues](#reporting-issues)
- [Pull Request Process](#pull-request-process)

---

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment:

```bash
cd PolyWorkBench
pip install -r src/agent/requirements.txt
cp src/agent/.env.example src/agent/.env
# Edit .env with your API keys
```

4. Verify your setup:

```bash
bash scripts/run_smoke.sh
```

---

## Adding New Tasks

Tasks are the core contribution type for PolyWorkBench. Each task tests an agent's ability to work with multilingual, long-horizon scenarios.

### Task Naming Convention

```
{DOMAIN}-{NUM}_{lang}_{short_description}
```

- **DOMAIN**: `COM` (Commerce), `KNW` (Knowledge), `LEG` (Legal), `LOC` (Localization), `MFG` (Manufacturing)
- **NUM**: Two-digit sequential number (e.g., `09`, `15`)
- **lang**: Primary instruction language code (e.g., `ko`, `en`, `fr`, `ja`)
- **short_description**: Brief snake_case description (e.g., `compliance_check`, `receipt_analysis`)

### Task Directory Structure

```
full_tasks/COM-09_ko_compliance_check/
├── task.toml              # Task metadata (see config/task.example.toml)
├── instruction.md         # Full task instruction in target language
├── task.md                # (Optional) Human-readable task summary
├── environment/
│   ├── Dockerfile         # Container environment specification
│   └── inputs/            # Source files (multilingual, read-only mounted)
│       ├── source_en.json
│       ├── source_zh.txt
│       └── source_ja.csv
└── tests/
    ├── test.sh            # Grading entry point (runs pytest)
    ├── test_outputs.py    # grade() function + pytest assertions
    ├── expected_output_schema.json  # JSON schema for answer validation
    └── rubric.md          # LLM-as-Judge evaluation dimensions
```

### Writing `task.toml`

See [`config/task.example.toml`](config/task.example.toml) for a fully annotated example.

Key requirements:
- `id` must exactly match the directory name
- `difficulty` should be 3-6 (start with 4 if unsure)
- `timeout_sec` should be generous (at least 2x expected completion time)
- `tags` must include language tags: `{lang}-instruction`, `{lang}-source`, `{lang}-output`

### Writing `instruction.md`

- Write in the target instruction language (e.g., Korean for `ko` tasks)
- Be precise about expected output format (file names, JSON schema)
- Include all information needed to complete the task
- Do NOT include hints about which source files contain which information

### Writing `tests/test_outputs.py`

Must implement:

1. **`grade()` function** - Returns a dictionary with `overall_score` (0.0-1.0) and `dimensions`:

```python
def grade() -> dict:
    """Multi-dimensional grading with ground-truth assertions."""
    dimensions = {}

    # Dimension 1: Structural completeness (weight 1.0)
    dimensions["structure"] = {"score": 0.0, "weight": 1.0, "details": ""}

    # Dimension 2: Ground-truth accuracy (weight 2.0 - higher priority)
    dimensions["accuracy"] = {"score": 0.0, "weight": 2.0, "details": ""}

    # Dimension 3: Cross-lingual coverage (weight 1.5)
    dimensions["coverage"] = {"score": 0.0, "weight": 1.5, "details": ""}

    # ... scoring logic ...

    # Calculate weighted overall
    total_weight = sum(d["weight"] for d in dimensions.values())
    overall = sum(d["score"] * d["weight"] for d in dimensions.values()) / total_weight

    return {"overall_score": round(overall, 4), "dimensions": dimensions}
```

2. **pytest test functions** - Structural assertions:

```python
def test_answer_json_exists():
    """answer.json must exist."""
    assert Path("/workspace/answer.json").exists()

def test_answer_json_valid():
    """answer.json must be valid JSON with required fields."""
    data = json.loads(Path("/workspace/answer.json").read_text())
    assert "result" in data
    assert "summary" in data
```

### Writing `tests/rubric.md`

Define 3-5 evaluation dimensions for the LLM judge:

```markdown
## Evaluation Dimensions

### 1. Content Accuracy (0-10)
- Are the extracted facts correct?
- Are numerical values precise?

### 2. Language Quality (0-10)
- Is the output in the correct target language?
- Is the language natural and professional?

### 3. Completeness (0-10)
- Are all required deliverables present?
- Are all source languages utilized?
```

### Seeding Ground Truth

Every task must contain verifiable facts in the input files:
- Specific numerical values (amounts, dates, quantities)
- Named entities (company names, product IDs)
- Logical relationships that can be computationally verified

The grading script (`test_outputs.py`) checks these facts precisely.

---

## Code Contributions

### Code Style

- Python 3.9+ compatibility
- Type hints for function signatures
- Docstrings for public functions (Google style)
- Maximum line length: 100 characters

### Adding a New Harness

1. Create `src/agent/agents/{harness_name}/`
2. Implement `runner.py` extending `BaseAgent` from `src/agent/base.py`
3. Register in `src/agent/harness_registry.py`
4. Add Docker image reference
5. Update documentation

### Testing

```bash
# Run a single task to verify changes
python3 -m src.agent --task COM-00_ja_receipt_to_en_excel --harness openclaw --grade-on-error

# Run smoke tests
bash scripts/run_smoke.sh
```

---

## Reporting Issues

When reporting issues, please include:
- Python version (`python3 --version`)
- Docker version (`docker --version`)
- Operating system
- Full error message / stack trace
- Task ID (if task-specific)

---

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run smoke tests to verify nothing is broken
4. Submit a PR with:
   - Clear title describing the change
   - Description of what and why
   - For new tasks: include expected difficulty and sample run results

### PR Checklist for New Tasks

- [ ] `task.toml` follows schema (validate with `config/task.example.toml`)
- [ ] `instruction.md` is in the correct target language
- [ ] `tests/test_outputs.py` implements both `grade()` and pytest functions
- [ ] `tests/rubric.md` defines clear LLM judge dimensions
- [ ] Input files contain seeded, verifiable ground truth
- [ ] Task runs successfully with at least one harness
- [ ] `grade()` returns a score between 0.0 and 1.0

---

## Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please be respectful in all interactions.

---

## Questions?

Open an issue with the `question` label, or reach out to the maintainers.
