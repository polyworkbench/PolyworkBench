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


def test_decision_report_exists():
    path = _find_file("decision_report.md")
    assert path.exists(), "decision_report.md not found"
    content = path.read_text(encoding="utf-8")
    assert len(content) > 800, "Report too short"
    # Should contain key supplier references
    assert "SKR-7" in content or "skr-7" in content.lower(), "SKR-7 supplier not mentioned"
    assert "SZH-3" in content or "szh-3" in content.lower(), "SZH-3 supplier not mentioned"
    assert "SEN-2" in content or "sen-2" in content.lower(), "SEN-2 supplier not mentioned"


def test_decision_report_financial_risk():
    path = _find_file("decision_report.md")
    assert path.exists(), "decision_report.md not found"
    content = path.read_text(encoding="utf-8")
    # Should mention total risk of $2.4M
    assert "2.4" in content or "2,400,000" in content or "2400000" in content, \
        "Total risk exposure $2.4M not mentioned in report"


def test_action_plan_json():
    path = _find_file("action_plan.json")
    assert path.exists(), "action_plan.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))

    # Should have immediate actions
    actions = data.get("immediate_actions", data.get("actions", []))
    assert len(actions) >= 3, f"Expected at least 3 actions, found {len(actions)}"

    # Check that actions reference the suppliers
    all_text = json.dumps(data).upper()
    assert "SKR-7" in all_text or "SKR" in all_text, "SKR-7 not in action plan"
    assert "SZH-3" in all_text or "SZH" in all_text, "SZH-3 not in action plan"
    assert "SEN-2" in all_text or "SEN" in all_text, "SEN-2 not in action plan"


def test_risk_matrix_json():
    path = _find_file("risk_matrix.json")
    assert path.exists(), "risk_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))

    # Should have critical suppliers
    suppliers = data.get("critical_suppliers", data.get("suppliers", []))
    assert len(suppliers) >= 3, f"Expected at least 3 critical suppliers, found {len(suppliers)}"


def test_risk_scores():
    path = _find_file("risk_matrix.json")
    assert path.exists(), "risk_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Check risk scores
    assert "92" in all_text, "SKR-7 risk score 92 not found"
    assert "87" in all_text, "SZH-3 risk score 87 not found"
    assert "78" in all_text, "SEN-2 risk score 78 not found"


def test_total_financial_exposure():
    path = _find_file("risk_matrix.json")
    assert path.exists(), "risk_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Total exposure should be $2.4M = 2400000
    assert "2400000" in all_text or "2.4" in all_text, \
        "Total financial exposure $2.4M not found in risk matrix"


def test_supplier_financial_breakdown():
    path = _find_file("risk_matrix.json")
    assert path.exists(), "risk_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Individual exposures
    assert "1100000" in all_text or "1,100,000" in all_text, \
        "SKR-7 exposure $1,100,000 not found"
    assert "850000" in all_text or "850,000" in all_text, \
        "SZH-3 exposure $850,000 not found"
    assert "450000" in all_text or "450,000" in all_text, \
        "SEN-2 exposure $450,000 not found"



# === Ground-truth assertions (P1) ===

def test_critical_suppliers_identified():
    """Ground truth: SKR-7, SZH-3, SEN-2 are the 3 critical suppliers"""
    d = json.loads(_find_file("risk_matrix.json").read_text()) if _find_file("risk_matrix.json").exists() else {}
    content = json.dumps(d).upper()
    assert "SKR-7" in content, "Critical supplier SKR-7 not identified"
    assert "SZH-3" in content, "Critical supplier SZH-3 not identified"

def test_risk_cost_estimate():
    """Ground truth: Total disruption cost ~$2.4M"""
    d = json.loads(_find_file("action_plan.json").read_text()) if _find_file("action_plan.json").exists() else {}
    content = json.dumps(d)
    assert any(x in content for x in ["2.4", "2,400,000", "2400000", "2.4M"]), "Disruption cost $2.4M not found"

def test_three_suppliers_in_report():
    """All 3 critical suppliers must appear in decision report"""
    f = _find_file("decision_report.md")
    content = f.read_text() if f.exists() else ""
    assert "SKR-7" in content and "SZH-3" in content, "Report missing critical suppliers"

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
