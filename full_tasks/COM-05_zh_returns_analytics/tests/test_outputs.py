"""
BabelAgentBench grading for COM-05: Multilingual returns analytics with Chinese reporting.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

TOTAL_RETURNS_RU = 20
TOTAL_RETURNS_VN = 20
TOTAL_RETURNS = 40
EXPECTED_SKUS = 10


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_answer() -> Dict[str, Any]:
    candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    for path in candidates:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    return {}


def _is_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    if not text:
        return False
    cjk_count = sum(1 for c in text if '一' <= c <= '鿿')
    return cjk_count >= 5


def _score_data_extraction(data: Dict[str, Any]) -> Dict[str, float]:
    """Score data extraction from multilingual sources."""
    scores = {}
    analysis_path = _find_file("returns_analysis_zh.json")

    analysis = None
    if analysis_path.exists():
        try:
            analysis = json.loads(analysis_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not analysis:
        return {"file_present": 0.0, "market_coverage": 0.0,
                "reason_extraction": 0.0, "sku_matching": 0.0}

    scores["file_present"] = 1.0

    # Check both markets are represented
    blob = json.dumps(analysis, ensure_ascii=False).lower()
    has_russia = any(k in blob for k in ["russia", "ru", "俄罗斯", "俄"])
    has_vietnam = any(k in blob for k in ["vietnam", "vn", "越南", "越"])
    scores["market_coverage"] = 1.0 if (has_russia and has_vietnam) else 0.5 if (has_russia or has_vietnam) else 0.0

    # Check reason codes are extracted
    reason_codes = ["DEFECTIVE", "QUALITY", "NOT_AS_DESCRIBED", "WRONG_SIZE",
                    "DAMAGED", "COMFORT", "ALLERGIC"]
    reasons_found = sum(1 for r in reason_codes if r.lower() in blob)
    scores["reason_extraction"] = min(1.0, reasons_found / 5)

    # Check SKU matching
    sku_pattern = r'SKU-[A-Z]+-\d+'
    skus_found = set(re.findall(sku_pattern, json.dumps(analysis, ensure_ascii=False)))
    scores["sku_matching"] = min(1.0, len(skus_found) / 6)

    return scores


def _score_analytics_accuracy(data: Dict[str, Any]) -> Dict[str, float]:
    """Score analytics computation accuracy."""
    scores = {}
    dashboard_path = _find_file("dashboard_data.json")
    category_path = _find_file("category_breakdown.json")

    dashboard = None
    if dashboard_path.exists():
        try:
            dashboard = json.loads(dashboard_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    category = None
    if category_path.exists():
        try:
            category = json.loads(category_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not dashboard and not category:
        return {"dashboard_present": 0.0, "category_present": 0.0,
                "return_rates": 0.0, "trend_data": 0.0}

    scores["dashboard_present"] = 1.0 if dashboard else 0.0
    scores["category_present"] = 1.0 if category else 0.0

    # Check return rate calculations
    all_data = json.dumps(dashboard or {}, ensure_ascii=False) + json.dumps(category or {}, ensure_ascii=False)
    blob_lower = all_data.lower()

    # Should contain percentage/rate values
    has_rates = bool(re.search(r'\d+\.?\d*\s*%', all_data)) or "rate" in blob_lower or "ratio" in blob_lower
    scores["return_rates"] = 1.0 if has_rates else 0.0

    # Check for time trend data
    has_trend = any(k in blob_lower for k in ["trend", "monthly", "weekly", "time",
                                               "october", "november", "10月", "11月",
                                               "2024-10", "2024-11"])
    scores["trend_data"] = 1.0 if has_trend else 0.0

    return scores


def _score_chinese_report(data: Dict[str, Any]) -> Dict[str, float]:
    """Score Chinese recommendations report."""
    scores = {}
    report_path = _find_file("recommendations_zh.md")

    if not report_path.exists():
        return {"file_present": 0.0, "chinese_language": 0.0,
                "structure": 0.0, "actionable": 0.0}

    report_text = report_path.read_text(encoding="utf-8-sig")

    scores["file_present"] = 1.0
    scores["chinese_language"] = 1.0 if _is_chinese(report_text) and len(report_text) > 500 else 0.5 if _is_chinese(report_text) else 0.0

    # Check structure
    headers = re.findall(r'^#{1,3}\s+.+', report_text, re.MULTILINE)
    scores["structure"] = min(1.0, len(headers) / 4)

    # Check actionable recommendations
    action_keywords = ["建议", "改进", "优化", "加强", "提升", "解决", "措施",
                       "方案", "优先", "计划", "目标", "预期"]
    action_found = sum(1 for kw in action_keywords if kw in report_text)
    scores["actionable"] = min(1.0, action_found / 4)

    return scores


def _score_dashboard_completeness(data: Dict[str, Any]) -> Dict[str, float]:
    """Score dashboard data completeness."""
    scores = {}
    dashboard_path = _find_file("dashboard_data.json")

    dashboard = None
    if dashboard_path.exists():
        try:
            dashboard = json.loads(dashboard_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not dashboard:
        return {"file_present": 0.0, "visualizable": 0.0, "comparisons": 0.0}

    scores["file_present"] = 1.0

    # Check if data is structured for visualization
    blob = json.dumps(dashboard, ensure_ascii=False).lower()

    # Should have array/list data suitable for charts
    has_arrays = "[]" not in json.dumps(dashboard) and isinstance(dashboard, (dict, list))
    has_labels = any(k in blob for k in ["label", "name", "category", "period", "month"])
    has_values = any(k in blob for k in ["value", "count", "total", "amount", "rate"])
    visualizable = sum([has_arrays, has_labels, has_values])
    scores["visualizable"] = visualizable / 3

    # Check for market comparisons
    has_comparison = any(k in blob for k in ["russia", "vietnam", "ru", "vn",
                                              "俄罗斯", "越南", "comparison", "对比"])
    scores["comparisons"] = 1.0 if has_comparison else 0.0

    return scores


def _score_recommendations(data: Dict[str, Any]) -> Dict[str, float]:
    """Score quality of recommendations."""
    scores = {}
    report_path = _find_file("recommendations_zh.md")
    analysis_path = _find_file("returns_analysis_zh.json")

    report_text = ""
    if report_path.exists():
        report_text = report_path.read_text(encoding="utf-8-sig")

    analysis = None
    if analysis_path.exists():
        try:
            analysis = json.loads(analysis_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not report_text and not analysis:
        return {"root_cause": 0.0, "prioritization": 0.0, "policy_reference": 0.0}

    blob = report_text + json.dumps(analysis or {}, ensure_ascii=False)

    # Check root cause analysis
    root_cause_keywords = ["根因", "原因分析", "根本原因", "主要原因", "核心问题",
                           "root cause", "原因", "导致", "造成"]
    rc_found = sum(1 for kw in root_cause_keywords if kw in blob)
    scores["root_cause"] = min(1.0, rc_found / 3)

    # Check prioritization
    priority_keywords = ["优先", "紧急", "重要", "priority", "P1", "P2",
                         "首先", "其次", "最后", "排序"]
    pri_found = sum(1 for kw in priority_keywords if kw in blob)
    scores["prioritization"] = min(1.0, pri_found / 3)

    # Check policy reference
    policy_keywords = ["政策", "policy", "退货率", "return rate", "5%", "10%",
                       "合规", "compliance", "超标", "threshold"]
    pol_found = sum(1 for kw in policy_keywords if kw.lower() in blob.lower())
    scores["policy_reference"] = min(1.0, pol_found / 3)

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for COM-05."""
    data = _load_answer()

    dimensions = {}

    # Dimension 1: Data Extraction (weight: 0.25)
    extract_scores = _score_data_extraction(data)
    dimensions["data_extraction"] = {
        "score": sum(extract_scores.values()) / max(len(extract_scores), 1),
        "weight": 0.25,
        "details": extract_scores
    }

    # Dimension 2: Analytics Accuracy (weight: 0.25)
    analytics_scores = _score_analytics_accuracy(data)
    dimensions["analytics_accuracy"] = {
        "score": sum(analytics_scores.values()) / max(len(analytics_scores), 1),
        "weight": 0.25,
        "details": analytics_scores
    }

    # Dimension 3: Chinese Report (weight: 0.20)
    report_scores = _score_chinese_report(data)
    dimensions["chinese_report"] = {
        "score": sum(report_scores.values()) / max(len(report_scores), 1),
        "weight": 0.20,
        "details": report_scores
    }

    # Dimension 4: Dashboard Completeness (weight: 0.15)
    dash_scores = _score_dashboard_completeness(data)
    dimensions["dashboard_completeness"] = {
        "score": sum(dash_scores.values()) / max(len(dash_scores), 1),
        "weight": 0.15,
        "details": dash_scores
    }

    # Dimension 5: Recommendations (weight: 0.15)
    rec_scores = _score_recommendations(data)
    dimensions["recommendations"] = {
        "score": sum(rec_scores.values()) / max(len(rec_scores), 1),
        "weight": 0.15,
        "details": rec_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-05 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_both_markets_covered():
    result = grade()
    extraction = result["dimensions"].get("data_extraction", {})
    details = extraction.get("details", {})
    assert details.get("market_coverage", 0) >= 0.5, "Both Russia and Vietnam markets should be covered"


def test_chinese_report_present():
    result = grade()
    report = result["dimensions"].get("chinese_report", {})
    details = report.get("details", {})
    assert details.get("file_present", 0) == 1.0, "recommendations_zh.md must be present"
    assert details.get("chinese_language", 0) >= 0.5, "Report must be in Chinese"


def test_dashboard_data_present():
    result = grade()
    dash = result["dimensions"].get("dashboard_completeness", {})
    details = dash.get("details", {})
    assert details.get("file_present", 0) == 1.0, "dashboard_data.json must be present"


def test_reason_codes_extracted():
    result = grade()
    extraction = result["dimensions"].get("data_extraction", {})
    details = extraction.get("details", {})
    assert details.get("reason_extraction", 0) >= 0.4, "Return reason codes should be properly extracted"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["returns_analysis_zh.json", "recommendations_zh.md",
                          "dashboard_data.json", "category_breakdown.json"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify output is in Chinese (CJK characters), not English fallback."""
    report_path = _find_file("recommendations_zh.md")
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8-sig")
    cjk_chars = sum(1 for c in text if '一' <= c <= '鿿')
    ratio = cjk_chars / max(len(text.replace(" ", "").replace("\n", "")), 1)
    assert ratio > 0.2, f"Chinese report CJK ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    blob = json.dumps(data, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Chinese report isn't in English."""
    report_path = _find_file("recommendations_zh.md")
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8-sig")
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Chinese report appears to be mostly English ({english_ratio:.0%})"


def test_return_analysis_counts():
    """Verify returns analysis covers expected data volume."""
    analysis_path = _find_file("returns_analysis_zh.json")
    if not analysis_path.exists():
        return
    try:
        analysis = json.loads(analysis_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return
    blob = json.dumps(analysis, ensure_ascii=False)
    # Should reference SKU patterns from both markets
    sku_pattern = r'SKU-[A-Z]+-\d+'
    skus_found = set(re.findall(sku_pattern, blob))
    assert len(skus_found) >= 4, f"Only {len(skus_found)} SKUs found, expected analysis across multiple"
