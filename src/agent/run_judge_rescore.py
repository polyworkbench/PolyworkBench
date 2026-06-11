#!/usr/bin/env python3
"""Re-run LLM-as-Judge scoring on all completed task outputs."""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from dotenv import load_dotenv
load_dotenv(override=True)

import requests

EVAL_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "full_eval_v2" / "openclaw"
JUDGE_API_KEY = os.environ.get("JUDGE_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
JUDGE_BASE_URL = os.environ.get("JUDGE_BASE_URL", os.environ.get("ANTHROPIC_BASE_URL", ""))
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "minimax/MiniMax-M2.7")
TASKS_DIR = Path(__file__).resolve().parent.parent.parent / "full_tasks"


def call_judge(prompt, max_retries=3):
    """Call judge with retry and thinking-block handling."""
    url = f"{JUDGE_BASE_URL}/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": JUDGE_API_KEY,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": JUDGE_MODEL,
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}],
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", [])

            # Handle thinking blocks (MiniMax-M3 style)
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    return block.get("text", "")

            # Fallback
            if content and isinstance(content[0], dict):
                return content[0].get("text", "")
            return ""
        except Exception as e:
            if attempt == max_retries - 1:
                return f"ERROR: {e}"
            time.sleep(5 * (attempt + 1))
    return ""


def judge_task(task_id, workspace_path):
    """Score a task output using LLM judge."""
    # Load rubric
    rubric_path = TASKS_DIR / task_id / "tests" / "rubric.md"
    if not rubric_path.exists():
        return {"judge_score": 0.0, "error": "No rubric.md"}

    rubric = rubric_path.read_text(encoding="utf-8")[:1500]

    # Load answer
    answer_path = workspace_path / "answer.json"
    if not answer_path.exists():
        answer_path = workspace_path / "output" / "answer.json"

    answer = ""
    if answer_path.exists():
        answer = answer_path.read_text(encoding="utf-8-sig")[:2000]
    else:
        # Try to find output files
        out_dir = workspace_path / "output"
        if out_dir.exists():
            files = list(out_dir.iterdir())
            answer = f"Files: {[f.name for f in files[:10]]}\n"
            for f in files[:3]:
                if f.suffix in ('.json', '.md', '.txt') and f.stat().st_size < 2000:
                    answer += f"\n--- {f.name} ---\n{f.read_text(encoding='utf-8-sig')[:1500]}\n"

    if not answer.strip() or answer.strip() == "{}":
        return {"judge_score": 0.0, "error": "No output to judge"}

    prompt = f"""Score this AI agent output (0-10) for task: {task_id}

Rubric dimensions (rate each 0-10):
{rubric[:1000]}

Agent output excerpt:
{answer[:1200]}

Return ONLY a JSON object: {{"scores": {{"dim1": N, "dim2": N}}, "overall": N, "reasoning": "one sentence"}}"""

    response = call_judge(prompt)
    if response.startswith("ERROR:"):
        return {"judge_score": 0.0, "error": response}

    # Parse
    import re

    # Strip markdown code fences (```json ... ```)
    cleaned = response.strip()
    cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned)
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        match = re.search(r'\{[^{}]*"scores"[^{}]*\{[^}]*\}[^}]*\}', response, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
            except:
                return {"judge_score": 0.0, "error": "Parse failed", "raw": response[:200]}
        else:
            # Try simpler pattern
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                except:
                    return {"judge_score": 0.0, "error": "Parse failed", "raw": response[:200]}
            else:
                return {"judge_score": 0.0, "error": "No JSON found", "raw": response[:200]}

    scores = parsed.get("scores", {})
    overall = parsed.get("overall", 0)

    if isinstance(overall, (int, float)) and overall > 0:
        judge_score = min(1.0, overall / 10.0)
    elif scores:
        vals = [v for v in scores.values() if isinstance(v, (int, float))]
        judge_score = min(1.0, sum(vals) / (len(vals) * 10.0)) if vals else 0.0
    else:
        judge_score = 0.0

    return {
        "judge_score": round(judge_score, 4),
        "dimensions": {k: round(min(1.0, v / 10.0), 3) for k, v in scores.items() if isinstance(v, (int, float))},
        "reasoning": parsed.get("reasoning", ""),
    }


def main():
    results = {}
    task_dirs = sorted(EVAL_DIR.iterdir())

    print(f"Re-scoring {len(task_dirs)} tasks with LLM Judge...")
    print(f"Judge model: {JUDGE_MODEL}")
    print(f"Judge URL: {JUDGE_BASE_URL}")
    print()

    for task_dir in task_dirs:
        if not task_dir.is_dir():
            continue
        task_id = task_dir.name

        # Find latest run
        runs = sorted([d for d in task_dir.iterdir() if d.is_dir()], reverse=True)
        if not runs:
            continue

        run_dir = runs[0]
        workspace = run_dir / "task_output" / "workspace"
        if not workspace.exists():
            print(f"  [{task_id}] No workspace found, skipping")
            continue

        print(f"  [{task_id}] Judging...", end=" ", flush=True)
        result = judge_task(task_id, workspace)
        results[task_id] = result

        score = result.get("judge_score", 0)
        error = result.get("error", "")
        dims = result.get("dimensions", {})
        dim_str = " ".join(f"{k}:{v:.1f}" for k, v in list(dims.items())[:3])
        if error:
            print(f"judge={score:.3f} [ERR: {error[:40]}]")
        else:
            print(f"judge={score:.3f} ({dim_str})")

        # Save per-task
        (run_dir / "judge_result.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Rate limit
        time.sleep(1)

    # Summary
    valid_scores = [r["judge_score"] for r in results.values() if r.get("judge_score", 0) > 0]
    print(f"\n{'='*60}")
    print(f"Judge Scoring Complete")
    print(f"  Tasks scored: {len(results)}")
    print(f"  Tasks with score > 0: {len(valid_scores)}")
    print(f"  Average judge score: {sum(valid_scores)/len(valid_scores):.4f}" if valid_scores else "  No valid scores")
    print(f"{'='*60}")

    # Save all results
    output_path = EVAL_DIR.parent / "judge_scores.json"
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
