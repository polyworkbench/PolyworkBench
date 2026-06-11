"""
Test suite for COM-09: Multi-framework regulatory compliance check with Korean output.
Evaluates compliance accuracy, gap detection, Korean output, action items, and regulatory mapping.
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


def _contains_korean(text: str) -> bool:
    """Check if text contains Korean hangul characters."""
    hangul_pattern = re.compile(r'[가-힣ㄱ-ㅎㅏ-ㅣ]')
    return bool(hangul_pattern.search(text))


def _score_compliance_accuracy() -> float:
    """Score compliance matrix accuracy (weight: 0.30)."""
    score = 0.0
    matrix = _load_json_file("compliance_matrix_ko.json")

    if not matrix:
        return 0.0

    score += 0.15  # File exists

    content_str = json.dumps(matrix, ensure_ascii=False)

    # Check for Korean content
    if _contains_korean(content_str):
        score += 0.15

    # Check for product references
    prod_refs = re.findall(r'PROD-\d+', content_str)
    if len(set(prod_refs)) >= 4:
        score += 0.15
    elif len(set(prod_refs)) >= 2:
        score += 0.1

    # Check for regulatory framework references
    frameworks = ["FDA", "GB", "JIS"]
    found_frameworks = sum(1 for f in frameworks if f in content_str)
    if found_frameworks == 3:
        score += 0.2
    elif found_frameworks >= 2:
        score += 0.1

    # Check for compliance status categories
    status_terms = ["적합", "부적합", "부분", "해당없음", "compliant", "non-compliant", "partial", "N/A"]
    found_statuses = sum(1 for s in status_terms if s in content_str)
    if found_statuses >= 3:
        score += 0.2
    elif found_statuses >= 1:
        score += 0.1

    # Check structure (should be a matrix format)
    if isinstance(matrix, (list, dict)) and len(str(matrix)) > 500:
        score += 0.15

    return min(score, 1.0)


def _score_gap_detection() -> float:
    """Score gap detection quality (weight: 0.25)."""
    score = 0.0
    report = _load_text_file("gap_analysis_ko.md")
    answer = _load_answer()

    if not report:
        return 0.0

    score += 0.15  # File exists

    # Check for Korean content
    if _contains_korean(report):
        score += 0.15

    # Check for specific gap identifications
    gap_indicators = ["갭", "차이", "미달", "부족", "미준수", "gap", "불일치"]
    found = sum(1 for g in gap_indicators if g in report)
    if found >= 3:
        score += 0.2
    elif found >= 1:
        score += 0.1

    # Check for regulatory references
    reg_refs = re.findall(r'(FDA-[A-Z]\d+|GB-[A-Z]+\d+|JIS-[A-Z]+\d+)', report)
    if len(reg_refs) >= 5:
        score += 0.2
    elif len(reg_refs) >= 2:
        score += 0.1

    # Check for critical gaps in answer
    if isinstance(answer.get("critical_gaps"), int) and answer["critical_gaps"] > 0:
        score += 0.15

    # Check for conflicting requirements detection
    if isinstance(answer.get("conflicting_requirements"), int):
        score += 0.15

    return min(score, 1.0)


def _score_korean_output() -> float:
    """Score Korean language quality across outputs (weight: 0.20)."""
    score = 0.0
    report = _load_text_file("gap_analysis_ko.md")
    matrix_str = json.dumps(_load_json_file("compliance_matrix_ko.json"), ensure_ascii=False)
    actions_str = json.dumps(_load_json_file("action_items_ko.json"), ensure_ascii=False)

    all_text = report + matrix_str + actions_str

    if not all_text or len(all_text) < 50:
        return 0.0

    score += 0.2  # Output exists

    # Check Korean presence across files
    korean_in_report = _contains_korean(report) if report else False
    korean_in_matrix = _contains_korean(matrix_str)
    korean_in_actions = _contains_korean(actions_str)

    korean_files = sum([korean_in_report, korean_in_matrix, korean_in_actions])
    if korean_files == 3:
        score += 0.3
    elif korean_files == 2:
        score += 0.2
    elif korean_files == 1:
        score += 0.1

    # Check Korean content ratio in report
    if report:
        hangul_chars = len(re.findall(r'[가-힣]', report))
        total_alpha = len(re.findall(r'[a-zA-Z가-힣]', report))
        if total_alpha > 0:
            ratio = hangul_chars / total_alpha
            if ratio > 0.35:
                score += 0.25
            elif ratio > 0.2:
                score += 0.15
            elif ratio > 0.1:
                score += 0.1

    # Check markdown structure in report
    if report:
        headers = re.findall(r'^#+\s+.+$', report, re.MULTILINE)
        if len(headers) >= 3:
            score += 0.15
        elif len(headers) >= 1:
            score += 0.1

    # Check report length
    if len(report) > 2000:
        score += 0.1

    return min(score, 1.0)


def _score_action_items() -> float:
    """Score action items quality (weight: 0.15)."""
    score = 0.0
    actions = _load_json_file("action_items_ko.json")

    if not actions:
        return 0.0

    score += 0.2  # File exists

    content_str = json.dumps(actions, ensure_ascii=False)

    # Check for Korean content
    if _contains_korean(content_str):
        score += 0.2

    # Check for structured items
    items = actions if isinstance(actions, list) else actions.get("action_items", actions.get("items", []))
    if isinstance(items, list) and len(items) > 0:
        score += 0.2

        first = items[0] if items else {}
        # Check for priority field
        if any(k in str(first).lower() for k in ["priority", "우선순위", "긴급"]):
            score += 0.2

        # Check for cost/timeline estimates
        if any(k in str(first).lower() for k in ["cost", "비용", "time", "기간", "소요"]):
            score += 0.2

    elif isinstance(actions, dict) and len(actions) > 2:
        score += 0.4

    return min(score, 1.0)


def _score_regulatory_mapping() -> float:
    """Score regulatory framework mapping (weight: 0.10)."""
    score = 0.0
    summary = _load_json_file("regulatory_summary.json")

    if not summary:
        return 0.0

    score += 0.3  # File exists

    content_str = json.dumps(summary, ensure_ascii=False)

    # Check for all three frameworks
    frameworks = ["FDA", "GB", "JIS"]
    found = sum(1 for f in frameworks if f in content_str)
    if found == 3:
        score += 0.3
    elif found >= 2:
        score += 0.15

    # Check for requirement IDs
    req_ids = re.findall(r'(FDA-[A-Z]\d+|GB-[A-Z]+\d+|JIS-[A-Z]+\d+)', content_str)
    if len(req_ids) >= 8:
        score += 0.2
    elif len(req_ids) >= 4:
        score += 0.1

    # Check structure has useful data
    if len(content_str) > 500:
        score += 0.2

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Main grading function."""
    dimensions = {
        "compliance_accuracy": {
            "score": _score_compliance_accuracy(),
            "weight": 0.30,
            "description": "Accuracy of compliance matrix across three frameworks"
        },
        "gap_detection": {
            "score": _score_gap_detection(),
            "weight": 0.25,
            "description": "Quality of gap identification and conflict detection"
        },
        "korean_output": {
            "score": _score_korean_output(),
            "weight": 0.20,
            "description": "Korean language quality and consistency"
        },
        "action_items": {
            "score": _score_action_items(),
            "weight": 0.15,
            "description": "Quality of corrective action items with priorities"
        },
        "regulatory_mapping": {
            "score": _score_regulatory_mapping(),
            "weight": 0.10,
            "description": "Mapping between regulatory frameworks"
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
    assert "total_products" in answer, "Missing total_products"
    assert "compliant_count" in answer, "Missing compliant_count"
    assert "non_compliant_count" in answer, "Missing non_compliant_count"
    assert "critical_gaps" in answer, "Missing critical_gaps"


def test_compliance_matrix_exists():
    """Test that compliance matrix exists and has Korean content."""
    data = _load_json_file("compliance_matrix_ko.json")
    assert data, "compliance_matrix_ko.json not found or empty"
    content_str = json.dumps(data, ensure_ascii=False)
    assert _contains_korean(content_str), "Compliance matrix should contain Korean text"


def test_gap_analysis_is_korean():
    """Test that gap analysis report is in Korean."""
    report = _load_text_file("gap_analysis_ko.md")
    assert report, "gap_analysis_ko.md not found or empty"
    assert _contains_korean(report), "Gap analysis should be in Korean"


def test_action_items_exist():
    """Test that action items exist with Korean content."""
    data = _load_json_file("action_items_ko.json")
    assert data, "action_items_ko.json not found or empty"
    content_str = json.dumps(data, ensure_ascii=False)
    assert _contains_korean(content_str), "Action items should contain Korean text"


def test_all_frameworks_covered():
    """Test that all three regulatory frameworks are covered."""
    matrix_str = json.dumps(_load_json_file("compliance_matrix_ko.json"))
    assert "FDA" in matrix_str, "FDA framework not found in compliance matrix"
    assert "GB" in matrix_str, "GB framework not found in compliance matrix"
    assert "JIS" in matrix_str, "JIS framework not found in compliance matrix"


if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))


