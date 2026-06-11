#!/usr/bin/env python3
"""
BabelAgentBench Full Task Evaluation Runner
============================================
Runs all 55 tasks × 3 repetitions using MiniMax-M2.7 via OpenClaw harness.
Outputs real-time results to terminal and log file.

Metrics computed:
- Pass@3: at least 1 of 3 runs passes (score > threshold)
- Pass^3: all 3 runs pass
- Avg score across 3 runs
- Std deviation (stability)
- Tool use count per run
- Runtime per run
- LLM-as-Judge score

Usage:
    python run_full_eval.py 2>&1 | tee eval_log.txt
"""

import json
import os
import sys
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Add project paths
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR.parent.parent))  # multilingual_multimodal_agent_tasks/

from dotenv import load_dotenv
load_dotenv(override=True)

# Import the runner infrastructure
from src.agent.run_batch import run_single_task, _create_backend
from src.agent.utils.task_parser import discover_tasks

# Configuration
TASKS_DIR = _THIS_DIR.parent.parent / "full_tasks"
OUTPUT_DIR = _THIS_DIR.parent.parent / "output" / "full_eval"
MODEL = os.environ.get("DEFAULT_MODEL", "minimax/MiniMax-M2.7")
HARNESS = "openclaw"
RUNS_PER_TASK = 3
PARALLEL_TASKS = 3  # How many tasks to run in parallel
PASS_THRESHOLD = 0.3  # Score >= this counts as "pass"
LOG_FILE = OUTPUT_DIR / "eval_report.jsonl"
SUMMARY_FILE = OUTPUT_DIR / "eval_summary.json"


def print_header():
    """Print evaluation header."""
    print(f"""
{'='*70}
  BabelAgentBench Full Evaluation
  Model: {MODEL}
  Harness: {HARNESS}
  Tasks: {TASKS_DIR}
  Runs per task: {RUNS_PER_TASK}
  Pass threshold: {PASS_THRESHOLD}
  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}
""")


def run_task_n_times(task, backend, n=3):
    """Run a single task n times and collect results."""
    task_id = task["task_id"]
    results = []

    for run_idx in range(n):
        start_time = time.time()
        try:
            result = run_single_task(
                task,
                backend,
                MODEL,
                OUTPUT_DIR,
                grade_on_error=True,
            )
            elapsed = time.time() - start_time
            result["elapsed_time"] = elapsed
            result["run_index"] = run_idx
        except Exception as exc:
            elapsed = time.time() - start_time
            result = {
                "task_id": task_id,
                "run_index": run_idx,
                "scores": {"overall_score": 0.0},
                "error": str(exc),
                "elapsed_time": elapsed,
                "usage": {},
            }

        results.append(result)

        # Print immediate result
        score = result.get("scores", {}).get("overall_score", 0.0)
        error = result.get("error", "")
        tool_calls = result.get("usage", {}).get("request_count", 0)
        status = "✓" if score >= PASS_THRESHOLD else "✗"
        error_msg = f" [ERR: {error[:50]}]" if error else ""
        print(f"  [{task_id}] Run {run_idx+1}/{n}: {status} score={score:.3f} "
              f"time={elapsed:.0f}s tools={tool_calls}{error_msg}")

    return results


