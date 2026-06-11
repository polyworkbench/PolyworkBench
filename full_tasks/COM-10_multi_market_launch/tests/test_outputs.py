"""
Test suite for COM-10: Multi-market product launch planning with 5-language synthesis.
Evaluates synthesis quality, contradiction detection, Chinese plan, English brief,
timeline feasibility, and data accuracy.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any


OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))
ANSWER_PATH = "/workspace/answer.json"


def _load_answer() -> Dict[str, Any]:
    """Load answer.json with fallback paths."""
    paths = [ANSWER_PATH, os.path.join(OUTPUT_DIR, "answer.json")]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def _load_json_file(filename: str) -> Any:
    """Load a JSON file from output directory."""
    paths = [os.path.join(OUTPUT_DIR, filename), f"/workspace/{filename}"]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def _load_text_file(filename: str) -> str:
    """Load a text file from output directory."""
    paths = [os.path.join(OUTPUT_DIR, filename), f"/workspace/{filename}"]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return ""


def _contains_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    chinese_pattern = re.compile(r'[一-鿿]')
    return bool(chinese_pattern.search(text))


def _is_primarily_english(text: str) -> bool:
    """Check if text is primarily in English."""
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    total_alpha = len(re.findall(r'[a-zA-Z一-鿿가-힣а-яА-Я]', text))
    if total_alpha == 0:
        return False
    return latin_chars / total_alpha > 0.6


def _score_synthesis_quality() -> float:
    """Score market data synthesis quality (weight: 0.20)."""
    score = 0.0
    synthesis = _load_json_file("market_synthesis.json")

    if not synthesis:
        return 0.0

    score += 0.15  # File exists

    content_str = json.dumps(synthesis, ensure_ascii=False).lower()

    # Check coverage of all markets
    markets = ["japan", "korea", "russia", "vietnam", "日本", "韩国", "俄罗斯", "越南"]
    found_markets = sum(1 for m in markets if m in content_str)
    if found_markets >= 4:
        score += 0.25
    elif found_markets >= 2:
        score += 0.15

    # Check for quantitative data
    numbers = re.findall(r'\d+\.?\d*', content_str)
    if len(numbers) >= 20:
        score += 0.2
    elif len(numbers) >= 10:
        score += 0.1

    # Check for market size data
    if any(term in content_str for term in ["market_size", "size", "规模", "revenue"]):
        score += 0.2

    # Check for consumer insights
    if any(term in content_str for term in ["consumer", "trend", "preference", "消费者", "趋势"]):
        score += 0.2

    return min(score, 1.0)


def _score_contradiction_detection() -> float:
    """Score contradiction detection (weight: 0.20)."""
    score = 0.0
    contradictions = _load_json_file("contradiction_report.json")
    answer = _load_answer()

    if not contradictions:
        return 0.0

    score += 0.2  # File exists

    content_str = json.dumps(contradictions, ensure_ascii=False)

    # Check for actual contradiction entries
    if isinstance(contradictions, list) and len(contradictions) > 0:
        score += 0.2
        if len(contradictions) >= 3:
            score += 0.1
    elif isinstance(contradictions, dict):
        items = contradictions.get("contradictions", contradictions.get("items", []))
        if isinstance(items, list) and len(items) > 0:
            score += 0.2
            if len(items) >= 3:
                score += 0.1

    # Check answer has contradiction count
    if isinstance(answer.get("total_contradictions_found"), int) and answer["total_contradictions_found"] > 0:
        score += 0.2

    # Check for specific contradiction types (market size, growth rates, etc.)
    contradiction_indicators = ["market size", "growth", "cagr", "inconsisten", "conflict", "矛盾", "不一致", "差异"]
    found = sum(1 for c in contradiction_indicators if c in content_str.lower())
    if found >= 3:
        score += 0.2
    elif found >= 1:
        score += 0.1

    # Check for source attribution
    sources = ["japan", "korea", "russia", "vietnam", "competitive", "日本", "韩国"]
    found_sources = sum(1 for s in sources if s in content_str.lower())
    if found_sources >= 3:
        score += 0.1

    return min(score, 1.0)


def _score_chinese_plan() -> float:
    """Score Chinese strategic plan (weight: 0.20)."""
    score = 0.0
    plan = _load_text_file("launch_plan_zh.md")

    if not plan:
        return 0.0

    score += 0.15  # File exists

    # Check for Chinese content
    if _contains_chinese(plan):
        score += 0.15

    # Check Chinese content ratio
    chinese_chars = len(re.findall(r'[一-鿿]', plan))
    total_chars = len(plan.replace(" ", "").replace("\n", ""))
    if total_chars > 0:
        ratio = chinese_chars / total_chars
        if ratio > 0.3:
            score += 0.15
        elif ratio > 0.15:
            score += 0.1

    # Check length (should be 3000+ chars)
    if len(plan) > 3000:
        score += 0.15
    elif len(plan) > 1500:
        score += 0.1

    # Check for markdown structure
    headers = re.findall(r'^#+\s+.+$', plan, re.MULTILINE)
    if len(headers) >= 5:
        score += 0.15
    elif len(headers) >= 3:
        score += 0.1

    # Check for strategic content
    strategy_terms = ["策略", "市场", "定价", "渠道", "风险", "预算", "时间", "目标"]
    found = sum(1 for t in strategy_terms if t in plan)
    if found >= 5:
        score += 0.15
    elif found >= 3:
        score += 0.1

    # Check for multi-market coverage
    market_terms = ["日本", "韩国", "俄罗斯", "越南"]
    found_markets = sum(1 for m in market_terms if m in plan)
    if found_markets == 4:
        score += 0.1
    elif found_markets >= 2:
        score += 0.05

    return min(score, 1.0)


def _score_english_brief() -> float:
    """Score English executive brief (weight: 0.15)."""
    score = 0.0
    brief = _load_text_file("executive_brief_en.md")

    if not brief:
        return 0.0

    score += 0.2  # File exists

    # Check it's primarily English
    if _is_primarily_english(brief):
        score += 0.2

    # Check length (800-1500 words recommended)
    word_count = len(brief.split())
    if 600 <= word_count <= 2000:
        score += 0.2
    elif 300 <= word_count <= 3000:
        score += 0.1

    # Check for executive summary structure
    exec_terms = ["summary", "recommendation", "budget", "timeline", "risk", "opportunity", "market"]
    found = sum(1 for t in exec_terms if t in brief.lower())
    if found >= 4:
        score += 0.2
    elif found >= 2:
        score += 0.1

    # Check for markdown structure
    headers = re.findall(r'^#+\s+.+$', brief, re.MULTILINE)
    if len(headers) >= 3:
        score += 0.2
    elif len(headers) >= 1:
        score += 0.1

    return min(score, 1.0)


def _score_timeline_feasibility() -> float:
    """Score timeline feasibility (weight: 0.15)."""
    score = 0.0
    timeline = _load_json_file("timeline.json")

    if not timeline:
        return 0.0

    score += 0.2  # File exists

    content_str = json.dumps(timeline, ensure_ascii=False)

    # Check for date/time references
    dates = re.findall(r'20\d{2}[-/]\d{2}', content_str)
    if len(dates) >= 4:
        score += 0.2
    elif len(dates) >= 2:
        score += 0.1

    # Check for multiple markets in timeline
    markets = ["japan", "korea", "russia", "vietnam", "JP", "KR", "RU", "VN", "日本", "韩国"]
    found = sum(1 for m in markets if m.lower() in content_str.lower())
    if found >= 4:
        score += 0.2
    elif found >= 2:
        score += 0.1

    # Check for phases/milestones
    phase_terms = ["phase", "milestone", "launch", "preparation", "阶段", "里程碑"]
    found_phases = sum(1 for p in phase_terms if p in content_str.lower())
    if found_phases >= 2:
        score += 0.2
    elif found_phases >= 1:
        score += 0.1

    # Check structure
    if isinstance(timeline, (list, dict)) and len(content_str) > 300:
        score += 0.2

    return min(score, 1.0)


def _score_data_accuracy() -> float:
    """Score data accuracy (weight: 0.10)."""
    score = 0.0
    answer = _load_answer()

    if not answer:
        return 0.0

    score += 0.2  # Answer exists

    # Check markets_covered
    if answer.get("markets_covered") == 4:
        score += 0.2
    elif isinstance(answer.get("markets_covered"), int) and answer["markets_covered"] >= 2:
        score += 0.1

    # Check recommended launch order
    launch_order = answer.get("recommended_launch_order", [])
    if isinstance(launch_order, list) and len(launch_order) >= 3:
        score += 0.2

    # Check budget allocation is within constraints (8.5M USD total)
    budget = answer.get("total_budget_allocated_usd", 0)
    if isinstance(budget, (int, float)) and 0 < budget <= 8500000:
        score += 0.2

    # Check go/no-go recommendation
    if answer.get("go_no_go_recommendation") in ["go", "no-go", "conditional"]:
        score += 0.2

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Main grading function."""
    dimensions = {
        "synthesis_quality": {
            "score": _score_synthesis_quality(),
            "weight": 0.20,
            "description": "Quality of multi-language market data synthesis"
        },
        "contradiction_detection": {
            "score": _score_contradiction_detection(),
            "weight": 0.20,
            "description": "Detection of contradictions across data sources"
        },
        "chinese_plan": {
            "score": _score_chinese_plan(),
            "weight": 0.20,
            "description": "Quality of Chinese strategic launch plan"
        },
        "english_brief": {
            "score": _score_english_brief(),
            "weight": 0.15,
            "description": "Quality of English executive brief"
        },
        "timeline_feasibility": {
            "score": _score_timeline_feasibility(),
            "weight": 0.15,
            "description": "Feasibility and completeness of launch timeline"
        },
        "data_accuracy": {
            "score": _score_data_accuracy(),
            "weight": 0.10,
            "description": "Accuracy of numerical data and budget alignment"
        }
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": dimensions
    }


