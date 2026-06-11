"""
Test suite for COM-07: Cross-market pricing validation and English strategy memo.
Evaluates cross-validation, inconsistency detection, strategy memo, script quality, and data accuracy.
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
    paths = [
        ANSWER_PATH,
        os.path.join(OUTPUT_DIR, "answer.json"),
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def _load_json_file(filename: str) -> Any:
    """Load a JSON file from output directory."""
    paths = [
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/{filename}",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def _load_text_file(filename: str) -> str:
    """Load a text file from output directory."""
    paths = [
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/{filename}",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return ""


def _score_cross_validation() -> float:
    """Score cross-market price validation (weight: 0.25)."""
    score = 0.0
    analysis = _load_json_file("pricing_analysis.json")
    comparison = _load_json_file("market_comparison.json")

    if not analysis and not comparison:
        return 0.0

    # Check pricing analysis
    if analysis:
        score += 0.2  # File exists

        # Check if USD conversion was done
        content_str = json.dumps(analysis).lower()
        if "usd" in content_str or "dollar" in content_str:
            score += 0.2

        # Check for multiple markets
        markets = ["cn", "ru", "kr", "vn", "china", "russia", "korea", "vietnam"]
        found_markets = sum(1 for m in markets if m in content_str)
        if found_markets >= 4:
            score += 0.2
        elif found_markets >= 2:
            score += 0.1

    # Check market comparison
    if comparison:
        score += 0.2

        # Check if it has product-level data
        if isinstance(comparison, (list, dict)) and len(comparison) > 0:
            score += 0.2

    return min(score, 1.0)


def _score_inconsistency_detection() -> float:
    """Score inconsistency detection (weight: 0.25)."""
    score = 0.0
    report = _load_text_file("inconsistency_report.md")
    answer = _load_answer()

    if not report:
        return 0.0

    score += 0.2  # Report exists

    # Check answer has inconsistency count
    if answer.get("inconsistency_count", 0) > 0:
        score += 0.15

    # Check for specific product references
    prd_refs = re.findall(r'PRD-\d+', report)
    if len(prd_refs) >= 5:
        score += 0.2
    elif len(prd_refs) >= 2:
        score += 0.1

    # Check for percentage mentions (price gap analysis)
    percentages = re.findall(r'\d+\.?\d*%', report)
    if len(percentages) >= 5:
        score += 0.2
    elif len(percentages) >= 2:
        score += 0.1

    # Check for arbitrage opportunities
    if answer.get("arbitrage_opportunities", 0) > 0:
        score += 0.15

    # Check for margin violations
    if answer.get("margin_violations", 0) >= 0:
        score += 0.1

    return min(score, 1.0)


def _score_strategy_memo() -> float:
    """Score the pricing strategy memo (weight: 0.20)."""
    score = 0.0
    memo = _load_text_file("pricing_strategy.md")

    if not memo:
        return 0.0

    score += 0.2  # File exists

    # Check for markdown structure
    headers = re.findall(r'^#+\s+.+$', memo, re.MULTILINE)
    if len(headers) >= 4:
        score += 0.2
    elif len(headers) >= 2:
        score += 0.1

    # Check for market-specific recommendations
    market_terms = ["china", "russia", "korea", "vietnam", "CN", "RU", "KR", "VN"]
    found_markets = sum(1 for m in market_terms if m.lower() in memo.lower())
    if found_markets >= 4:
        score += 0.2
    elif found_markets >= 2:
        score += 0.1

    # Check for actionable recommendations
    action_words = ["recommend", "adjust", "increase", "decrease", "align", "reduce", "should", "must"]
    found_actions = sum(1 for w in action_words if w in memo.lower())
    if found_actions >= 4:
        score += 0.2
    elif found_actions >= 2:
        score += 0.1

    # Check length (should be substantial strategy document)
    if len(memo) > 3000:
        score += 0.2
    elif len(memo) > 1000:
        score += 0.1

    return min(score, 1.0)


def _score_script_quality() -> float:
    """Score the validation script (weight: 0.15)."""
    score = 0.0
    script_path = None

    for p in [os.path.join(OUTPUT_DIR, "validation_script.py"), "/workspace/validation_script.py"]:
        if os.path.exists(p):
            script_path = p
            break

    if not script_path:
        return 0.0

    score += 0.2  # Script exists

    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for valid Python
    try:
        compile(content, script_path, "exec")
        score += 0.3
    except SyntaxError:
        pass

    # Check for FX conversion logic
    if "rate" in content.lower() or "exchange" in content.lower() or "fx" in content.lower():
        score += 0.15

    # Check for threshold/margin logic
    if "margin" in content.lower() or "threshold" in content.lower() or "15%" in content or "0.15" in content:
        score += 0.15

    # Check for data loading
    if "csv" in content.lower() or "json" in content.lower():
        score += 0.1

    # Check for reusability (functions defined)
    if "def " in content:
        score += 0.1

    return min(score, 1.0)


def _score_data_accuracy() -> float:
    """Score data accuracy (weight: 0.15)."""
    score = 0.0
    answer = _load_answer()
    comparison = _load_json_file("market_comparison.json")

    if not answer:
        return 0.0

    score += 0.2  # Answer exists

    # Check total products count (should be 20)
    total = answer.get("total_products", 0)
    if total == 20:
        score += 0.3
    elif 15 <= total <= 25:
        score += 0.15

    # Check markets analyzed
    markets = answer.get("markets_analyzed", [])
    if len(markets) == 4:
        score += 0.2
    elif len(markets) >= 2:
        score += 0.1

    # Check that numerical fields are reasonable
    if isinstance(answer.get("inconsistency_count"), int) and answer["inconsistency_count"] >= 0:
        score += 0.15

    if answer.get("most_inconsistent_product") and "PRD" in str(answer.get("most_inconsistent_product", "")):
        score += 0.15

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Main grading function."""
    dimensions = {
        "cross_validation": {
            "score": _score_cross_validation(),
            "weight": 0.25,
            "description": "Cross-market price validation with FX conversion"
        },
        "inconsistency_detection": {
            "score": _score_inconsistency_detection(),
            "weight": 0.25,
            "description": "Detection of pricing inconsistencies and arbitrage risks"
        },
        "strategy_memo": {
            "score": _score_strategy_memo(),
            "weight": 0.20,
            "description": "Quality of English pricing strategy memo"
        },
        "script_quality": {
            "score": _score_script_quality(),
            "weight": 0.15,
            "description": "Validation script quality and reusability"
        },
        "data_accuracy": {
            "score": _score_data_accuracy(),
            "weight": 0.15,
            "description": "Accuracy of numerical analysis and data handling"
        }
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": dimensions
    }


