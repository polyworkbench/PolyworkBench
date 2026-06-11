"""
LLM-as-Judge scoring for BabelAgentBench.

Calls JUDGE_MODEL to evaluate content quality, language quality, and semantic correctness
that rule-based pytest cannot assess.

Each task has specific judge criteria focusing on:
1. Content correctness & logical soundness
2. Target language quality & professionalism
3. Completeness of the requested deliverables
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict

import requests

# Judge API configuration
JUDGE_API_KEY = os.environ.get("JUDGE_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
JUDGE_BASE_URL = os.environ.get("JUDGE_BASE_URL", "https://api.anthropic.com")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-20250514")


def _call_judge(prompt: str, max_tokens: int = 2000) -> str:
    """Call the judge model via Anthropic messages API."""
    url = f"{JUDGE_BASE_URL}/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": JUDGE_API_KEY,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": JUDGE_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("content", [])
        if content and isinstance(content, list):
            return content[0].get("text", "")
        return ""
    except Exception as e:
        return f"JUDGE_ERROR: {e}"


def _parse_scores(response: str) -> Dict[str, float]:
    """Parse judge response for numeric scores (0-10 scale)."""
    scores = {}

    # Try to parse entire response as JSON first
    try:
        parsed = json.loads(response.strip())
        if "scores" in parsed:
            for k, v in parsed["scores"].items():
                if isinstance(v, (int, float)):
                    scores[k] = min(1.0, v / 10.0)
            return scores
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in response
    json_match = re.search(r'\{.*"scores".*\}', response, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            for k, v in parsed.get("scores", {}).items():
                if isinstance(v, (int, float)):
                    scores[k] = min(1.0, v / 10.0)
            return scores
        except json.JSONDecodeError:
            pass

    # Fallback: look for patterns like "key: N/10"
    for match in re.finditer(r'(\w+)[\s:]+(\d+(?:\.\d+)?)\s*/\s*10', response, re.IGNORECASE):
        key = match.group(1).lower()
        score = float(match.group(2)) / 10.0
        scores[key] = min(1.0, score)

    return scores


# === Task-specific Judge Criteria ===

JUDGE_CRITERIA = {
    "HQ-01_neurips_to_acl": {
        "dimensions": ["format_correctness", "compilation_quality", "completeness"],
        "prompt_template": """You are evaluating an AI agent's output for a LaTeX template migration task.

Task: Migrate a NeurIPS paper to ACL ARR format (anonymization, add Limitations/Ethics, create acl.sty, compile).

Agent's output files:
{file_listing}

Main tex file content (first 2000 chars):
{main_content}

Rate on 0-10 scale:
1. format_correctness: Does the output follow ACL ARR format? (anonymized, correct sections, bibliography)
2. compilation_quality: Did LaTeX compile successfully? Are there residual errors?
3. completeness: Are all required deliverables present? (acl.sty, diff, validation_report, answer.json)

Respond with ONLY a JSON object: {{"scores": {{"format_correctness": X, "compilation_quality": X, "completeness": X}}}}""",
    },

    "HQ-02_jp_receipt_to_en_excel": {
        "dimensions": ["extraction_accuracy", "calculation_correctness", "compliance_judgment"],
        "prompt_template": """You are evaluating an AI agent's output for a Japanese receipt processing task.

Task: Extract data from 3 Japanese receipts (OCR text), apply 上様 rule (≥30K JPY not reimbursable), calculate tax/FX, generate Concur CSV.

Ground truth:
- R001: ¥1,149 (8%+10% tax, reimbursable)
- R002: ¥14,400 (shinkansen, reimbursable)
- R003: ~¥34,243 (上様, ≥30K → NOT reimbursable)
- FX rate: 1 JPY = 0.04632 CNY

Agent's answer.json content:
{answer_content}

Rate on 0-10 scale:
1. extraction_accuracy: Are amounts, dates, tax rates correctly extracted from Japanese text?
2. calculation_correctness: Are FX conversions and tax calculations correct?
3. compliance_judgment: Is the 上様 ≥30K rule correctly applied (R003 rejected)?

