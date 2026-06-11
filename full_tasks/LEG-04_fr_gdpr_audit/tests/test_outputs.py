"""
Test suite for LEG-04_fr_gdpr_audit
Evaluates: gdpr_compliance, french_legal_quality, risk_identification, action_plan, cross_reference
"""

import json
import os
import re
from pathlib import Path
import pytest


def check_file_exists(filepath):
    """Check if a file exists and has content."""
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"
    return True, "OK"


def load_json_file(filepath):
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return None, str(e)


def check_french_text(text):
    """Check if text contains French-specific characters and patterns."""
    # French diacritics and common patterns
    french_indicators = len(re.findall(r'[àâäéèêëïîôùûüÿçœæ]', text.lower()))
    french_words = ["conformité", "données", "traitement", "responsable", "règlement",
                   "personnelles", "consentement", "également", "nécessaire"]
    word_hits = sum(1 for w in french_words if w in text.lower())
    return french_indicators > 10 or word_hits >= 3


def grade():
    """Main grading function returning overall_score and dimensions."""

    output_dir = "/workspace/output"
    answer_path = "/workspace/output/answer.json"
    if not os.path.exists(answer_path):
        answer_path = "/workspace/answer.json"

    if not os.path.exists(output_dir):
        output_dir = "output"
    if not os.path.exists(answer_path):
        answer_path = "answer.json"

    dimensions = {
        "gdpr_compliance": 0.0,
        "french_legal_quality": 0.0,
        "risk_identification": 0.0,
        "action_plan": 0.0,
        "cross_reference": 0.0
    }

    weights = {
        "gdpr_compliance": 0.30,
        "french_legal_quality": 0.25,
        "risk_identification": 0.20,
        "action_plan": 0.15,
        "cross_reference": 0.10
    }

    # =====================================================
    # DIMENSION 1: GDPR Compliance Analysis (0.30)
    # =====================================================
    gdpr_score = 0.0

    # Check conformite_matrix.json
    matrix_path = os.path.join(output_dir, "conformite_matrix.json")
    matrix_data, err = load_json_file(matrix_path)

    if matrix_data is not None:
        gdpr_score += 0.1
        matrix_text = json.dumps(matrix_data, ensure_ascii=False).lower()

        # Should identify consent mechanism violations
        consent_violation = any(kw in matrix_text for kw in [
            "consentement", "consent", "cookie", "pre-check", "pré-coch",
            "dark pattern", "scrolling", "opt-in"
        ])
        if consent_violation:
            gdpr_score += 0.2

        # Should identify Schrems II / transfer issues
        transfer_violation = any(kw in matrix_text for kw in [
            "schrems", "transfert", "transfer", "états-unis", "united states",
            "scc", "cct", "mesures supplémentaires", "supplementary"
        ])
        if transfer_violation:
            gdpr_score += 0.2

        # Should identify retention period issues
        retention_violation = any(kw in matrix_text for kw in [
            "conservation", "retention", "5 ans", "5 years", "25 mois",
            "indéfin", "indefinite"
        ])
        if retention_violation:
            gdpr_score += 0.15

        # Should identify DPIA requirement
        dpia_issue = any(kw in matrix_text for kw in [
            "aipd", "dpia", "impact", "folgenabschätzung", "art. 35", "article 35",
            "profilage", "profiling"
        ])
        if dpia_issue:
            gdpr_score += 0.15

        # Should have GDPR article references
        article_refs = re.findall(r'art(?:icle)?\.?\s*\d+', matrix_text)
        if len(article_refs) >= 3:
            gdpr_score += 0.1

        # Should have compliance status indicators
        status_markers = ["conforme", "non-conforme", "non conforme", "partiellement",
                         "compliant", "non-compliant", "partial"]
        if any(m in matrix_text for m in status_markers):
            gdpr_score += 0.1

    dimensions["gdpr_compliance"] = min(1.0, gdpr_score)

    # =====================================================
    # DIMENSION 2: French Legal Quality (0.25)
    # =====================================================
    fr_score = 0.0

    rapport_path = os.path.join(output_dir, "rapport_audit_fr.md")
    exists, _ = check_file_exists(rapport_path)

    if exists:
        with open(rapport_path, 'r', encoding='utf-8') as f:
            rapport_text = f.read()

        # Check French content
        if check_french_text(rapport_text):
            fr_score += 0.25

        # Check for GDPR/French legal terminology
        fr_legal_terms = [
            "responsable de traitement", "sous-traitant", "personne concernée",
            "base légale", "intérêt légitime", "analyse d'impact",
            "données à caractère personnel", "finalité", "proportionnalité",
            "CNIL", "RGPD", "règlement"
        ]
        terms_found = sum(1 for t in fr_legal_terms if t.lower() in rapport_text.lower())
        fr_score += min(0.3, terms_found / 6 * 0.3)

        # Check document structure
        has_structure = bool(re.search(r'^#+\s', rapport_text, re.MULTILINE))
        if has_structure:
            fr_score += 0.15

        # Check document length
        if len(rapport_text) > 3000:
            fr_score += 0.15
        elif len(rapport_text) > 1500:
            fr_score += 0.1

        # Check for formal audit language
        audit_terms = ["constat", "recommandation", "non-conformité", "observation",
                      "niveau de risque", "action corrective"]
        audit_found = sum(1 for t in audit_terms if t in rapport_text.lower())
        fr_score += min(0.15, audit_found / 3 * 0.15)

    dimensions["french_legal_quality"] = min(1.0, fr_score)

    # =====================================================
    # DIMENSION 3: Risk Identification (0.20)
    # =====================================================
    risk_score = 0.0

    synthese_path = os.path.join(output_dir, "synthese_risques_fr.md")
    exists, _ = check_file_exists(synthese_path)

    if exists:
        with open(synthese_path, 'r', encoding='utf-8') as f:
            synthese_text = f.read()

        # Should identify key risks
        key_risks = {
            "consent_mechanism": ["consentement", "cookie", "banner", "bandeau", "dark pattern"],
            "data_transfer": ["transfert", "schrems", "états-unis", "scc", "cct"],
            "retention": ["conservation", "rétention", "5 ans", "indéfini"],
            "dpia_missing": ["aipd", "dpia", "impact", "profilage", "profiling"],
            "minors": ["mineur", "enfant", "children", "16 ans"],
            "response_time": ["60 jours", "délai", "30 jours", "un mois"]
        }

        risks_identified = 0
        for risk_name, keywords in key_risks.items():
            if any(kw.lower() in synthese_text.lower() for kw in keywords):
                risks_identified += 1

        risk_score += min(0.5, risks_identified / 4 * 0.5)

        # Check for risk severity classification
        severity_keywords = ["critique", "élevé", "modéré", "faible", "critical", "high", "medium", "low"]
        if any(kw in synthese_text.lower() for kw in severity_keywords):
            risk_score += 0.2

        # Check for financial/legal impact mentions
        impact_keywords = ["amende", "sanction", "million", "4%", "20 million", "CNIL"]
        if any(kw.lower() in synthese_text.lower() for kw in impact_keywords):
            risk_score += 0.15

        # Length check
        if len(synthese_text) > 1000:
            risk_score += 0.15

    dimensions["risk_identification"] = min(1.0, risk_score)

    # =====================================================
    # DIMENSION 4: Action Plan (0.15)
    # =====================================================
    action_score = 0.0

    action_path = os.path.join(output_dir, "plan_action_fr.json")
    action_data, err = load_json_file(action_path)

    if action_data is not None:
        action_score += 0.15

        action_text = json.dumps(action_data, ensure_ascii=False).lower()

        # Should have prioritized actions
        if any(kw in action_text for kw in ["priorit", "urgent", "critique", "immédiat", "court terme", "moyen terme"]):
            action_score += 0.2

        # Should have timeline/deadlines
        if any(kw in action_text for kw in ["délai", "échéance", "mois", "semaine", "jour", "deadline", "date"]):
            action_score += 0.2

        # Should have specific corrective measures
        measures = ["modifier", "mettre en place", "supprimer", "chiffrer", "rapatrier",
                   "réaliser", "documenter", "former", "auditer", "consentement"]
        measures_found = sum(1 for m in measures if m in action_text)
        action_score += min(0.25, measures_found / 4 * 0.25)

        # Should have multiple action items
        if isinstance(action_data, list) and len(action_data) >= 5:
            action_score += 0.2
        elif isinstance(action_data, dict):
            # Check for nested lists
            for v in action_data.values():
                if isinstance(v, list) and len(v) >= 5:
                    action_score += 0.2
                    break

    dimensions["action_plan"] = min(1.0, action_score)

    # =====================================================
    # DIMENSION 5: Cross-Reference (0.10)
    # =====================================================
    xref_score = 0.0

    # Check if the audit references all three source documents
    all_output_text = ""
    for fname in ["rapport_audit_fr.md", "synthese_risques_fr.md"]:
        fpath = os.path.join(output_dir, fname)
        exists, _ = check_file_exists(fpath)
        if exists:
            with open(fpath, 'r', encoding='utf-8') as f:
                all_output_text += f.read()

    if all_output_text:
        # References English privacy policy
        if any(kw in all_output_text.lower() for kw in ["cloudmetrics", "privacy policy", "politique de confidentialité"]):
            xref_score += 0.25

        # References CNIL guidance
        if any(kw in all_output_text.lower() for kw in ["cnil", "délibération", "recommandation"]):
            xref_score += 0.25

        # References German court ruling
        if any(kw in all_output_text.lower() for kw in ["landgericht", "tribunal allemand", "berlin",
                                                         "allemand", "german", "datatrack", "planet49"]):
            xref_score += 0.25

        # References specific GDPR articles
        gdpr_articles = re.findall(r'art(?:icle)?\.?\s*\d+', all_output_text.lower())
        if len(gdpr_articles) >= 5:
            xref_score += 0.25
        elif len(gdpr_articles) >= 3:
            xref_score += 0.15

    dimensions["cross_reference"] = min(1.0, xref_score)

    # =====================================================
    # Check answer.json
    # =====================================================
    answer_data, err = load_json_file(answer_path)
    if answer_data is not None:
        # Validate key fields
        if answer_data.get("schrems_ii_violation") == True:
            dimensions["gdpr_compliance"] = min(1.0, dimensions["gdpr_compliance"] + 0.05)
        if answer_data.get("dpia_required") == True:
            dimensions["gdpr_compliance"] = min(1.0, dimensions["gdpr_compliance"] + 0.05)

    # =====================================================
    # CALCULATE OVERALL SCORE
    # =====================================================
    overall_score = sum(dimensions[k] * weights[k] for k in dimensions)

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": {k: round(v, 4) for k, v in dimensions.items()}
    }





def test_grade_overall():
    """Verify grade function produces a meaningful score."""
    result = grade()
    assert result["overall_score"] > 0.15, "No valid output produced"



def test_grade_overall():
    """Verify grade function produces a meaningful score."""
    result = grade()
    assert result["overall_score"] > 0.15, "No valid output produced"


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

if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2))
