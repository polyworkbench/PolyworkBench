"""
Test suite for COM-06: Multi-warehouse inventory reconciliation and Japanese forecast.
Evaluates reconciliation accuracy, forecast quality, script execution, Japanese report, and discrepancy detection.
"""

import json
import os
import subprocess
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
        "/workspace/answer.json",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def _load_json_file(filename: str) -> Dict[str, Any]:
    """Load a JSON file from output directory."""
    paths = [
        os.path.join(OUTPUT_DIR, "output", filename),
        os.path.join(OUTPUT_DIR, "outputs", filename),
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/output/{filename}",
        f"/workspace/outputs/{filename}",
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
        os.path.join(OUTPUT_DIR, "output", filename),
        os.path.join(OUTPUT_DIR, "outputs", filename),
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/output/{filename}",
        f"/workspace/outputs/{filename}",
        f"/workspace/{filename}",
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return ""


def _contains_japanese(text: str) -> bool:
    """Check if text contains Japanese characters (hiragana, katakana, or kanji)."""
    japanese_pattern = re.compile(r'[぀-ゟ゠-ヿ一-鿿]')
    return bool(japanese_pattern.search(text))


def _score_reconciliation() -> float:
    """Score the inventory reconciliation output (weight: 0.25)."""
    score = 0.0
    reconciliation = _load_json_file("inventory_reconciliation.json")

    if not reconciliation:
        return 0.0

    # Check if it's a list or has a key containing the data
    items = reconciliation if isinstance(reconciliation, list) else reconciliation.get("items", reconciliation.get("skus", reconciliation.get("reconciliation", [])))

    if isinstance(items, list) and len(items) > 0:
        score += 0.3  # Has data

        # Check if SKUs are present
        first_item = items[0] if items else {}
        if any(k in first_item for k in ["sku_id", "sku", "SKU", "sku_id"]):
            score += 0.2

        # Check for inventory quantities
        if any(k in first_item for k in ["quantity", "stock", "inventory", "current_stock", "当前库存"]):
            score += 0.2

        # Check coverage (should have ~30 SKUs)
        if len(items) >= 25:
            score += 0.2
        elif len(items) >= 15:
            score += 0.1

        # Check for location/source info
        if any(k in first_item for k in ["location", "warehouse", "source", "仓库", "위치"]):
            score += 0.1

    elif isinstance(reconciliation, dict) and len(reconciliation) > 0:
        score += 0.3
        if len(reconciliation) >= 20:
            score += 0.3
        if any("SKU" in str(k) for k in reconciliation.keys()):
            score += 0.2
        score += 0.2  # Structure exists

    return min(score, 1.0)


def _score_forecast_quality() -> float:
    """Score the forecast quality (weight: 0.25)."""
    score = 0.0
    report = _load_text_file("forecast_report_ja.md")
    answer = _load_answer()

    if not report:
        return 0.0

    score += 0.2  # Report exists

    # Check for forecast period
    if answer.get("forecast_period"):
        score += 0.15

    # Check for top demand SKUs
    if answer.get("top_demand_skus") and len(answer.get("top_demand_skus", [])) >= 3:
        score += 0.15

    # Check for holiday impact
    if answer.get("holiday_impact_percentage") and answer["holiday_impact_percentage"] > 0:
        score += 0.15

    # Check report has quantitative data (numbers)
    numbers_in_report = re.findall(r'\d+', report)
    if len(numbers_in_report) >= 10:
        score += 0.15
    elif len(numbers_in_report) >= 5:
        score += 0.1

    # Check for seasonal/holiday mentions in report
    holiday_keywords = ["ゴールデンウィーク", "お盆", "年末", "祝日", "需要", "予測", "増加"]
    found_keywords = sum(1 for kw in holiday_keywords if kw in report)
    if found_keywords >= 4:
        score += 0.2
    elif found_keywords >= 2:
        score += 0.1

    return min(score, 1.0)


def _score_script_execution() -> float:
    """Score the forecast script (weight: 0.20)."""
    score = 0.0
    script_path = None

    for p in [os.path.join(OUTPUT_DIR, "output", "forecast_script.py"), os.path.join(OUTPUT_DIR, "forecast_script.py"), "/workspace/output/forecast_script.py", "/workspace/forecast_script.py"]:
        if os.path.exists(p):
            script_path = p
            break

    if not script_path:
        return 0.0

    score += 0.2  # Script exists

    with open(script_path, "r", encoding="utf-8") as f:
        script_content = f.read()

    # Check for Python syntax validity
    try:
        compile(script_content, script_path, "exec")
        score += 0.3  # Valid Python
    except SyntaxError:
        pass

    # Check for Japanese comments
    if _contains_japanese(script_content):
        score += 0.15

    # Check for forecasting logic
    forecast_indicators = ["forecast", "predict", "trend", "moving_average", "exponential", "regression", "pandas", "numpy"]
    found = sum(1 for ind in forecast_indicators if ind.lower() in script_content.lower())
    if found >= 3:
        score += 0.2
    elif found >= 1:
        score += 0.1

    # Check for data loading
    if "csv" in script_content.lower() or "read_csv" in script_content.lower():
        score += 0.15

    return min(score, 1.0)


def _score_japanese_report() -> float:
    """Score the Japanese language quality of the report (weight: 0.20)."""
    score = 0.0
    report = _load_text_file("forecast_report_ja.md")

    if not report:
        return 0.0

    score += 0.2  # Report exists

    # Check it's primarily Japanese
    if _contains_japanese(report):
        score += 0.2

    # Estimate Japanese content ratio
    japanese_chars = len(re.findall(r'[぀-ゟ゠-ヿ一-鿿]', report))
    total_chars = len(report.replace(" ", "").replace("\n", ""))
    if total_chars > 0:
        ratio = japanese_chars / total_chars
        if ratio > 0.3:
            score += 0.2
        elif ratio > 0.15:
            score += 0.1

    # Check for markdown structure
    if "# " in report or "## " in report:
        score += 0.15

    # Check for sections (headers)
    headers = re.findall(r'^#+\s+.+$', report, re.MULTILINE)
    if len(headers) >= 3:
        score += 0.15
    elif len(headers) >= 1:
        score += 0.1

    # Check report length (should be substantial)
    if len(report) > 2000:
        score += 0.1
    elif len(report) > 500:
        score += 0.05

    return min(score, 1.0)


def _score_discrepancy_detection() -> float:
    """Score discrepancy detection (weight: 0.10)."""
    score = 0.0
    discrepancies = _load_json_file("discrepancies.json")

    if not discrepancies:
        return 0.0

    score += 0.3  # File exists

    # Check if it's a list or has structure
    items = discrepancies if isinstance(discrepancies, list) else discrepancies.get("discrepancies", discrepancies.get("items", []))

    if isinstance(items, list) and len(items) > 0:
        score += 0.3  # Has detected discrepancies

        first = items[0]
        # Check for SKU reference
        if any(k in first for k in ["sku_id", "sku", "SKU"]):
            score += 0.2

        # Check for explanation/reason
        if any(k in first for k in ["reason", "cause", "explanation", "description", "原因", "理由"]):
            score += 0.2

    elif isinstance(discrepancies, dict) and len(discrepancies) > 0:
        score += 0.4
        if any("reason" in str(v).lower() or "cause" in str(v).lower() for v in discrepancies.values() if isinstance(v, (str, dict))):
            score += 0.3

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Main grading function returning overall score and dimensions."""
    dimensions = {
        "reconciliation": {
            "score": _score_reconciliation(),
            "weight": 0.25,
            "description": "Inventory reconciliation accuracy and completeness"
        },
        "forecast_quality": {
            "score": _score_forecast_quality(),
            "weight": 0.25,
            "description": "Quality of demand forecast with holiday integration"
        },
        "script_execution": {
            "score": _score_script_execution(),
            "weight": 0.20,
            "description": "Forecast script quality and executability"
        },
        "japanese_report": {
            "score": _score_japanese_report(),
            "weight": 0.20,
            "description": "Japanese language quality and report structure"
        },
        "discrepancy_detection": {
            "score": _score_discrepancy_detection(),
            "weight": 0.10,
            "description": "Detection and explanation of inventory discrepancies"
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
    assert "total_skus" in answer, "Missing total_skus field"
    assert "discrepancy_count" in answer, "Missing discrepancy_count field"


def test_reconciliation_file_exists():
    """Test that inventory reconciliation file exists."""
    data = _load_json_file("inventory_reconciliation.json")
    assert data, "inventory_reconciliation.json not found or empty"


def test_forecast_report_is_japanese():
    """Test that forecast report is written in Japanese."""
    report = _load_text_file("forecast_report_ja.md")
    assert report, "forecast_report_ja.md not found or empty"
    assert _contains_japanese(report), "Report does not contain Japanese text"


def test_forecast_script_valid_python():
    """Test that forecast script is valid Python."""
    script_path = None
    for p in [os.path.join(OUTPUT_DIR, "output", "forecast_script.py"), os.path.join(OUTPUT_DIR, "forecast_script.py"), "/workspace/output/forecast_script.py", "/workspace/forecast_script.py"]:
        if os.path.exists(p):
            script_path = p
            break
    assert script_path, "forecast_script.py not found"
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        compile(content, script_path, "exec")
    except SyntaxError as e:
        assert False, f"Script has syntax error: {e}"


def test_discrepancies_detected():
    """Test that discrepancies were detected."""
    data = _load_json_file("discrepancies.json")
    assert data, "discrepancies.json not found or empty"


if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))


# === Additional standard pytest tests ===

def test_grade_overall():
    """Verify overall score meets minimum threshold."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-06 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["inventory_reconciliation.json", "forecast_report_ja.md",
                          "forecast_script.py", "discrepancies.json"]
    answer = _load_answer()
    assert answer, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _load_json_file(f) or _load_text_file(f))
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify forecast report is in Japanese, not English fallback."""
    report = _load_text_file("forecast_report_ja.md")
    if not report:
        return
    jp_chars = len(re.findall(r'[぀-ゟ゠-ヿ一-鿿]', report))
    total_chars = len(report.replace(" ", "").replace("\n", ""))
    ratio = jp_chars / max(total_chars, 1)
    assert ratio > 0.2, f"Japanese report char ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    answer = _load_answer()
    assert answer, "answer.json is empty"
    report = _load_text_file("forecast_report_ja.md")
    assert len(report) > 500, f"Forecast report too short ({len(report)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify forecast report isn't in English."""
    report = _load_text_file("forecast_report_ja.md")
    if not report:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', report))
    total_chars = len(report)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Forecast report appears to be mostly English ({english_ratio:.0%})"