# Pytest-compatible tests

def test_answer_json_exists():
    """Test that answer.json exists and has required fields."""
    answer = _load_answer()
    assert answer, "answer.json not found or empty"
    assert "markets_covered" in answer, "Missing markets_covered"
    assert "total_contradictions_found" in answer, "Missing total_contradictions_found"
    assert "recommended_launch_order" in answer, "Missing recommended_launch_order"
    assert "go_no_go_recommendation" in answer, "Missing go_no_go_recommendation"


def test_launch_plan_is_chinese():
    """Test that launch plan is in Chinese."""
    plan = _load_text_file("launch_plan_zh.md")
    assert plan, "launch_plan_zh.md not found or empty"
    assert _contains_chinese(plan), "Launch plan should be in Chinese"


def test_executive_brief_is_english():
    """Test that executive brief is in English."""
    brief = _load_text_file("executive_brief_en.md")
    assert brief, "executive_brief_en.md not found or empty"
    assert _is_primarily_english(brief), "Executive brief should be primarily in English"


def test_contradictions_detected():
    """Test that contradictions were detected."""
    data = _load_json_file("contradiction_report.json")
    assert data, "contradiction_report.json not found or empty"
    answer = _load_answer()
    assert answer.get("total_contradictions_found", 0) > 0, "Should detect at least one contradiction"


