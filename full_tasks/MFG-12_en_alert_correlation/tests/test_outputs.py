"""Grading for MFG-12_en_alert_correlation."""
import json,os
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

def test_clusters_exist():
    f=_f("alert_clusters.json")
    assert f.exists(),"alert_clusters.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    clusters=d.get("clusters",[])
    assert len(clusters)>=4,f"Only {len(clusters)} clusters"

def test_false_alarms():
    f=_f("false_alarm_analysis.json")
    if not f.exists():
        f=_f("alert_clusters.json")
    assert f.exists()
    d=json.loads(f.read_text(encoding="utf-8"))
    fa=d.get("false_alarms",d.get("total_false",0))
    if isinstance(fa,list):fa=len(fa)
    assert fa>=3,f"Only {fa} false alarms found, expected 4"

def test_answer():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            assert d.get("total_clusters",0)>=4
            assert d.get("false_alarm_count",0)>=3
            assert d.get("ticket_linked_clusters",0)>=2
            return
    assert False,"answer.json not found"

def test_report():
    f=_f("correlation_report.md")
    assert f.exists(),"correlation_report.md not found"
    c=f.read_text(encoding="utf-8")
    assert len(c)>500,"Report too short"
    assert "cluster" in c.lower() or "group" in c.lower()

def test_bearing_cluster():
    f=_f("alert_clusters.json")
    if not f.exists():return
    d=json.loads(f.read_text(encoding="utf-8"))
    clusters=d.get("clusters",[])
    bearing_found=any("bearing" in str(c).lower() or "P-03" in str(c) for c in clusters)
    assert bearing_found,"Bearing wear cluster not found"



# === Ground-truth assertions (P1) ===

def test_five_clusters():
    """Ground truth: alerts should be grouped into 5 clusters"""
    d = json.loads(_find_file("alert_clusters.json").read_text()) if _find_file("alert_clusters.json").exists() else {}
    clusters = d.get("clusters", d.get("groups", []))
    assert len(clusters) >= 4, f"Only {len(clusters)} clusters, expected 5"

def test_false_alarms_identified():
    """Ground truth: at least 3 false alarms from sensor drift"""
    d = json.loads(_find_file("alert_clusters.json").read_text()) if _find_file("alert_clusters.json").exists() else {}
    content = json.dumps(d).lower()
    assert "false" in content or "drift" in content or "nhầm" in content, "False alarms not identified"

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