def compute_task_metrics(task_id, results):
    """Compute Pass@3, Pass^3, avg, std for a task's results."""
    scores = [r.get("scores", {}).get("overall_score", 0.0) for r in results]
    times = [r.get("elapsed_time", 0) for r in results]
    tool_counts = [r.get("usage", {}).get("request_count", 0) for r in results]
    errors = [r.get("error") for r in results]

    passes = [s >= PASS_THRESHOLD for s in scores]

    metrics = {
        "task_id": task_id,
        "scores": scores,
        "avg_score": statistics.mean(scores) if scores else 0,
        "std_score": statistics.stdev(scores) if len(scores) > 1 else 0,
        "max_score": max(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "pass_at_3": any(passes),  # At least 1 pass
        "pass_3": all(passes),     # All 3 pass
        "pass_count": sum(passes),
        "avg_time": statistics.mean(times) if times else 0,
        "avg_tool_calls": statistics.mean(tool_counts) if tool_counts else 0,
        "error_count": sum(1 for e in errors if e),
        "errors": [e for e in errors if e],
    }
    return metrics


def print_task_summary(metrics):
    """Print a one-line summary for a completed task."""
    tid = metrics["task_id"]
    avg = metrics["avg_score"]
    std = metrics["std_score"]
    p3 = "✓" if metrics["pass_at_3"] else "✗"
    p33 = "✓" if metrics["pass_3"] else "✗"
    bar = "█" * int(avg * 10) + "░" * (10 - int(avg * 10))
    t = metrics["avg_time"]
    tools = metrics["avg_tool_calls"]

    print(f"\n{'─'*70}")
    print(f"  {tid}")
    print(f"  Score: {bar} {avg:.3f} ± {std:.3f} | Pass@3: {p3} | Pass^3: {p33}")
    print(f"  Time: {t:.0f}s avg | Tools: {tools:.0f} avg | Errors: {metrics['error_count']}/3")
    print(f"{'─'*70}")


def print_final_report(all_metrics):
    """Print the final evaluation report."""
    print(f"\n\n{'#'*70}")
    print(f"  FINAL EVALUATION REPORT")
    print(f"  Model: {MODEL}")
    print(f"  Tasks: {len(all_metrics)} | Runs: {len(all_metrics)*RUNS_PER_TASK}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}\n")

    # Group by domain
    domains = {}
    for m in all_metrics:
        prefix = m["task_id"].split("-")[0]
        domains.setdefault(prefix, []).append(m)

    # Overall stats
    all_scores = [m["avg_score"] for m in all_metrics]
    pass_at_3_count = sum(1 for m in all_metrics if m["pass_at_3"])
    pass_3_count = sum(1 for m in all_metrics if m["pass_3"])

    print(f"  Overall Average Score: {statistics.mean(all_scores):.4f}")
    print(f"  Pass@3 Rate: {pass_at_3_count}/{len(all_metrics)} ({pass_at_3_count/len(all_metrics)*100:.1f}%)")
    print(f"  Pass^3 Rate: {pass_3_count}/{len(all_metrics)} ({pass_3_count/len(all_metrics)*100:.1f}%)")
    print(f"  Avg Runtime: {statistics.mean([m['avg_time'] for m in all_metrics]):.0f}s")
    print(f"  Avg Tool Calls: {statistics.mean([m['avg_tool_calls'] for m in all_metrics]):.0f}")
    print()

    # Per-domain breakdown
    print(f"  {'Domain':<10} {'Avg Score':<12} {'Pass@3':<10} {'Pass^3':<10} {'Avg Time':<10} {'Avg Tools':<10}")
    print(f"  {'─'*62}")
    for domain, metrics in sorted(domains.items()):
        avg = statistics.mean([m["avg_score"] for m in metrics])
        p3 = sum(1 for m in metrics if m["pass_at_3"])
        p33 = sum(1 for m in metrics if m["pass_3"])
        t = statistics.mean([m["avg_time"] for m in metrics])
        tools = statistics.mean([m["avg_tool_calls"] for m in metrics])
        n = len(metrics)
        print(f"  {domain:<10} {avg:<12.4f} {p3}/{n:<8} {p33}/{n:<8} {t:<10.0f} {tools:<10.0f}")

    # Per-difficulty breakdown
    print(f"\n  {'Difficulty':<12} {'Avg Score':<12} {'Pass@3':<10} {'Pass^3':<10}")
    print(f"  {'─'*44}")
    diff_groups = {}
    for m in all_metrics:
        # We'll need difficulty from task discovery - store it during eval
        d = m.get("difficulty", "?")
        diff_groups.setdefault(d, []).append(m)
    for d, metrics in sorted(diff_groups.items()):
        avg = statistics.mean([m["avg_score"] for m in metrics])
        p3 = sum(1 for m in metrics if m["pass_at_3"])
        p33 = sum(1 for m in metrics if m["pass_3"])
        n = len(metrics)
        print(f"  L{d:<11} {avg:<12.4f} {p3}/{n:<8} {p33}/{n:<8}")

    # Stability analysis (high variance tasks)
    print(f"\n  Most Unstable Tasks (highest std dev):")
    sorted_by_std = sorted(all_metrics, key=lambda m: m["std_score"], reverse=True)[:10]
    for m in sorted_by_std:
        if m["std_score"] > 0:
            print(f"    {m['task_id']}: σ={m['std_score']:.3f} scores={m['scores']}")

    # Hardest tasks
    print(f"\n  Hardest Tasks (lowest avg score):")
    sorted_by_score = sorted(all_metrics, key=lambda m: m["avg_score"])[:10]
    for m in sorted_by_score:
        print(f"    {m['task_id']}: avg={m['avg_score']:.3f} scores={m['scores']}")

    # Longest tasks
    print(f"\n  Longest Tasks (highest avg runtime):")
    sorted_by_time = sorted(all_metrics, key=lambda m: m["avg_time"], reverse=True)[:10]
    for m in sorted_by_time:
        print(f"    {m['task_id']}: {m['avg_time']:.0f}s avg, {m['avg_tool_calls']:.0f} tools")

    print(f"\n{'#'*70}")


def main():
    """Main evaluation loop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print_header()

    # Discover all tasks
    tasks = discover_tasks(TASKS_DIR)
    print(f"Discovered {len(tasks)} tasks in {TASKS_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Create backend
    backend = _create_backend(HARNESS, MODEL)
    print(f"Backend: {HARNESS}, Image: {backend.docker_image}")
    print(f"Model: {MODEL}")
    print()

    # Open log file
    log_fh = open(LOG_FILE, "w", encoding="utf-8")

    all_metrics = []
    total_start = time.time()

    # Process tasks sequentially (each task gets 3 runs)
    for task_idx, task in enumerate(tasks):
        task_id = task["task_id"]
        difficulty = task.get("difficulty", "?")

        print(f"\n[{task_idx+1}/{len(tasks)}] Starting {task_id} (difficulty={difficulty}, "
              f"timeout={task['timeout_seconds']}s)")

        # Run task 3 times
        results = run_task_n_times(task, backend, n=RUNS_PER_TASK)

        # Compute metrics
        metrics = compute_task_metrics(task_id, results)
        metrics["difficulty"] = difficulty
        all_metrics.append(metrics)

        # Print task summary
        print_task_summary(metrics)

        # Write to log
        log_entry = {
            "task_id": task_id,
            "difficulty": difficulty,
            "metrics": metrics,
            "raw_results": results,
            "timestamp": datetime.now().isoformat(),
        }
        log_fh.write(json.dumps(log_entry, ensure_ascii=False, default=str) + "\n")
        log_fh.flush()

        # Write intermediate summary
        _write_intermediate_summary(all_metrics)

    log_fh.close()

    # Final report
    total_elapsed = time.time() - total_start
    print(f"\nTotal evaluation time: {total_elapsed/3600:.1f} hours")
    print_final_report(all_metrics)

    # Save final summary
    summary = {
        "model": MODEL,
        "harness": HARNESS,
        "total_tasks": len(all_metrics),
        "total_runs": len(all_metrics) * RUNS_PER_TASK,
        "total_time_seconds": total_elapsed,
        "overall_avg_score": statistics.mean([m["avg_score"] for m in all_metrics]),
        "pass_at_3_rate": sum(1 for m in all_metrics if m["pass_at_3"]) / len(all_metrics),
        "pass_3_rate": sum(1 for m in all_metrics if m["pass_3"]) / len(all_metrics),
        "per_task_metrics": all_metrics,
        "timestamp": datetime.now().isoformat(),
    }
    SUMMARY_FILE.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    print(f"\nSummary saved to: {SUMMARY_FILE}")


def _write_intermediate_summary(all_metrics):
    """Write intermediate summary for live monitoring."""
    if not all_metrics:
        return
    intermediate = {
        "completed": len(all_metrics),
        "overall_avg": statistics.mean([m["avg_score"] for m in all_metrics]),
        "pass_at_3": sum(1 for m in all_metrics if m["pass_at_3"]),
        "pass_3": sum(1 for m in all_metrics if m["pass_3"]),
        "last_updated": datetime.now().isoformat(),
    }
    (OUTPUT_DIR / "progress.json").write_text(
        json.dumps(intermediate, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
