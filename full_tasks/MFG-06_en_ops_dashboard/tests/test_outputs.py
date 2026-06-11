"""
WildClawBench-style grading for MFG-06: Multi-factory operations dashboard from trilingual data.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

FACTORIES = ["shenzhen", "haiphong", "busan"]
EXPECTED_KPIS = ["oee", "yield_rate", "throughput", "downtime_pct", "defect_rate", "energy_efficiency"]
NUM_DAYS = 14


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


def _score_data_aggregation() -> Dict[str, float]:
    """Score the dashboard data aggregation (weight: 0.30)."""
    scores = {}
    dashboard = _load_json("dashboard_data.json")

    if not dashboard:
        return {"dashboard_exists": 0.0, "factory_coverage": 0.0,
                "daily_data": 0.0, "weekly_rollup": 0.0, "field_mapping": 0.0}

    scores["dashboard_exists"] = 1.0

    # Check factory coverage
    blob = json.dumps(dashboard, ensure_ascii=False).lower()
    factory_found = sum(1 for f in FACTORIES if f in blob)
    scores["factory_coverage"] = factory_found / len(FACTORIES)

    # Check for daily data presence
    if isinstance(dashboard, dict):
        # Look for daily data structure
        has_daily = any(k in blob for k in ["daily", "2024-11", "day"])
        scores["daily_data"] = 1.0 if has_daily else 0.0

        # Check for weekly rollup
        has_weekly = any(k in blob for k in ["weekly", "week", "w1", "week_1"])
        scores["weekly_rollup"] = 1.0 if has_weekly else 0.0
    else:
        scores["daily_data"] = 0.3
        scores["weekly_rollup"] = 0.0

    # Check field mapping (translated from zh/vi/ko to en)
    en_fields = ["production", "yield", "output", "downtime", "defect", "quality", "oee"]
    field_hits = sum(1 for f in en_fields if f in blob)
    scores["field_mapping"] = min(1.0, field_hits / 4)

    return scores


def _score_kpi_accuracy() -> Dict[str, float]:
    """Score KPI calculation accuracy (weight: 0.25)."""
    scores = {}
    dashboard = _load_json("dashboard_data.json")
    summary_path = _find_file("kpi_summary.md")

    if not dashboard and not (summary_path.exists()):
        return {"kpis_calculated": 0.0, "kpi_coverage": 0.0,
                "reasonable_values": 0.0, "targets_referenced": 0.0}

    blob = ""
    if dashboard:
        blob += json.dumps(dashboard, ensure_ascii=False).lower()
    if summary_path.exists():
        blob += summary_path.read_text(encoding="utf-8-sig").lower()

    # Check KPI coverage
    kpi_patterns = {
        "oee": ["oee", "overall equipment effectiveness"],
        "yield_rate": ["yield", "first pass", "良率"],
        "throughput": ["throughput", "output", "production"],
        "downtime_pct": ["downtime", "停机"],
        "defect_rate": ["defect", "reject", "不良"],
        "energy_efficiency": ["energy", "efficiency", "kwh"]
    }

    kpis_found = 0
    for kpi, patterns in kpi_patterns.items():
        if any(p in blob for p in patterns):
            kpis_found += 1

    scores["kpis_calculated"] = 1.0 if kpis_found >= 4 else kpis_found / 6.0
    scores["kpi_coverage"] = kpis_found / len(EXPECTED_KPIS)

    # Check for reasonable numeric values
    numbers = re.findall(r'\d+\.?\d*', blob)
    numeric_vals = [float(n) for n in numbers if 0 < float(n) < 100]
    scores["reasonable_values"] = 1.0 if len(numeric_vals) > 20 else min(1.0, len(numeric_vals) / 20)

    # Check targets are referenced
    target_keywords = ["target", "threshold", "goal"]
    scores["targets_referenced"] = 1.0 if any(k in blob for k in target_keywords) else 0.0

    return scores


def _score_script_quality() -> Dict[str, float]:
    """Score the aggregation script (weight: 0.20)."""
    scores = {}
    script_path = _find_file("aggregation_script.py")

    if not script_path.exists():
        return {"script_exists": 0.0, "reads_csvs": 0.0,
                "handles_encoding": 0.0, "calculates_kpis": 0.0, "produces_output": 0.0}

    content = script_path.read_text(encoding="utf-8-sig")
    scores["script_exists"] = 1.0

    # Check if it reads CSVs
    csv_patterns = ["csv", "read_csv", "pandas", "open("]
    scores["reads_csvs"] = 1.0 if any(p in content for p in csv_patterns) else 0.0

    # Check encoding handling
    encoding_patterns = ["utf-8", "encoding", "utf8"]
    scores["handles_encoding"] = 1.0 if any(p in content.lower() for p in encoding_patterns) else 0.0

    # Check KPI calculations
    calc_patterns = ["oee", "yield", "downtime", "defect", "throughput"]
    calc_found = sum(1 for p in calc_patterns if p in content.lower())
    scores["calculates_kpis"] = min(1.0, calc_found / 3)

    # Check if it produces output files
    output_patterns = ["json.dump", "to_json", "write", "open("]
    scores["produces_output"] = 1.0 if any(p in content for p in output_patterns) else 0.0

    return scores


def _score_anomaly_detection() -> Dict[str, float]:
    """Score anomaly detection (weight: 0.15)."""
    scores = {}
    anomalies = _load_json("anomaly_report.json")

    if not anomalies:
        return {"anomaly_report_exists": 0.0, "anomalies_found": 0.0,
                "severity_levels": 0.0, "fields_complete": 0.0}

    scores["anomaly_report_exists"] = 1.0

    # Check anomalies are found (we expect some - Nov 6, Nov 10 have issues)
    if isinstance(anomalies, list):
        anomaly_list = anomalies
    elif isinstance(anomalies, dict):
        anomaly_list = anomalies.get("anomalies", anomalies.get("findings", []))
        if isinstance(anomaly_list, dict):
            anomaly_list = list(anomaly_list.values())
    else:
        anomaly_list = []

    # There should be anomalies on Nov 6 and Nov 10 (power outages across factories)
    scores["anomalies_found"] = min(1.0, len(anomaly_list) / 4) if anomaly_list else 0.0

    # Check for severity classification
    blob = json.dumps(anomalies, ensure_ascii=False).lower()
    has_severity = any(s in blob for s in ["severity", "critical", "warning", "level"])
    scores["severity_levels"] = 1.0 if has_severity else 0.0

    # Check field completeness (factory, date, kpi, value, range)
    required_fields = ["factory", "date", "kpi", "value", "actual"]
    if anomaly_list and isinstance(anomaly_list[0], dict):
        first = str(anomaly_list[0].keys()).lower()
        fields_found = sum(1 for f in required_fields if f in first or f in str(anomaly_list[0]).lower())
        scores["fields_complete"] = min(1.0, fields_found / 3)
    else:
        scores["fields_complete"] = 0.0

    return scores


def _score_report_quality() -> Dict[str, float]:
    """Score the KPI summary markdown report (weight: 0.10)."""
    scores = {}
    summary_path = _find_file("kpi_summary.md")

    if not summary_path.exists():
        return {"report_exists": 0.0, "has_table": 0.0,
                "factory_comparison": 0.0, "trend_indicators": 0.0}

    content = summary_path.read_text(encoding="utf-8-sig")
    scores["report_exists"] = 1.0

    # Check for markdown table
    has_table = "|" in content and "-" in content
    scores["has_table"] = 1.0 if has_table else 0.0

    # Check factory comparison (all three mentioned)
    content_lower = content.lower()
    factories_mentioned = sum(1 for f in FACTORIES if f in content_lower)
    scores["factory_comparison"] = factories_mentioned / len(FACTORIES)

    # Check for trend indicators
    trend_patterns = ["improving", "stable", "declining", "↑", "↓", "→", "▲", "▼"]
    has_trends = any(t in content.lower() or t in content for t in trend_patterns)
    scores["trend_indicators"] = 1.0 if has_trends else 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for MFG-06."""
    dimensions = {}

    # Dimension 1: Data Aggregation (weight: 0.30)
    agg_scores = _score_data_aggregation()
    dimensions["data_aggregation"] = {
        "score": sum(agg_scores.values()) / max(len(agg_scores), 1),
        "weight": 0.30,
        "details": agg_scores
    }

    # Dimension 2: KPI Accuracy (weight: 0.25)
    kpi_scores = _score_kpi_accuracy()
    dimensions["kpi_accuracy"] = {
        "score": sum(kpi_scores.values()) / max(len(kpi_scores), 1),
        "weight": 0.25,
        "details": kpi_scores
    }

    # Dimension 3: Script Quality (weight: 0.20)
    script_scores = _score_script_quality()
    dimensions["script_quality"] = {
        "score": sum(script_scores.values()) / max(len(script_scores), 1),
        "weight": 0.20,
        "details": script_scores
    }

    # Dimension 4: Anomaly Detection (weight: 0.15)
    anomaly_scores = _score_anomaly_detection()
    dimensions["anomaly_detection"] = {
        "score": sum(anomaly_scores.values()) / max(len(anomaly_scores), 1),
        "weight": 0.15,
        "details": anomaly_scores
    }

    # Dimension 5: Report Quality (weight: 0.10)
    report_scores = _score_report_quality()
    dimensions["report_quality"] = {
        "score": sum(report_scores.values()) / max(len(report_scores), 1),
        "weight": 0.10,
        "details": report_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"MFG-06 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_dashboard_data_exists():
    result = grade()
    agg = result["dimensions"].get("data_aggregation", {})
    details = agg.get("details", {})
    assert details.get("dashboard_exists", 0) == 1.0, (
        "dashboard_data.json must exist"
    )


def test_all_factories_covered():
    result = grade()
    agg = result["dimensions"].get("data_aggregation", {})
    details = agg.get("details", {})
    assert details.get("factory_coverage", 0) >= 0.66, (
        "Dashboard must cover at least 2 of 3 factories"
    )


def test_kpis_calculated():
    result = grade()
    kpi = result["dimensions"].get("kpi_accuracy", {})
    details = kpi.get("details", {})
    assert details.get("kpi_coverage", 0) >= 0.5, (
        "At least half of defined KPIs must be calculated"
    )


def test_script_exists_and_functional():
    result = grade()
    script = result["dimensions"].get("script_quality", {})
    details = script.get("details", {})
    assert details.get("script_exists", 0) == 1.0, (
        "aggregation_script.py must exist"
    )


def test_anomalies_detected():
    result = grade()
    anomaly = result["dimensions"].get("anomaly_detection", {})
    details = anomaly.get("details", {})
    assert details.get("anomaly_report_exists", 0) == 1.0, (
        "anomaly_report.json must exist"
    )
    assert details.get("anomalies_found", 0) > 0, (
        "At least some anomalies should be detected (e.g., Nov 6 power outage)"
    )


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["dashboard_data.json", "kpi_summary.md",
                          "aggregation_script.py", "anomaly_report.json"]
    # Check answer.json
    answer_path = _find_file("answer.json")
    # Use custom check since _find_file may not suit here
    found = 0
    for fname in optional_important:
        p = _find_file(fname)
        if p.exists():
            found += 1
    assert found >= 2, f"Only {found}/4 key output files found"


def test_target_language():
    """Verify output is in English (for this EN-target task)."""
    summary_path = _find_file("kpi_summary.md")
    if not summary_path.exists():
        return
    content = summary_path.read_text(encoding="utf-8-sig")
    latin_chars = len(re.findall(r'[a-zA-Z]', content))
    total_alpha = len(re.findall(r'\w', content))
    if total_alpha > 0:
        ratio = latin_chars / total_alpha
        assert ratio > 0.5, f"KPI summary should be primarily English, got ratio {ratio:.1%}"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    dashboard = _load_json("dashboard_data.json")
    assert dashboard, "dashboard_data.json is empty or missing"
    blob = json.dumps(dashboard, ensure_ascii=False)
    assert len(blob) > 500, f"Dashboard data too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """For EN target: verify data isn't in source languages (zh/vi/ko) only."""
    dashboard = _load_json("dashboard_data.json")
    if not dashboard:
        return
    blob = json.dumps(dashboard, ensure_ascii=False)
    # English dashboard should have English field names, not only CJK
    en_fields = ["production", "yield", "output", "downtime", "defect", "quality", "oee"]
    field_hits = sum(1 for f in en_fields if f in blob.lower())
    assert field_hits >= 2, "Dashboard should use English field names (not only zh/vi/ko source fields)"


def test_three_factory_kpis():
    """Verify KPI calculations cover all 3 factories."""
    dashboard = _load_json("dashboard_data.json")
    if not dashboard:
        return
    blob = json.dumps(dashboard, ensure_ascii=False).lower()
    factories_found = sum(1 for f in FACTORIES if f in blob)
    assert factories_found >= 2, f"Only {factories_found}/3 factories found in dashboard data"
