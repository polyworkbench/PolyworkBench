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


def test_pricing_strategy_ar_exists():
    path = _find_file("pricing_strategy_ar.md")
    assert path.exists(), "pricing_strategy_ar.md not found"
    content = path.read_text(encoding="utf-8")
    assert len(content) > 500, "Report too short"
    # Should be in Arabic (check for Arabic characters)
    arabic_chars = sum(1 for c in content if '؀' <= c <= 'ۿ')
    assert arabic_chars > 100, f"Report does not appear to be in Arabic (only {arabic_chars} Arabic characters)"


def test_executive_summary_en_exists():
    path = _find_file("executive_summary_en.md")
    assert path.exists(), "executive_summary_en.md not found"
    content = path.read_text(encoding="utf-8")
    assert len(content) > 300, "Executive summary too short"
    # Should be in English
    assert "pricing" in content.lower() or "price" in content.lower() or "margin" in content.lower(), \
        "Executive summary does not appear to discuss pricing"


def test_pricing_matrix_json_exists():
    path = _find_file("pricing_matrix.json")
    assert path.exists(), "pricing_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "pricing_matrix.json must be a JSON object"


def test_product_a_prices():
    path = _find_file("pricing_matrix.json")
    assert path.exists(), "pricing_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Product A: MENA=$129, China=¥899, US=$149
    assert "129" in all_text, "Product A MENA price $129 not found"
    assert "899" in all_text, "Product A China price ¥899 not found"
    assert "149" in all_text, "Product A US price $149 not found"


def test_product_b_prices():
    path = _find_file("pricing_matrix.json")
    assert path.exists(), "pricing_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Product B: MENA=$249, China=¥1699, US=$299
    assert "249" in all_text, "Product B MENA price $249 not found"
    assert "1699" in all_text, "Product B China price ¥1699 not found"
    assert "299" in all_text, "Product B US price $299 not found"


def test_product_c_prices():
    path = _find_file("pricing_matrix.json")
    assert path.exists(), "pricing_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Product C: MENA=$79, China=¥549, US=$89
    assert "549" in all_text, "Product C China price ¥549 not found"


def test_margins():
    path = _find_file("pricing_matrix.json")
    assert path.exists(), "pricing_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # Margins: MENA=45%, China=35%, US=50%
    assert "0.45" in all_text or "45" in all_text, "MENA margin 45% not found"
    assert "0.35" in all_text or "35" in all_text, "China margin 35% not found"
    assert "0.50" in all_text or "0.5" in all_text or "50" in all_text, "US margin 50% not found"


def test_tam():
    path = _find_file("pricing_matrix.json")
    assert path.exists(), "pricing_matrix.json not found"
    data = json.loads(path.read_text(encoding="utf-8"))
    all_text = json.dumps(data)

    # TAM = $12.7M = 12700000
    assert "12700000" in all_text or "12.7" in all_text or "12,700,000" in all_text, \
        "TAM of $12.7M not found in pricing matrix"



# === Ground-truth assertions (P1) ===

def test_product_a_mena_price():
    """Ground truth: Product A MENA price ~$129"""
    d = json.loads(_find_file("pricing_matrix.json").read_text()) if _find_file("pricing_matrix.json").exists() else {}
    content = json.dumps(d)
    assert "129" in content, "Product A MENA price $129 not found"

def test_margin_targets():
    """Ground truth: MENA=45%, China=35%, US=50%"""
    d = json.loads(_find_file("pricing_matrix.json").read_text()) if _find_file("pricing_matrix.json").exists() else {}
    content = json.dumps(d)
    assert any(x in content for x in ["45", "0.45"]), "MENA margin 45% not found"
    assert any(x in content for x in ["35", "0.35"]), "China margin 35% not found"

def test_tam_value():
    """Ground truth: TAM = $12.7M"""
    d = json.loads(_find_file("pricing_matrix.json").read_text()) if _find_file("pricing_matrix.json").exists() else {}
    content = json.dumps(d)
    assert any(x in content for x in ["12.7", "12,700,000", "12700000"]), "TAM $12.7M not found"

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
