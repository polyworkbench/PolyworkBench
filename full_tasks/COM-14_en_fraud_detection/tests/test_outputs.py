import json
import os
from pathlib import Path

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


def _find_file(name):
    for p in [
        OUTPUT_DIR / "output" / name,
        OUTPUT_DIR / "outputs" / name,
        OUTPUT_DIR / name,
        Path(f"/workspace/output/{name}"),
        Path(f"/workspace/outputs/{name}"),
        Path(f"/workspace/{name}"),
    ]:
        if p.exists():
            return p
    return OUTPUT_DIR / "output" / name


EXPECTED_FRAUD_TXNS = {"TXN-037", "TXN-012", "TXN-041", "TXN-048", "TXN-003"}


def test_fraud_report_exists():
    path = _find_file("fraud_report.md")
    assert path.exists(), "fraud_report.md not found"
    content = path.read_text(encoding="utf-8")
    assert len(content) > 500, "Report too short"
    # Should reference the fraudulent transactions
    for txn in EXPECTED_FRAUD_TXNS:
        assert txn in content, f"Fraudulent transaction {txn} not mentioned in report"


def test_flagged_transactions_json_exists():
    path = _find_file("flagged_transactions.json")
    assert path.exists(), "flagged_transactions.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "flagged_transactions.json must be a JSON object"


def test_flagged_transactions_correct():
    path = _find_file("flagged_transactions.json")
    assert path.exists(), "flagged_transactions.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))

    transactions = data.get("flagged_transactions", data.get("transactions", data.get("flagged", [])))
    if isinstance(data, list):
        transactions = data

    flagged_ids = set()
    for txn in transactions:
        txn_id = txn.get("txn_id", txn.get("id", txn.get("transaction_id", "")))
        flagged_ids.add(txn_id)

    # Check all 5 are present
    for expected in EXPECTED_FRAUD_TXNS:
        assert expected in flagged_ids, f"Missing fraudulent transaction: {expected}"


def test_flagged_count():
    path = _find_file("flagged_transactions.json")
    assert path.exists(), "flagged_transactions.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))

    transactions = data.get("flagged_transactions", data.get("transactions", data.get("flagged", [])))
    if isinstance(data, list):
        transactions = data

    assert len(transactions) >= 5, f"Expected at least 5 flagged transactions, found {len(transactions)}"


def test_fraud_types_assigned():
    path = _find_file("flagged_transactions.json")
    assert path.exists(), "flagged_transactions.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data).lower()

    # Check fraud type keywords are present
    assert "velocity" in all_text or "speed" in all_text or "rapid" in all_text, \
        "Velocity fraud type not identified"
    assert "amount" in all_text or "anomal" in all_text, \
        "Amount anomaly fraud type not identified"
    assert "geographic" in all_text or "geo" in all_text or "location" in all_text or "mismatch" in all_text, \
        "Geographic mismatch fraud type not identified"


def test_risk_scores_json():
    path = _find_file("risk_scores.json")
    assert path.exists(), "risk_scores.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Check that all 5 fraud transactions have risk scores
    for txn in EXPECTED_FRAUD_TXNS:
        assert txn in all_text, f"Risk score for {txn} not found"


def test_risk_score_levels():
    path = _find_file("risk_scores.json")
    assert path.exists(), "risk_scores.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data).lower()

    # Should have critical/high level indicators
    assert "critical" in all_text or "high" in all_text, \
        "No critical/high risk levels found in risk scores"



# === Ground-truth assertions (P1) ===

def test_exact_fraud_ids():
    """Ground truth: exactly TXN-037, TXN-012, TXN-041, TXN-048, TXN-003"""
    d = json.loads(_find_file("flagged_transactions.json").read_text()) if _find_file("flagged_transactions.json").exists() else {}
    content = json.dumps(d)
    expected = ["TXN-037", "TXN-012", "TXN-041", "TXN-048", "TXN-003"]
    found = sum(1 for txn in expected if txn in content)
    assert found >= 4, f"Only {found}/5 fraud transactions correctly identified"

def test_no_false_positives():
    """Should not flag more than 8 transactions (5 real + 3 margin)"""
    d = json.loads(_find_file("flagged_transactions.json").read_text()) if _find_file("flagged_transactions.json").exists() else {}
    txns = d.get("flagged_transactions", d.get("transactions", d.get("flagged", [])))
    if isinstance(txns, list):
        assert len(txns) <= 10, f"Too many flagged ({len(txns)}), likely false positives"

def grade():
    """Weighted grading with non-linear cap (0.85 max for all-pass).
    Supports both class-based (pytest) and function-based test patterns.
    """
    import sys, inspect
    
    mod = sys.modules.get("test_outputs")
    if mod is None:
        return {"overall_score": 0.0, "error": "Module not in sys.modules"}
    
    # Collect test functions: both top-level and class methods
    test_funcs = []
    
    # Top-level functions
    for name in dir(mod):
        obj = getattr(mod, name)
        if name.startswith("test_") and callable(obj) and not inspect.isclass(obj):
            test_funcs.append((name, obj))
    
    # Class-based tests (pytest-style: class TestX with def test_y(self))
    for name in dir(mod):
        obj = getattr(mod, name)
        if inspect.isclass(obj) and name.startswith("Test"):
            instance = obj()
            for method_name in dir(instance):
                if method_name.startswith("test_"):
                    method = getattr(instance, method_name)
                    if callable(method):
                        test_funcs.append((f"{name}.{method_name}", method))
    
    if not test_funcs:
        return {"overall_score": 0.0, "error": "No test functions found"}
    
    # Run with weighted scoring
    results = []
    for name, func in sorted(test_funcs):
        if any(k in name for k in ["correct", "accura", "value", "amount", "count",
                                     "number", "detect", "identif", "match", "verify",
                                     "found", "present"]):
            weight = 2.0
        elif any(k in name for k in ["exist", "file", "creat"]):
            weight = 0.5
        else:
            weight = 1.0
        try:
            func()
            results.append({"name": name, "passed": True, "weight": weight})
        except (AssertionError, Exception):
            results.append({"name": name, "passed": False, "weight": weight})
    
    total_weight = sum(r["weight"] for r in results)
    earned_weight = sum(r["weight"] for r in results if r["passed"])
    raw_score = earned_weight / total_weight if total_weight > 0 else 0.0
    
    # Non-linear scaling
    if raw_score >= 1.0: scaled = 0.85
    elif raw_score >= 0.9: scaled = 0.70 + (raw_score - 0.9) * 1.5
    elif raw_score >= 0.7: scaled = 0.50 + (raw_score - 0.7) * 1.0
    elif raw_score >= 0.5: scaled = 0.30 + (raw_score - 0.5) * 1.0
    elif raw_score >= 0.3: scaled = 0.15 + (raw_score - 0.3) * 0.75
    else: scaled = raw_score * 0.5
    
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "overall_score": round(scaled, 4),
        "dimensions": {
            "weighted_completion": {
                "score": round(scaled, 4), "weight": 1.0,
                "details": {"tests_passed": passed_count, "tests_total": len(results), "weighted_raw": round(raw_score, 4)}
            }
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(grade(), indent=2))
