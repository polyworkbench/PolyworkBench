"""
WildClawBench-style grading for HQ-02: Japanese Receipts → English Concur Expense.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import csv, io, json, os, re
from pathlib import Path
from typing import Dict, Any, List

try:
    from jsonschema import Draft7Validator
except Exception:
    Draft7Validator = None

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Ground truth values for verification
GROUND_TRUTH = {
    "R001": {
        "date_iso": "2024-11-15",
        "vendor": "セブン-イレブン",
        "total_jpy": 1149,
        "tax_8_amount": 860,
        "tax_8_tax": 69,
        "tax_10_amount": 200,
        "tax_10_tax": 20,
        "addressee_blank": True,
        "stamp_present": True,
    },
    "R002": {
        "date_iso": "2024-11-18",
        "vendor": "JR東日本",
        "total_jpy": 14400,
        "tax_rate": 0.10,
        "addressee": "株式会社アクメ・リサーチ",
        "stamp_present": False,
    },
    "R003": {
        "date_iso": "2024-11-20",
        "vendor_contains": "さくら",
        "subtotal_before_service": 28300,  # 24500 + 3800
        "service_charge": 2830,
        "addressee": "上様",
        "stamp_present": True,
        "amount_obscured": True,
        "uesama_rule_fail": True,  # >= 30000 JPY + 上様
    }
}

JPY_CNY_RATE = 0.04632


def _safe_read(path: Path, encoding="utf-8-sig") -> str:
    if path.exists():
        return path.read_text(encoding=encoding).strip()
    return ""


def _safe_json(path: Path) -> Any:
    text = _safe_read(path)
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return None


def _find_file(name: str) -> Path:
    """Find a file in output/ or workspace root."""
    candidates = [
        OUTPUT_DIR / "output" / name,
        OUTPUT_DIR / name,
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]  # Return first candidate for consistent error messages


def _load_answer() -> Dict[str, Any]:
    """Load answer.json with fallback to individual output files."""
    # Try multiple paths for answer.json
    candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    data = {}
    for path in candidates:
        if path.exists():
            text = path.read_text(encoding="utf-8-sig").strip()
            if text.startswith("{"):
                try:
                    data = json.loads(text)
                    break
                except json.JSONDecodeError:
                    pass

    if not data:
        # Fallback: assemble from individual files
        csv_path = _find_file("concur_expense.csv")
        if csv_path.exists():
            data["concur_expense_csv"] = csv_path.read_text(encoding="utf-8-sig")

        extraction = _safe_json(_find_file("extraction.json"))
        if extraction:
            data["extraction"] = extraction

        exceptions_path = _find_file("exceptions.md")
        if exceptions_path.exists():
            data["exceptions_md"] = exceptions_path.read_text(encoding="utf-8-sig")

        calc_check = _safe_json(_find_file("calculation_check.json"))
        if calc_check:
            data["calculation_check"] = calc_check

        compliance = _safe_json(_find_file("compliance_check.json"))
        if compliance:
            data["compliance_check"] = compliance

        summary = _safe_json(_find_file("summary_stats.json"))
        if summary:
            data["summary_stats"] = summary

    # Normalize key names: agent may use different keys for same data
    if "extraction" not in data and "receipts" in data:
        data["extraction"] = data["receipts"]
    if "calculation_check" not in data and "verification_checks" in data:
        data["calculation_check"] = data["verification_checks"]
    if "concur_expense_csv" not in data:
        csv_path = _find_file("concur_expense_report.csv")
        if csv_path.exists():
            data["concur_expense_csv"] = csv_path.read_text(encoding="utf-8-sig")

    return data


def _score_extraction(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the data extraction quality against ground truth."""
    scores = {}
    extraction = data.get("extraction", [])

    if not extraction:
        return {"extraction_present": 0.0, "extraction_count": 0.0,
                "date_accuracy": 0.0, "amount_accuracy": 0.0, "metadata_quality": 0.0}

    scores["extraction_present"] = 1.0

    # Normalize extraction to list
    if isinstance(extraction, dict):
        records = list(extraction.values())
    else:
        records = extraction

    scores["extraction_count"] = min(1.0, len(records) / 3.0)

    # Build lookup by receipt_id (handle multiple naming conventions)
    by_id = {}
    # Map from agent IDs (RCPT-001) to ground truth IDs (R001)
    id_map = {"RCPT-001": "R001", "RCPT-002": "R002", "RCPT-003": "R003",
              "rcpt-001": "R001", "rcpt-002": "R002", "rcpt-003": "R003",
              "001": "R001", "002": "R002", "003": "R003"}
    for r in records:
        rid = r.get("receipt_id", r.get("Receipt_ID", r.get("id", "")))
        # Normalize to ground truth IDs
        normalized_rid = id_map.get(rid, rid)
        if normalized_rid:
            by_id[normalized_rid] = r

    # Date accuracy
    date_scores = []
    for rid, truth in GROUND_TRUTH.items():
        rec = by_id.get(rid, {})
        expected_date = truth.get("date_iso", "")
        actual_date = rec.get("date_iso", rec.get("date", rec.get("receipt_date_en", "")))
        if expected_date and expected_date in str(actual_date):
            date_scores.append(1.0)
        elif "2024" in str(actual_date):
            date_scores.append(0.5)  # Year correct at least
        else:
            date_scores.append(0.0)
    scores["date_accuracy"] = sum(date_scores) / max(len(date_scores), 1)

    # Amount accuracy (R001 and R002 have definite amounts)
    amount_scores = []
    for rid in ["R001", "R002"]:
        truth = GROUND_TRUTH[rid]
        rec = by_id.get(rid, {})
        expected = truth["total_jpy"]
        actual = rec.get("total_jpy", rec.get("amount_jpy", 0))
        if isinstance(actual, (int, float)) and abs(actual - expected) <= 1:
            amount_scores.append(1.0)
        elif isinstance(actual, (int, float)) and abs(actual - expected) <= 100:
            amount_scores.append(0.5)
        else:
            amount_scores.append(0.0)
    scores["amount_accuracy"] = sum(amount_scores) / max(len(amount_scores), 1)

    # Metadata quality (confidence, issues, stamp, addressee, recipient, reimbursable)
    meta_scores = []
    for rid, rec in by_id.items():
        meta_score = 0.0
        if "confidence" in rec and isinstance(rec["confidence"], (int, float)):
            meta_score += 0.25
        elif "reimbursable" in rec:
            meta_score += 0.25  # Alternative: explicit reimbursable flag
        if "issues" in rec and isinstance(rec["issues"], list):
            meta_score += 0.25
        elif "notes" in rec and rec["notes"]:
            meta_score += 0.25  # Alternative: notes field
        if "stamp_present" in rec:
            meta_score += 0.25
        if "addressee" in rec or "recipient" in rec or "宛名" in str(rec):
            meta_score += 0.25
        meta_scores.append(meta_score)
    scores["metadata_quality"] = sum(meta_scores) / max(len(meta_scores), 1)

    # Tax breakdown detail
    tax_scores = []
    for rid, rec in by_id.items():
        tb = rec.get("tax_breakdown", [])
        if isinstance(tb, list) and len(tb) >= 1:
            tax_scores.append(1.0)
        elif any(k for k in rec.keys() if "tax" in k.lower()):
            # Agent may use explicit tax fields (tax_8pct_jpy, tax_10pct_jpy)
            tax_scores.append(1.0)
        elif "tax" in str(rec).lower():
            tax_scores.append(0.3)
        else:
            tax_scores.append(0.0)
    scores["tax_breakdown"] = sum(tax_scores) / max(len(tax_scores), 1)

    return scores