def test_timeline_covers_all_markets():
    """Test that timeline covers all 4 markets."""
    timeline = _load_json_file("timeline.json")
    assert timeline, "timeline.json not found or empty"
    content_str = json.dumps(timeline).lower()
    markets_found = 0
    for m in ["japan", "korea", "russia", "vietnam", "jp", "kr", "ru", "vn"]:
        if m in content_str:
            markets_found += 1
    assert markets_found >= 4, f"Timeline should cover all 4 markets, found {markets_found}"


def test_budget_within_constraints():
    """Test that budget allocation respects constraints."""
    answer = _load_answer()
    budget = answer.get("total_budget_allocated_usd", 0)
    assert isinstance(budget, (int, float)), "Budget should be a number"
    assert budget > 0, "Budget should be positive"
    assert budget <= 8500000, f"Budget ${budget} exceeds max $8,500,000"


if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))


# === Additional standard pytest tests ===

def test_grade_overall():
    """Verify overall score meets minimum threshold."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-10 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["launch_plan_zh.md", "executive_brief_en.md",
                          "market_synthesis.json", "contradiction_report.json",
                          "timeline.json"]
    answer = _load_answer()
    assert answer, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _load_json_file(f) or _load_text_file(f))
    assert found_optional >= 3, f"Only {found_optional}/5 key output files found"


def test_target_language_chinese():
    """Verify Chinese plan contains CJK characters."""
    plan = _load_text_file("launch_plan_zh.md")
    if not plan:
        return
    chinese_chars = len(re.findall(r'[一-鿿]', plan))
    total_chars = len(plan.replace(" ", "").replace("\n", ""))
    ratio = chinese_chars / max(total_chars, 1)
    assert ratio > 0.2, f"Chinese plan CJK ratio too low ({ratio:.1%}), likely English fallback"


def test_target_language_english():
    """Verify English brief is primarily English."""
    brief = _load_text_file("executive_brief_en.md")
    if not brief:
        return
    assert _is_primarily_english(brief), "Executive brief should be primarily in English"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    answer = _load_answer()
    assert answer, "answer.json is empty"
    plan = _load_text_file("launch_plan_zh.md")
    brief = _load_text_file("executive_brief_en.md")
    assert len(plan) > 500, f"Chinese plan too short ({len(plan)} chars), likely incomplete"
    assert len(brief) > 300, f"English brief too short ({len(brief)} chars), likely incomplete"


def test_no_english_fallback_in_chinese_plan():
    """Verify Chinese plan isn't entirely in English."""
    plan = _load_text_file("launch_plan_zh.md")
    if not plan:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', plan))
    total_chars = len(plan)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Chinese plan appears to be mostly English ({english_ratio:.0%})"


def test_both_languages_present():
    """Verify both Chinese plan and English brief exist with correct languages."""
    plan = _load_text_file("launch_plan_zh.md")
    brief = _load_text_file("executive_brief_en.md")
    assert plan and _contains_chinese(plan), "Chinese launch plan must exist and contain Chinese"
    assert brief and _is_primarily_english(brief), "English brief must exist and be in English"
