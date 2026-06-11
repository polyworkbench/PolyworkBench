"""
WildClawBench-style grading for MFG-08: French CE marking documentation.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _is_french(text: str) -> bool:
    """Check if text contains significant French content."""
    if not text:
        return False
    fr_indicators = ["conformité", "déclaration", "directive", "fabricant",
                     "sécurité", "équipement", "électrique", "harmonisée",
                     "est", "les", "des", "dans", "pour", "une", "cette"]
    text_lower = text.lower()
    hits = sum(1 for w in fr_indicators if w in text_lower)
    return hits >= 3


def _score_declaration_compliance() -> Dict[str, float]:
    """Score the Declaration of Conformity (weight: 0.30)."""
    scores = {}
    decl_path = _find_file("declaration_conformite_fr.md")

    if not decl_path.exists():
        return {"declaration_exists": 0.0, "manufacturer_info": 0.0,
                "directives_listed": 0.0, "standards_listed": 0.0,
                "format_compliance": 0.0, "signature_block": 0.0}

    content = decl_path.read_text(encoding="utf-8-sig")
    content_lower = content.lower()
    scores["declaration_exists"] = 1.0

    # Check manufacturer information
    mfr_keywords = ["greensource", "shenzhen", "深圳", "fabricant", "manufacturer"]
    scores["manufacturer_info"] = 1.0 if sum(1 for k in mfr_keywords if k in content_lower) >= 2 else 0.0

    # Check directives are listed
    directives = ["2014/35", "2014/30", "2011/65"]
    dir_found = sum(1 for d in directives if d in content)
    scores["directives_listed"] = min(1.0, dir_found / 2)

    # Check harmonized standards are referenced
    standards = ["62368", "55032", "55035", "63000", "EN"]
    std_found = sum(1 for s in standards if s in content)
    scores["standards_listed"] = min(1.0, std_found / 3)

    # Check format compliance (proper declaration structure)
    format_keywords = ["responsabilité", "seule responsabilité", "sous la",
                       "déclaration", "conformité"]
    scores["format_compliance"] = 1.0 if sum(1 for k in format_keywords if k in content_lower) >= 2 else 0.0

    # Check signature block
    sig_keywords = ["signature", "date", "lieu", "signataire", "chen", "陈"]
    scores["signature_block"] = 1.0 if sum(1 for k in sig_keywords if k in content_lower) >= 2 else 0.0

    return scores


def _score_french_quality() -> Dict[str, float]:
    """Score French language quality (weight: 0.25)."""
    scores = {}

    decl_path = _find_file("declaration_conformite_fr.md")
    report_path = _find_file("rapport_technique_fr.md")

    # Check declaration is in French
    if decl_path.exists():
        decl_content = decl_path.read_text(encoding="utf-8-sig")
        scores["declaration_french"] = 1.0 if _is_french(decl_content) else 0.0
    else:
        scores["declaration_french"] = 0.0

    # Check technical report is in French
    if report_path.exists():
        report_content = report_path.read_text(encoding="utf-8-sig")
        scores["report_french"] = 1.0 if _is_french(report_content) else 0.0
    else:
        scores["report_french"] = 0.0

    # Check for proper French technical terminology
    if report_path.exists():
        fr_tech_terms = ["essai", "résultat", "conformité", "directive",
                         "norme", "fabricant", "sécurité", "compatibilité",
                         "électromagnétique", "tension", "isolement"]
        content_lower = report_content.lower()
        terms_found = sum(1 for t in fr_tech_terms if t in content_lower)
        scores["technical_terminology"] = min(1.0, terms_found / 5)
    else:
        scores["technical_terminology"] = 0.0

    return scores


def _score_technical_accuracy() -> Dict[str, float]:
    """Score technical accuracy of standards mapping (weight: 0.20)."""
    scores = {}
    summary = None
    summary_path = _find_file("test_summary.json")

    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    if not summary:
        return {"test_summary_exists": 0.0, "mapping_present": 0.0,
                "results_included": 0.0, "pass_fail_status": 0.0}

    scores["test_summary_exists"] = 1.0
    blob = json.dumps(summary, ensure_ascii=False)

    # Check GB→EN standard mapping
    mapping_indicators = ["EN 62368", "EN 55032", "EN 55035", "GB4943", "GB/T9254"]
    mapping_found = sum(1 for m in mapping_indicators if m in blob)
    scores["mapping_present"] = min(1.0, mapping_found / 3)

    # Check test results are included
    result_indicators = ["pass", "合格", "conforme", "result", "résultat"]
    scores["results_included"] = 1.0 if any(r in blob.lower() for r in result_indicators) else 0.0

    # Check pass/fail status for each test
    if isinstance(summary, list):
        scores["pass_fail_status"] = min(1.0, len(summary) / 10)
    elif isinstance(summary, dict):
        items = summary.get("tests", summary.get("results", summary.get("essais", [])))
        if isinstance(items, list):
            scores["pass_fail_status"] = min(1.0, len(items) / 10)
        else:
            scores["pass_fail_status"] = 0.5
    else:
        scores["pass_fail_status"] = 0.0

    return scores


def _score_standards_mapping() -> Dict[str, float]:
    """Score the standards mapping quality (weight: 0.15)."""
    scores = {}
    report_path = _find_file("rapport_technique_fr.md")

    if not report_path.exists():
        return {"report_exists": 0.0, "test_coverage": 0.0, "risk_assessment": 0.0}

    content = report_path.read_text(encoding="utf-8-sig")
    content_lower = content.lower()
    scores["report_exists"] = 1.0

    # Check test coverage (LVD + EMC + RoHS)
    coverage_checks = {
        "lvd": any(k in content_lower for k in ["sécurité", "62368", "basse tension", "lvd"]),
        "emc": any(k in content_lower for k in ["électromagnétique", "emc", "55032", "55035", "cem"]),
        "rohs": any(k in content_lower for k in ["rohs", "substance", "dangereuse", "63000"])
    }
    scores["test_coverage"] = sum(coverage_checks.values()) / len(coverage_checks)

    # Check for risk assessment
    risk_keywords = ["risque", "évaluation", "analyse", "danger", "risk"]
    scores["risk_assessment"] = 1.0 if any(k in content_lower for k in risk_keywords) else 0.0

    return scores


def _score_completeness() -> Dict[str, float]:
    """Score overall completeness (weight: 0.10)."""
    scores = {}

    checklist = None
    checklist_path = _find_file("checklist_ce.json")
    if checklist_path.exists():
        try:
            checklist = json.loads(checklist_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    if not checklist:
        return {"checklist_exists": 0.0, "items_covered": 0.0, "status_indicated": 0.0}

    scores["checklist_exists"] = 1.0

    blob = json.dumps(checklist, ensure_ascii=False).lower()

    # Check items are covered
    checklist_items = ["lvd", "emc", "rohs", "documentation", "marquage", "marking"]
    items_found = sum(1 for i in checklist_items if i in blob)
    scores["items_covered"] = min(1.0, items_found / 3)

    # Check status indicators
    status_keywords = ["conforme", "non conforme", "non applicable", "pass", "fail", "n/a",
                       "compliant", "non-compliant"]
    scores["status_indicated"] = 1.0 if any(s in blob for s in status_keywords) else 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for MFG-08."""
    dimensions = {}

    # Dimension 1: Declaration Compliance (weight: 0.30)
    decl_scores = _score_declaration_compliance()
    dimensions["declaration_compliance"] = {
        "score": sum(decl_scores.values()) / max(len(decl_scores), 1),
        "weight": 0.30,
        "details": decl_scores
    }

    # Dimension 2: French Quality (weight: 0.25)
    french_scores = _score_french_quality()
    dimensions["french_quality"] = {
        "score": sum(french_scores.values()) / max(len(french_scores), 1),
        "weight": 0.25,
        "details": french_scores
    }

    # Dimension 3: Technical Accuracy (weight: 0.20)
    tech_scores = _score_technical_accuracy()
    dimensions["technical_accuracy"] = {
        "score": sum(tech_scores.values()) / max(len(tech_scores), 1),
        "weight": 0.20,
        "details": tech_scores
    }

    # Dimension 4: Standards Mapping (weight: 0.15)
    std_scores = _score_standards_mapping()
    dimensions["standards_mapping"] = {
        "score": sum(std_scores.values()) / max(len(std_scores), 1),
        "weight": 0.15,
        "details": std_scores
    }

    # Dimension 5: Completeness (weight: 0.10)
    comp_scores = _score_completeness()
    dimensions["completeness"] = {
        "score": sum(comp_scores.values()) / max(len(comp_scores), 1),
        "weight": 0.10,
        "details": comp_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"MFG-08 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_declaration_exists_and_french():
    decl_path = _find_file("declaration_conformite_fr.md")
    assert decl_path.exists(), "Declaration of conformity must exist"
    content = decl_path.read_text(encoding="utf-8-sig")
    assert _is_french(content), "Declaration must be in French"


def test_directives_referenced():
    result = grade()
    decl = result["dimensions"].get("declaration_compliance", {})
    details = decl.get("details", {})
    assert details.get("directives_listed", 0) >= 0.66, (
        "At least 2 of 3 directives (LVD, EMC, RoHS) must be referenced"
    )


def test_technical_report_exists():
    report_path = _find_file("rapport_technique_fr.md")
    assert report_path.exists(), "Technical report must exist in French"


def test_test_summary_maps_standards():
    result = grade()
    tech = result["dimensions"].get("technical_accuracy", {})
    details = tech.get("details", {})
    assert details.get("test_summary_exists", 0) == 1.0, (
        "test_summary.json must exist"
    )
    assert details.get("mapping_present", 0) >= 0.5, (
        "Test summary should map Chinese tests to EN standards"
    )


def test_checklist_present():
    checklist_path = _find_file("checklist_ce.json")
    assert checklist_path.exists(), "CE checklist must exist"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["declaration_conformite_fr.md", "rapport_technique_fr.md",
                          "test_summary.json", "checklist_ce.json"]
    # answer.json check
    answer_candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    answer_exists = any(p.exists() for p in answer_candidates)
    assert answer_exists, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify declaration is in French, not English fallback."""
    decl_path = _find_file("declaration_conformite_fr.md")
    if not decl_path.exists():
        return
    content = decl_path.read_text(encoding="utf-8-sig")
    fr_chars = set("àâæçéèêëîïôœùûüÿ")
    fr_count = sum(1 for c in content.lower() if c in fr_chars)
    assert fr_count >= 10, f"Only {fr_count} French accent chars found — likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    decl_path = _find_file("declaration_conformite_fr.md")
    if decl_path.exists():
        content = decl_path.read_text(encoding="utf-8-sig")
        assert len(content) > 500, f"Declaration too short ({len(content)} chars), likely incomplete"
    report_path = _find_file("rapport_technique_fr.md")
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8-sig")
        assert len(content) > 500, f"Technical report too short ({len(content)} chars)"


def test_no_english_fallback():
    """Verify French declaration isn't in English."""
    decl_path = _find_file("declaration_conformite_fr.md")
    if not decl_path.exists():
        return
    text = decl_path.read_text(encoding="utf-8-sig")
    if not text:
        return
    assert _is_french(text), "Declaration doesn't appear to be in French"


def test_ce_declaration_standards():
    """Verify CE declaration references proper EU directives."""
    decl_path = _find_file("declaration_conformite_fr.md")
    if not decl_path.exists():
        return
    content = decl_path.read_text(encoding="utf-8-sig")
    directives = ["2014/35", "2014/30", "2011/65"]
    found = sum(1 for d in directives if d in content)
    assert found >= 1, "CE declaration should reference at least one EU directive"
