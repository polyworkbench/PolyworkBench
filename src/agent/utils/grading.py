"""Grading and evaluation module for LongHorizon.

Runs test.sh / pytest inside containers to evaluate agent outputs.
Results are scored and reported in a format compatible with the
existing LongHorizon evaluation framework.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from src.agent.utils.docker_utils import (
    WORKSPACE_DIR,
    copy_file_from_container,
    copy_tests_to_container,
    exec_in_container,
)

logger = logging.getLogger(__name__)


def run_grade_function(
    container_name: str,
    task_dir: Path,
    output_dir: Path,
    *,
    timeout: int = 60,
) -> dict[str, Any]:
    """Call grade() inside the container and capture multi-dimensional scores.

    This calls the grade() function from test_outputs.py directly, which returns
    the actual weighted scores rather than just pass/fail from pytest.

    Returns:
        Dictionary with {overall_score, dimensions} from grade(), or error.
    """
    copy_tests_to_container(container_name, task_dir / "tests")

    # Run grade() function directly and capture JSON output
    grade_script = (
        f"cd {WORKSPACE_DIR} && python3 -c \""
        "import sys, json; sys.path.insert(0, 'tests'); "
        "from test_outputs import grade; "
        "result = grade(); "
        "print(json.dumps(result, ensure_ascii=False))"
        "\""
    )

    try:
        r = exec_in_container(container_name, grade_script, timeout=timeout)
        output = (r.stdout or "").strip()

        if r.returncode == 0 and output:
            # Try to parse last line as JSON (in case there's debug output before)
            lines = output.strip().split("\n")
            for line in reversed(lines):
                line = line.strip()
                if line.startswith("{"):
                    try:
                        result = json.loads(line)
                        # Save to file
                        (output_dir / "grade_result.json").write_text(
                            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
                        )
                        return result
                    except json.JSONDecodeError:
                        continue

        # If we couldn't parse, return error with raw output
        return {
            "overall_score": 0.0,
            "error": f"Failed to parse grade() output: {output[:500]}",
            "raw_output": output[:1000],
        }

    except subprocess.TimeoutExpired:
        return {"overall_score": 0.0, "error": f"grade() timed out after {timeout}s"}
    except Exception as exc:
        return {"overall_score": 0.0, "error": f"grade() exception: {exc}"}


def run_judge_scoring(
    container_name: str,
    task_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Run LLM-as-Judge scoring using rubric.md criteria.

    Reads the agent's output from the container, loads rubric.md from the task,
    and calls the judge model to evaluate quality.

    Returns:
        Dictionary with judge_score and per-dimension scores.
    """
    import os
    import requests

    # Load rubric
    rubric_path = task_dir / "tests" / "rubric.md"
    if not rubric_path.exists():
        return {"judge_score": 0.0, "error": "No rubric.md found"}

    rubric_content = rubric_path.read_text(encoding="utf-8")

    # Get agent output from container
    try:
        r = exec_in_container(
            container_name,
            f"cat {WORKSPACE_DIR}/answer.json 2>/dev/null || "
            f"cat {WORKSPACE_DIR}/output/answer.json 2>/dev/null || "
            f"echo '{{}}'"
        )
        answer_content = (r.stdout or "{}").strip()[:6000]
    except Exception:
        answer_content = "{}"

    # Also get file listing
    try:
        r = exec_in_container(
            container_name,
            f"find {WORKSPACE_DIR}/output -type f 2>/dev/null | head -20"
        )
        file_listing = (r.stdout or "").strip()
    except Exception:
        file_listing = ""

    # Build judge prompt
    task_id = task_dir.name
    prompt = f"""You are evaluating an AI agent's output for task: {task_id}

## Rubric
{rubric_content}

## Agent Output Files
{file_listing}

## Agent answer.json Content (first 6000 chars)
{answer_content}

## Instructions
Based on the rubric above, rate this output on each dimension (0-10 scale).
Respond with ONLY a JSON object in this format:
{{"scores": {{"dimension_name": score, ...}}, "overall": score, "reasoning": "brief explanation"}}
"""

    # Call judge model
    judge_api_key = os.environ.get("JUDGE_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
    judge_base_url = os.environ.get("JUDGE_BASE_URL", os.environ.get("ANTHROPIC_BASE_URL", ""))
    judge_model = os.environ.get("JUDGE_MODEL", "minimax/MiniMax-M2.7")

    url = f"{judge_base_url}/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": judge_api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": judge_model,
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}],
    }

    # Retry up to 3 times for judge API
    response_text = ""
    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", [])
            # Handle models with thinking blocks (e.g., MiniMax-M3)
            # Find the first "text" type block, skip "thinking" blocks
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        response_text = block.get("text", "")
                        break
                    elif block.get("type") != "thinking" and "text" in block:
                        response_text = block.get("text", "")
                        break
            # Fallback: try first block's text if no explicit type
            if not response_text and content:
                if isinstance(content[0], dict):
                    response_text = content[0].get("text", "")
                elif isinstance(content[0], str):
                    response_text = content[0]
            if response_text:
                break
        except Exception as exc:
            if attempt == 2:
                return {"judge_score": 0.0, "error": f"Judge API error after 3 retries: {exc}"}
            import time
            time.sleep(5 * (attempt + 1))  # 5s, 10s backoff

    # Parse judge response
    import re

    # Strip markdown code fences (```json ... ```) that some models wrap around JSON
    cleaned_response = response_text.strip()
    cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response)
    cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
    cleaned_response = cleaned_response.strip()

    try:
        # Try full JSON parse
        parsed = json.loads(cleaned_response)
        scores = parsed.get("scores", {})
        overall = parsed.get("overall", 0)
        if isinstance(overall, (int, float)):
            judge_score = min(1.0, overall / 10.0)
        elif scores:
            judge_score = min(1.0, sum(scores.values()) / (len(scores) * 10.0))
        else:
            judge_score = 0.0

        result = {
            "judge_score": round(judge_score, 4),
            "dimensions": {k: min(1.0, v / 10.0) for k, v in scores.items() if isinstance(v, (int, float))},
            "reasoning": parsed.get("reasoning", ""),
        }
    except json.JSONDecodeError:
        # Try to find JSON in response
        json_match = re.search(r'\{[^{}]*"scores"[^{}]*\{[^}]*\}[^}]*\}', response_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                scores = parsed.get("scores", {})
                judge_score = sum(v for v in scores.values() if isinstance(v, (int, float))) / (len(scores) * 10.0) if scores else 0.0
                result = {
                    "judge_score": round(min(1.0, judge_score), 4),
                    "dimensions": {k: min(1.0, v / 10.0) for k, v in scores.items() if isinstance(v, (int, float))},
                }
            except Exception:
                result = {"judge_score": 0.0, "error": "Failed to parse judge response", "raw": response_text[:300]}
        else:
            result = {"judge_score": 0.0, "error": "No JSON in judge response", "raw": response_text[:300]}

    # Save result
    (output_dir / "judge_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return result


def run_grading(
    container_name: str,
    task_dir: Path,
    output_dir: Path,
    *,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run the full evaluation: pytest + grade() + LLM Judge.

    Executes tests/test.sh (which typically runs pytest) and captures
    the test results for scoring. Also calls grade() directly for
    multi-dimensional scores, and runs LLM-as-Judge for quality assessment.

    Args:
        container_name: The running container with the agent's outputs.
        task_dir: Host path to the task directory (for copying tests).
        output_dir: Where to write grading results.
        timeout: Maximum grading time in seconds.

    Returns:
        Dictionary with grading results:
          - overall_score: float (0.0 to 1.0) — from grade() function
          - pytest_score: float — pass/fail ratio from pytest
          - judge_score: float — LLM-as-Judge score
          - dimensions: dict — per-dimension scores from grade()
          - tests_passed: int
          - tests_total: int
          - details: str (test output)
          - error: str | None
    """
    tests_dir = task_dir / "tests"
    if not tests_dir.is_dir():
        logger.warning("[%s] No tests directory found: %s", container_name, tests_dir)
        return {"overall_score": 0.0, "error": "No tests directory found"}

    # Ensure tests are in the container
    copy_tests_to_container(container_name, tests_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────────────────────────────────
    # Track 1: Run pytest (pass/fail)
    # ──────────────────────────────────────────────────────────────────────
    test_entrypoint = f"{WORKSPACE_DIR}/tests/test.sh"
    logger.info("[%s] Running grading: %s", container_name, test_entrypoint)

    try:
        r = exec_in_container(
            container_name,
            f"cd {WORKSPACE_DIR} && chmod +x tests/test.sh && bash tests/test.sh",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        logger.error("[%s] Grading timed out after %ds", container_name, timeout)
        scores = {"overall_score": 0.0, "error": f"Grading timed out after {timeout}s"}
        _write_score(output_dir, container_name, scores)
        return scores

    test_output = (r.stdout or "") + ("\n" if r.stdout else "") + (r.stderr or "")
    (output_dir / "test_output.txt").write_text(test_output, encoding="utf-8")
    pytest_scores = _parse_pytest_results(r.returncode, test_output)

    # ──────────────────────────────────────────────────────────────────────
    # Track 2: Call grade() for multi-dimensional structural scores
    # ──────────────────────────────────────────────────────────────────────
    grade_result = run_grade_function(container_name, task_dir, output_dir)
    grade_overall = grade_result.get("overall_score", 0.0)
    grade_dimensions = grade_result.get("dimensions", {})

    # ──────────────────────────────────────────────────────────────────────
    # Track 3: LLM-as-Judge (using rubric.md)
    # ──────────────────────────────────────────────────────────────────────
    judge_result = run_judge_scoring(container_name, task_dir, output_dir)
    judge_score = judge_result.get("judge_score", 0.0)

    # ──────────────────────────────────────────────────────────────────────
    # Combine results
    # ──────────────────────────────────────────────────────────────────────
    combined_scores = {
        # Primary score: grade() structural score (0.0-1.0)
        "overall_score": grade_overall,
        # Pytest pass/fail ratio
        "pytest_score": pytest_scores.get("overall_score", 0.0),
        "tests_passed": pytest_scores.get("tests_passed", 0),
        "tests_total": pytest_scores.get("tests_total", 0),
        # Multi-dimensional breakdown from grade()
        "dimensions": grade_dimensions,
        # LLM-as-Judge score
        "judge_score": judge_score,
        "judge_dimensions": judge_result.get("dimensions", {}),
        "judge_reasoning": judge_result.get("reasoning", ""),
        # Details
        "details": test_output[-2000:] if len(test_output) > 2000 else test_output,
    }

    # Log summary
    logger.info(
        "[%s] Scores — grade: %.3f | pytest: %.2f (%d/%d) | judge: %.3f",
        container_name,
        grade_overall,
        pytest_scores.get("overall_score", 0.0),
        pytest_scores.get("tests_passed", 0),
        pytest_scores.get("tests_total", 0),
        judge_score,
    )

    # Write score file
    _write_score(output_dir, container_name, combined_scores)

    return combined_scores


def run_pytest_grading(
    container_name: str,
    task_dir: Path,
    output_dir: Path,
    *,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run pytest directly inside the container for more detailed results.

    This is an alternative to test.sh that provides structured JSON output.
    """
    tests_dir = task_dir / "tests"
    if not tests_dir.is_dir():
        return {"overall_score": 0.0, "error": "No tests directory found"}

    copy_tests_to_container(container_name, tests_dir)

    # Run pytest with JSON report
    try:
        r = exec_in_container(
            container_name,
            (
                f"cd {WORKSPACE_DIR} && "
                f"python3 -m pytest tests/test_outputs.py -v --tb=short "
                f"--json-report --json-report-file=/tmp/pytest_report.json 2>&1 || "
                f"python3 -m pytest tests/test_outputs.py -v --tb=short 2>&1"
            ),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        scores = {"overall_score": 0.0, "error": f"Pytest timed out after {timeout}s"}
        _write_score(output_dir, container_name, scores)
        return scores

    test_output = (r.stdout or "") + (r.stderr or "")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "pytest_output.txt").write_text(test_output, encoding="utf-8")

    # Try to get JSON report
    json_report_host = output_dir / "pytest_report.json"
    copy_file_from_container(
        container_name, "/tmp/pytest_report.json", json_report_host
    )

    if json_report_host.exists():
        scores = _parse_pytest_json_report(json_report_host)
    else:
        scores = _parse_pytest_results(r.returncode, test_output)

    _write_score(output_dir, container_name, scores)
    return scores


def _parse_pytest_results(returncode: int, output: str) -> dict[str, Any]:
    """Parse pytest text output to extract pass/fail counts.

    Args:
        returncode: The pytest exit code (0 = all passed).
        output: Combined stdout/stderr from pytest.

    Returns:
        Grading results dictionary.
    """
    scores: dict[str, Any] = {
        "overall_score": 0.0,
        "tests_passed": 0,
        "tests_total": 0,
        "details": output[-2000:] if len(output) > 2000 else output,
    }

    if returncode == 0:
        # All tests passed
        scores["overall_score"] = 1.0
        # Try to parse count from output like "5 passed"
        import re
        match = re.search(r"(\d+)\s+passed", output)
        if match:
            passed = int(match.group(1))
            scores["tests_passed"] = passed
            scores["tests_total"] = passed
        else:
            scores["tests_passed"] = 1
            scores["tests_total"] = 1
    else:
        # Some tests failed - try to extract counts
        import re
        passed_match = re.search(r"(\d+)\s+passed", output)
        failed_match = re.search(r"(\d+)\s+failed", output)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 1
        total = passed + failed

        scores["tests_passed"] = passed
        scores["tests_total"] = total
        scores["overall_score"] = round(passed / total, 4) if total > 0 else 0.0

    return scores


def _parse_pytest_json_report(report_path: Path) -> dict[str, Any]:
    """Parse a pytest JSON report for detailed results."""
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"overall_score": 0.0, "error": f"Failed to parse JSON report: {exc}"}

    summary = report.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    error = summary.get("error", 0)
    total = passed + failed + error

    overall_score = round(passed / total, 4) if total > 0 else 0.0

    return {
        "overall_score": overall_score,
        "tests_passed": passed,
        "tests_total": total,
        "tests_failed": failed,
        "tests_error": error,
    }


def _write_score(output_dir: Path, task_id: str, scores: dict[str, Any]) -> None:
    """Write score.json to the output directory."""
    score_path = output_dir / "score.json"
    score_path.parent.mkdir(parents=True, exist_ok=True)
    score_path.write_text(
        json.dumps(scores, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("[%s] Grading results written to %s", task_id, score_path)


def format_scores(task_id: str, scores: dict[str, Any]) -> str:
    """Format scores for display."""
    if "error" in scores and not scores.get("overall_score"):
        return f"[{task_id}] Grading error: {scores['error']}"

    overall = scores.get("overall_score", 0.0)
    pytest_score = scores.get("pytest_score", scores.get("overall_score", 0.0))
    judge = scores.get("judge_score", 0.0)
    passed = scores.get("tests_passed", 0)
    total = scores.get("tests_total", 0)
    bar = "█" * int(overall * 10) + "░" * (10 - int(overall * 10))

    line = f"[{task_id}] {bar} grade={overall:.3f} | pytest={pytest_score:.2f} ({passed}/{total}) | judge={judge:.3f}"

    # Show dimension breakdown if available
    dims = scores.get("dimensions", {})
    if dims and isinstance(dims, dict):
        dim_strs = []
        for name, dim_data in list(dims.items())[:4]:
            if isinstance(dim_data, dict):
                s = dim_data.get("score", 0)
                dim_strs.append(f"{name}:{s:.2f}")
            elif isinstance(dim_data, (int, float)):
                dim_strs.append(f"{name}:{dim_data:.2f}")
        if dim_strs:
            line += f"\n  Dims: {' | '.join(dim_strs)}"

    return line


def print_summary(results: list[dict[str, Any]], output_dir: Path) -> None:
    """Print a summary table of all task results."""
    print(f"\n{'#' * 60}")
    print("  LongHorizon Evaluation Summary")
    print(f"{'#' * 60}")

    total_score = 0.0
    scored_count = 0

    for r in results:
        task_id = r.get("task_id", "unknown")
        scores = r.get("scores", {})
        error = r.get("error")

        if error:
            print(f"  ✗ {task_id}: ERROR - {error}")
            continue

        overall = scores.get("overall_score", 0.0)
        passed = scores.get("tests_passed", 0)
        total = scores.get("tests_total", 0)
        bar = "█" * int(overall * 10) + "░" * (10 - int(overall * 10))
        print(f"  ✓ {task_id}: {bar} {overall:.2f} ({passed}/{total})")
        total_score += overall
        scored_count += 1

    if scored_count > 0:
        avg_score = total_score / scored_count
        print(f"\n  Average score: {avg_score:.4f} ({scored_count} tasks)")
    else:
        print("\n  No tasks scored successfully.")

    # Write summary JSON with timestamp to avoid overwriting previous runs
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = output_dir / f"summary_{timestamp}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    # Also write a latest symlink/copy for convenience
    latest_path = output_dir / "summary_latest.json"
    latest_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"  Summary written to: {summary_path}")
    print("#" * 60)
