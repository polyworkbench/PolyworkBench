"""Task parser for LongHorizon benchmark tasks.

Parses task.toml files and instruction.md to produce AgentTaskSpec instances.
Unlike WildClawBench which uses YAML frontmatter in markdown files,
LongHorizon uses TOML for task metadata and separate instruction.md for prompts.

Task directory structure:
    <task_id>/
        task.toml               # Task metadata (id, timeout, tags, etc.)
        instruction.md          # Prompt for the agent
        environment/
            Dockerfile
            inputs/             # Input files mounted into container
        tests/
            test.sh             # Grading entrypoint
            test_outputs.py     # Pytest-based evaluation
            expected_output_schema.json
            rubric.md
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


def parse_task_toml(task_dir: Path) -> dict[str, Any]:
    """Parse a LongHorizon task directory into a task specification dict.

    Args:
        task_dir: Path to the task directory (e.g., <project_root>/HQ-01_neurips_to_acl/)

    Returns:
        Dictionary with task metadata ready for evaluation:
          - task_id: str
          - instruction: str (content of instruction.md)
          - task_dir: Path
          - inputs_path: Path (resolved path to environment/inputs/)
          - tests_dir: Path (resolved path to tests/)
          - timeout_seconds: int
          - difficulty: int
          - tags: list[str]
          - category: str
          - collection: str
          - outputs: dict (expected output configuration)
          - scoring: dict (scoring configuration)

    Raises:
        FileNotFoundError: If task.toml or instruction.md is missing.
        ValueError: If required fields are missing from task.toml.
    """
    task_dir = task_dir.resolve()

    # Parse task.toml
    toml_path = task_dir / "task.toml"
    if not toml_path.exists():
        raise FileNotFoundError(f"task.toml not found: {toml_path}")

    with open(toml_path, "rb") as f:
        metadata = tomllib.load(f)

    # Parse instruction.md
    instruction_path = task_dir / "instruction.md"
    if not instruction_path.exists():
        raise FileNotFoundError(f"instruction.md not found: {instruction_path}")

    instruction = instruction_path.read_text(encoding="utf-8").strip()

    # Extract required fields
    task_id = metadata.get("id")
    if not task_id:
        raise ValueError(f"Missing 'id' field in {toml_path}")

    # Resolve paths
    env_config = metadata.get("environment", {})
    inputs_rel = env_config.get("inputs", "environment/inputs")
    inputs_path = (task_dir / inputs_rel).resolve()

    tests_dir = (task_dir / "tests").resolve()

    # Build the task dict
    return {
        "task_id": task_id,
        "instruction": instruction,
        "task_dir": task_dir,
        "inputs_path": inputs_path,
        "tests_dir": tests_dir,
        "timeout_seconds": int(metadata.get("timeout_sec", 1200)),
        "difficulty": int(metadata.get("difficulty", 1)),
        "tags": metadata.get("tags", []),
        "category": metadata.get("category", "multilingual-multimodal"),
        "collection": metadata.get("collection", "baseline"),
        "name": metadata.get("name", task_id),
        "estimated_steps": int(metadata.get("estimated_steps", 5)),
        "outputs": metadata.get("outputs", {}),
        "scoring": metadata.get("scoring", {}),
    }


def discover_tasks(tasks_root: Path) -> list[dict[str, Any]]:
    """Discover all valid tasks under a root directory.

    Scans for directories containing both task.toml and instruction.md.

    Args:
        tasks_root: Root directory to scan for tasks.

    Returns:
        List of parsed task dictionaries, sorted by task_id.
    """
    tasks: list[dict[str, Any]] = []

    if not tasks_root.is_dir():
        logger.error("Tasks root directory not found: %s", tasks_root)
        return tasks

    for task_dir in sorted(tasks_root.iterdir()):
        if not task_dir.is_dir():
            continue
        if not (task_dir / "task.toml").exists():
            continue
        if not (task_dir / "instruction.md").exists():
            continue

        try:
            task = parse_task_toml(task_dir)
            tasks.append(task)
            logger.info(
                "Discovered task: %s (difficulty=%d, timeout=%ds)",
                task["task_id"],
                task["difficulty"],
                task["timeout_seconds"],
            )
        except Exception as exc:
            logger.error("Failed to parse task in %s: %s", task_dir, exc)

    logger.info("Discovered %d tasks in %s", len(tasks), tasks_root)
    return tasks


def filter_tasks(
    tasks: list[dict[str, Any]],
    *,
    collection: str | None = None,
    max_difficulty: int | None = None,
    tags: list[str] | None = None,
    task_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter tasks by various criteria.

    Args:
        tasks: List of task dictionaries to filter.
        collection: Only include tasks from this collection (e.g., "smoke", "baseline").
        max_difficulty: Only include tasks with difficulty <= this value.
        tags: Only include tasks that have ALL specified tags.
        task_ids: Only include tasks with these specific IDs.

    Returns:
        Filtered list of task dictionaries.
    """
    filtered = tasks

    if task_ids is not None:
        id_set = set(task_ids)
        filtered = [t for t in filtered if t["task_id"] in id_set]

    if collection is not None:
        filtered = [t for t in filtered if t["collection"] == collection]

    if max_difficulty is not None:
        filtered = [t for t in filtered if t["difficulty"] <= max_difficulty]

    if tags:
        tag_set = set(tags)
        filtered = [t for t in filtered if tag_set.issubset(set(t.get("tags", [])))]

    return filtered
