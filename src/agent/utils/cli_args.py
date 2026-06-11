"""CLI argument parser for LongHorizon evaluation runner."""

from __future__ import annotations

import argparse
import os


def build_parser(
    default_model: str | None = None,
    default_parallel: int = 1,
) -> argparse.ArgumentParser:
    """Build the argument parser for run_batch.py.

    Returns:
        Configured ArgumentParser instance.
    """
    # Use DEFAULT_MODEL from env if available, otherwise fallback
    if default_model is None:
        default_model = os.environ.get("DEFAULT_MODEL", "openrouter/anthropic/claude-sonnet-4.6")

    parser = argparse.ArgumentParser(
        description="LongHorizon evaluation runner - agent benchmark for multilingual multimodal tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a single task with OpenClaw harness
  python -m src.agent.run_batch --task HQ-01_neurips_to_acl --harness openclaw

  # Run all tasks with Claude Code harness
  python -m src.agent.run_batch --all --harness claudecode

  # Run smoke tests only with parallelism
  python -m src.agent.run_batch --collection smoke --parallel 3

  # Run tasks filtered by difficulty
  python -m src.agent.run_batch --all --max-difficulty 3
""",
    )

    # Task selection (mutually exclusive)
    task_group = parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument(
        "--task", "-t",
        help="Run a specific task by ID (e.g., HQ-01_neurips_to_acl)",
    )
    task_group.add_argument(
        "--all", "-a",
        action="store_true",
        help="Run all discovered tasks",
    )
    task_group.add_argument(
        "--collection",
        choices=["smoke", "baseline", "stress"],
        help="Run tasks from a specific collection",
    )

    # Harness selection
    parser.add_argument(
        "--harness",
        default="openclaw",
        choices=["openclaw", "claudecode", "codex", "hermesagent"],
        help="Agent harness to use (determines docker image by harness name)",
    )

    # Model configuration
    parser.add_argument(
        "--model", "-m",
        default=default_model,
        help=f"Model name for the agent (default: {default_model})",
    )
    parser.add_argument(
        "--thinking",
        default=None,
        help="Thinking/reasoning level: off, low, medium, high (default: None)",
    )

    # Execution parameters
    parser.add_argument(
        "--parallel", "-p",
        type=int,
        default=default_parallel,
        help="Number of parallel task executions (default: 1 = sequential)",
    )
    parser.add_argument(
        "--max-difficulty",
        type=int,
        default=None,
        help="Only run tasks with difficulty <= this value",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=None,
        help="Only run tasks that have ALL specified tags",
    )
    parser.add_argument(
        "--timeout-override",
        type=int,
        default=None,
        help="Override timeout_sec from task.toml (useful for debugging)",
    )

    # Paths
    parser.add_argument(
        "--tasks-dir",
        default=None,
        help="Path to tasks root directory (default: auto-detect from project)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Path to output directory (default: <project_root>/output/)",
    )

    # Docker image override
    parser.add_argument(
        "--image",
        default=None,
        help="Override docker image (bypasses harness registry resolution)",
    )

    # Evaluation options
    parser.add_argument(
        "--skip-grading",
        action="store_true",
        help="Skip running tests after task execution",
    )
    parser.add_argument(
        "--grade-on-error",
        action="store_true",
        help="Run grading even if the agent reported an error",
    )

    return parser


def parse_args() -> argparse.Namespace:
    """Parse and return command line arguments."""
    return build_parser().parse_args()
