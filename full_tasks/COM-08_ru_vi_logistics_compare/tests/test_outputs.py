"""
Test suite for COM-08: China-Russia vs China-Vietnam logistics comparison.
Evaluates route comparison, cost calculations, Russian report, script quality, and recommendations.
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


def _contains_russian(text: str) -> bool:
    """Check if text contains Russian Cyrillic characters."""
    cyrillic_pattern = re.compile(r'[а-яА-ЯёЁ]')
    return bool(cyrillic_pattern.search(text))


def _score_route_comparison() -> float:
    """Score route comparison analysis (weight: 0.25)."""
    score = 0.0
    analysis = _load_json_file("route_analysis.json")

    if not analysis:
        return 0.0

    score += 0.2  # File exists

    content_str = json.dumps(analysis).lower()

    # Check for both destinations
    russia_refs = any(term in content_str for term in ["russia", "москва", "moscow", "россия", "ru"])
    vietnam_refs = any(term in content_str for term in ["vietnam", "вьетнам", "hanoi", "hcm", "vn"])

    if russia_refs and vietnam_refs:
        score += 0.25
    elif russia_refs or vietnam_refs:
        score += 0.1

    # Check for multiple transport modes
    modes = ["air", "rail", "sea", "road", "ocean", "авиа", "жд", "морск"]
    found_modes = sum(1 for m in modes if m in content_str)
    if found_modes >= 3:
        score += 0.2
    elif found_modes >= 1:
        score += 0.1

    # Check for cost data
    if any(term in content_str for term in ["cost", "price", "rate", "usd", "стоимость", "цена"]):
        score += 0.15

    # Check for time data
    if any(term in content_str for term in ["days", "time", "transit", "дней", "срок"]):
        score += 0.2

    return min(score, 1.0)


def _score_cost_calculations() -> float:
    """Score cost calculation accuracy (weight: 0.25)."""
    score = 0.0
    answer = _load_answer()
    analysis = _load_json_file("route_analysis.json")

    if not answer:
        return 0.0

    score += 0.2  # Answer exists

    # Check route identification
    if answer.get("cheapest_route_russia"):
        score += 0.15
    if answer.get("fastest_route_russia"):
        score += 0.15
    if answer.get("cheapest_route_vietnam"):
        score += 0.15
    if answer.get("fastest_route_vietnam"):
        score += 0.15

    # Check comparative metrics
    if isinstance(answer.get("avg_cost_difference_pct"), (int, float)):
        score += 0.1
    if isinstance(answer.get("avg_time_difference_days"), (int, float)):
        score += 0.1

    return min(score, 1.0)


def _score_russian_report() -> float:
    """Score Russian language report (weight: 0.20)."""
    score = 0.0
    report = _load_text_file("logistics_comparison_ru.md")

    if not report:
        return 0.0

    score += 0.2  # File exists

    # Check for Russian content
    if _contains_russian(report):
        score += 0.2

    # Check Russian content ratio
    cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁ]', report))
    total_alpha = len(re.findall(r'[a-zA-Zа-яА-ЯёЁ]', report))
    if total_alpha > 0:
        ratio = cyrillic_chars / total_alpha
        if ratio > 0.4:
            score += 0.2
        elif ratio > 0.2:
            score += 0.1

    # Check for markdown structure
    headers = re.findall(r'^#+\s+.+$', report, re.MULTILINE)
    if len(headers) >= 3:
        score += 0.2
    elif len(headers) >= 1:
        score += 0.1

    # Check report length
    if len(report) > 2000:
        score += 0.2
    elif len(report) > 800:
        score += 0.1

    return min(score, 1.0)


def _score_script_quality() -> float:
    """Score cost calculator script (weight: 0.15)."""
    score = 0.0
    script_path = None

    for p in [os.path.join(OUTPUT_DIR, "cost_calculator.py"), "/workspace/cost_calculator.py"]:
        if os.path.exists(p):
            script_path = p
            break

    if not script_path:
        return 0.0

    score += 0.2  # File exists

    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Valid Python
    try:
        compile(content, script_path, "exec")
        score += 0.3
    except SyntaxError:
        pass

    # Check for parameterization (weight, volume, etc.)
    params = ["weight", "volume", "route", "mode", "type", "category"]
    found_params = sum(1 for p in params if p in content.lower())
    if found_params >= 3:
        score += 0.2
    elif found_params >= 1:
        score += 0.1

    # Check for calculation logic
    if any(op in content for op in ["*", "+", "cost", "total", "calculate"]):
        score += 0.15

    # Check for functions
    if "def " in content:
        score += 0.15

    return min(score, 1.0)


def _score_recommendations() -> float:
    """Score recommendations quality (weight: 0.15)."""
    score = 0.0
    recommendations = _load_json_file("recommendations_ru.json")

    if not recommendations:
        return 0.0

    score += 0.3  # File exists

    content_str = json.dumps(recommendations, ensure_ascii=False)

    # Check for Russian content in recommendations
    if _contains_russian(content_str):
        score += 0.25

    # Check for structured recommendations
    if isinstance(recommendations, list) and len(recommendations) > 0:
        score += 0.2
    elif isinstance(recommendations, dict) and len(recommendations) > 0:
        score += 0.2

    # Check for actionable content
    if any(term in content_str.lower() for term in ["рекоменд", "оптимальн", "recommend", "suggest"]):
        score += 0.25

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Main grading function."""
    dimensions = {
        "route_comparison": {
            "score": _score_route_comparison(),
            "weight": 0.25,
            "description": "Completeness of route comparison across destinations"
        },
        "cost_calculations": {
            "score": _score_cost_calculations(),
            "weight": 0.25,
            "description": "Accuracy of cost and time calculations"
        },
        "russian_report": {
            "score": _score_russian_report(),
            "weight": 0.20,
            "description": "Quality of Russian language report"
        },
        "script_quality": {
            "score": _score_script_quality(),
            "weight": 0.15,
            "description": "Cost calculator script quality"
        },
        "recommendations": {
            "score": _score_recommendations(),
            "weight": 0.15,
            "description": "Quality and actionability of recommendations"
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
    assert "total_routes_analyzed" in answer
    assert "cheapest_route_russia" in answer
    assert "fastest_route_russia" in answer


def test_route_analysis_exists():
    """Test that route analysis file exists."""
    data = _load_json_file("route_analysis.json")
    assert data, "route_analysis.json not found or empty"


def test_logistics_report_is_russian():
    """Test that logistics report is in Russian."""
    report = _load_text_file("logistics_comparison_ru.md")
    assert report, "logistics_comparison_ru.md not found or empty"
    assert _contains_russian(report), "Report does not contain Russian text"


def test_cost_calculator_valid_python():
    """Test that cost calculator is valid Python."""
    script_path = None
    for p in [os.path.join(OUTPUT_DIR, "cost_calculator.py"), "/workspace/cost_calculator.py"]:
        if os.path.exists(p):
            script_path = p
            break
    assert script_path, "cost_calculator.py not found"
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        compile(content, script_path, "exec")
    except SyntaxError as e:
        assert False, f"Script has syntax error: {e}"


def test_recommendations_exist():
    """Test that recommendations file exists and has Russian content."""
    data = _load_json_file("recommendations_ru.json")
    assert data, "recommendations_ru.json not found or empty"
    content_str = json.dumps(data, ensure_ascii=False)
    assert _contains_russian(content_str), "Recommendations should contain Russian text"


if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))