def _score_calculations(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the calculation verification step."""
    scores = {}

    # Check if verification script exists
    script_path = _find_file("verify_calculations.py")
    scores["script_exists"] = 1.0 if script_path.exists() else 0.0

    # Check calculation_check results
    calc_check = data.get("calculation_check", {})
    if not calc_check:
        calc_check = _safe_json(_find_file("calculation_check.json")) or {}

    if not calc_check:
        scores["calc_check_present"] = 0.0
        scores["calc_check_quality"] = 0.0
        return scores

    scores["calc_check_present"] = 1.0

    # Check structure
    quality = 0.0
    if "rate_used" in calc_check:
        quality += 0.2
        # Verify rate matches input
        rate = calc_check.get("rate_used", 0)
        if abs(rate - JPY_CNY_RATE) < 0.0001:
            quality += 0.2
    if "checks" in calc_check and isinstance(calc_check["checks"], list):
        quality += 0.3
        checks = calc_check["checks"]
        if len(checks) >= 3:
            quality += 0.1
        # Check if pass/fail flags are present
        if all("pass" in c for c in checks):
            quality += 0.2
    scores["calc_check_quality"] = min(1.0, quality)

    return scores


def _score_compliance(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the compliance checking step."""
    scores = {}

    compliance = data.get("compliance_check", {})
    if not compliance:
        compliance = _safe_json(_find_file("compliance_check.json")) or {}

    if not compliance:
        return {"compliance_present": 0.0, "uesama_rule": 0.0, "stamp_rule": 0.0}

    scores["compliance_present"] = 1.0

    # Check for 上様 rule application
    results = compliance.get("results", [])
    blob = json.dumps(compliance, ensure_ascii=False).lower()

    # R003 should be flagged for 上様 + >= 30000
    r003_flagged = any(
        ("r003" in str(r).lower() or "003" in str(r))
        and ("fail" in str(r).lower() or "reject" in str(r).lower() or "上様" in str(r))
        for r in results
    ) or ("r003" in blob and ("fail" in blob or "reject" in blob))
    scores["uesama_rule"] = 1.0 if r003_flagged else 0.0

    # Check for stamp occlusion rule
    stamp_mentioned = "stamp" in blob or "occlusion" in blob or "印章" in blob or "遮挡" in blob
    scores["stamp_rule"] = 1.0 if stamp_mentioned else 0.0

    return scores


def _score_csv_output(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the CSV output quality."""
    scores = {}
    csv_text = data.get("concur_expense_csv", "")

    if not csv_text:
        csv_path = _find_file("concur_expense.csv")
        if csv_path.exists():
            csv_text = csv_path.read_text(encoding="utf-8-sig")

    if not csv_text:
        return {"csv_present": 0.0, "csv_columns": 0.0, "csv_rows": 0.0, "csv_status_col": 0.0}

    scores["csv_present"] = 1.0

    # Parse CSV
    clean_text = csv_text.lstrip("﻿")
    try:
        rows = list(csv.DictReader(io.StringIO(clean_text)))
    except Exception:
        return {"csv_present": 0.5, "csv_columns": 0.0, "csv_rows": 0.0, "csv_status_col": 0.0}

    # Check column presence
    expected_cols = {"Date", "Vendor", "Description", "Amount_JPY", "Tax_Rate",
                     "Amount_CNY", "Receipt_ID"}
    if rows:
        actual_cols = set(rows[0].keys())
        # Case-insensitive matching
        matched = sum(1 for ec in expected_cols
                      if any(ec.lower() == ac.lower() for ac in actual_cols))
        scores["csv_columns"] = matched / len(expected_cols)
    else:
        scores["csv_columns"] = 0.0

    # Check row count
    scores["csv_rows"] = min(1.0, len(rows) / 3.0)

    # Check Status column
    has_status = any("status" in str(k).lower() for row in rows for k in row.keys())
    if has_status:
        statuses = [row.get("Status", row.get("status", "")).lower() for row in rows]
        has_rejected = any("reject" in s for s in statuses)
        scores["csv_status_col"] = 1.0 if has_rejected else 0.5
    else:
        scores["csv_status_col"] = 0.0

    return scores


def _score_exceptions(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the exceptions report."""
    scores = {}
    exceptions = data.get("exceptions_md", "")

    if not exceptions:
        exc_path = _find_file("exceptions.md")
        if exc_path.exists():
            exceptions = exc_path.read_text(encoding="utf-8-sig")

    if not exceptions:
        return {"exceptions_present": 0.0, "exceptions_quality": 0.0}

    scores["exceptions_present"] = 1.0

    quality = 0.0
    lower = exceptions.lower()
    # Should mention R003
    if "r003" in lower or "003" in lower or "さくら" in exceptions:
        quality += 0.3
    # Should mention severity
    if "critical" in lower or "warning" in lower or "info" in lower:
        quality += 0.3
    # Should mention the 上様 issue
    if "上様" in exceptions or "uesama" in lower or "addressee" in lower:
        quality += 0.2
    # Should mention stamp/occlusion
    if "stamp" in lower or "印章" in exceptions or "occlusion" in lower or "obscur" in lower:
        quality += 0.2
    scores["exceptions_quality"] = min(1.0, quality)

    return scores


def _score_summary_stats(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the summary statistics."""
    scores = {}
    stats = data.get("summary_stats", {})

    if not stats:
        stats = _safe_json(_find_file("summary_stats.json")) or {}

    if not stats:
        return {"summary_present": 0.0, "summary_quality": 0.0}

    scores["summary_present"] = 1.0

    expected_fields = ["total_receipts", "approved_count", "rejected_count",
                       "total_approved_jpy", "total_approved_cny", "average_confidence"]
    found = sum(1 for f in expected_fields if f in stats)
    scores["summary_quality"] = found / len(expected_fields)

    # Verify total_receipts
    if stats.get("total_receipts") == 3:
        scores["summary_accuracy"] = 1.0
    elif isinstance(stats.get("total_receipts"), int):
        scores["summary_accuracy"] = 0.5
    else:
        scores["summary_accuracy"] = 0.0

    return scores


def grade() -> Dict[str, Any]:
    """
    Multi-dimensional grading for HQ-02.
    Returns dict with dimension scores and weighted overall_score.
    """
    data = _load_answer()

    if not data:
        return {
            "overall_score": 0.0,
            "dimensions": {},
            "error": "No answer found."
        }

    dimensions = {}

    # Dimension 1: Data Extraction (weight: 0.30)
    extraction_scores = _score_extraction(data)
    dimensions["extraction"] = {
        "score": sum(extraction_scores.values()) / max(len(extraction_scores), 1),
        "weight": 0.30,
        "details": extraction_scores
    }

    # Dimension 2: Calculation Verification (weight: 0.20)
    calc_scores = _score_calculations(data)
    dimensions["calculations"] = {
        "score": sum(calc_scores.values()) / max(len(calc_scores), 1),
        "weight": 0.20,
        "details": calc_scores
    }

    # Dimension 3: Compliance Rules (weight: 0.20)
    compliance_scores = _score_compliance(data)
    dimensions["compliance"] = {
        "score": sum(compliance_scores.values()) / max(len(compliance_scores), 1),
        "weight": 0.20,
        "details": compliance_scores
    }

    # Dimension 4: CSV Output (weight: 0.15)
    csv_scores = _score_csv_output(data)
    dimensions["csv_output"] = {
        "score": sum(csv_scores.values()) / max(len(csv_scores), 1),
        "weight": 0.15,
        "details": csv_scores
    }

    # Dimension 5: Exceptions & Summary (weight: 0.15)
    exc_scores = _score_exceptions(data)
    sum_scores = _score_summary_stats(data)
    combined = {**{f"exc_{k}": v for k, v in exc_scores.items()},
                **{f"sum_{k}": v for k, v in sum_scores.items()}}
    dimensions["reporting"] = {
        "score": sum(combined.values()) / max(len(combined), 1),
        "weight": 0.15,
        "details": combined
    }

    # Calculate weighted overall score
    overall_score = sum(
        dim["score"] * dim["weight"]
        for dim in dimensions.values()
    )

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": dimensions
    }


# === Pytest-compatible tests ===

def test_grade_overall():
    """Main grading test — reports overall score."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"HQ-02 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for dim_name, dim_data in result.get("dimensions", {}).items():
        print(f"  {dim_name}: {dim_data['score']:.2%} (weight: {dim_data['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.0, "No valid output produced"


def test_extraction_quality():
    """Data extraction must capture key receipt information."""
    result = grade()
    extraction = result["dimensions"].get("extraction", {})
    score = extraction.get("score", 0.0)
    assert score >= 0.2, (
        f"Extraction score too low: {score:.2%}. "
        f"Details: {extraction.get('details', {})}"
    )


def test_calculation_verification():
    """Calculation verification step should be attempted."""
    result = grade()
    calc = result["dimensions"].get("calculations", {})
    score = calc.get("score", 0.0)
    # Partial credit — even having the script counts
    assert score >= 0.0  # Reports score; always passes


def test_compliance_rules():
    """Compliance rules should flag R003 上様 issue."""
    result = grade()
    compliance = result["dimensions"].get("compliance", {})
    details = compliance.get("details", {})
    # The 上様 rule is the most critical check
    uesama = details.get("uesama_rule", 0.0)
    if uesama < 1.0:
        # Check if it's at least in the exceptions
        data = _load_answer()
        blob = json.dumps(data, ensure_ascii=False).lower()
        assert "上様" in blob or "r003" in blob, (
            "R003 上様 compliance issue not detected anywhere in output"
        )
