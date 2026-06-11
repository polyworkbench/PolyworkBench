"""Grading for LOC-05v2."""
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

MANDATORY_TERMS=["Conditions Générales","Politique de Confidentialité","Données Personnelles","Responsable du traitement","Consentement","Traitement"]

def test_three_documents():
    for name in ["cgu_fr.md","privacy_policy_fr.md","cookie_policy_fr.md"]:
        f=_f(name)
        assert f.exists(),f"{name} not found"
        c=f.read_text(encoding="utf-8")
        assert len(c)>300,f"{name} too short"

def test_glossary_compliance():
    f=_f("glossary_compliance.json")
    assert f.exists(),"glossary_compliance.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    assert d.get("correctly_applied",0)>=15

def test_french_content():
    f=_f("cgu_fr.md")
    if not f.exists():return
    c=f.read_text(encoding="utf-8")
    fr_markers=["à","é","è","ê","ô","û","ç"]
    found=sum(c.count(m) for m in fr_markers)
    assert found>20,f"Only {found} French accent chars"

def test_cross_references():
    f=_f("cross_reference_validation.json")
    assert f.exists(),"cross_reference_validation.json not found"
    d=json.loads(f.read_text(encoding="utf-8"))
    assert d.get("valid",0)>=3

def test_mandatory_terms_in_docs():
    all_content=""
    for name in ["cgu_fr.md","privacy_policy_fr.md","cookie_policy_fr.md"]:
        f=_f(name)
        if f.exists():all_content+=f.read_text(encoding="utf-8")
    found=sum(1 for t in MANDATORY_TERMS if t in all_content)
    assert found>=4,f"Only {found} mandatory terms found in docs"

def test_answer():
    for p in [OUT/"answer.json",OUT/"output"/"answer.json"]:
        if p.exists():
            d=json.loads(p.read_text(encoding="utf-8"))
            assert d.get("documents_translated",0)==3
            assert d.get("glossary_compliance_percent",0)>=70
            return
    assert False,"answer.json not found"



# === Ground-truth assertions (P1) ===

def test_three_documents_translated():
    """Must produce 3 translated legal documents"""
    found = 0
    for name in ["contract_fr.md", "terms_fr.md", "privacy_fr.md", "document_1_fr.md", "document_2_fr.md", "document_3_fr.md"]:
        if _find_file(name).exists(): found += 1
    assert found >= 2, f"Only {found} French documents found, expected 3"

def test_french_legal_terminology():
    """Must use proper French legal terms"""
    for name in ["contract_fr.md", "terms_fr.md", "document_1_fr.md"]:
        f = _find_file(name)
        if f.exists():
            content = f.read_text()
            legal_terms = ["conformément", "en vertu", "dispositions", "obligations", "responsabilité"]
            found = sum(1 for t in legal_terms if t in content.lower())
            assert found >= 2, f"Only {found} French legal terms found"
            return
    assert False, "No French legal document found"

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
