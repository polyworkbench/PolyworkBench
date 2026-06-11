"""LongHorizon Agent Evaluation Runner.

Main entry point for running the LongHorizon benchmark evaluation.
Deploys mature agent harness frameworks (following WildClawBench's approach)
and evaluates tasks using harness-named docker images.

Key design principles:
  1. Docker images are pulled by HARNESS NAME (not task name)
     - Terminal_Bench: `ziheliu/tb2-{task_id}:v3` (per-task)
     - LongHorizon:   `longhorizon-{harness}:v1` (per-harness)

  2. Each harness is a pre-built, mature agent framework (OpenClaw, ClaudeCode)
     that is deployed directly — not built from scratch.

  3. Tasks share the same harness image, reducing storage overhead from
     N images (one per task) to K images (one per harness, K << N).

Usage:
    python -m src.agent.run_batch --task HQ-01_neurips_to_acl --harness openclaw
    python -m src.agent.run_batch --all --harness claudecode --parallel 3
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure project root is on path for imports
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parents[1]  # PolyWorkBench/ (parent of src/)
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Resolve project root
# Layout: <PROJECT_ROOT>/src/agent/run_batch.py
#   PROJECT_ROOT/HQ-*           -> single-task entries
#   PROJECT_ROOT/full_tasks/    -> full task suite
ROOT_DIR = Path(__file__).resolve().parents[2]  # project root (PolyWorkBench/)
TASKS_DIR = ROOT_DIR  # HQ-* tasks live directly under project root
OUTPUT_DIR = ROOT_DIR / "output"


def _create_backend(harness: str, model: str, image: str | None = None):
    """Create the appropriate agent backend based on harness selection.

    The harness determines which docker image to pull (by harness name).
    """
    from src.agent.agents.openclaw.runner import OpenClawAgent
    from src.agent.agents.claudecode.runner import ClaudeCodeAgent
    from src.agent.agents.codex.runner import CodexAgent
    from src.agent.agents.hermesagent.runner import HermesAgentAgent

    if harness == "openclaw":
        return OpenClawAgent(image=image)
    elif harness == "claudecode":
        return ClaudeCodeAgent(image=image)
    elif harness == "codex":
        return CodexAgent(image=image)
    elif harness == "hermesagent":
        return HermesAgentAgent(image=image)
    else:
        # Default to OpenClaw for unknown harnesses
        logger.warning(
            "Harness '%s' not recognized, falling back to openclaw",
            harness,
        )
        return OpenClawAgent(image=image)


def run_single_task(
    task: dict[str, Any],
    backend,
    model: str,
    output_root: Path,
    *,
    timeout_override: int | None = None,
    skip_grading: bool = False,
    grade_on_error: bool = False,
    thinking: str | None = None,
) -> dict[str, Any]:
    """Execute and evaluate a single task.

    Thread-safe: each task has its own container name and output directory.

    Args:
        task: Parsed task dictionary from task_parser.
        backend: The agent backend (BaseAgent implementation).
        model: Model name to use.
        output_root: Root directory for outputs.
        timeout_override: Override task timeout (for debugging).
        skip_grading: Skip running tests after execution.
        grade_on_error: Run grading even if agent errored.
        thinking: Thinking/reasoning level.

    Returns:
        Result dictionary with task_id, scores, error, usage.
    """
    from src.agent.base import AgentTaskSpec
    from src.agent.utils.docker_utils import (
        collect_task_output,
        close_proc_log,
        remove_container,
    )
    from src.agent.utils.grading import run_grading, format_scores

    task_id_base = task["task_id"]
    timeout_seconds = timeout_override or task["timeout_seconds"]

    # Generate unique run ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    run_id = uuid.uuid4().hex[:6]
    safe_model = re.sub(r"[^a-zA-Z0-9.\-_]", "_", model.rsplit("/", 1)[-1])
    container_name = f"lh_{task_id_base}_{safe_model}_{timestamp}_{run_id}"

    # Output directory
    output_dir = output_root / backend.harness_name / task_id_base / f"{safe_model}_{timestamp}_{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "task_id": task_id_base,
        "container_name": container_name,
        "harness": backend.harness_name,
        "model": model,
        "scores": {},
        "error": None,
        "usage": {},
    }

    gateway_proc = None
    agent_proc = None
    elapsed_time = float(timeout_seconds)

    try:
        # Build task spec
        spec = AgentTaskSpec(
            task_id=container_name,
            task_dir=task["task_dir"],
            instruction=task["instruction"],
            inputs_path=task["inputs_path"],
            timeout_seconds=timeout_seconds,
            output_dir=output_dir,
            model=model,
            harness=backend.harness_name,
            difficulty=task["difficulty"],
            tags=task.get("tags", []),
            thinking=thinking,
        )

        logger.info(
            "[%s] Starting task (harness=%s, image=%s, timeout=%ds)",
            task_id_base,
            backend.harness_name,
            backend.docker_image,
            timeout_seconds,
        )

        # Execute the task
        execution = backend.run_task(spec)
        gateway_proc = execution.gateway_proc
        agent_proc = execution.agent_proc
        elapsed_time = execution.elapsed_time

        if execution.error:
            result["error"] = execution.error
            logger.error("[%s] Agent error: %s", task_id_base, execution.error)

    except Exception as exc:
        result["error"] = str(exc)
        logger.error("[%s] Unexpected error: %s", task_id_base, exc)

    finally:
        # Grading
        should_grade = not skip_grading and (not result.get("error") or grade_on_error)
        if should_grade:
            try:
                scores = run_grading(
                    container_name,
                    task["task_dir"],
                    output_dir,
                )
                result["scores"] = scores
                print(format_scores(task_id_base, scores))
            except Exception as exc:
                logger.error("[%s] Grading failed: %s", task_id_base, exc)
                result["scores"] = {"overall_score": 0.0, "error": str(exc)}

        # Collect usage
        try:
            usage = backend.collect_usage(container_name, output_dir, elapsed_time)
            result["usage"] = usage
            if usage.get("request_count", 0) > 0:
                logger.info(
                    "[%s] Usage - input:%d output:%d cost:$%.4f elapsed:%.1fs",
                    task_id_base,
                    usage.get("input_tokens", 0),
                    usage.get("output_tokens", 0),
                    usage.get("cost_usd", 0.0),
                    usage.get("elapsed_time", 0.0),
                )
        except Exception as exc:
            logger.warning("[%s] Usage collection failed: %s", task_id_base, exc)

        # Collect task output files
        try:
            collect_task_output(container_name, output_dir)
        except Exception as exc:
            logger.warning("[%s] Output collection failed: %s", task_id_base, exc)

        # Cleanup
        if gateway_proc is not None:
            try:
                gateway_proc.terminate()
            except Exception:
                pass
        for proc in [gateway_proc, agent_proc]:
            if proc is not None:
                try:
                    close_proc_log(proc)
                except Exception:
                    pass

        remove_container(container_name)

    # Save result
    result_path = output_dir / "result.json"
    result_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    return result


def main() -> None:
    """Main evaluation entry point."""
    from src.agent.utils.cli_args import parse_args
    from src.agent.utils.task_parser import (
        discover_tasks,
        filter_tasks,
        parse_task_toml,
    )
    from src.agent.utils.grading import print_summary

    args = parse_args()

    # Resolve tasks directory
    tasks_dir = Path(args.tasks_dir) if args.tasks_dir else TASKS_DIR
    if not tasks_dir.is_dir():
        logger.error("Tasks directory not found: %s", tasks_dir)
        sys.exit(1)

    # Resolve output directory
    output_root = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
    output_root.mkdir(parents=True, exist_ok=True)

    # Create backend
    backend = _create_backend(args.harness, args.model, args.image)
    logger.info(
        "Backend: harness=%s, image=%s, model=%s",
        backend.harness_name,
        backend.docker_image,
        args.model,
    )

    # Discover and filter tasks
    if args.task:
        # Single task mode
        task_dir = tasks_dir / args.task
        if not task_dir.is_dir():
            # Try finding by prefix
            candidates = [d for d in tasks_dir.iterdir() if d.name.startswith(args.task)]
            if len(candidates) == 1:
                task_dir = candidates[0]
            else:
                logger.error("Task not found: %s", args.task)
                sys.exit(1)

        try:
            task = parse_task_toml(task_dir)
        except Exception as exc:
            logger.error("Failed to parse task %s: %s", args.task, exc)
            sys.exit(1)

        tasks = [task]
    else:
        # Multi-task mode
        tasks = discover_tasks(tasks_dir)
        tasks = filter_tasks(
            tasks,
            collection=args.collection,
            max_difficulty=args.max_difficulty,
            tags=args.tags,
        )

    if not tasks:
        logger.error("No tasks found matching the criteria")
        sys.exit(1)

    logger.info(
        "Running %d task(s) with harness=%s, model=%s, parallel=%d",
        len(tasks),
        args.harness,
        args.model,
        args.parallel,
    )

    # Execute tasks
    all_results: list[dict[str, Any]] = []

    if args.parallel <= 1:
        # Sequential execution
        for task in tasks:
            result = run_single_task(
                task,
                backend,
                args.model,
                output_root,
                timeout_override=args.timeout_override,
                skip_grading=args.skip_grading,
                grade_on_error=args.grade_on_error,
                thinking=args.thinking,
            )
            all_results.append(result)
    else:
        # Parallel execution
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = {
                pool.submit(
                    run_single_task,
                    task,
                    backend,
                    args.model,
                    output_root,
                    timeout_override=args.timeout_override,
                    skip_grading=args.skip_grading,
                    grade_on_error=args.grade_on_error,
                    thinking=args.thinking,
                ): task["task_id"]
                for task in tasks
            }
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    all_results.append(future.result())
                except Exception as exc:
                    logger.error("[%s] Thread exception: %s", task_id, exc)
                    all_results.append({
                        "task_id": task_id,
                        "scores": {},
                        "error": str(exc),
                    })

    # Print summary
    print_summary(all_results, output_root)

    # Exit with error if any task failed completely
    has_failures = any(
        r.get("error") and not r.get("scores", {}).get("overall_score", 0)
        for r in all_results
    )
    if has_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