# Pytest-compatible test functions

def test_answer_json_exists():
    """Test that answer.json exists and has required fields."""
    answer = _load_answer()
    assert answer, "answer.json not found or empty"
    assert "total_products" in answer, "Missing total_products field"
    assert "inconsistency_count" in answer, "Missing inconsistency_count field"
    assert "markets_analyzed" in answer, "Missing markets_analyzed field"


def test_pricing_analysis_exists():
    """Test that pricing analysis file exists."""
    data = _load_json_file("pricing_analysis.json")
    assert data, "pricing_analysis.json not found or empty"


def test_inconsistency_report_exists():
    """Test that inconsistency report exists and has content."""
    report = _load_text_file("inconsistency_report.md")
    assert report, "inconsistency_report.md not found or empty"
    assert len(report) > 100, "Inconsistency report too short"


def test_strategy_memo_in_english():
    """Test that strategy memo is primarily in English."""
    memo = _load_text_file("pricing_strategy.md")
    assert memo, "pricing_strategy.md not found or empty"
    # Check for English content (no dominant non-Latin script)
    latin_chars = len(re.findall(r'[a-zA-Z]', memo))
    total_alpha = len(re.findall(r'\w', memo))
    if total_alpha > 0:
        assert latin_chars / total_alpha > 0.5, "Strategy memo should be primarily in English"


def test_validation_script_valid():
    """Test that validation script is valid Python."""
    script_path = None
    for p in [os.path.join(OUTPUT_DIR, "validation_script.py"), "/workspace/validation_script.py"]:
        if os.path.exists(p):
            script_path = p
            break
    assert script_path, "validation_script.py not found"
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        compile(content, script_path, "exec")
    except SyntaxError as e:
        assert False, f"Script has syntax error: {e}"


def test_market_comparison_has_all_markets():
    """Test that market comparison includes all 4 markets."""
    data = _load_json_file("market_comparison.json")
    assert data, "market_comparison.json not found or empty"
    content_str = json.dumps(data).lower()
    markets_found = sum(1 for m in ["cn", "ru", "kr", "vn"] if m in content_str)
    assert markets_found >= 3, f"Only found {markets_found} markets in comparison"


if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))


# === Additional standard pytest tests ===

def test_grade_overall():
    """Verify overall score meets minimum threshold."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-07 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["pricing_analysis.json", "market_comparison.json",
                          "inconsistency_report.md", "pricing_strategy.md",
                          "validation_script.py"]
    answer = _load_answer()
    assert answer, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _load_json_file(f) or _load_text_file(f))
    assert found_optional >= 3, f"Only {found_optional}/5 key output files found"


def test_target_language():
    """Verify output is primarily in English (for this EN-target task)."""
    memo = _load_text_file("pricing_strategy.md")
    if not memo:
        return
    latin_chars = len(re.findall(r'[a-zA-Z]', memo))
    total_alpha = len(re.findall(r'\w', memo))
    if total_alpha > 0:
        ratio = latin_chars / total_alpha
        assert ratio > 0.5, f"Strategy memo should be primarily English, got ratio {ratio:.1%}"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    answer = _load_answer()
    assert answer, "answer.json is empty"
    blob = json.dumps(answer, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_four_currencies_covered():
    """Verify pricing covers all 4 market currencies."""
    answer = _load_answer()
    markets = answer.get("markets_analyzed", [])
    assert len(markets) >= 3, f"Only {len(markets)} markets analyzed, expected 4 (CN, RU, KR, VN)"


def test_numeric_accuracy():
    """Verify inconsistency count and product count are reasonable."""
    answer = _load_answer()
    total = answer.get("total_products", 0)
    assert isinstance(total, int) and total >= 10, f"total_products={total}, expected >=10"
    inconsistencies = answer.get("inconsistency_count", -1)
    assert isinstance(inconsistencies, int) and inconsistencies >= 0, "inconsistency_count should be non-negative integer"