# === Additional standard pytest tests ===

def test_grade_overall():
    """Verify overall score meets minimum threshold."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-09 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["compliance_matrix_ko.json", "gap_analysis_ko.md",
                          "action_items_ko.json", "regulatory_summary.json"]
    answer = _load_answer()
    assert answer, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _load_json_file(f) or _load_text_file(f))
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify output is in Korean (Hangul), not English fallback."""
    report = _load_text_file("gap_analysis_ko.md")
    if not report:
        return
    hangul_chars = len(re.findall(r'[가-힣]', report))
    total_alpha = len(re.findall(r'[a-zA-Z가-힣]', report))
    ratio = hangul_chars / max(total_alpha, 1)
    assert ratio > 0.2, f"Korean report Hangul ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    answer = _load_answer()
    assert answer, "answer.json is empty"
    blob = json.dumps(answer, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Korean output isn't in English."""
    report = _load_text_file("gap_analysis_ko.md")
    if not report:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', report))
    total_chars = len(report)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Report appears to be mostly English ({english_ratio:.0%})"


def test_compliance_matrix_coverage():
    """Verify compliance matrix covers multiple products and frameworks."""
    matrix = _load_json_file("compliance_matrix_ko.json")
    if not matrix:
        return
    content_str = json.dumps(matrix, ensure_ascii=False)
    prod_refs = set(re.findall(r'PROD-\d+', content_str))
    assert len(prod_refs) >= 3, f"Only {len(prod_refs)} products in compliance matrix, expected more"
    # Check frameworks
    frameworks = ["FDA", "GB", "JIS"]
    found = sum(1 for f in frameworks if f in content_str)
    assert found >= 2, f"Only {found}/3 regulatory frameworks covered"