Respond with ONLY a JSON object: {{"scores": {{"extraction_accuracy": X, "calculation_correctness": X, "compliance_judgment": X}}}}""",
    },

    "HQ-03_ko_kr_sre_zh_logs": {
        "dimensions": ["rca_quality", "timeline_accuracy", "korean_output_quality"],
        "prompt_template": """You are evaluating an AI agent's output for a K8s incident RCA task.

Task: Analyze a Redis Sentinel + Redlock payment failure. Instructions were in Korean. Required outputs include English RCA, Korean executive summary (≤80 chars), and timeline in KST.

Key facts:
- Root cause: Redis master failover caused Redlock TTL expiry → payment failures
- Impact: success rate dropped to 45%, MTTR ~30min
- Fix: lock TTL 30s → 60s hotpatch by zhang.wei

Agent's answer.json content:
{answer_content}

Rate on 0-10 scale:
1. rca_quality: Is the root cause analysis technically correct? Does it identify Redis Redlock as the issue?
2. timeline_accuracy: Are events correctly placed in KST timezone? Is the timeline comprehensive?
3. korean_output_quality: Is there a Korean executive summary? Is it natural Korean (not machine-translated garbage)?

Respond with ONLY a JSON object: {{"scores": {{"rca_quality": X, "timeline_accuracy": X, "korean_output_quality": X}}}}""",
    },

    "HQ-04_es_privacy_compliance": {
        "dimensions": ["legal_accuracy", "spanish_quality", "completeness"],
        "prompt_template": """You are evaluating an AI agent's output for a privacy compliance gap analysis task.

Task: Compare CCPA (English) + DSGVO (German) against Mexico's LFPDPPP. Output a Spanish compliance report with article-by-article mapping, risk scores, and action plan.

Agent's answer.json content:
{answer_content}

Rate on 0-10 scale:
1. legal_accuracy: Is the legal analysis correct? Are CCPA/DSGVO/LFPDPPP properly compared?
2. spanish_quality: Is the output in proper Spanish legal register? (Not English, not informal)
3. completeness: Does it include compliance matrix, risk assessment, glossary, action plan?

Respond with ONLY a JSON object: {{"scores": {{"legal_accuracy": X, "spanish_quality": X, "completeness": X}}}}""",
    },

    "HQ-05_ma_due_diligence_stress": {
        "dimensions": ["financial_accuracy", "contradiction_detection", "french_quality"],
        "prompt_template": """You are evaluating an AI agent's output for a cross-border M&A due diligence task.

Task: Analyze AsiaCommerce Holdings acquisition using sources in Chinese, Japanese, Korean, and English. Output a French DD memo. Must detect a ~1亿 CNY net income discrepancy between sources.

Key facts:
- Revenue 2023: 156,800万 CNY
- Net income discrepancy: Japan CFO PV says ~142M, China HQ says 152M (1亿 difference)
- Purchase price: EUR 280M
- Korean litigation risk: ₩12B transfer pricing

Agent's answer.json content:
{answer_content}

Rate on 0-10 scale:
1. financial_accuracy: Are CNY→EUR conversions correct? Are growth rates accurate?
2. contradiction_detection: Was the 1亿 CNY net income discrepancy identified and sourced?
3. french_quality: Is the output in proper French business/legal register? (Not English)

