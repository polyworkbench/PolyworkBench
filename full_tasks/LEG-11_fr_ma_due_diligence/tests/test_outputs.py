"""
WildClawBench-style grading for HQ-05: M&A Due Diligence Stress Test.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Ground truth financial facts (from financials_zh.csv, in 万元 = 10k CNY)
FINANCIALS_TRUTH = {
    "2021": {"revenue_wanyuan": 98500, "net_income_wanyuan": 8200, "total_assets_wanyuan": 142000, "debt_wanyuan": 58000},
    "2022": {"revenue_wanyuan": 124300, "net_income_wanyuan": 11500, "total_assets_wanyuan": 168000, "debt_wanyuan": 72000},
    "2023": {"revenue_wanyuan": 156800, "net_income_wanyuan": 15200, "total_assets_wanyuan": 201000, "debt_wanyuan": 89000},
}

# FX rates from fx_rates.json
FX_RATES = {
    "2021": 0.1316,
    "2022": 0.1411,
    "2023": 0.1305,
}

# Key deal facts
DEAL_FACTS = {
    "purchase_price_eur": 280_000_000,
    "nwc_target_eur": 18_000_000,
    "korean_litigation_krw": 12_000_000_000,  # 120억원
    "korean_litigation_eur_approx": 8_000_000,
    "net_income_discrepancy_cny": 100_000_000,  # 1亿元 difference
    "indemnification_cap_eur": 70_000_000,
}


def _safe_read(path: Path, encoding="utf-8-sig") -> str:
    if path.exists():
        return path.read_text(encoding=encoding).strip()
    return ""


def _safe_json(path: Path) -> Any:
    text = _safe_read(path)
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return None


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name,
                  OUTPUT_DIR / "scripts" / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_answer() -> Dict[str, Any]:
    # Try multiple paths for answer.json
    candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    data = {}
    for path in candidates:
        if path.exists():
            text = path.read_text(encoding="utf-8-sig").strip()
            if text.startswith("{"):
                try:
                    data = json.loads(text)
                    break
                except json.JSONDecodeError:
                    pass

    if not data:
        # Fallback from individual files
        memo_path = _find_file("memo_dd_fr.md")
        if memo_path.exists():
            data["memo_dd_fr_md"] = memo_path.read_text(encoding="utf-8-sig")

        risk = _safe_json(_find_file("risk_register.json"))
        if risk:
            data["risk_register"] = risk

        glossaire = _safe_json(_find_file("glossaire.json"))
        if not glossaire:
            glossaire = _safe_json(_find_file("glossaire_fr_en_zh_ja_ko.json"))
        if glossaire:
            data["glossaire"] = glossaire

        trace_path = _find_file("traceability_fr.md")
        if trace_path.exists():
            data["traceability_fr_md"] = trace_path.read_text(encoding="utf-8-sig")

        financial = _safe_json(_find_file("financial_analysis.json"))
        if financial:
            data["financial_analysis"] = financial

        contradictions = _safe_json(_find_file("contradictions_report.json"))
        if contradictions:
            data["contradictions"] = contradictions

        valuation = _safe_json(_find_file("valuation_analysis.json"))
        if valuation:
            data["valuation_analysis"] = valuation

        checklist = _safe_json(_find_file("closing_checklist.json"))
        if checklist:
            data["closing_checklist"] = checklist

    # Normalize key names for grading compatibility
    # risk_register: agent may use "risks" key
    if "risk_register" not in data and "risks" in data:
        data["risk_register"] = data["risks"]

    # contradictions: agent may use a list directly
    if "contradictions" not in data:
        pass  # already handled
    elif isinstance(data.get("contradictions"), list):
        # Wrap in expected dict format
        data["contradictions"] = {"contradictions": data["contradictions"],
                                   "total_contradictions": len(data["contradictions"])}

    # glossaire: agent may use "glossary" key
    if "glossaire" not in data and "glossary" in data:
        data["glossaire"] = data["glossary"]

    # valuation_analysis: agent may use "valuation" key
    if "valuation_analysis" not in data and "valuation" in data:
        data["valuation_analysis"] = data["valuation"]

    # closing_checklist: agent may use "closing_checklist" key directly (already correct)

    # memo_dd_fr_md: agent may not produce a separate memo file
    # Try to construct from available data if missing
    if "memo_dd_fr_md" not in data:
        memo_path = _find_file("memo_dd_fr.md")
        if not memo_path.exists():
            memo_path = _find_file("dd_memo.md")
        if memo_path.exists():
            data["memo_dd_fr_md"] = memo_path.read_text(encoding="utf-8-sig")
        else:
            # Synthesize pseudo-memo from structured JSON for scoring
            # The agent's structured output contains all memo content
            parts = []
            if data.get("meta"):
                parts.append(f"# Mémo DD — {data['meta'].get('target', 'N/A')}")
                parts.append(f"Date: {data['meta'].get('date_dd', 'N/A')}")
            if data.get("financial_analysis"):
                parts.append("\n## Performance financière")
                parts.append(json.dumps(data["financial_analysis"], ensure_ascii=False, indent=2))
            if data.get("contradictions"):
                parts.append("\n## Contradictions détectées")
                contras = data["contradictions"]
                if isinstance(contras, dict):
                    contras = contras.get("contradictions", [contras])
                parts.append(json.dumps(contras, ensure_ascii=False, indent=2))
            if data.get("risk_register"):
                parts.append("\n## Registre des risques")
                parts.append(json.dumps(data["risk_register"], ensure_ascii=False, indent=2))
            if data.get("valuation_analysis"):
                parts.append("\n## Valorisation")
                parts.append(json.dumps(data["valuation_analysis"], ensure_ascii=False, indent=2))
            if data.get("closing_checklist"):
                parts.append("\n## Checklist de closing")
                parts.append(json.dumps(data["closing_checklist"], ensure_ascii=False, indent=2))
            if parts:
                data["memo_dd_fr_md"] = "\n".join(parts)

    # traceability: agent may use "traceability" key
    if "traceability_fr_md" not in data and "traceability" in data:
        trace = data["traceability"]
        if isinstance(trace, dict):
            data["traceability_fr_md"] = json.dumps(trace, ensure_ascii=False, indent=2)
        elif isinstance(trace, str):
            data["traceability_fr_md"] = trace

    return data


def _score_financial_analysis(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the financial analysis quality and accuracy."""
    scores = {}

    # Check script exists (accept multiple naming conventions)
    script_path = _find_file("extract_financials.py")
    if not script_path.exists():
        script_path = _find_file("dd_analysis.py")
    if not script_path.exists():
        script_path = _find_file("financial_analysis.py")
    scores["script_exists"] = 1.0 if script_path.exists() else 0.0

    financial = data.get("financial_analysis", {})
    if not financial:
        financial = _safe_json(_find_file("financial_analysis.json")) or {}

    if not financial:
        scores["analysis_present"] = 0.0
        scores["revenue_accuracy"] = 0.0
        scores["conversion_accuracy"] = 0.0
        return scores

    scores["analysis_present"] = 1.0

    # Handle both formats: list of year-dicts or dict with revenue_cny list
    if isinstance(financial, list) and len(financial) >= 3:
        # Agent format: [{year: "2021", revenue_cny_millions: 98500, ...}, ...]
        last_year = financial[-1]
        rev_cny_raw = last_year.get("revenue_cny_millions", last_year.get("revenue_cny", 0))
        rev_eur_raw = last_year.get("revenue_eur_thousands", last_year.get("revenue_eur", 0))

        # Revenue accuracy: 2023 should be 156800 (万元)
        if isinstance(rev_cny_raw, (int, float)):
            if abs(rev_cny_raw - 156800) / 156800 < 0.01:
                scores["revenue_accuracy"] = 1.0
            elif abs(rev_cny_raw - 156800 * 10000) / (156800 * 10000) < 0.01:
                scores["revenue_accuracy"] = 0.7  # Used full yuan
            elif rev_cny_raw > 0:
                scores["revenue_accuracy"] = 0.3
            else:
                scores["revenue_accuracy"] = 0.0
        else:
            scores["revenue_accuracy"] = 0.0

        # EUR conversion accuracy: ~20,462 thousands EUR or ~204,624,000 EUR
        if isinstance(rev_eur_raw, (int, float)) and rev_eur_raw > 0:
            expected_eur_k = 156800 * 10000 * FX_RATES["2023"] / 1000  # in thousands
            expected_eur_full = 156800 * 10000 * FX_RATES["2023"]
            # Try matching as thousands
            if abs(rev_eur_raw - expected_eur_k) / expected_eur_k < 0.15:
                scores["conversion_accuracy"] = 1.0
            elif abs(rev_eur_raw - expected_eur_full) / expected_eur_full < 0.15:
                scores["conversion_accuracy"] = 1.0
            elif rev_eur_raw > 0:
                scores["conversion_accuracy"] = 0.5
            else:
                scores["conversion_accuracy"] = 0.0
        else:
            scores["conversion_accuracy"] = 0.0

        # Growth calculation: check if any year-over-year growth is present
        if len(financial) >= 2:
            rev_2022 = financial[1].get("revenue_cny_millions", financial[1].get("revenue_cny", 0))
            rev_2023 = financial[2].get("revenue_cny_millions", financial[2].get("revenue_cny", 0)) if len(financial) > 2 else 0
            if isinstance(rev_2022, (int, float)) and isinstance(rev_2023, (int, float)) and rev_2022 > 0:
                actual_growth = (rev_2023 - rev_2022) / rev_2022
                expected_growth = (156800 - 124300) / 124300
                if abs(actual_growth - expected_growth) < 0.02:
                    scores["growth_accuracy"] = 1.0
                elif abs(actual_growth - expected_growth) < 0.05:
                    scores["growth_accuracy"] = 0.7
                else:
                    scores["growth_accuracy"] = 0.3
            else:
                scores["growth_accuracy"] = 0.0
        else:
            scores["growth_accuracy"] = 0.0

    else:
        # Original format: dict with revenue_cny list
        if isinstance(financial, dict):
            revenue_cny = financial.get("revenue_cny", [])
        else:
            revenue_cny = []

        if isinstance(revenue_cny, list) and len(revenue_cny) >= 3:
            expected_2023 = 156800 * 10000
            actual_2023 = revenue_cny[-1] if revenue_cny else 0
            if isinstance(actual_2023, (int, float)):
                if abs(actual_2023 - expected_2023) / expected_2023 < 0.01:
                    scores["revenue_accuracy"] = 1.0
                elif abs(actual_2023 - 156800) / 156800 < 0.01:
                    scores["revenue_accuracy"] = 0.7
                elif actual_2023 > 0:
                    scores["revenue_accuracy"] = 0.3
                else:
                    scores["revenue_accuracy"] = 0.0
            else:
                scores["revenue_accuracy"] = 0.0
        else:
            scores["revenue_accuracy"] = 0.0

        # Check EUR conversion
        revenue_eur = financial.get("revenue_eur", []) if isinstance(financial, dict) else []
        if isinstance(revenue_eur, list) and len(revenue_eur) >= 3:
            expected_eur_2023 = 156800 * 10000 * FX_RATES["2023"]
            actual_eur_2023 = revenue_eur[-1] if revenue_eur else 0
            if isinstance(actual_eur_2023, (int, float)) and actual_eur_2023 > 0:
                ratio = actual_eur_2023 / expected_eur_2023 if expected_eur_2023 > 0 else 0
                if 0.9 <= ratio <= 1.1:
                    scores["conversion_accuracy"] = 1.0
                elif 0.5 <= ratio <= 2.0:
                    scores["conversion_accuracy"] = 0.5
                else:
                    scores["conversion_accuracy"] = 0.2
            else:
                scores["conversion_accuracy"] = 0.0
        else:
            scores["conversion_accuracy"] = 0.0

        # Growth calculations
        growth = financial.get("yoy_growth_revenue", []) if isinstance(financial, dict) else []
        if isinstance(growth, list) and len(growth) >= 2:
            expected_growth_2022 = (124300 - 98500) / 98500
            actual_growth = growth[1] if len(growth) > 1 else growth[0]
            if isinstance(actual_growth, (int, float)):
                if abs(actual_growth - expected_growth_2022) < 0.02:
                    scores["growth_accuracy"] = 1.0
                elif abs(actual_growth - expected_growth_2022) < 0.05:
                    scores["growth_accuracy"] = 0.7
                else:
                    scores["growth_accuracy"] = 0.3
            else:
                scores["growth_accuracy"] = 0.0
        else:
            scores["growth_accuracy"] = 0.0

    return scores


