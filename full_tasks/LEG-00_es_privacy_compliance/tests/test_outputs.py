"""
WildClawBench-style grading for HQ-04: Spanish LFPDPPP Privacy Compliance Report.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Expected compliance categories
REQUIRED_CATEGORIES = [
    "base legal",
    "derechos",  # ARCO rights
    "retención",
    "transferencias",
    "menores",
    "brechas",  # security breaches
    "aviso de privacidad",
]

# Key legal terms that should appear in a proper analysis
KEY_LEGAL_TERMS = {
    "es": ["LFPDPPP", "ARCO", "INAI", "titular", "responsable", "encargado",
           "aviso de privacidad", "consentimiento", "datos personales sensibles"],
    "en": ["CCPA", "personal information", "consumer rights", "data subject"],
    "de": ["DSGVO", "Betroffene", "Verantwortlicher", "Datenschutzbeauftragter"],
}


def _safe_read(path: Path, encoding="utf-8-sig") -> str:
    if path.exists():
        return path.read_text(encoding=encoding).strip()
    return ""


def _safe_json(path: Path) -> Any:
    """Load JSON from a file. If the file is .md, attempt to extract JSON content."""
    text = _safe_read(path)
    if not text:
        return None

    # Direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # If it's a markdown file, try to extract JSON from code blocks
    if path.suffix == ".md":
        json_blocks = re.findall(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
        for block in json_blocks:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                continue

    return None


def _find_file(name: str) -> Path:
    """Find output file, tolerating common naming variations.

    Search order:
      1. Exact name in /output/
      2. Exact name in root workspace
      3. Same basename with .md extension (when .json expected)
      4. Variant names (e.g., informe_final.md for informe.md)
    """
    stem = Path(name).stem
    suffix = Path(name).suffix

    candidates = [
        OUTPUT_DIR / "output" / name,
        OUTPUT_DIR / name,
    ]

    # If looking for .json, also accept .md with same stem
    if suffix == ".json":
        candidates += [
            OUTPUT_DIR / "output" / f"{stem}.md",
            OUTPUT_DIR / f"{stem}.md",
        ]

    # Common naming variants
    variants = {
        "informe.md": ["informe_final.md", "informe_completo.md", "informe_gap.md"],
        "matriz_cumplimiento.json": ["matriz_cumplimiento.md", "compliance_matrix.json"],
        "glosario_trilingue.json": ["glosario_trilingue.md", "glosario.json", "glossary.json"],
        "acciones_recomendadas.json": ["acciones_recomendadas.md", "plan_acciones.md", "action_plan.json"],
        "risk_scores.json": ["resultados_riesgo.json", "risk_assessment.json"],
        "compute_risk_scores.py": ["risk_scoring.py", "compute_risk.py", "risk_calculator.py"],
    }
    if name in variants:
        for variant in variants[name]:
            candidates += [
                OUTPUT_DIR / "output" / variant,
                OUTPUT_DIR / variant,
            ]

    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_answer() -> Dict[str, Any]:
    path = OUTPUT_DIR / "answer.json"
    if path.exists():
        text = path.read_text(encoding="utf-8-sig").strip()
        if text.startswith("{"):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

    # Fallback
    data = {}
    informe_path = _find_file("informe.md")
    if informe_path.exists():
        data["informe_md"] = informe_path.read_text(encoding="utf-8-sig")

    matriz = _safe_json(_find_file("matriz_cumplimiento.json"))
    if matriz:
        data["matriz_cumplimiento"] = matriz

    glosario = _safe_json(_find_file("glosario_trilingue.json"))
    if glosario:
        data["glosario_trilingue"] = glosario

    acciones = _safe_json(_find_file("acciones_recomendadas.json"))
    if acciones:
        data["acciones_recomendadas"] = acciones

    risk = _safe_json(_find_file("risk_scores.json"))
    if risk:
        data["risk_scores"] = risk

    clause_map = _safe_json(_find_file("clause_mapping.json"))
    if clause_map:
        data["clause_mapping"] = clause_map

    return data


def _score_compliance_matrix(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the compliance matrix coverage and quality."""
    scores = {}
    matrix = data.get("matriz_cumplimiento", [])

    if not matrix:
        return {"matrix_present": 0.0, "matrix_coverage": 0.0,
                "matrix_states": 0.0, "matrix_sources": 0.0}

    scores["matrix_present"] = 1.0

    if not isinstance(matrix, list):
        return {"matrix_present": 0.5, "matrix_coverage": 0.0,
                "matrix_states": 0.0, "matrix_sources": 0.0}

    # Coverage: should have at least 6-7 categories
    scores["matrix_coverage"] = min(1.0, len(matrix) / 7.0)

    # Check that categories match expected ones
    categories_found = [row.get("categoria", "").lower() for row in matrix if isinstance(row, dict)]
    matched_categories = sum(
        1 for req_cat in REQUIRED_CATEGORIES
        if any(req_cat in cat for cat in categories_found)
    )
    scores["matrix_category_match"] = matched_categories / len(REQUIRED_CATEGORIES)

    # Check estados are valid
    valid_states = {"✅", "⚠️", "❌"}
    state_count = sum(
        1 for row in matrix
        if isinstance(row, dict) and row.get("estado") in valid_states
    )
    scores["matrix_states"] = state_count / max(len(matrix), 1)

    # Check source citations
    source_count = 0
    for row in matrix:
        if not isinstance(row, dict):
            continue
        row_text = json.dumps(row, ensure_ascii=False)
        if "[Fuente:" in row_text or "[fuente:" in row_text.lower() or "source" in row_text.lower():
            source_count += 1
        elif "policy_" in row_text or "lfpdppp" in row_text.lower():
            source_count += 0.5
    scores["matrix_sources"] = min(1.0, source_count / max(len(matrix), 1))

    # Check for brecha_detectada field
    brecha_count = sum(1 for row in matrix if isinstance(row, dict) and "brecha_detectada" in row)
    scores["matrix_brechas"] = brecha_count / max(len(matrix), 1)

    return scores