# === Additional standard pytest tests ===

def test_grade_overall():
    """Verify overall score meets minimum threshold."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-08 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["route_analysis.json", "logistics_comparison_ru.md",
                          "cost_calculator.py", "recommendations_ru.json"]
    answer = _load_answer()
    assert answer, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _load_json_file(f) or _load_text_file(f))
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify logistics report is in Russian (Cyrillic), not English fallback."""
    report = _load_text_file("logistics_comparison_ru.md")
    if not report:
        return
    cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁ]', report))
    total_alpha = len(re.findall(r'[a-zA-Zа-яА-ЯёЁ]', report))
    ratio = cyrillic_chars / max(total_alpha, 1)
    assert ratio > 0.3, f"Russian report Cyrillic ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    answer = _load_answer()
    assert answer, "answer.json is empty"
    report = _load_text_file("logistics_comparison_ru.md")
    assert len(report) > 500, f"Report too short ({len(report)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Russian report isn't in English."""
    report = _load_text_file("logistics_comparison_ru.md")
    if not report:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', report))
    total_chars = len(report)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Report appears to be mostly English ({english_ratio:.0%})"


def test_route_comparison_completeness():
    """Verify route analysis covers both Russia and Vietnam destinations."""
    analysis = _load_json_file("route_analysis.json")
    if not analysis:
        return
    content_str = json.dumps(analysis).lower()
    has_russia = any(t in content_str for t in ["russia", "москва", "moscow", "россия", "ru"])
    has_vietnam = any(t in content_str for t in ["vietnam", "вьетнам", "hanoi", "hcm", "vn"])
    assert has_russia and has_vietnam, "Route analysis must cover both Russia and Vietnam"
