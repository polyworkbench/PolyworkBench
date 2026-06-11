"""Grading for MFG-11_ko_root_cause_analysis."""
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

def test_timeline():
    f=_f("timeline.json")
    assert f.exists(),"timeline.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    events=d.get("events",d.get("timeline",[]))
    assert len(events)>=4,"Too few events in timeline"

def test_root_cause():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            rc=d.get("root_cause","").lower()
            assert "bearing" in rc or "베어링" in rc,"Root cause should be bearing"
            sid=d.get("sensor_id","")
            assert sid=="T-07","Wrong sensor ID: "+str(sid)
            return
    assert False,"answer.json not found"

def test_temperature():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            t=d.get("peak_temperature",0)
            assert 80<=t<=85,"Peak temp not in range 80-85"
            return

def test_korean_report():
    f=_f("root_cause_report_ko.md")
    assert f.exists(),"root_cause_report_ko.md not found"
    c=f.read_text(encoding="utf-8")
    ko=re.findall(r"[가-힣]",c)
    assert len(ko)>50,"Too few Korean characters"

def test_stoppage_time():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            st=d.get("stoppage_time","")
            assert "14:32" in st,"Stoppage time should contain 14:32"
            return



# === Ground-truth assertions (P1) ===

def test_root_cause_sensor_t07():
    """Ground truth: root cause is sensor T-07 temperature spike"""
    f = _find_file("root_cause_report.md")
    if not f.exists(): f = _find_file("analysis_report_ko.md")
    if not f.exists(): f = _find_file("report.md")
    content = f.read_text() if f.exists() else ""
    assert "T-07" in content or "T07" in content, "Root cause sensor T-07 not identified"

def test_timeline_14_23():
    """Ground truth: initial anomaly at 14:23"""
    f = _find_file("timeline.json")
    if not f.exists(): f = _find_file("root_cause_report.md")
    content = f.read_text() if f.exists() else ""
    assert "14:23" in content or "1423" in content, "Timeline start 14:23 not found"

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
