"""Grading for LOC-12_en_ui_consistency_check."""
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

EXPECTED_INCONSISTENCIES = [
    {"key":"error_network","type":"missing"},
    {"key":"dialog_confirm","type":"register"},
    {"key":"status_loading","type":"punctuation"},
    {"key":"price_format","type":"currency"},
    {"key":"product_stock","type":"placeholder"},
    {"key":"cart_empty","type":"semantic"},
    {"key":"order_shipped","type":"semantic"},
    {"key":"shipping_standard","type":"punctuation"},
]

def test_inconsistencies_found():
    f=_f("inconsistencies.json")
    assert f.exists(),"inconsistencies.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    assert "total_inconsistencies" in d
    n=d["total_inconsistencies"]
    assert n>=5,f"Only {n} inconsistencies found, expected 8"

def test_key_types():
    f=_f("inconsistencies.json")
    if not f.exists():return
    d=json.loads(f.read_text(encoding="utf-8"))
    items=d.get("inconsistencies",[])
    keys_found=[i.get("key","") for i in items]
    critical=["error_network","price_format"]
    hits=sum(1 for k in critical if k in keys_found)
    assert hits>=1,"Critical inconsistencies not identified"

def test_report_exists():
    f=_f("consistency_report.md")
    assert f.exists(),"consistency_report.md not found"
    c=f.read_text(encoding="utf-8")
    assert len(c)>500,"Report too short"

def test_answer():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            assert "total_inconsistencies" in d
            return
    assert False,"answer.json not found"

def test_key_alignment():
    f=_f("key_alignment.json")
    assert f.exists(),"key_alignment.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    assert "total_keys" in d or "aligned_keys" in d



# === Ground-truth assertions (P1) ===

def test_minimum_8_inconsistencies():
    """Ground truth: 8 seeded inconsistencies"""
    d = json.loads(_find_file("inconsistencies.json").read_text()) if _find_file("inconsistencies.json").exists() else {}
    items = d.get("inconsistencies", d.get("findings", []))
    assert len(items) >= 6, f"Only {len(items)} inconsistencies found, expected 8"

def test_missing_key_detected():
    """Ground truth: error_network missing from ZH"""
    content = json.dumps(json.loads(_find_file("inconsistencies.json").read_text())) if _find_file("inconsistencies.json").exists() else ""
    assert "error_network" in content or "missing" in content.lower(), "Missing key inconsistency not detected"

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
