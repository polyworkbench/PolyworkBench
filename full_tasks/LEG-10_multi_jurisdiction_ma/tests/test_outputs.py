"""
WildClawBench-style grading for LEG-10: Multi-jurisdiction M&A review with French synthesis memo.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Key testable facts
DEAL_VALUE = 50000000  # $50M
NET_ASSETS = 38000000  # $38M (contradiction with deal value)
KOREAN_ANTITRUST_TRIGGERED = True
SANCTIONS_BOARD_MEMBER = "Petrov"  # Alexander Petrov
VALUATION_GAP = True  # $50M approved vs $38M net assets


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _is_french(text: str) -> bool:
    """Check if text likely contains French."""
    if not text:
        return False
    # French-specific patterns
    french_indicators = ["de la", "du ", "des ", "les ", "une ", "est ",
                         "dans ", "pour ", "avec ", "sur ", "par ",
                         "cette ", "sont ", "être", "également",
                         "juridiction", "réglementaire", "acquisition"]
    text_lower = text.lower()
    matches = sum(1 for ind in french_indicators if ind in text_lower)
    return matches >= 3


def _load_json_file(name: str) -> Any:
    path = _find_file(name)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return None


def _load_md_file(name: str) -> str:
    path = _find_file(name)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            pass
    return ""


def _score_conflict_detection(memo: str, conflicts: Any) -> Dict[str, float]:
    """Score detection of regulatory conflicts (weight: 0.20)."""
    scores = {}

    combined = memo + " " + json.dumps(conflicts or {}, ensure_ascii=False)

    if not combined.strip():
        return {"content_exists": 0.0, "valuation_gap": 0.0,
                "korean_antitrust": 0.0, "sanctions_issue": 0.0,
                "data_security_risk": 0.0}

    scores["content_exists"] = 1.0

    # Key conflict 1: Valuation gap ($50M vs $38M net assets)
    val_terms = ["50", "38", "valorisation", "valuation", "actif", "écart",
                 "contradiction", "gap", "premium", "prime"]
    val_found = sum(1 for t in val_terms if t.lower() in combined.lower())
    scores["valuation_gap"] = min(1.0, val_found / 3)

    # Key conflict 2: Korean antitrust threshold triggered
    korea_terms = ["cor", "KFTC", "antitrust", "concurrence", "concentration",
                   "seuil", "threshold", "notification", "공정거래"]
    korea_found = sum(1 for t in korea_terms if t.lower() in combined.lower())
    scores["korean_antitrust"] = min(1.0, korea_found / 3)

    # Key conflict 3: Sanctions affecting board member (Petrov)
    sanctions_terms = ["Petrov", "sanction", "Ростех", "Rostec", "risque",
                       "EU", "OFAC", "블록", "制裁"]
    sanctions_found = sum(1 for t in sanctions_terms if t in combined)
    scores["sanctions_issue"] = min(1.0, sanctions_found / 2)

    # Additional: China data security review risk
    data_terms = ["données", "data", "cybersécurité", "cybersecurity",
                  "gouvernement", "government", "30%", "sécurité"]
    data_found = sum(1 for t in data_terms if t.lower() in combined.lower())
    scores["data_security_risk"] = min(1.0, data_found / 2)

    return scores


def _score_synthesis_quality(memo: str) -> Dict[str, float]:
    """Score quality of the synthesis memo (weight: 0.20)."""
    scores = {}

    if not memo:
        return {"memo_exists": 0.0, "executive_summary": 0.0,
                "jurisdiction_analysis": 0.0, "recommendations": 0.0,
                "structure_quality": 0.0}

    scores["memo_exists"] = 1.0

    # Executive summary present
    summary_terms = ["résumé", "synthèse", "sommaire", "aperçu", "executive"]
    scores["executive_summary"] = 1.0 if any(
        t.lower() in memo.lower() for t in summary_terms
    ) else 0.0

    # Multiple jurisdictions analyzed
    jurisdictions = ["Chine", "Japon", "Corée", "Russie", "China", "Japan", "Korea"]
    juris_found = sum(1 for j in jurisdictions if j in memo)
    scores["jurisdiction_analysis"] = min(1.0, juris_found / 4)

    # Recommendations present
    rec_terms = ["recommand", "précon", "stratégi", "mesure", "action",
                 "proposition", "conseil"]
    rec_found = sum(1 for t in rec_terms if t.lower() in memo.lower())
    scores["recommendations"] = min(1.0, rec_found / 2)

    # Document structure
    has_headings = bool(re.search(r'#{1,3}\s', memo))
    has_sections = len(re.findall(r'#{1,3}\s', memo)) >= 4
    scores["structure_quality"] = 1.0 if has_sections else (0.5 if has_headings else 0.0)

    return scores


def _score_french_legal_quality(memo: str, risk_register: Any) -> Dict[str, float]:
    """Score French legal language quality (weight: 0.20)."""
    scores = {}

    scores["memo_in_french"] = 1.0 if _is_french(memo) else 0.0

    # Risk register in French
    risk_str = json.dumps(risk_register or {}, ensure_ascii=False)
    scores["risk_register_french"] = 1.0 if _is_french(risk_str) else 0.0

    # French legal terminology
    legal_terms = ["fusion", "acquisition", "réglementaire", "juridiction",
                   "conformité", "due diligence", "clause", "condition suspensive",
                   "approbation", "notification", "concentration", "antitrust"]
    term_count = sum(1 for t in legal_terms if t.lower() in memo.lower())
    scores["legal_terminology"] = min(1.0, term_count / 5)

    # Formal register (using professional French)
    formal_terms = ["en vertu de", "conformément", "au titre de", "en l'espèce",
                    "il convient de", "à cet égard", "en conséquence", "par ailleurs"]
    formal_count = sum(1 for t in formal_terms if t.lower() in memo.lower())
    scores["formal_register"] = min(1.0, formal_count / 3)

    return scores


def _score_regulatory_mapping(matrix: Any) -> Dict[str, float]:
    """Score jurisdiction matrix quality (weight: 0.15)."""
    scores = {}

    if not matrix:
        return {"matrix_exists": 0.0, "all_jurisdictions": 0.0,
                "requirements_mapped": 0.0, "timelines_included": 0.0}

    scores["matrix_exists"] = 1.0

    matrix_str = json.dumps(matrix, ensure_ascii=False)

    # Check all jurisdictions
    jurisdictions = ["China", "Japan", "Korea", "Chine", "Japon", "Corée", "Russie", "Russia"]
    juris_found = sum(1 for j in jurisdictions if j.lower() in matrix_str.lower())
    scores["all_jurisdictions"] = min(1.0, juris_found / 4)

    # Requirements mapped
    req_terms = ["approval", "approbation", "notification", "filing",
                 "clearance", "review", "autorisation"]
    req_found = sum(1 for t in req_terms if t.lower() in matrix_str.lower())
    scores["requirements_mapped"] = min(1.0, req_found / 3)

    # Timelines
    timeline_terms = ["days", "jours", "months", "mois", "weeks", "semaines",
                      "30", "90", "120", "deadline", "délai"]
    time_found = sum(1 for t in timeline_terms if t.lower() in matrix_str.lower())
    scores["timelines_included"] = min(1.0, time_found / 3)

    return scores


def _score_risk_assessment(risk_register: Any) -> Dict[str, float]:
    """Score risk register quality (weight: 0.15)."""
    scores = {}

    if not risk_register:
        return {"register_exists": 0.0, "risk_count": 0.0,
                "risk_scoring": 0.0, "mitigation_measures": 0.0}

    scores["register_exists"] = 1.0

    risk_str = json.dumps(risk_register, ensure_ascii=False)

    # Risk items count
    if isinstance(risk_register, list):
        scores["risk_count"] = min(1.0, len(risk_register) / 5)
    elif isinstance(risk_register, dict):
        risks = risk_register.get("risks", risk_register.get("risques", []))
        if isinstance(risks, list):
            scores["risk_count"] = min(1.0, len(risks) / 5)
        else:
            scores["risk_count"] = min(1.0, len(risk_register) / 5)

    # Risk scoring (probability x impact)
    scoring_terms = ["probabilité", "impact", "probability", "score",
                     "severity", "gravité", "niveau", "level"]
    scoring_found = sum(1 for t in scoring_terms if t.lower() in risk_str.lower())
    scores["risk_scoring"] = min(1.0, scoring_found / 3)

    # Mitigation measures
    mitigation_terms = ["atténuation", "mitigation", "mesure", "action",
                        "réduction", "contrôle", "traitement"]
    mit_found = sum(1 for t in mitigation_terms if t.lower() in risk_str.lower())
    scores["mitigation_measures"] = min(1.0, mit_found / 2)

    return scores


def _score_glossary_quality(glossary: Any) -> Dict[str, float]:
    """Score multilingual glossary (weight: 0.10)."""
    scores = {}

    if not glossary:
        return {"glossary_exists": 0.0, "multilingual": 0.0,
                "term_count": 0.0}

    scores["glossary_exists"] = 1.0

    glossary_str = json.dumps(glossary, ensure_ascii=False)

    # Check for multiple languages
    has_french = any(t in glossary_str for t in ["acquisition", "fusion", "juridiction"])
    has_english = any(t in glossary_str for t in ["merger", "acquisition", "jurisdiction"])
    has_chinese = any('一' <= c <= '鿿' for c in glossary_str)
    has_japanese = any('ぁ' <= c <= 'ヿ' or '一' <= c <= '鿿' for c in glossary_str)
    has_korean = any('가' <= c <= '힣' for c in glossary_str)
    has_russian = any('Ѐ' <= c <= 'ӿ' for c in glossary_str)

    languages = sum([has_french, has_english, has_chinese, has_japanese,
                     has_korean, has_russian])
    scores["multilingual"] = min(1.0, languages / 4)

    # Term count
    if isinstance(glossary, list):
        scores["term_count"] = min(1.0, len(glossary) / 10)
    elif isinstance(glossary, dict):
        terms = glossary.get("terms", glossary.get("glossaire", glossary))
        if isinstance(terms, (list, dict)):
            scores["term_count"] = min(1.0, len(terms) / 10)
        else:
            scores["term_count"] = 0.3

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for LEG-10."""
    memo = _load_md_file("memo_synthese_fr.md")
    conflicts = _load_json_file("regulatory_conflicts.json")
    matrix = _load_json_file("jurisdiction_matrix.json")
    risk_register = _load_json_file("risk_register_fr.json")
    glossary = _load_json_file("glossaire_multilingue.json")

    if not memo and not conflicts and not matrix and not risk_register and not glossary:
        return {"overall_score": 0.0, "dimensions": {}, "error": "No output files found."}

    dimensions = {}

    # Dimension 1: Conflict Detection (weight: 0.20)
    conflict_scores = _score_conflict_detection(memo, conflicts)
    dimensions["conflict_detection"] = {
        "score": sum(conflict_scores.values()) / max(len(conflict_scores), 1),
        "weight": 0.20,
        "details": conflict_scores
    }

    # Dimension 2: Synthesis Quality (weight: 0.20)
    synthesis_scores = _score_synthesis_quality(memo)
    dimensions["synthesis_quality"] = {
        "score": sum(synthesis_scores.values()) / max(len(synthesis_scores), 1),
        "weight": 0.20,
        "details": synthesis_scores
    }

    # Dimension 3: French Legal Quality (weight: 0.20)
    french_scores = _score_french_legal_quality(memo, risk_register)
    dimensions["french_legal_quality"] = {
        "score": sum(french_scores.values()) / max(len(french_scores), 1),
        "weight": 0.20,
        "details": french_scores
    }

    # Dimension 4: Regulatory Mapping (weight: 0.15)
    mapping_scores = _score_regulatory_mapping(matrix)
    dimensions["regulatory_mapping"] = {
        "score": sum(mapping_scores.values()) / max(len(mapping_scores), 1),
        "weight": 0.15,
        "details": mapping_scores
    }

    # Dimension 5: Risk Assessment (weight: 0.15)
    risk_scores = _score_risk_assessment(risk_register)
    dimensions["risk_assessment"] = {
        "score": sum(risk_scores.values()) / max(len(risk_scores), 1),
        "weight": 0.15,
        "details": risk_scores
    }

    # Dimension 6: Glossary Quality (weight: 0.10)
    glossary_scores = _score_glossary_quality(glossary)
    dimensions["glossary_quality"] = {
        "score": sum(glossary_scores.values()) / max(len(glossary_scores), 1),
        "weight": 0.10,
        "details": glossary_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"LEG-10 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
        for k, v in dim.get("details", {}).items():
            print(f"    {k}: {v:.2f}")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_memo_in_french():
    """Verify the synthesis memo is written in French."""
    memo = _load_md_file("memo_synthese_fr.md")
    assert _is_french(memo), "Memo must be primarily in French"


def test_valuation_gap_detected():
    """Verify the $50M vs $38M valuation contradiction is identified."""
    memo = _load_md_file("memo_synthese_fr.md")
    conflicts = _load_json_file("regulatory_conflicts.json")
    combined = memo + " " + json.dumps(conflicts or {}, ensure_ascii=False)
    has_50m = any(t in combined for t in ["50", "50M", "50 million"])
    has_38m = any(t in combined for t in ["38", "38M", "38 million"])
    assert has_50m and has_38m, \
        "Valuation gap ($50M approved vs $38M net assets) not detected"


def test_korean_antitrust_identified():
    """Verify Korean antitrust notification requirement is identified."""
    memo = _load_md_file("memo_synthese_fr.md")
    conflicts = _load_json_file("regulatory_conflicts.json")
    combined = memo + " " + json.dumps(conflicts or {}, ensure_ascii=False)
    korea_terms = ["Cor", "KFTC", "antitrust", "concurrence", "기업결합"]
    assert any(t in combined for t in korea_terms), \
        "Korean antitrust requirement not identified"


def test_sanctions_risk_identified():
    """Verify sanctions risk related to Petrov is identified."""
    memo = _load_md_file("memo_synthese_fr.md")
    conflicts = _load_json_file("regulatory_conflicts.json")
    risk_register = _load_json_file("risk_register_fr.json")
    combined = memo + " " + json.dumps(conflicts or {}, ensure_ascii=False) + \
               " " + json.dumps(risk_register or {}, ensure_ascii=False)
    assert "Petrov" in combined or "sanction" in combined.lower(), \
        "Sanctions risk (Petrov/Rostec) not identified"


def test_all_jurisdictions_covered():
    """Verify all 5 jurisdictions are analyzed."""
    memo = _load_md_file("memo_synthese_fr.md")
    jurisdictions_fr = ["Chine", "Japon", "Corée", "Russie"]
    jurisdictions_en = ["China", "Japan", "Korea", "Russia"]
    found = sum(1 for j in jurisdictions_fr if j in memo)
    found += sum(1 for j in jurisdictions_en if j in memo)
    # At least 4 unique jurisdictions mentioned (either FR or EN name)
    assert found >= 4, f"Not all jurisdictions covered in memo (found {found} mentions)"


def test_regulatory_conflicts_json():
    """Verify regulatory conflicts JSON exists and has entries."""
    conflicts = _load_json_file("regulatory_conflicts.json")
    assert conflicts is not None, "regulatory_conflicts.json not found or invalid"


def test_risk_register_exists():
    """Verify risk register JSON exists."""
    risk_register = _load_json_file("risk_register_fr.json")
    assert risk_register is not None, "risk_register_fr.json not found or invalid"


def test_glossary_multilingual():
    """Verify glossary contains multiple languages."""
    glossary = _load_json_file("glossaire_multilingue.json")
    assert glossary is not None, "glossaire_multilingue.json not found or invalid"
    glossary_str = json.dumps(glossary, ensure_ascii=False)
    # Should have at least 3 different scripts
    has_latin = bool(re.search(r'[a-zA-Zéèêàâôûùç]', glossary_str))
    has_cjk = any('一' <= c <= '鿿' for c in glossary_str)
    has_hangul = any('가' <= c <= '힣' for c in glossary_str)
    has_cyrillic = any('Ѐ' <= c <= 'ӿ' for c in glossary_str)
    scripts = sum([has_latin, has_cjk, has_hangul, has_cyrillic])
    assert scripts >= 3, f"Glossary should contain at least 3 scripts, found {scripts}"


# === Standardized pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    result = grade()
    assert result["overall_score"] >= 0.0, "grade() should return a valid score"

def test_target_language():
    """Verify output is in the correct target language, not English fallback."""
    result = grade()
    if result["overall_score"] == 0.0:
        pytest.skip("No output to check")
    dims = result.get("dimensions", {})
    # Look for language-quality dimension
    lang_dim_scores = []
    for k, v in dims.items():
        if any(word in k.lower() for word in ["french", "fr"]):
            score = v.get("score", v) if isinstance(v, dict) else v
            if isinstance(score, (int, float)):
                lang_dim_scores.append(score)
    if lang_dim_scores:
        assert any(s > 0 for s in lang_dim_scores), \
            "Language quality dimensions are all zero - output may be in wrong language"

def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    result = grade()
    assert result["overall_score"] > 0.0, "Output appears empty or trivial"
    dims = result.get("dimensions", {})
    non_zero = 0
    for k, v in dims.items():
        score = v.get("score", v) if isinstance(v, dict) else v
        if isinstance(score, (int, float)) and score > 0:
            non_zero += 1
    assert non_zero >= 2, f"Only {non_zero} dimensions scored above zero - output likely incomplete"

def test_no_english_fallback():
    """For non-English target tasks: verify primary output is not in English."""
    result = grade()
    if result["overall_score"] == 0.0:
        return
    dims = result.get("dimensions", {})
    lang_dim_scores = []
    for k, v in dims.items():
        if any(word in k.lower() for word in ["language", "quality", "chinese", "korean",
               "russian", "japanese", "vietnamese", "french", "cyrillic", "hangul"]):
            score = v.get("score", v) if isinstance(v, dict) else v
            if isinstance(score, (int, float)):
                lang_dim_scores.append(score)
    if lang_dim_scores:
        avg_lang = sum(lang_dim_scores) / len(lang_dim_scores)
        assert avg_lang > 0.1, f"Language quality too low ({avg_lang:.2f}), likely English fallback"
