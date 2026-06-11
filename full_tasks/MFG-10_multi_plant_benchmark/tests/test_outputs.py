"""
WildClawBench-style grading for MFG-10: Multi-plant benchmarking with inconsistency detection.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

PLANTS = ["china", "vietnam", "korea", "japan", "russia"]
# Known inconsistencies seeded in the data:
# - Korea: yield is EXACTLY 98.0% for 11 of 12 months (suspiciously constant)
# - Korea: zero safety incidents all year (possibly unreported)
# - Japan: ALL metrics show unrealistically low variance (too perfect)
# - Japan: yield is EXACTLY 98.8% every month (constant)
# - Japan: energy per unit is EXACTLY 12.9 every month (constant)
# - China: yield jumps to exactly 98.0% from month 3 onward (suspiciously round)
# - China: energy per unit is exactly 14.4 from month 3 onward (constant)
# - Russia: defect rate is exactly 4.0% for 9 of 12 months (constant)

KNOWN_INCONSISTENCIES = [
    "korea_constant_yield",
    "korea_zero_safety",
    "japan_low_variance",
    "japan_constant_yield",
    "japan_constant_energy",
    "china_constant_yield",
    "china_constant_energy",
    "russia_constant_defect"
]


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_json(name: str) -> Any:
    path = _find_file(name)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return None


def _score_data_normalization() -> Dict[str, float]:
    """Score data normalization across plants (weight: 0.20)."""
    scores = {}
    comparison = _load_json("plant_comparison.json")

    if not comparison:
        return {"comparison_exists": 0.0, "all_plants_present": 0.0,
                "common_schema": 0.0, "normalized_units": 0.0}

    scores["comparison_exists"] = 1.0
    blob = json.dumps(comparison, ensure_ascii=False).lower()

    # Check all plants present
    plant_names = ["china", "shenzhen", "vietnam", "haiphong", "korea", "busan",
                   "japan", "osaka", "russia", "kaluga"]
    plants_found = sum(1 for p in plant_names if p in blob)
    scores["all_plants_present"] = min(1.0, plants_found / 5)

    # Check common schema (English field names)
    common_fields = ["oee", "yield", "output", "productivity", "energy",
                     "safety", "delivery", "changeover"]
    fields_found = sum(1 for f in common_fields if f in blob)
    scores["common_schema"] = min(1.0, fields_found / 5)

    # Check normalization (per-line or per-capita metrics)
    norm_indicators = ["per_line", "per_capita", "per_person", "normalized",
                       "per line", "per capita", "/line", "/person"]
    scores["normalized_units"] = 1.0 if any(n in blob for n in norm_indicators) else 0.5

    return scores


def _score_inconsistency_detection() -> Dict[str, float]:
    """Score inconsistency detection (weight: 0.20)."""
    scores = {}
    findings = _load_json("inconsistency_findings.json")

    if not findings:
        return {"findings_exist": 0.0, "findings_count": 0.0,
                "constant_values_detected": 0.0, "plants_flagged": 0.0,
                "evidence_provided": 0.0}

    scores["findings_exist"] = 1.0
    blob = json.dumps(findings, ensure_ascii=False).lower()

    # Get findings list
    if isinstance(findings, list):
        finding_list = findings
    elif isinstance(findings, dict):
        finding_list = findings.get("findings", findings.get("inconsistencies", []))
        if isinstance(finding_list, dict):
            finding_list = list(finding_list.values())
        if not isinstance(finding_list, list):
            finding_list = [findings]
    else:
        finding_list = []

    # Should find at least 3-4 inconsistencies
    scores["findings_count"] = min(1.0, len(finding_list) / 4)

    # Check if constant values are detected (major seeded issue)
    constant_keywords = ["constant", "zero variance", "no variation", "same value",
                         "identical", "unchanged", "일정", "不变", "fixed"]
    scores["constant_values_detected"] = 1.0 if any(k in blob for k in constant_keywords) else 0.0

    # Check multiple plants are flagged
    plants_in_findings = sum(1 for p in ["japan", "korea", "china", "russia", "osaka", "busan"]
                            if p in blob)
    scores["plants_flagged"] = min(1.0, plants_in_findings / 3)

    # Check evidence is provided
    evidence_keywords = ["evidence", "value", "month", "data", "variance",
                         "deviation", "pattern", "coefficient"]
    scores["evidence_provided"] = min(1.0, sum(1 for k in evidence_keywords if k in blob) / 3)

    return scores


def _score_comparative_analysis() -> Dict[str, float]:
    """Score comparative analysis quality (weight: 0.20)."""
    scores = {}
    report_path = _find_file("benchmark_report.md")

    if not report_path.exists():
        return {"report_exists": 0.0, "ranking_present": 0.0,
                "strengths_weaknesses": 0.0, "data_quality_section": 0.0}

    content = report_path.read_text(encoding="utf-8-sig")
    content_lower = content.lower()
    scores["report_exists"] = 1.0

    # Check for rankings
    rank_keywords = ["rank", "ranking", "#1", "#2", "#3", "first", "second", "best",
                     "worst", "top", "bottom", "leader"]
    scores["ranking_present"] = 1.0 if sum(1 for k in rank_keywords if k in content_lower) >= 2 else 0.0

    # Check strengths/weaknesses analysis
    sw_keywords = ["strength", "weakness", "strong", "weak", "advantage",
                   "disadvantage", "excels", "lags", "outperform", "underperform"]
    scores["strengths_weaknesses"] = 1.0 if sum(1 for k in sw_keywords if k in content_lower) >= 2 else 0.0

    # Check data quality assessment
    dq_keywords = ["data quality", "inconsisten", "suspicious", "reliable",
                   "reporting", "accuracy", "trustworth", "constant value"]
    scores["data_quality_section"] = 1.0 if sum(1 for k in dq_keywords if k in content_lower) >= 2 else 0.0

    return scores


def _score_script_quality() -> Dict[str, float]:
    """Score the analysis script (weight: 0.15)."""
    scores = {}
    script_path = _find_file("analysis_script.py")

    if not script_path.exists():
        return {"script_exists": 0.0, "reads_all_csvs": 0.0,
                "handles_encodings": 0.0, "statistical_analysis": 0.0,
                "produces_outputs": 0.0}

    content = script_path.read_text(encoding="utf-8-sig")
    content_lower = content.lower()
    scores["script_exists"] = 1.0

    # Check reads all CSVs
    csv_refs = sum(1 for plant in ["china", "vietnam", "korea", "japan", "russia"]
                   if plant in content_lower)
    scores["reads_all_csvs"] = min(1.0, csv_refs / 4)

    # Check encoding handling
    encoding_keywords = ["utf-8", "encoding", "utf8"]
    scores["handles_encodings"] = 1.0 if any(k in content_lower for k in encoding_keywords) else 0.0

    # Check statistical analysis
    stat_keywords = ["std", "mean", "variance", "deviation", "statistics",
                     "numpy", "pandas", "scipy", "cv", "coefficient"]
    scores["statistical_analysis"] = min(1.0, sum(1 for k in stat_keywords if k in content_lower) / 3)

    # Check produces output
    output_keywords = ["json.dump", "to_json", "write", "open("]
    scores["produces_outputs"] = 1.0 if any(k in content for k in output_keywords) else 0.0

    return scores


def _score_report_quality() -> Dict[str, float]:
    """Score report quality (weight: 0.15)."""
    scores = {}
    report_path = _find_file("benchmark_report.md")

    if not report_path.exists():
        return {"report_exists": 0.0, "executive_format": 0.0,
                "all_plants_discussed": 0.0, "actionable_content": 0.0}

    content = report_path.read_text(encoding="utf-8-sig")
    content_lower = content.lower()
    scores["report_exists"] = 1.0

    # Check executive summary format
    has_headers = bool(re.search(r'^#+\s', content, re.MULTILINE))
    has_structure = "|" in content or "- " in content
    scores["executive_format"] = 1.0 if (has_headers and has_structure) else 0.5 if has_headers else 0.0

    # Check all plants discussed
    plant_refs = ["china", "shenzhen", "vietnam", "haiphong", "korea", "busan",
                  "japan", "osaka", "russia", "kaluga"]
    plants_discussed = sum(1 for p in plant_refs if p in content_lower)
    scores["all_plants_discussed"] = min(1.0, plants_discussed / 5)

    # Check for actionable content
    action_keywords = ["recommend", "suggest", "improve", "action", "priority",
                       "investment", "timeline", "target"]
    scores["actionable_content"] = min(1.0, sum(1 for k in action_keywords if k in content_lower) / 3)

    return scores


def _score_recommendations() -> Dict[str, float]:
    """Score recommendations (weight: 0.10)."""
    scores = {}
    recs = _load_json("recommendations.json")

    if not recs:
        return {"recommendations_exist": 0.0, "per_plant": 0.0, "prioritized": 0.0}

    scores["recommendations_exist"] = 1.0
    blob = json.dumps(recs, ensure_ascii=False).lower()

    # Check per-plant recommendations
    plants_in_recs = sum(1 for p in ["china", "shenzhen", "vietnam", "haiphong",
                                      "korea", "busan", "japan", "osaka",
                                      "russia", "kaluga"]
                         if p in blob)
    scores["per_plant"] = min(1.0, plants_in_recs / 4)

    # Check prioritization
    priority_keywords = ["priority", "high", "medium", "low", "critical",
                         "urgent", "important", "1", "2", "3"]
    scores["prioritized"] = 1.0 if sum(1 for k in priority_keywords if k in blob) >= 2 else 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for MFG-10."""
    dimensions = {}

    # Dimension 1: Data Normalization (weight: 0.20)
    norm_scores = _score_data_normalization()
    dimensions["data_normalization"] = {
        "score": sum(norm_scores.values()) / max(len(norm_scores), 1),
        "weight": 0.20,
        "details": norm_scores
    }

    # Dimension 2: Inconsistency Detection (weight: 0.20)
    incon_scores = _score_inconsistency_detection()
    dimensions["inconsistency_detection"] = {
        "score": sum(incon_scores.values()) / max(len(incon_scores), 1),
        "weight": 0.20,
        "details": incon_scores
    }

    # Dimension 3: Comparative Analysis (weight: 0.20)
    comp_scores = _score_comparative_analysis()
    dimensions["comparative_analysis"] = {
        "score": sum(comp_scores.values()) / max(len(comp_scores), 1),
        "weight": 0.20,
        "details": comp_scores
    }

    # Dimension 4: Script Quality (weight: 0.15)
    script_scores = _score_script_quality()
    dimensions["script_quality"] = {
        "score": sum(script_scores.values()) / max(len(script_scores), 1),
        "weight": 0.15,
        "details": script_scores
    }

    # Dimension 5: Report Quality (weight: 0.15)
    report_scores = _score_report_quality()
    dimensions["report_quality"] = {
        "score": sum(report_scores.values()) / max(len(report_scores), 1),
        "weight": 0.15,
        "details": report_scores
    }

    # Dimension 6: Recommendations (weight: 0.10)
    rec_scores = _score_recommendations()
    dimensions["recommendations"] = {
        "score": sum(rec_scores.values()) / max(len(rec_scores), 1),
        "weight": 0.10,
        "details": rec_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"MFG-10 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_plant_comparison_exists():
    comparison = _load_json("plant_comparison.json")
    assert comparison is not None, "plant_comparison.json must exist and be valid JSON"


def test_all_plants_covered():
    result = grade()
    norm = result["dimensions"].get("data_normalization", {})
    details = norm.get("details", {})
    assert details.get("all_plants_present", 0) >= 0.8, (
        "All 5 plants must be represented in comparison"
    )


def test_inconsistencies_detected():
    result = grade()
    incon = result["dimensions"].get("inconsistency_detection", {})
    details = incon.get("details", {})
    assert details.get("findings_exist", 0) == 1.0, (
        "inconsistency_findings.json must exist"
    )
    assert details.get("findings_count", 0) >= 0.5, (
        "At least 2 inconsistencies should be detected"
    )


def test_constant_values_flagged():
    """The data has several seeded constant-value anomalies that should be detected."""
    result = grade()
    incon = result["dimensions"].get("inconsistency_detection", {})
    details = incon.get("details", {})
    assert details.get("constant_values_detected", 0) > 0, (
        "Suspiciously constant values (e.g., Japan yield=98.8% every month) should be flagged"
    )


def test_benchmark_report_exists():
    report_path = _find_file("benchmark_report.md")
    assert report_path.exists(), "benchmark_report.md must exist"


def test_analysis_script_exists():
    script_path = _find_file("analysis_script.py")
    assert script_path.exists(), "analysis_script.py must exist"


def test_recommendations_present():
    recs = _load_json("recommendations.json")
    assert recs is not None, "recommendations.json must exist and be valid JSON"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["plant_comparison.json", "inconsistency_findings.json",
                          "benchmark_report.md", "analysis_script.py",
                          "recommendations.json"]
    # answer.json check
    answer_candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    answer_exists = any(p.exists() for p in answer_candidates)
    assert answer_exists, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 3, f"Only {found_optional}/5 key output files found"


def test_target_language():
    """Verify benchmark report is in English (for this EN-target task)."""
    report_path = _find_file("benchmark_report.md")
    if not report_path.exists():
        return
    content = report_path.read_text(encoding="utf-8-sig")
    latin_chars = len(re.findall(r'[a-zA-Z]', content))
    total_alpha = len(re.findall(r'\w', content))
    if total_alpha > 0:
        ratio = latin_chars / total_alpha
        assert ratio > 0.5, f"Report should be primarily English, got ratio {ratio:.1%}"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    comparison = _load_json("plant_comparison.json")
    assert comparison, "plant_comparison.json is empty or missing"
    blob = json.dumps(comparison, ensure_ascii=False)
    assert len(blob) > 500, f"Comparison data too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """For EN target: verify report contains substantive analysis."""
    report_path = _find_file("benchmark_report.md")
    if not report_path.exists():
        return
    content = report_path.read_text(encoding="utf-8-sig")
    assert len(content) > 500, f"Report too short ({len(content)} chars), likely incomplete"
    # Should have analytical content
    headers = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
    assert len(headers) >= 2, "Report should have structured sections"


def test_five_plant_comparison():
    """Verify comparison covers all 5 plants."""
    comparison = _load_json("plant_comparison.json")
    if not comparison:
        return
    blob = json.dumps(comparison, ensure_ascii=False).lower()
    plant_names = ["china", "shenzhen", "vietnam", "haiphong", "korea", "busan",
                   "japan", "osaka", "russia", "kaluga"]
    plants_found = sum(1 for p in plant_names if p in blob)
    assert plants_found >= 4, f"Only {plants_found} plant references found, expected coverage of 5 plants"


def test_inconsistency_detection_quality():
    """Verify seeded inconsistencies are detected."""
    findings = _load_json("inconsistency_findings.json")
    if not findings:
        return
    blob = json.dumps(findings, ensure_ascii=False).lower()
    # Check for constant/suspicious value detection
    suspicious_keywords = ["constant", "zero variance", "no variation", "same value",
                           "identical", "unchanged", "suspicious", "fixed", "unrealistic"]
    detected = sum(1 for k in suspicious_keywords if k in blob)
    assert detected >= 1, "Should detect suspicious constant/identical values in the data"