def _score_risk_assessment(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the quantitative risk assessment."""
    scores = {}

    risk = data.get("risk_scores", {})
    if not risk:
        risk = _safe_json(_find_file("risk_scores.json")) or {}

    # Check script exists
    script_path = _find_file("compute_risk_scores.py")
    scores["risk_script"] = 1.0 if script_path.exists() else 0.0

    if not risk:
        scores["risk_present"] = 0.0
        scores["risk_quality"] = 0.0
        return scores

    scores["risk_present"] = 1.0

    quality = 0.0
    # Should have categorias with scores
    categorias = risk.get("categorias", [])
    if isinstance(categorias, list) and len(categorias) >= 5:
        quality += 0.3
    elif isinstance(categorias, list) and len(categorias) >= 3:
        quality += 0.15

    # Check scoring fields
    if categorias:
        scored = sum(1 for c in categorias if isinstance(c, dict) and
                     "puntaje_ponderado" in c or "riesgo_probabilidad" in c)
        if scored >= len(categorias) * 0.8:
            quality += 0.3

    # Should have global risk level
    if "nivel_riesgo_global" in risk or "puntaje_total" in risk:
        quality += 0.2

    # Should mention UMA / financial estimate
    risk_text = json.dumps(risk, ensure_ascii=False).lower()
    if "uma" in risk_text or "multa" in risk_text:
        quality += 0.2

    scores["risk_quality"] = min(1.0, quality)

    return scores


def _score_glossary(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the trilingual glossary."""
    scores = {}
    glosario = data.get("glosario_trilingue", [])

    if not glosario:
        return {"glossary_present": 0.0, "glossary_count": 0.0,
                "glossary_trilingual": 0.0}

    scores["glossary_present"] = 1.0

    if not isinstance(glosario, list):
        return {"glossary_present": 0.5, "glossary_count": 0.0,
                "glossary_trilingual": 0.0}

    # Count
    scores["glossary_count"] = min(1.0, len(glosario) / 12.0)

    # Check trilingual completeness
    trilingual_count = 0
    for entry in glosario:
        if isinstance(entry, dict):
            has_es = bool(entry.get("es"))
            has_en = bool(entry.get("en"))
            has_de = bool(entry.get("de"))
            if has_es and has_en and has_de:
                trilingual_count += 1
    scores["glossary_trilingual"] = trilingual_count / max(len(glosario), 1)

    # Check for key legal terms
    all_terms = json.dumps(glosario, ensure_ascii=False).lower()
    key_found = sum(1 for term in KEY_LEGAL_TERMS["es"] if term.lower() in all_terms)
    scores["glossary_relevance"] = min(1.0, key_found / 5.0)

    return scores


def _score_actions(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the recommended actions."""
    scores = {}
    acciones = data.get("acciones_recomendadas", [])

    if not acciones:
        return {"actions_present": 0.0, "actions_structured": 0.0,
                "actions_timeline": 0.0}

    scores["actions_present"] = 1.0

    if not isinstance(acciones, list):
        return {"actions_present": 0.5, "actions_structured": 0.0,
                "actions_timeline": 0.0}

    # Count
    scores["actions_count"] = min(1.0, len(acciones) / 5.0)

    # Structure: check required fields
    required_fields = {"id", "accion", "prioridad", "responsable", "plazo"}
    structured_count = 0
    for action in acciones:
        if isinstance(action, dict):
            found = sum(1 for f in required_fields if f in action)
            if found >= 4:
                structured_count += 1
    scores["actions_structured"] = structured_count / max(len(acciones), 1)

    # Priority distribution: should have P0, P1, P2
    priorities = [a.get("prioridad", "") for a in acciones if isinstance(a, dict)]
    has_p0 = any(p == "P0" for p in priorities)
    has_p1 = any(p == "P1" for p in priorities)
    scores["actions_priority_mix"] = (0.5 if has_p0 else 0.0) + (0.5 if has_p1 else 0.0)

    # Timeline: check dates are present and reasonable
    dates = [a.get("plazo", "") for a in acciones if isinstance(a, dict)]
    valid_dates = sum(1 for d in dates if re.match(r"\d{4}-\d{2}-\d{2}", str(d)))
    scores["actions_timeline"] = valid_dates / max(len(acciones), 1)

    # Check for Gantt/timeline script
    gantt_script = _find_file("generate_gantt.py")
    scores["gantt_script"] = 1.0 if gantt_script.exists() else 0.0

    timeline_json = _safe_json(_find_file("project_timeline.json"))
    scores["project_timeline"] = 1.0 if timeline_json else 0.0

    return scores


def _score_informe(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the complete report quality."""
    scores = {}
    informe = data.get("informe_md", "")

    if not informe:
        return {"informe_present": 0.0, "informe_structure": 0.0,
                "informe_legal_register": 0.0, "informe_sources": 0.0}

    scores["informe_present"] = 1.0

    # Length check (a proper report should be substantial)
    if len(informe) >= 3000:
        scores["informe_length"] = 1.0
    elif len(informe) >= 1500:
        scores["informe_length"] = 0.7
    elif len(informe) >= 500:
        scores["informe_length"] = 0.4
    else:
        scores["informe_length"] = 0.2

    # Structure: check for key sections
    informe_lower = informe.lower()
    expected_sections = [
        "resumen ejecutivo", "metodología", "hallazgo",
        "matriz", "riesgo", "recomendaci", "glosario"
    ]
    found_sections = [s for s in expected_sections if s in informe_lower]
    scores["informe_structure"] = len(found_sections) / len(expected_sections)

    # Legal register: check for formal Spanish legal language
    legal_markers = [
        "conforme", "en virtud", "toda vez que", "a efecto de",
        "el responsable", "el titular", "tratamiento de datos",
        "según lo dispuesto", "con fundamento en"
    ]
    legal_found = sum(1 for m in legal_markers if m in informe_lower)
    scores["informe_legal_register"] = min(1.0, legal_found / 4.0)

    # Source citations
    source_refs = re.findall(r'\[Fuente:.*?\]', informe, re.IGNORECASE)
    alt_refs = re.findall(r'\[fuente:.*?\]|\[source:.*?\]', informe, re.IGNORECASE)
    total_refs = len(source_refs) + len(alt_refs)
    if total_refs >= 10:
        scores["informe_sources"] = 1.0
    elif total_refs >= 6:
        scores["informe_sources"] = 0.7
    elif total_refs >= 3:
        scores["informe_sources"] = 0.4
    else:
        # Check for any file references
        file_refs = informe.count("policy_") + informe.count("lfpdppp") + informe.count("COMPANY_CONTEXT")
        scores["informe_sources"] = min(0.3, file_refs * 0.05)

    # LFPDPPP specific content
    lfpdppp_refs = informe.count("LFPDPPP") + informe.count("Art.")
    scores["informe_lfpdppp_depth"] = min(1.0, lfpdppp_refs / 8.0)

    return scores


def _score_clause_mapping(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the cross-jurisdictional clause mapping."""
    scores = {}

    mapping = data.get("clause_mapping", [])
    if not mapping:
        mapping = _safe_json(_find_file("clause_mapping.json")) or []

    if not mapping:
        return {"mapping_present": 0.0, "mapping_quality": 0.0}

    scores["mapping_present"] = 1.0

    if isinstance(mapping, list) and len(mapping) >= 6:
        scores["mapping_coverage"] = 1.0
    elif isinstance(mapping, list) and len(mapping) >= 4:
        scores["mapping_coverage"] = 0.6
    else:
        scores["mapping_coverage"] = 0.3

    # Check structure quality
    if isinstance(mapping, list):
        well_structured = 0
        for entry in mapping:
            if isinstance(entry, dict):
                has_cat = "categoria" in entry
                has_ccpa = "ccpa" in json.dumps(entry).lower()
                has_dsgvo = "dsgvo" in json.dumps(entry).lower()
                has_lfpdppp = "lfpdppp" in json.dumps(entry).lower()
                if has_cat and has_ccpa and has_dsgvo and has_lfpdppp:
                    well_structured += 1
        scores["mapping_quality"] = well_structured / max(len(mapping), 1)
    else:
        scores["mapping_quality"] = 0.0

    return scores


def _score_derechos_table(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the rights equivalence table."""
    scores = {}
    equiv_path = _find_file("equivalencia_derechos.md")
    equiv = _safe_read(equiv_path)

    if not equiv:
        return {"derechos_present": 0.0}

    scores["derechos_present"] = 1.0

    # Check for table structure
    if "|" in equiv and "ARCO" in equiv.upper() or "acceso" in equiv.lower():
        scores["derechos_quality"] = 1.0
    elif "|" in equiv:
        scores["derechos_quality"] = 0.5
    else:
        scores["derechos_quality"] = 0.3

    return scores


def grade() -> Dict[str, Any]:
    """
    Multi-dimensional grading for HQ-04.
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

    # Dimension 1: Compliance Matrix (weight: 0.25)
    matrix_scores = _score_compliance_matrix(data)
    dimensions["compliance_matrix"] = {
        "score": sum(matrix_scores.values()) / max(len(matrix_scores), 1),
        "weight": 0.25,
        "details": matrix_scores
    }

    # Dimension 2: Risk Assessment (weight: 0.20)
    risk_scores = _score_risk_assessment(data)
    dimensions["risk_assessment"] = {
        "score": sum(risk_scores.values()) / max(len(risk_scores), 1),
        "weight": 0.20,
        "details": risk_scores
    }

    # Dimension 3: Informe Quality (weight: 0.20)
    informe_scores = _score_informe(data)
    dimensions["informe_quality"] = {
        "score": sum(informe_scores.values()) / max(len(informe_scores), 1),
        "weight": 0.20,
        "details": informe_scores
    }

    # Dimension 4: Glossary & Documentation (weight: 0.10)
    glossary_scores = _score_glossary(data)
    derechos_scores = _score_derechos_table(data)
    combined_doc = {**{f"glos_{k}": v for k, v in glossary_scores.items()},
                    **{f"der_{k}": v for k, v in derechos_scores.items()}}
    dimensions["documentation"] = {
        "score": sum(combined_doc.values()) / max(len(combined_doc), 1),
        "weight": 0.10,
        "details": combined_doc
    }

    # Dimension 5: Actions & Timeline (weight: 0.15)
    action_scores = _score_actions(data)
    dimensions["actions_timeline"] = {
        "score": sum(action_scores.values()) / max(len(action_scores), 1),
        "weight": 0.15,
        "details": action_scores
    }

    # Dimension 6: Clause Mapping (weight: 0.10)
    mapping_scores = _score_clause_mapping(data)
    dimensions["clause_mapping"] = {
        "score": sum(mapping_scores.values()) / max(len(mapping_scores), 1),
        "weight": 0.10,
        "details": mapping_scores
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
    print(f"HQ-04 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for dim_name, dim_data in result.get("dimensions", {}).items():
        print(f"  {dim_name}: {dim_data['score']:.2%} (weight: {dim_data['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.0, "No valid output produced"


def test_compliance_matrix_minimum():
    """Compliance matrix must have sufficient coverage."""
    result = grade()
    matrix = result["dimensions"].get("compliance_matrix", {})
    score = matrix.get("score", 0.0)
    assert score >= 0.2, (
        f"Compliance matrix score too low: {score:.2%}. "
        f"Details: {matrix.get('details', {})}"
    )


def test_lfpdppp_referenced():
    """Output must substantially reference LFPDPPP."""
    data = _load_answer()
    blob = json.dumps(data, ensure_ascii=False)
    assert "LFPDPPP" in blob, "LFPDPPP must be referenced in the output"
    # Should also reference specific articles
    art_refs = re.findall(r'Art\.?\s*\d+', blob)
    assert len(art_refs) >= 3, (
        f"Expected at least 3 article references, found {len(art_refs)}"
    )


def test_actions_have_structure():
    """Recommended actions should be structured with priorities."""
    data = _load_answer()
    acciones = data.get("acciones_recomendadas", [])
    assert len(acciones) >= 3, (
        f"Expected at least 3 recommended actions, got {len(acciones)}"
    )
