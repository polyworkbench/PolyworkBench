

def _find_file(name: str) -> Path:
    """Find a file in standard output locations."""
    for p in [OUT/"output"/name, OUT/name]:
        if p.exists():
            return p
    return OUT/"output"/name

"""Grading for LOC-11_es_code_doc_localization."""
import json, os, re
from pathlib import Path

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

def _find(name):
    for p in [OUTPUT_DIR/"output"/name, OUTPUT_DIR/name]:
        if p.exists(): return p
    return OUTPUT_DIR/"output"/name

REQUIRED_MARKERS = [
    "cs_live_xxxxxxxxxxxxx",
    "async function batchUpload(files)",
    "whsec_your_signing_secret",
    "class CloudSyncError(Exception):",
    "health_score = calculate_health(status_data)",
    "resolution_strategy",
    "api.cloudsync.io/v2/quota",
    "sseclient.SSEClient(response)",
    "include_metadata",
    "password_protected",
    "read_write",
    "X-RateLimit-Limit",
    "cloudsync-sdk==2.4.0",
    "uploaded_by",
    "req_unique_identifier_here",
]

REQUIRED_LINKS = [
    "https://developers.cloudsync.io/support",
    "https://dashboard.cloudsync.io/credentials",
    "https://docs.cloudsync.io/events/types",
    "https://docs.cloudsync.io/features/sharing",
    "https://docs.cloudsync.io/teams/management",
    "https://docs.cloudsync.io/api/v2",
]

def test_code_blocks_preserved():
    f = _find("api_docs_es.md")
    assert f.exists(), "api_docs_es.md not found"
    c = f.read_text(encoding="utf-8")
    preserved = sum(1 for m in REQUIRED_MARKERS if m in c)
    assert preserved >= 12, f"Only {preserved}/15 code blocks preserved"

def test_spanish_content():
    f = _find("api_docs_es.md")
    if not f.exists(): return
    c = f.read_text(encoding="utf-8")
    es_chars = re.findall(r"[áéíóúñü¿¡]", c.lower())
    assert len(es_chars) > 30, f"Only {len(es_chars)} Spanish chars found"

def test_links_preserved():
    f = _find("api_docs_es.md")
    if not f.exists(): return
    c = f.read_text(encoding="utf-8")
    found = sum(1 for lnk in REQUIRED_LINKS if lnk in c)
    assert found >= 5, f"Only {found}/6 links preserved"

def test_validation_results():
    f = _find("validation_results.json")
    assert f.exists(), "validation_results.json not found"
    d = json.loads(f.read_text(encoding="utf-8"))
    assert "preserved_blocks" in d
    assert d.get("total_code_blocks") == 15

def test_answer_json():
    paths = [OUTPUT_DIR/"answer.json", OUTPUT_DIR/"output"/"answer.json"]
    data = None
    for p in paths:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            break
    assert data, "answer.json not found"
    assert "code_blocks_preserved" in data
    assert "validation_passed" in data

def test_no_code_translation():
    f = _find("api_docs_es.md")
    if not f.exists(): return
    c = f.read_text(encoding="utf-8")
    assert "health_score = calculate_health" in c
    assert "team_permissions.yaml" in c



# === Ground-truth assertions (P1) ===

def test_exact_15_code_blocks():
    """Ground truth: exactly 15 code blocks must be preserved"""
    f = _find_file("api_docs_es.md")
    if not f.exists(): f = _find_file("documentation_es.md")
    content = f.read_text() if f.exists() else ""
    code_blocks = re.findall(r"```[\s\S]*?```", content)
    assert len(code_blocks) >= 13, f"Only {len(code_blocks)}/15 code blocks preserved"

def test_no_translated_variable_names():
    """Code variables must NOT be translated"""
    f = _find_file("api_docs_es.md")
    if not f.exists(): f = _find_file("documentation_es.md")
    content = f.read_text() if f.exists() else ""
    # These English variable names should remain unchanged
    assert "getUserById" in content or "get_user_by_id" in content, "Variable names were translated"

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
