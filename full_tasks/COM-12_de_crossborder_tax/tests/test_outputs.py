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


def test_tax_compliance_report_exists():
    path = _find_file("tax_compliance_report_de.md")
    assert path.exists(), "tax_compliance_report_de.md not found"
    content = path.read_text(encoding="utf-8")
    assert len(content) > 500, "Report too short"
    # Should be in German
    german_terms = ["steuer", "mehrwertsteuer", "berechnung", "jurisdiktion", "gesamt", "bericht"]
    found = sum(1 for t in german_terms if t.lower() in content.lower())
    assert found >= 3, f"Report does not appear to be in German (found {found}/6 German terms)"


def test_tax_calculations_json_exists():
    path = _find_file("tax_calculations.json")
    assert path.exists(), "tax_calculations.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "tax_calculations.json must be a JSON object"


def test_de_tax_total():
    path = _find_file("tax_calculations.json")
    assert path.exists(), "tax_calculations.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # DE total tax should be 4523.70
    assert "4523" in all_text, "DE tax total €4,523.70 not found"


def test_us_tax_total():
    path = _find_file("tax_calculations.json")
    assert path.exists(), "tax_calculations.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # US total tax should be 2187.45
    assert "2187" in all_text, "US tax total $2,187.45 not found"


def test_jp_tax_total():
    path = _find_file("tax_calculations.json")
    assert path.exists(), "tax_calculations.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # JP total tax should be 89100
    assert "89100" in all_text, "JP tax total ¥89,100 not found"


def test_tax_rates_correct():
    path = _find_file("tax_calculations.json")
    assert path.exists(), "tax_calculations.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Check rates are present
    assert "0.19" in all_text or "19" in all_text, "DE VAT 19% not found"
    assert "0.0725" in all_text or "7.25" in all_text, "US CA 7.25% not found"
    assert "0.08" in all_text or "8" in all_text, "US NY 8% not found"


def test_transaction_counts():
    path = _find_file("tax_calculations.json")
    assert path.exists(), "tax_calculations.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))

    # Check if jurisdictions have correct transaction counts
    jurisdictions = data.get("jurisdictions", data)

    if "DE" in jurisdictions:
        de_data = jurisdictions["DE"]
        if "transactions_count" in de_data:
            assert de_data["transactions_count"] == 7, f"DE should have 7 transactions, got {de_data['transactions_count']}"

    if "US" in jurisdictions:
        us_data = jurisdictions["US"]
        if "transactions_count" in us_data:
            assert us_data["transactions_count"] == 7, f"US should have 7 transactions, got {us_data['transactions_count']}"

    if "JP" in jurisdictions:
        jp_data = jurisdictions["JP"]
        if "transactions_count" in jp_data:
            assert jp_data["transactions_count"] == 6, f"JP should have 6 transactions, got {jp_data['transactions_count']}"



# === Ground-truth assertions (P1) ===

def test_de_tax_total_correct():
    """Ground truth: DE VAT total should be ~€4,523.70"""
    d = json.loads(_find_file("tax_calculations.json").read_text()) if _find_file("tax_calculations.json").exists() else {}
    totals = d.get("totals", d.get("summary", d))
    de_total = totals.get("de_total", totals.get("DE", totals.get("germany", 0)))
    if isinstance(de_total, (int, float)):
        assert 4000 < de_total < 5000, f"DE VAT total {de_total} not in expected range 4000-5000"
    else:
        # Try to find in nested structure
        content = json.dumps(d)
        assert "4523" in content or "4524" in content or "452" in content, "DE VAT ~4523.70 not found"

def test_jp_tax_total_correct():
    """Ground truth: JP consumption tax total should be ~¥89,100"""
    d = json.loads(_find_file("tax_calculations.json").read_text()) if _find_file("tax_calculations.json").exists() else {}
    content = json.dumps(d)
    assert "89100" in content or "89,100" in content or "8910" in content, "JP tax ¥89,100 not found"

def test_transaction_count():
    """Ground truth: 20 transactions total (7 DE + 7 US + 6 JP)"""
    d = json.loads(_find_file("tax_calculations.json").read_text()) if _find_file("tax_calculations.json").exists() else {}
    content = json.dumps(d)
    assert "20" in content or len(d.get("transactions", d.get("details", []))) >= 15, "Should process 20 transactions"

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