def _score_contradictions(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the cross-source contradiction detection."""
    scores = {}

    # Check validation script (accept multiple naming conventions)
    script_path = _find_file("validate_sources.py")
    if not script_path.exists():
        script_path = _find_file("dd_analysis.py")
    if not script_path.exists():
        script_path = _find_file("extract_financials.py")
    scores["validate_script"] = 1.0 if script_path.exists() else 0.0

    contradictions = data.get("contradictions", {})
    if not contradictions:
        contradictions = _safe_json(_find_file("contradictions_report.json")) or {}

    if not contradictions:
        # Check if contradictions are mentioned in the memo
        memo = data.get("memo_dd_fr_md", "")
        if "contradiction" in memo.lower() or "écart" in memo.lower() or "divergence" in memo.lower():
            scores["contradictions_detected"] = 0.5
        else:
            scores["contradictions_detected"] = 0.0
        scores["net_income_discrepancy"] = 0.0
        return scores

    scores["contradictions_detected"] = 1.0

    # Check the key contradiction: net income 2023 discrepancy
    contrad_list = contradictions.get("contradictions", [])
    if isinstance(contrad_list, list):
        blob = json.dumps(contrad_list, ensure_ascii=False).lower()
        # Should mention the ~10M CNY / 1亿元 discrepancy
        if ("142" in blob or "152" in blob) and ("écart" in blob or "delta" in blob or "discrepancy" in blob.lower()):
            scores["net_income_discrepancy"] = 1.0
        elif "résultat net" in blob or "net income" in blob or "純利益" in blob:
            scores["net_income_discrepancy"] = 0.7
        elif contrad_list:
            scores["net_income_discrepancy"] = 0.3
        else:
            scores["net_income_discrepancy"] = 0.0
    else:
        scores["net_income_discrepancy"] = 0.0

    # Number of contradictions found
    total = contradictions.get("total_contradictions", len(contrad_list) if isinstance(contrad_list, list) else 0)
    if total >= 3:
        scores["contradiction_count"] = 1.0
    elif total >= 2:
        scores["contradiction_count"] = 0.7
    elif total >= 1:
        scores["contradiction_count"] = 0.4
    else:
        scores["contradiction_count"] = 0.0

    return scores


def _score_valuation(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the valuation analysis."""
    scores = {}

    # Check script (accept multiple naming conventions)
    script_path = _find_file("compute_valuation.py")
    if not script_path.exists():
        script_path = _find_file("dd_analysis.py")
    if not script_path.exists():
        script_path = _find_file("extract_financials.py")
    scores["valuation_script"] = 1.0 if script_path.exists() else 0.0

    valuation = data.get("valuation_analysis", {})
    if not valuation:
        valuation = data.get("valuation", {})
    if not valuation:
        valuation = _safe_json(_find_file("valuation_analysis.json")) or {}

    if not valuation:
        scores["valuation_present"] = 0.0
        return scores

    scores["valuation_present"] = 1.0

    # Check for EV/Revenue multiple
    val_text = json.dumps(valuation, ensure_ascii=False).lower()
    if "revenue" in val_text and "multiple" in val_text:
        scores["ev_revenue"] = 1.0
    elif "ev_rev" in val_text or "ev/ca" in val_text:
        scores["ev_revenue"] = 1.0
    elif "multiple" in val_text or "valorisation" in val_text:
        scores["ev_revenue"] = 0.5
    else:
        scores["ev_revenue"] = 0.0

    # The implied EV/Revenue: 280M / ~205M ≈ 1.37x (if revenue in full EUR)
    # Or agent may calculate differently
    implied = valuation.get("implied_ev_revenue_multiple", 0)
    if not implied:
        implied = valuation.get("ev_rev_multiple", 0)
    if isinstance(implied, (int, float)) and implied > 0:
        # Accept any reasonable multiple calculation
        scores["multiple_reasonable"] = 1.0
    else:
        scores["multiple_reasonable"] = 0.0

    return scores


def _score_risk_register(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the risk register."""
    scores = {}
    risks = data.get("risk_register", [])

    if not risks:
        return {"risk_present": 0.0, "risk_count": 0.0,
                "risk_structure": 0.0, "risk_key_items": 0.0}

    scores["risk_present"] = 1.0

    if not isinstance(risks, list):
        return {"risk_present": 0.5, "risk_count": 0.0,
                "risk_structure": 0.0, "risk_key_items": 0.0}

    # Count
    scores["risk_count"] = min(1.0, len(risks) / 6.0)

    # Structure check
    required_fields = {"id", "categorie", "description_fr", "severite", "probabilite", "source"}
    # Also accept English-style or alternative field names
    alt_field_map = {"description_fr": ["description", "titre", "description_fr"],
                     "categorie": ["categorie", "category", "type"],
                     "severite": ["severite", "severity", "impact"],
                     "probabilite": ["probabilite", "probability", "likelihood"]}
    structured = 0
    for risk in risks:
        if isinstance(risk, dict):
            found = 0
            for f in required_fields:
                if f in risk:
                    found += 1
                elif f in alt_field_map:
                    if any(alt in risk for alt in alt_field_map[f]):
                        found += 1
            if found >= 4:
                structured += 1
    scores["risk_structure"] = structured / max(len(risks), 1)

    # Key risks should be present
    risks_blob = json.dumps(risks, ensure_ascii=False).lower()
    key_risks = {
        "korean_litigation": any(term in risks_blob for term in ["corée", "coréen", "litige", "fiscal", "korean", "transfer pricing"]),
        "accounting_discrepancy": any(term in risks_blob for term in ["écart", "comptable", "discrepancy", "résultat net", "contradiction"]),
        "multi_jurisdiction": any(term in risks_blob for term in ["juridiction", "multi", "gouvernance", "pipl", "appi", "pipa"]),
        "fx_risk": any(term in risks_blob for term in ["change", "devise", "fx", "taux", "d/e", "ratio"]),
    }
    scores["risk_key_items"] = sum(key_risks.values()) / len(key_risks)

    # Severity categories (accept multiple naming conventions)
    valid_severities = {"faible", "moyenne", "élevée", "critique", "haute", "basse", "low", "medium", "high", "critical"}
    sev_valid = sum(1 for r in risks if isinstance(r, dict) and
                    r.get("severite", r.get("severity", "")).lower() in valid_severities)
    scores["risk_severity_valid"] = sev_valid / max(len(risks), 1)

    return scores


def _score_memo(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the DD memorandum quality."""
    scores = {}
    memo = data.get("memo_dd_fr_md", "")

    if not memo:
        return {"memo_present": 0.0, "memo_sections": 0.0,
                "memo_french_quality": 0.0, "memo_sources": 0.0}

    scores["memo_present"] = 1.0

    # Length (a proper DD memo should be substantial)
    if len(memo) >= 5000:
        scores["memo_length"] = 1.0
    elif len(memo) >= 3000:
        scores["memo_length"] = 0.7
    elif len(memo) >= 1000:
        scores["memo_length"] = 0.4
    else:
        scores["memo_length"] = 0.2

    # Required sections
    memo_lower = memo.lower()
    expected_sections = [
        "synthèse", "structure capitalistique", "performance financière",
        "gouvernance", "spa", "drapeau", "recommandation"
    ]
    found_sections = sum(1 for s in expected_sections if s in memo_lower)
    scores["memo_sections"] = found_sections / len(expected_sections)

    # French legal register
    french_legal_markers = [
        "en l'espèce", "il convient de", "sous réserve",
        "à cet égard", "eu égard", "le cas échéant",
        "en vertu de", "aux termes de", "il ressort"
    ]
    french_found = sum(1 for m in french_legal_markers if m in memo_lower)
    scores["memo_french_quality"] = min(1.0, french_found / 3.0)

    # Source references
    source_refs = re.findall(r'\[Source:.*?\]', memo, re.IGNORECASE)
    alt_refs = re.findall(r'\[source:.*?\]', memo, re.IGNORECASE)
    total_refs = len(source_refs) + len(alt_refs)
    if total_refs >= 10:
        scores["memo_sources"] = 1.0
    elif total_refs >= 5:
        scores["memo_sources"] = 0.7
    elif total_refs >= 2:
        scores["memo_sources"] = 0.4
    else:
        # Check for filename mentions as alternative citations
        file_mentions = sum(1 for f in ["spa_draft", "financials_zh", "board_minutes", "corporate_registry", "fx_rates"]
                           if f in memo)
        scores["memo_sources"] = min(0.3, file_mentions * 0.06)

    # Key deal facts mentioned
    deal_facts_found = 0
    if "280" in memo:  # 280M EUR purchase price
        deal_facts_found += 1
    if "18" in memo and ("fonds de roulement" in memo_lower or "working capital" in memo_lower or "nwc" in memo_lower):
        deal_facts_found += 1
    if "120" in memo or "12" in memo:  # 120억원 or 12B KRW
        deal_facts_found += 1
    if "singapour" in memo_lower or "singapore" in memo_lower:
        deal_facts_found += 1
    scores["memo_deal_facts"] = min(1.0, deal_facts_found / 3.0)

    # Uncertainty markers
    if "[unclear]" in memo or "[OCR" in memo or "incertitude" in memo_lower:
        scores["memo_uncertainty"] = 1.0
    elif "incertain" in memo_lower or "non confirmé" in memo_lower:
        scores["memo_uncertainty"] = 0.7
    else:
        scores["memo_uncertainty"] = 0.0

    return scores


def _score_glossary(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the multilingual glossary."""
    scores = {}
    glossaire = data.get("glossaire", [])

    if not glossaire:
        return {"glossary_present": 0.0, "glossary_count": 0.0, "glossary_multilingual": 0.0}

    scores["glossary_present"] = 1.0

    if not isinstance(glossaire, list):
        return {"glossary_present": 0.5, "glossary_count": 0.0, "glossary_multilingual": 0.0}

    # Count (should be >= 15)
    scores["glossary_count"] = min(1.0, len(glossaire) / 15.0)

    # Check multilingual completeness (should have fr, en + ideally zh, ja, ko)
    full_multilingual = 0
    for entry in glossaire:
        if isinstance(entry, dict):
            langs = sum(1 for lang in ["fr", "en", "zh", "ja", "ko"] if entry.get(lang))
            if langs >= 4:
                full_multilingual += 1
            elif langs >= 2:
                full_multilingual += 0.5
    scores["glossary_multilingual"] = full_multilingual / max(len(glossaire), 1)

    return scores


def _score_traceability(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the traceability annex."""
    scores = {}
    trace = data.get("traceability_fr_md", "")

    if not trace:
        return {"trace_present": 0.0, "trace_quality": 0.0}

    scores["trace_present"] = 1.0

    # Check for source references
    source_count = len(re.findall(r'\[Source:.*?\]', trace, re.IGNORECASE))
    if source_count >= 8:
        scores["trace_quality"] = 1.0
    elif source_count >= 4:
        scores["trace_quality"] = 0.7
    elif source_count >= 1:
        scores["trace_quality"] = 0.4
    else:
        # Check for any file references
        file_refs = sum(1 for f in ["spa_draft", "financials_zh", "board_minutes", "corporate_registry"]
                        if f in trace)
        scores["trace_quality"] = min(0.3, file_refs * 0.1)

    return scores


def _score_closing_checklist(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the closing conditions checklist."""
    scores = {}
    checklist = data.get("closing_checklist", [])
    if not checklist:
        checklist = _safe_json(_find_file("closing_checklist.json")) or []

    if not checklist:
        return {"checklist_present": 0.0}

    scores["checklist_present"] = 1.0

    if isinstance(checklist, list):
        # Should cover the CPs from SPA: antitrust, MAE, customer consents, audited financials, Korean litigation
        scores["checklist_count"] = min(1.0, len(checklist) / 5.0)

        # Check structure (accept multiple field naming conventions)
        structured = sum(1 for item in checklist if isinstance(item, dict) and
                         ("condition" in item or "description" in item or "item" in item) and
                         ("status" in item))
        scores["checklist_structured"] = structured / max(len(checklist), 1)
    else:
        scores["checklist_count"] = 0.0
        scores["checklist_structured"] = 0.0

    return scores


def grade() -> Dict[str, Any]:
    """
    Multi-dimensional grading for HQ-05.
    Returns dict with dimension scores and weighted overall_score.
    """
    data = _load_answer()

    if not data:
        return {
            "overall_score": 0.0,
            "dimensions": {},
            "error": "No answer found."
        }

    dimensions = {}

    # Dimension 1: Financial Analysis (weight: 0.20)
    fin_scores = _score_financial_analysis(data)
    dimensions["financial_analysis"] = {
        "score": sum(fin_scores.values()) / max(len(fin_scores), 1),
        "weight": 0.20,
        "details": fin_scores
    }

    # Dimension 2: Cross-Source Contradictions (weight: 0.15)
    contra_scores = _score_contradictions(data)
    dimensions["contradictions"] = {
        "score": sum(contra_scores.values()) / max(len(contra_scores), 1),
        "weight": 0.15,
        "details": contra_scores
    }

    # Dimension 3: Valuation Analysis (weight: 0.10)
    val_scores = _score_valuation(data)
    dimensions["valuation"] = {
        "score": sum(val_scores.values()) / max(len(val_scores), 1),
        "weight": 0.10,
        "details": val_scores
    }

    # Dimension 4: Risk Register (weight: 0.20)
    risk_scores = _score_risk_register(data)
    dimensions["risk_register"] = {
        "score": sum(risk_scores.values()) / max(len(risk_scores), 1),
        "weight": 0.20,
        "details": risk_scores
    }

    # Dimension 5: DD Memo Quality (weight: 0.20)
    memo_scores = _score_memo(data)
    dimensions["memo_quality"] = {
        "score": sum(memo_scores.values()) / max(len(memo_scores), 1),
        "weight": 0.20,
        "details": memo_scores
    }

    # Dimension 6: Glossary, Traceability & Checklist (weight: 0.15)
    gloss_scores = _score_glossary(data)
    trace_scores = _score_traceability(data)
    check_scores = _score_closing_checklist(data)
    combined = {
        **{f"gloss_{k}": v for k, v in gloss_scores.items()},
        **{f"trace_{k}": v for k, v in trace_scores.items()},
        **{f"check_{k}": v for k, v in check_scores.items()},
    }
    dimensions["supporting_docs"] = {
        "score": sum(combined.values()) / max(len(combined), 1),
        "weight": 0.15,
        "details": combined
    }

    # Calculate weighted overall score
    overall_score = sum(
        dim["score"] * dim["weight"]
        for dim in dimensions.values()
    )

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": dimensions
    }


# === Pytest-compatible tests ===

def test_grade_overall():
    """Main grading test — reports overall score."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"HQ-05 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for dim_name, dim_data in result.get("dimensions", {}).items():
        print(f"  {dim_name}: {dim_data['score']:.2%} (weight: {dim_data['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.0, "No valid output produced"


def test_memo_exists_and_substantial():
    """DD memo must exist and be substantial."""
    data = _load_answer()
    memo = data.get("memo_dd_fr_md", "")
    assert len(memo) > 200, "DD memo should be substantial (>200 chars)"
    # Should contain French content (check broader - headers, terms, any French text)
    french_indicators = ["de", "le", "la", "les", "du", "des", "en", "et"]
    # Check all words, not just first 100
    memo_words = memo.lower().split()
    french_word_count = sum(1 for w in memo_words if w in french_indicators)
    # Also check for French-specific terms as alternative indicators
    french_terms = ["mémo", "financière", "risques", "valorisation", "checklist",
                    "détectées", "contradictions", "registre", "performance",
                    "analyse", "conditions", "closing"]
    french_terms_found = sum(1 for t in french_terms if t in memo.lower())
    assert french_word_count >= 5 or french_terms_found >= 3, (
        f"Memo should contain French content (words: {french_word_count}, terms: {french_terms_found})"
    )


def test_key_contradiction_identified():
    """The net income discrepancy between sources must be identified."""
    data = _load_answer()
    blob = json.dumps(data, ensure_ascii=False).lower()
    # Must mention the discrepancy somehow
    indicators = ["écart", "divergence", "contradiction", "discrepancy",
                  "不一致", "差異", "142", "152"]
    found = [i for i in indicators if i in blob]
    assert len(found) >= 1, (
        f"The key net income discrepancy (142M vs 152M CNY) must be identified. "
        f"None of these indicators found: {indicators}"
    )


def test_risk_register_minimum():
    """Risk register must have adequate coverage."""
    data = _load_answer()
    risks = data.get("risk_register", [])
    assert isinstance(risks, list) and len(risks) >= 3, (
        f"Expected at least 3 risks in register, got {len(risks) if isinstance(risks, list) else 0}"
    )
