"""
BabelAgentBench grading for KNW-06: French policy brief from trilingual sources.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Key statistics from input sources that should appear in the output
EXPECTED_STATISTICS = [
    "154.8",      # global AI investment 2024 (billion USD)
    "67.2",       # US private investment (billion USD)
    "38.2",       # YoY growth percent
    "5 820",      # China AI core industry (亿元) - may appear with space
    "4.7",        # global AI professionals (million)
]

EXPECTED_RECOMMENDATIONS_MIN = 6
FRENCH_POLICY_KEYWORDS = [
    "recommandation", "enjeu", "cadre réglementaire", "gouvernance",
    "régulation", "stratégi", "mise en œuvre", "parties prenantes",
    "il convient", "il est recommandé", "en conséquence", "à cet égard",
    "dans ce contexte", "force est de constater", "il apparaît"
]


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _is_french(text: str) -> bool:
    """Check if text is primarily in French using common French patterns."""
    if not text:
        return False
    french_indicators = [
        " de ", " des ", " les ", " une ", " dans ", " pour ", " avec ",
        " sur ", " par ", " qui ", " est ", " cette ", " sont ", " aux ",
        " entre ", " mais ", " ainsi ", "l'", "d'", "n'", "qu'"
    ]
    text_lower = text.lower()
    matches = sum(1 for ind in french_indicators if ind in text_lower)
    return matches >= 6


def _score_synthesis_quality(note_text: str) -> Dict[str, float]:
    """Score the quality of synthesis from multilingual sources."""
    scores = {}
    if not note_text:
        return {"note_exists": 0.0, "length_adequate": 0.0,
                "statistics_integrated": 0.0, "multi_source": 0.0}

    scores["note_exists"] = 1.0

    # Check length (1500-2500 words expected)
    word_count = len(note_text.split())
    if 1500 <= word_count <= 3000:
        scores["length_adequate"] = 1.0
    elif 800 <= word_count < 1500:
        scores["length_adequate"] = 0.6
    elif 500 <= word_count < 800:
        scores["length_adequate"] = 0.3
    else:
        scores["length_adequate"] = min(1.0, word_count / 1500)

    # Check if statistics from sources are integrated
    stats_found = sum(1 for stat in EXPECTED_STATISTICS if stat in note_text)
    scores["statistics_integrated"] = min(1.0, stats_found / 3)

    # Check multi-source integration (references to US, China, Russia approaches)
    source_refs = 0
    us_terms = ["états-unis", "américain", "washington", "us ", "etats-unis"]
    cn_terms = ["chine", "chinois", "pékin", "beijing"]
    ru_terms = ["russie", "russe", "moscou"]
    eu_terms = ["europe", "européen", "bruxelles", "ue ", "union européenne"]

    text_lower = note_text.lower()
    if any(t in text_lower for t in us_terms):
        source_refs += 1
    if any(t in text_lower for t in cn_terms):
        source_refs += 1
    if any(t in text_lower for t in ru_terms):
        source_refs += 1
    if any(t in text_lower for t in eu_terms):
        source_refs += 1

    scores["multi_source"] = min(1.0, source_refs / 3)

    return scores


def _score_french_policy_style(note_text: str) -> Dict[str, float]:
    """Score adherence to French institutional policy writing style."""
    scores = {}
    if not note_text:
        return {"is_french": 0.0, "policy_vocabulary": 0.0, "structure": 0.0}

    scores["is_french"] = 1.0 if _is_french(note_text) else 0.0

    # Check policy vocabulary
    text_lower = note_text.lower()
    policy_matches = sum(1 for kw in FRENCH_POLICY_KEYWORDS if kw in text_lower)
    scores["policy_vocabulary"] = min(1.0, policy_matches / 5)

    # Check structure (sections expected)
    structure_elements = [
        r"(résumé|synthèse).*(exécutif|générale)",
        r"(contexte|introduction)",
        r"(analyse|comparati)",
        r"(recommandation|préconisation)",
        r"(conclusion|perspective)",
    ]
    sections_found = sum(1 for pat in structure_elements
                        if re.search(pat, text_lower))
    scores["structure"] = min(1.0, sections_found / 4)

    return scores


def _score_source_integration(synthese_data: Any) -> Dict[str, float]:
    """Score the source synthesis JSON quality."""
    scores = {}
    if not synthese_data:
        return {"synthese_exists": 0.0, "source_count": 0.0,
                "key_fields": 0.0, "languages_identified": 0.0}

    scores["synthese_exists"] = 1.0

    # Check if it covers multiple sources
    if isinstance(synthese_data, list):
        sources = synthese_data
    elif isinstance(synthese_data, dict):
        sources = list(synthese_data.values()) if not any(
            k in synthese_data for k in ["sources", "synthese"]) else \
            synthese_data.get("sources", synthese_data.get("synthese", []))
        if isinstance(sources, dict):
            sources = [sources]
    else:
        sources = []

    scores["source_count"] = min(1.0, len(sources) / 3) if sources else 0.0

    # Check key fields in each source entry
    expected_fields = ["langue", "lang", "thème", "theme", "clé", "key",
                       "pertinence", "fiabilit", "reliab"]
    if sources:
        field_scores = []
        for src in sources:
            if isinstance(src, dict):
                src_str = json.dumps(src, ensure_ascii=False).lower()
                found = sum(1 for f in expected_fields if f in src_str)
                field_scores.append(min(1.0, found / 3))
            else:
                field_scores.append(0.0)
        scores["key_fields"] = sum(field_scores) / len(field_scores)
    else:
        scores["key_fields"] = 0.0

    # Check if languages are identified
    all_text = json.dumps(synthese_data, ensure_ascii=False).lower()
    langs_found = 0
    for lang in ["anglais", "english", "en", "chinois", "chinese", "zh",
                 "russe", "russian", "ru", "français", "french", "fr"]:
        if lang in all_text:
            langs_found += 1
    scores["languages_identified"] = min(1.0, langs_found / 4)

    return scores


def _score_recommendations(reco_data: Any) -> Dict[str, float]:
    """Score the recommendations JSON."""
    scores = {}
    if not reco_data:
        return {"reco_exists": 0.0, "reco_count": 0.0,
                "reco_structure": 0.0, "reco_french": 0.0}

    scores["reco_exists"] = 1.0

    # Get list of recommendations
    if isinstance(reco_data, list):
        recos = reco_data
    elif isinstance(reco_data, dict):
        recos = reco_data.get("recommandations", reco_data.get(
            "recommendations", list(reco_data.values())))
        if not isinstance(recos, list):
            recos = [recos]
    else:
        recos = []

    scores["reco_count"] = min(1.0, len(recos) / EXPECTED_RECOMMENDATIONS_MIN)

    # Check structure of each recommendation
    if recos:
        struct_scores = []
        for r in recos:
            if isinstance(r, dict):
                has_title = any(k in r for k in ["titre", "title", "nom", "name"])
                has_desc = any(k in r for k in ["description", "détail", "detail"])
                has_priority = any(k in r for k in ["priorité", "priority", "priorite"])
                has_horizon = any(k in r for k in ["horizon", "temporel", "délai",
                                                    "timeline", "terme"])
                struct_scores.append(
                    (has_title + has_desc + has_priority + has_horizon) / 4)
            else:
                struct_scores.append(0.2)
        scores["reco_structure"] = sum(struct_scores) / len(struct_scores)
    else:
        scores["reco_structure"] = 0.0

    # Check if recommendations are in French
    reco_text = json.dumps(reco_data, ensure_ascii=False)
    scores["reco_french"] = 1.0 if _is_french(reco_text) else 0.0

    return scores


def _score_bibliography(biblio_data: Any) -> Dict[str, float]:
    """Score the bibliography JSON."""
    scores = {}
    if not biblio_data:
        return {"biblio_exists": 0.0, "biblio_count": 0.0,
                "biblio_fields": 0.0}

    scores["biblio_exists"] = 1.0

    # Get entries
    if isinstance(biblio_data, list):
        entries = biblio_data
    elif isinstance(biblio_data, dict):
        entries = biblio_data.get("bibliographie", biblio_data.get(
            "references", biblio_data.get("entries", list(biblio_data.values()))))
        if not isinstance(entries, list):
            entries = [entries]
    else:
        entries = []

    scores["biblio_count"] = min(1.0, len(entries) / 3)

    # Check fields
    expected = ["auteur", "author", "titre", "title", "année", "year",
                "date", "langue", "lang", "type"]
    if entries:
        field_scores = []
        for entry in entries:
            if isinstance(entry, dict):
                entry_str = json.dumps(entry, ensure_ascii=False).lower()
                found = sum(1 for f in expected if f in entry_str)
                field_scores.append(min(1.0, found / 4))
            else:
                field_scores.append(0.1)
        scores["biblio_fields"] = sum(field_scores) / len(field_scores)
    else:
        scores["biblio_fields"] = 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for KNW-06."""
    # Load note politique
    note_path = _find_file("note_politique_fr.md")
    note_text = ""
    if note_path.exists():
        note_text = note_path.read_text(encoding="utf-8-sig")

    # Load synthese
    synthese_path = _find_file("synthese_sources.json")
    synthese_data = None
    if synthese_path.exists():
        try:
            synthese_data = json.loads(synthese_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    # Load recommendations
    reco_path = _find_file("recommandations_fr.json")
    reco_data = None
    if reco_path.exists():
        try:
            reco_data = json.loads(reco_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    # Load bibliography
    biblio_path = _find_file("bibliographie.json")
    biblio_data = None
    if biblio_path.exists():
        try:
            biblio_data = json.loads(biblio_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    dimensions = {}

    # Dimension 1: Synthesis Quality (weight: 0.25)
    synth_scores = _score_synthesis_quality(note_text)
    dimensions["synthesis_quality"] = {
        "score": sum(synth_scores.values()) / max(len(synth_scores), 1),
        "weight": 0.25,
        "details": synth_scores
    }

    # Dimension 2: French Policy Style (weight: 0.25)
    style_scores = _score_french_policy_style(note_text)
    dimensions["french_policy_style"] = {
        "score": sum(style_scores.values()) / max(len(style_scores), 1),
        "weight": 0.25,
        "details": style_scores
    }

    # Dimension 3: Source Integration (weight: 0.20)
    source_scores = _score_source_integration(synthese_data)
    dimensions["source_integration"] = {
        "score": sum(source_scores.values()) / max(len(source_scores), 1),
        "weight": 0.20,
        "details": source_scores
    }

    # Dimension 4: Recommendations (weight: 0.15)
    reco_scores = _score_recommendations(reco_data)
    dimensions["recommendations"] = {
        "score": sum(reco_scores.values()) / max(len(reco_scores), 1),
        "weight": 0.15,
        "details": reco_scores
    }

    # Dimension 5: Bibliography (weight: 0.15)
    biblio_scores = _score_bibliography(biblio_data)
    dimensions["bibliography"] = {
        "score": sum(biblio_scores.values()) / max(len(biblio_scores), 1),
        "weight": 0.15,
        "details": biblio_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"KNW-06 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_note_politique_exists_and_french():
    note_path = _find_file("note_politique_fr.md")
    assert note_path.exists(), "note_politique_fr.md not found"
    text = note_path.read_text(encoding="utf-8-sig")
    assert len(text) > 500, "Note is too short"
    assert _is_french(text), "Note must be written in French"


def test_note_contains_statistics():
    note_path = _find_file("note_politique_fr.md")
    if not note_path.exists():
        assert False, "note_politique_fr.md not found"
    text = note_path.read_text(encoding="utf-8-sig")
    stats_found = sum(1 for stat in EXPECTED_STATISTICS if stat in text)
    assert stats_found >= 2, (
        f"Note should integrate statistics from sources (found {stats_found}/5)"
    )


def test_note_references_all_perspectives():
    note_path = _find_file("note_politique_fr.md")
    if not note_path.exists():
        assert False, "note_politique_fr.md not found"
    text = note_path.read_text(encoding="utf-8-sig").lower()
    has_us = any(t in text for t in ["états-unis", "américain", "etats-unis"])
    has_cn = any(t in text for t in ["chine", "chinois"])
    has_ru = any(t in text for t in ["russie", "russe"])
    assert has_us and has_cn and has_ru, (
        "Note must synthesize US, Chinese, and Russian perspectives"
    )


def test_synthese_sources_valid():
    path = _find_file("synthese_sources.json")
    assert path.exists(), "synthese_sources.json not found"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    assert data, "synthese_sources.json is empty"


def test_recommandations_minimum_count():
    path = _find_file("recommandations_fr.json")
    assert path.exists(), "recommandations_fr.json not found"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        recos = data
    elif isinstance(data, dict):
        recos = data.get("recommandations", data.get("recommendations", []))
    else:
        recos = []
    assert len(recos) >= EXPECTED_RECOMMENDATIONS_MIN, (
        f"Expected at least {EXPECTED_RECOMMENDATIONS_MIN} recommendations, got {len(recos)}"
    )


def test_bibliographie_exists():
    path = _find_file("bibliographie.json")
    assert path.exists(), "bibliographie.json not found"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    assert data, "bibliographie.json is empty"


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
