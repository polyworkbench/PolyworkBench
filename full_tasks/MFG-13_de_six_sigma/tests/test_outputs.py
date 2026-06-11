"""Grading for MFG-13_de_six_sigma."""
import json,os,re
from pathlib import Path

OUT=Path(os.environ.get("OUTPUT_DIR",os.environ.get("WORKSPACE","/workspace")))


def _find_file(name: str) -> Path:
    """Find a file in standard output locations."""
    for p in [OUT/"output"/name, OUT/name]:
        if p.exists():
            return p
    return OUT/"output"/name


def _f(n):
    for p in [OUT/"output"/n,OUT/n]:
        if p.exists():return p
    return OUT/"output"/n

def test_capability_indices():
    f=_f("capability_analysis.json")
    assert f.exists(),"capability_analysis.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    cp=d.get("cp",0)
    cpk=d.get("cpk",0)
    assert 0.9<=cp<=1.3,f"Cp={cp}, expected ~1.111"
    assert 0.6<=cpk<=1.1,f"Cpk={cpk}, expected ~0.844"

def test_answer():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            assert "cp" in d and "cpk" in d
            assert 0.9<=d["cp"]<=1.3
            assert 0.6<=d["cpk"]<=1.1
            assert d.get("assignable_causes",0)>=2
            return
    assert False,"answer.json not found"

def test_german_report():
    f=_f("dmaic_report_de.md")
    assert f.exists(),"dmaic_report_de.md not found"
    c=f.read_text(encoding="utf-8")
    assert len(c)>500
    de_words=["Prozess","Messung","Mittelwert","Standardabweichung","Verbesserung"]
    found=sum(1 for w in de_words if w.lower() in c.lower())
    assert found>=3,f"Only {found} German terms found"

def test_assignable_causes():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            assert d.get("assignable_causes",0)>=2,"Expected at least 2 assignable causes"
            return

def test_control_chart():
    f=_f("control_chart_data.json")
    assert f.exists(),"control_chart_data.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    assert "ucl" in d or "UCL" in d
    assert "lcl" in d or "LCL" in d



# === Ground-truth assertions (P1) ===

def test_cp_value():
    """Ground truth: Cp = (10.05-9.95)/(6*0.015) = 1.111"""
    d = json.loads(_find_file("capability_analysis.json").read_text()) if _find_file("capability_analysis.json").exists() else json.loads(_find_file("six_sigma_results.json").read_text()) if _find_file("six_sigma_results.json").exists() else {}
    content = json.dumps(d)
    # Cp should be approximately 1.11
    assert any(x in content for x in ["1.11", "1.10", "1.12"]), f"Cp ~1.111 not found in output"

def test_cpk_value():
    """Ground truth: Cpk = min(0.844, 1.378) = 0.844"""
    d = json.loads(_find_file("capability_analysis.json").read_text()) if _find_file("capability_analysis.json").exists() else json.loads(_find_file("six_sigma_results.json").read_text()) if _find_file("six_sigma_results.json").exists() else {}
    content = json.dumps(d)
    assert any(x in content for x in ["0.84", "0.85", "0.83"]), f"Cpk ~0.844 not found"

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
