"""
BabelAgentBench grading for COM-04: French supplier negotiation memo.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

EXPECTED_PRODUCTS = 8
EXCHANGE_RATE_CNY_EUR = 0.128  # 1 CNY ~ 0.128 EUR


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_answer() -> Dict[str, Any]:
    candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    for path in candidates:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    return {}


def _is_french(text: str) -> bool:
    """Check if text contains French-specific characters and patterns."""
    if not text:
        return False
    fr_chars = set("àâæçéèêëîïôœùûüÿ")
    fr_count = sum(1 for c in text.lower() if c in fr_chars)
    # Also check common French words
    fr_words = ["les", "des", "une", "pour", "dans", "avec", "sur", "est", "sont", "par"]
    word_count = sum(1 for w in fr_words if f" {w} " in text.lower())
    return fr_count >= 3 or word_count >= 3


def _score_memo_quality(data: Dict[str, Any]) -> Dict[str, float]:
    """Score French negotiation memo quality."""
    scores = {}
    memo_path = _find_file("memo_negociation_fr.md")

    if not memo_path.exists():
        return {"file_present": 0.0, "french_language": 0.0, "structure": 0.0,
                "content_depth": 0.0, "professionalism": 0.0}

    memo_text = memo_path.read_text(encoding="utf-8-sig")

    scores["file_present"] = 1.0
    scores["french_language"] = 1.0 if _is_french(memo_text) else 0.0

    # Check structure (headings, sections)
    headers = re.findall(r'^#{1,3}\s+.+', memo_text, re.MULTILINE)
    scores["structure"] = min(1.0, len(headers) / 4)

    # Check content depth
    depth_score = 0.0
    depth_keywords = ["fournisseur", "prix", "qualité", "délai", "recommandation",
                      "analyse", "avantage", "inconvénient", "stratégi", "négoci"]
    found = sum(1 for kw in depth_keywords if kw.lower() in memo_text.lower())
    depth_score = min(1.0, found / 5)
    scores["content_depth"] = depth_score

    # Check professional tone (formal French business language)
    formal_markers = ["nous recommandons", "il convient de", "à cet égard",
                      "en ce qui concerne", "compte tenu", "par conséquent",
                      "en conclusion", "il est à noter", "ci-dessous", "objectif"]
    formal_found = sum(1 for m in formal_markers if m.lower() in memo_text.lower())
    scores["professionalism"] = min(1.0, formal_found / 3)

    return scores


def _score_landed_cost(data: Dict[str, Any]) -> Dict[str, float]:
    """Score landed cost analysis accuracy."""
    scores = {}
    cost_path = _find_file("landed_cost_analysis.json")

    cost_data = None
    if cost_path.exists():
        try:
            cost_data = json.loads(cost_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not cost_data:
        return {"file_present": 0.0, "product_coverage": 0.0,
                "cost_components": 0.0, "currency_eur": 0.0}

    scores["file_present"] = 1.0

    # Get product entries
    products = cost_data if isinstance(cost_data, list) else cost_data.get("products", cost_data.get("analysis", list(cost_data.values()) if isinstance(cost_data, dict) else []))
    if isinstance(products, dict):
        products = list(products.values())
    if not isinstance(products, list):
        products = [cost_data]

    scores["product_coverage"] = min(1.0, len(products) / EXPECTED_PRODUCTS)

    # Check cost components are present
    expected_components = ["fob", "fret", "freight", "assurance", "insurance",
                          "douane", "duty", "transport", "total", "landed"]
    blob = json.dumps(cost_data, ensure_ascii=False).lower()
    component_found = sum(1 for c in expected_components if c in blob)
    scores["cost_components"] = min(1.0, component_found / 5)

    # Check values are in EUR
    eur_indicators = ["eur", "euro", "€"]
    has_eur = any(ind in blob for ind in eur_indicators)
    # Also check if values are reasonable EUR amounts (not CNY-scale)
    numeric_values = re.findall(r'\d+\.?\d*', blob)
    reasonable_eur = 0
    for val in numeric_values[:20]:
        try:
            v = float(val)
            if 1 <= v <= 500:  # Reasonable per-unit EUR costs
                reasonable_eur += 1
        except ValueError:
            pass
    scores["currency_eur"] = 1.0 if has_eur else (0.5 if reasonable_eur > 3 else 0.0)

    return scores


def _score_counter_proposal(data: Dict[str, Any]) -> Dict[str, float]:
    """Score counter-proposal quality."""
    scores = {}
    proposal_path = _find_file("counter_proposal_fr.md")

    if not proposal_path.exists():
        return {"file_present": 0.0, "french_language": 0.0,
                "negotiation_elements": 0.0, "terms_present": 0.0}

    proposal_text = proposal_path.read_text(encoding="utf-8-sig")

    scores["file_present"] = 1.0
    scores["french_language"] = 1.0 if _is_french(proposal_text) else 0.0

    # Check negotiation elements
    negotiation_keywords = ["prix", "remise", "discount", "volume", "engagement",
                           "paiement", "délai", "qualité", "garantie", "pénalité",
                           "contre-proposition", "offre", "condition"]
    found = sum(1 for kw in negotiation_keywords if kw.lower() in proposal_text.lower())
    scores["negotiation_elements"] = min(1.0, found / 5)

    # Check contract terms integration
    terms_keywords = ["MOQ", "AQL", "FOB", "L/C", "inspection", "garantie",
                      "warranty", "payment", "paiement", "Incoterms"]
    terms_found = sum(1 for t in terms_keywords if t.lower() in proposal_text.lower())
    scores["terms_present"] = min(1.0, terms_found / 4)

    return scores


def _score_risk_assessment(data: Dict[str, Any]) -> Dict[str, float]:
    """Score risk matrix quality."""
    scores = {}
    risk_path = _find_file("risk_matrix.json")

    risk_data = None
    if risk_path.exists():
        try:
            risk_data = json.loads(risk_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not risk_data:
        return {"file_present": 0.0, "risk_categories": 0.0,
                "probability_impact": 0.0, "mitigation": 0.0}

    scores["file_present"] = 1.0

    # Check risk categories
    blob = json.dumps(risk_data, ensure_ascii=False).lower()
    expected_risks = ["change", "currency", "forex", "délai", "delay", "lead time",
                      "qualité", "quality", "fournisseur", "supplier", "dépendance",
                      "dependency", "réglementation", "regulatory"]
    risk_found = sum(1 for r in expected_risks if r in blob)
    scores["risk_categories"] = min(1.0, risk_found / 4)

    # Check probability and impact scores
    has_probability = any(k in blob for k in ["probabilit", "likelihood", "probability"])
    has_impact = any(k in blob for k in ["impact", "severity", "gravit"])
    scores["probability_impact"] = 1.0 if (has_probability and has_impact) else 0.5 if (has_probability or has_impact) else 0.0

    # Check mitigation measures
    has_mitigation = any(k in blob for k in ["mitigation", "atténuation", "mesure",
                                              "action", "recommandation", "couverture"])
    scores["mitigation"] = 1.0 if has_mitigation else 0.0

    return scores


def _score_french_professionalism(data: Dict[str, Any]) -> Dict[str, float]:
    """Score overall French language professionalism."""
    scores = {}

    memo_path = _find_file("memo_negociation_fr.md")
    proposal_path = _find_file("counter_proposal_fr.md")

    total_checks = 0
    fr_quality = 0

    for path in [memo_path, proposal_path]:
        if path.exists():
            text = path.read_text(encoding="utf-8-sig")
            total_checks += 1
            if _is_french(text) and len(text) > 500:
                fr_quality += 1.0
            elif _is_french(text):
                fr_quality += 0.5

    if total_checks == 0:
        return {"french_documents": 0.0}

    scores["french_documents"] = fr_quality / total_checks

    # Check for business French terminology
    all_text = ""
    for path in [memo_path, proposal_path]:
        if path.exists():
            all_text += path.read_text(encoding="utf-8-sig")

    business_terms = ["chiffre d'affaires", "coût débarqué", "marge", "rentabilité",
                      "appel d'offres", "bon de commande", "cahier des charges",
                      "conditions générales", "prix unitaire", "franco de port",
                      "hors taxes", "toutes taxes", "TVA"]
    terms_found = sum(1 for t in business_terms if t.lower() in all_text.lower())
    scores["business_terminology"] = min(1.0, terms_found / 4)

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for COM-04."""
    data = _load_answer()

    dimensions = {}

    # Dimension 1: Memo Quality (weight: 0.30)
    memo_scores = _score_memo_quality(data)
    dimensions["memo_quality_fr"] = {
        "score": sum(memo_scores.values()) / max(len(memo_scores), 1),
        "weight": 0.30,
        "details": memo_scores
    }

    # Dimension 2: Landed Cost Accuracy (weight: 0.25)
    cost_scores = _score_landed_cost(data)
    dimensions["landed_cost_accuracy"] = {
        "score": sum(cost_scores.values()) / max(len(cost_scores), 1),
        "weight": 0.25,
        "details": cost_scores
    }

    # Dimension 3: Counter Proposal (weight: 0.20)
    proposal_scores = _score_counter_proposal(data)
    dimensions["counter_proposal"] = {
        "score": sum(proposal_scores.values()) / max(len(proposal_scores), 1),
        "weight": 0.20,
        "details": proposal_scores
    }

    # Dimension 4: Risk Assessment (weight: 0.15)
    risk_scores = _score_risk_assessment(data)
    dimensions["risk_assessment"] = {
        "score": sum(risk_scores.values()) / max(len(risk_scores), 1),
        "weight": 0.15,
        "details": risk_scores
    }

    # Dimension 5: French Professionalism (weight: 0.10)
    fr_scores = _score_french_professionalism(data)
    dimensions["french_professionalism"] = {
        "score": sum(fr_scores.values()) / max(len(fr_scores), 1),
        "weight": 0.10,
        "details": fr_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-04 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_memo_in_french():
    result = grade()
    memo = result["dimensions"].get("memo_quality_fr", {})
    details = memo.get("details", {})
    assert details.get("french_language", 0) == 1.0, "Negotiation memo must be in French"


def test_landed_cost_present():
    result = grade()
    cost = result["dimensions"].get("landed_cost_accuracy", {})
    details = cost.get("details", {})
    assert details.get("file_present", 0) == 1.0, "landed_cost_analysis.json must be present"


def test_risk_matrix_complete():
    result = grade()
    risk = result["dimensions"].get("risk_assessment", {})
    details = risk.get("details", {})
    assert details.get("risk_categories", 0) >= 0.5, "Risk matrix should cover multiple risk categories"


def test_counter_proposal_french():
    result = grade()
    proposal = result["dimensions"].get("counter_proposal", {})
    details = proposal.get("details", {})
    assert details.get("french_language", 0) == 1.0, "Counter-proposal must be in French"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["memo_negociation_fr.md", "landed_cost_analysis.json",
                          "counter_proposal_fr.md", "risk_matrix.json"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify output is in French, not English fallback."""
    memo_path = _find_file("memo_negociation_fr.md")
    if not memo_path.exists():
        return
    text = memo_path.read_text(encoding="utf-8-sig")
    fr_chars = set("àâæçéèêëîïôœùûüÿ")
    fr_count = sum(1 for c in text.lower() if c in fr_chars)
    assert fr_count >= 10, f"Only {fr_count} French accent chars found — likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    memo_path = _find_file("memo_negociation_fr.md")
    if memo_path.exists():
        content = memo_path.read_text(encoding="utf-8-sig")
        assert len(content) > 500, f"Memo too short ({len(content)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify French memo isn't in English."""
    memo_path = _find_file("memo_negociation_fr.md")
    if not memo_path.exists():
        return
    text = memo_path.read_text(encoding="utf-8-sig")
    if not text:
        return
    # Check French words are present
    fr_words = ["les", "des", "une", "pour", "dans", "avec", "sur", "est", "sont", "par"]
    word_count = sum(1 for w in fr_words if f" {w} " in text.lower())
    assert word_count >= 3, f"Memo lacks common French words (found {word_count}), likely not French"


def test_eur_calculations_present():
    """Verify landed cost calculations use EUR."""
    cost_path = _find_file("landed_cost_analysis.json")
    if not cost_path.exists():
        return
    try:
        cost_data = json.loads(cost_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return
    blob = json.dumps(cost_data, ensure_ascii=False).lower()
    assert any(ind in blob for ind in ["eur", "euro", "€"]), "Landed cost should reference EUR currency"
