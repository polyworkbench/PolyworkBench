"""Grading for MFG-01v2."""
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

def test_verification():
    f=_f("verification_results.json")
    assert f.exists(),"verification_results.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    assert "match" in d or "script_output" in d

def test_maintenance_correlation():
    f=_f("maintenance_correlation.json")
    assert f.exists(),"maintenance_correlation.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    corr=d.get("correlations",[])
    assert len(corr)>=2,f"Only {len(corr)} correlations found"

def test_answer():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            assert "total_output" in d
            assert "verification_passed" in d
            assert "maintenance_events" in d
            assert d.get("maintenance_events",0)>=2
            return
    assert False,"answer.json not found"

def test_vietnamese_report():
    f=_f("production_report_vi.md")
    assert f.exists()
    c=f.read_text(encoding="utf-8")
    vi=re.findall(r"[à-ưẠ-ỹ]",c)
    assert len(vi)>30,f"Only {len(vi)} Vietnamese chars"

def test_yield():
    f=_f("yield_analysis.json")
    assert f.exists()
    d=json.loads(f.read_text(encoding="utf-8"))
    assert "overall" in d or "by_line" in d



# === Ground-truth assertions (P1) ===

def test_yield_in_range():
    """Ground truth: overall yield should be 95-99%"""
    d = json.loads(_find_file("yield_analysis.json").read_text()) if _find_file("yield_analysis.json").exists() else {}
    overall = d.get("overall", d.get("overall_yield", 0))
    if isinstance(overall, (int, float)):
        if overall > 1: overall = overall / 100  # handle percentage vs ratio
        assert 0.90 <= overall <= 1.0, f"Yield {overall} outside expected range 90-100%"

def test_total_output_range():
    """Ground truth: total output ~40,000-42,500"""
    ans = json.loads(Path(_find_file("../answer.json")).read_text()) if Path(_find_file("../answer.json")).exists() else {}
    if not ans:
        ans = json.loads(_find_file("answer.json").read_text()) if _find_file("answer.json").exists() else {}
    total = ans.get("total_output", 0)
    assert 35000 <= total <= 50000, f"Total output {total} outside range"

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