Respond with ONLY a JSON object: {{"scores": {{"financial_accuracy": X, "contradiction_detection": X, "french_quality": X}}}}""",
    },
}


def judge_task(task_id: str, workspace_path: Path) -> Dict[str, Any]:
    """Run LLM judge evaluation for a task's output."""
    criteria = JUDGE_CRITERIA.get(task_id)
    if not criteria:
        return {"error": f"No judge criteria for {task_id}"}

    # Load answer.json or equivalent
    answer_path = workspace_path / "answer.json"
    if not answer_path.exists():
        answer_path = workspace_path / "output" / "answer.json"

    answer_content = ""
    if answer_path.exists():
        answer_content = answer_path.read_text(encoding="utf-8-sig")[:8000]
    else:
        # Try to assemble from output files
        output_dir = workspace_path / "output"
        if output_dir.exists():
            files = list(output_dir.iterdir())
            answer_content = f"Files in output/: {[f.name for f in files]}\n"
            for f in files[:3]:
                if f.suffix in ('.json', '.md', '.txt', '.csv') and f.stat().st_size < 3000:
                    answer_content += f"\n--- {f.name} ---\n{f.read_text(encoding='utf-8-sig')[:2000]}\n"

    if not answer_content:
        return {"judge_score": 0.0, "dimensions": {}, "error": "No output found"}

    # Build file listing for HQ-01
    file_listing = ""
    output_dir = workspace_path / "output"
    if output_dir.exists():
        file_listing = str([f.name for f in output_dir.iterdir()])

    # Fill prompt template
    main_content = ""
    if task_id == "HQ-01_neurips_to_acl":
        main_tex = workspace_path / "output" / "main.tex"
        if main_tex.exists():
            main_content = main_tex.read_text(encoding="utf-8-sig")[:2000]

    prompt = criteria["prompt_template"].format(
        answer_content=answer_content[:6000],
        file_listing=file_listing,
        main_content=main_content,
    )

    # Call judge
    response = _call_judge(prompt)
    if response.startswith("JUDGE_ERROR"):
        return {"judge_score": 0.0, "error": response}

    # Parse scores
    scores = _parse_scores(response)
    if not scores:
        # Try to extract from raw response
        return {"judge_score": 0.0, "raw_response": response[:500], "error": "Failed to parse scores"}

    # Calculate weighted average
    dims = criteria["dimensions"]
    total = sum(scores.get(d, 0.0) for d in dims)
    judge_score = total / len(dims) if dims else 0.0

    return {
        "judge_score": round(judge_score, 4),
        "dimensions": {d: scores.get(d, 0.0) for d in dims},
        "raw_response": response[:200],
    }


def run_judge_all(output_root: Path) -> Dict[str, Any]:
    """Run judge evaluation for all tasks in an output directory."""
    results = {}
    for task_dir in sorted(output_root.iterdir()):
        if not task_dir.is_dir():
            continue
        task_id = task_dir.name
        # Find latest workspace
        runs = sorted(task_dir.iterdir(), reverse=True)
        for run_dir in runs:
            ws = run_dir / "task_output" / "workspace"
            if ws.exists():
                print(f"Judging {task_id} ({run_dir.name})...")
                result = judge_task(task_id, ws)
                results[task_id] = result
                print(f"  Judge score: {result.get('judge_score', 0):.2%}")
                break
    return results


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # Re-read env after dotenv
    JUDGE_API_KEY = os.environ.get("JUDGE_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
    JUDGE_BASE_URL = os.environ.get("JUDGE_BASE_URL", "https://api.anthropic.com")
    JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-20250514")

    output_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/openclaw")

    # Run for specific model if provided
    if len(sys.argv) > 2:
        model_filter = sys.argv[2]
        print(f"Running judge for model filter: {model_filter}")
    else:
        model_filter = None

    all_results = {}
    for task_dir in sorted(output_root.iterdir()):
        if not task_dir.is_dir() or not task_dir.name.startswith("HQ-"):
            continue
        task_id = task_dir.name
        runs = sorted([d for d in task_dir.iterdir() if d.is_dir()])
        for run_dir in runs:
            if model_filter and model_filter not in run_dir.name:
                continue
            ws = run_dir / "task_output" / "workspace"
            if ws.exists():
                model_key = run_dir.name.split("_2026")[0]
                print(f"Judging {task_id} ({model_key})...")
                result = judge_task(task_id, ws)
                all_results.setdefault(model_key, {})[task_id] = result
                print(f"  Judge: {result.get('judge_score', 0):.2%} {result.get('dimensions', {})}")

    # Print summary
    print("\n" + "=" * 60)
    print("LLM Judge Summary")
    print("=" * 60)
    for model, tasks in sorted(all_results.items()):
        scores = [t.get("judge_score", 0) for t in tasks.values()]
        avg = sum(scores) / len(scores) if scores else 0
        print(f"\n{model}: avg={avg:.2%}")
        for tid, res in sorted(tasks.items()):
            print(f"  {tid}: {res.get('judge_score', 0):.2%} {res.get('dimensions', {})}")
