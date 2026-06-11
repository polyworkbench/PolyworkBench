"""Grading for LOC-04v2."""
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

def test_japanese_doc():
    f=_f("api_docs_ja.md")
    assert f.exists(),"api_docs_ja.md not found"
    c=f.read_text(encoding="utf-8")
    ja=re.findall(r"[぀-ゟ゠-ヿ一-鿿]",c)
    assert len(ja)>100,f"Only {len(ja)} Japanese chars"

def test_code_preserved():
    f=_f("api_docs_ja.md")
    if not f.exists():return
    c=f.read_text(encoding="utf-8")
    markers=["Client(api_key","TokenManager","FilterProcessor","StreamError","MetricsCollector","RateLimiter","BatchProcessor","metrics-processor"]
    found=sum(1 for m in markers if m in c)
    assert found>=6,f"Only {found}/8 code blocks preserved"

def test_glossary():
    f=_f("glossary_applied.json")
    assert f.exists(),"glossary_applied.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    terms=d.get("terms_applied",[])
    assert len(terms)>=15,f"Only {len(terms)} terms applied"

def test_links():
    f=_f("link_validation.json")
    assert f.exists(),"link_validation.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    assert d.get("total_links",0)>=5

def test_answer():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            assert d.get("code_blocks_preserved",0)>=6
            assert d.get("glossary_terms_applied",0)>=15
            return
    assert False,"answer.json not found"



# === Ground-truth assertions (P1) ===

def test_glossary_consistency():
    """Must use glossary terms consistently"""
    f = _find_file("translated_docs_ja.md")
    if not f.exists(): f = _find_file("documentation_ja.md")
    content = f.read_text() if f.exists() else ""
    assert len(content) > 500, "Translation too short"
    # Japanese content should be present
    ja_chars = len(re.findall(r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]", content))
    assert ja_chars > 50, f"Only {ja_chars} Japanese characters, expected more"

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
