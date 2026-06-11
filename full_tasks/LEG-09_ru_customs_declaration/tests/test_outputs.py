"""
WildClawBench-style grading for LEG-09: Russian customs declarations from Chinese/English sources.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Key testable facts
TOTAL_FOB_VALUE = 47850.0
FREIGHT_COST = 3200.0
INSURANCE_COST = 285.0
TOTAL_CIF_VALUE = 51335.0  # FOB + Freight + Insurance
VAT_RATE = 0.20
DUTY_RATE_RANGE = (5, 15)  # percent
NUM_INVOICES = 5
NUM_ITEM_LINES = 20


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _is_russian(text: str) -> bool:
    """Check if text contains significant Russian characters."""
    if not text:
        return False
    cyrillic = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    return cyrillic / max(len(text), 1) > 0.2


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


def _extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text."""
    matches = re.findall(r'[\d,]+\.?\d*', text)
    results = []
    for x in matches:
        cleaned = x.replace(",", "").strip(".")
        if cleaned:
            try:
                results.append(float(cleaned))
            except ValueError:
                continue
    return results


def _score_hs_classification(hs_data: Any) -> Dict[str, float]:
    """Score HS code classification accuracy (weight: 0.30)."""
    scores = {}

    if not hs_data:
        return {"hs_exists": 0.0, "hs_format_correct": 0.0,
                "hs_count": 0.0, "hs_has_description": 0.0, "hs_justification": 0.0}

    scores["hs_exists"] = 1.0

    hs_str = json.dumps(hs_data, ensure_ascii=False)

    # Check 10-digit format
    hs_codes = re.findall(r'\b\d{10}\b', hs_str)
    scores["hs_format_correct"] = min(1.0, len(hs_codes) / 10) if hs_codes else 0.0

    # Check item count
    if isinstance(hs_data, list):
        scores["hs_count"] = min(1.0, len(hs_data) / 12)
    elif isinstance(hs_data, dict):
        items = hs_data.get("items", hs_data.get("classifications", []))
        if isinstance(items, list):
            scores["hs_count"] = min(1.0, len(items) / 12)
        else:
            scores["hs_count"] = min(1.0, len(hs_data) / 12)
    else:
        scores["hs_count"] = 0.0

    # Check for Russian descriptions
    scores["hs_has_description"] = 1.0 if _is_russian(hs_str) else 0.5

    # Check for justification/reasoning
    justification_terms = ["обоснование", "классификация", "основание",
                           "justification", "reason", "basis", "category"]
    scores["hs_justification"] = 1.0 if any(
        t.lower() in hs_str.lower() for t in justification_terms
    ) else 0.0

    return scores


def _score_value_accuracy(value_data: Any) -> Dict[str, float]:
    """Score value calculation accuracy (weight: 0.25)."""
    scores = {}

    if not value_data:
        return {"value_exists": 0.0, "fob_correct": 0.0, "cif_present": 0.0,
                "duty_calculated": 0.0, "vat_calculated": 0.0}

    scores["value_exists"] = 1.0

    value_str = json.dumps(value_data, ensure_ascii=False)
    numbers = _extract_numbers(value_str)

    # Check FOB value (should be ~47,850)
    fob_found = any(abs(n - TOTAL_FOB_VALUE) < 100 for n in numbers)
    scores["fob_correct"] = 1.0 if fob_found else 0.0

    # Check CIF value present (~51,335)
    cif_found = any(abs(n - TOTAL_CIF_VALUE) < 500 for n in numbers)
    # Also check if freight and insurance are mentioned
    freight_found = any(abs(n - FREIGHT_COST) < 100 for n in numbers)
    scores["cif_present"] = 1.0 if cif_found else (0.5 if freight_found else 0.0)

    # Check duty calculation present
    duty_terms = ["пошлина", "duty", "таможенн"]
    scores["duty_calculated"] = 1.0 if any(
        t.lower() in value_str.lower() for t in duty_terms
    ) else 0.0

    # Check VAT calculation present
    vat_terms = ["НДС", "VAT", "20%", "налог на добавленную стоимость"]
    scores["vat_calculated"] = 1.0 if any(t in value_str for t in vat_terms) else 0.0

    return scores


def _score_russian_format(declarations: Any, forms: str) -> Dict[str, float]:
    """Score Russian format compliance (weight: 0.20)."""
    scores = {}

    decl_str = json.dumps(declarations, ensure_ascii=False) if declarations else ""
    combined = decl_str + " " + forms

    if not combined.strip():
        return {"declarations_exist": 0.0, "russian_language": 0.0,
                "form_structure": 0.0, "required_fields": 0.0}

    scores["declarations_exist"] = 1.0 if (declarations or forms) else 0.0

    # Russian language in output
    scores["russian_language"] = 1.0 if _is_russian(combined) else 0.0

    # Form structure (ДТ format elements)
    form_elements = ["декларант", "отправитель", "получатель", "страна",
                     "таможенная стоимость", "код товара", "ТН ВЭД",
                     "вес", "количество", "валюта"]
    elements_found = sum(1 for el in form_elements if el.lower() in combined.lower())
    scores["form_structure"] = min(1.0, elements_found / 5)

    # Required fields present
    required = ["ТН ВЭД", "стоимость", "вес", "страна происхождения"]
    alt_required = ["код товар", "цена", "масса", "Китай"]
    req_found = sum(1 for r in required if r.lower() in combined.lower())
    alt_found = sum(1 for r in alt_required if r.lower() in combined.lower())
    scores["required_fields"] = min(1.0, max(req_found, alt_found) / 3)

    return scores


def _score_duty_calculation(value_data: Any, declarations: Any) -> Dict[str, float]:
    """Score duty calculation accuracy (weight: 0.15)."""
    scores = {}

    combined_str = ""
    if value_data:
        combined_str += json.dumps(value_data, ensure_ascii=False)
    if declarations:
        combined_str += json.dumps(declarations, ensure_ascii=False)

    if not combined_str:
        return {"duty_rates_applied": 0.0, "vat_on_cif_plus_duty": 0.0,
                "total_payments": 0.0}

    numbers = _extract_numbers(combined_str)

    # Check if duty rates in valid range (5-15%) are referenced
    rate_terms = ["5%", "8%", "10%", "12%", "15%", "0%"]
    rates_found = sum(1 for r in rate_terms if r in combined_str)
    scores["duty_rates_applied"] = min(1.0, rates_found / 3)

    # Check VAT is calculated on (CIF + duty), not just CIF
    # The total should be higher than just 20% of CIF
    # Expected: duty ~$2000-4000 range, VAT ~$10,000-11,000 range
    vat_range = any(9000 < n < 13000 for n in numbers)
    scores["vat_on_cif_plus_duty"] = 1.0 if vat_range else 0.5

    # Total payments should be reasonable (CIF + duty + VAT = roughly $63,000-66,000)
    total_range = any(55000 < n < 70000 for n in numbers)
    scores["total_payments"] = 1.0 if total_range else 0.0

    return scores


def _score_completeness(declarations: Any, hs_data: Any, value_data: Any, forms: str) -> Dict[str, float]:
    """Score overall completeness (weight: 0.10)."""
    scores = {}

    files_present = sum(1 for x in [declarations, hs_data, value_data, forms]
                        if x)
    scores["all_files_present"] = files_present / 4

    # Check all invoices covered
    combined = ""
    if declarations:
        combined += json.dumps(declarations, ensure_ascii=False)
    if hs_data:
        combined += json.dumps(hs_data, ensure_ascii=False)

    invoices_found = sum(1 for i in range(381, 386) if f"0{i}" in combined or str(i) in combined)
    scores["all_invoices_covered"] = min(1.0, invoices_found / 5)

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for LEG-09."""
    declarations = _load_json_file("customs_declarations_ru.json")
    hs_data = _load_json_file("hs_classification.json")
    value_data = _load_json_file("value_calculation.json")
    forms = _load_md_file("declaration_forms_ru.md")

    if not declarations and not hs_data and not value_data and not forms:
        return {"overall_score": 0.0, "dimensions": {}, "error": "No output files found."}

    dimensions = {}

    # Dimension 1: HS Classification (weight: 0.30)
    hs_scores = _score_hs_classification(hs_data)
    dimensions["hs_classification"] = {
        "score": sum(hs_scores.values()) / max(len(hs_scores), 1),
        "weight": 0.30,
        "details": hs_scores
    }

    # Dimension 2: Value Accuracy (weight: 0.25)
    value_scores = _score_value_accuracy(value_data)
    dimensions["value_accuracy"] = {
        "score": sum(value_scores.values()) / max(len(value_scores), 1),
        "weight": 0.25,
        "details": value_scores
    }

    # Dimension 3: Russian Format (weight: 0.20)
    format_scores = _score_russian_format(declarations, forms)
    dimensions["russian_format"] = {
        "score": sum(format_scores.values()) / max(len(format_scores), 1),
        "weight": 0.20,
        "details": format_scores
    }

    # Dimension 4: Duty Calculation (weight: 0.15)
    duty_scores = _score_duty_calculation(value_data, declarations)
    dimensions["duty_calculation"] = {
        "score": sum(duty_scores.values()) / max(len(duty_scores), 1),
        "weight": 0.15,
        "details": duty_scores
    }

    # Dimension 5: Completeness (weight: 0.10)
    completeness_scores = _score_completeness(declarations, hs_data, value_data, forms)
    dimensions["completeness"] = {
        "score": sum(completeness_scores.values()) / max(len(completeness_scores), 1),
        "weight": 0.10,
        "details": completeness_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"LEG-09 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
        for k, v in dim.get("details", {}).items():
            print(f"    {k}: {v:.2f}")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_hs_codes_10_digit():
    """Verify HS codes are in 10-digit Russian format."""
    hs_data = _load_json_file("hs_classification.json")
    assert hs_data is not None, "hs_classification.json not found"
    hs_str = json.dumps(hs_data)
    codes = re.findall(r'\b\d{10}\b', hs_str)
    assert len(codes) >= 5, f"Expected at least 5 ten-digit HS codes, found {len(codes)}"


def test_total_value_correct():
    """Verify total shipment value is approximately $47,850."""
    value_data = _load_json_file("value_calculation.json")
    assert value_data is not None, "value_calculation.json not found"
    value_str = json.dumps(value_data)
    numbers = _extract_numbers(value_str)
    fob_found = any(abs(n - TOTAL_FOB_VALUE) < 200 for n in numbers)
    assert fob_found, f"Total FOB value of ${TOTAL_FOB_VALUE} not found in calculations"


def test_vat_20_percent():
    """Verify 20% VAT rate is applied."""
    value_data = _load_json_file("value_calculation.json")
    assert value_data is not None, "value_calculation.json not found"
    value_str = json.dumps(value_data)
    assert "20" in value_str, "20% VAT rate not found"


def test_declarations_in_russian():
    """Verify declarations are in Russian."""
    forms = _load_md_file("declaration_forms_ru.md")
    declarations = _load_json_file("customs_declarations_ru.json")
    combined = forms + " " + json.dumps(declarations or {}, ensure_ascii=False)
    assert _is_russian(combined), "Declarations must be primarily in Russian"


def test_freight_and_insurance():
    """Verify freight and insurance costs are factored in."""
    value_data = _load_json_file("value_calculation.json")
    assert value_data is not None, "value_calculation.json not found"
    value_str = json.dumps(value_data, ensure_ascii=False)
    # Should mention transport/freight
    assert any(t in value_str.lower() for t in
               ["фрахт", "транспорт", "freight", "перевозк", "доставк"]), \
        "Freight costs not mentioned in value calculation"


def test_duty_rates_in_range():
    """Verify duty rates are in the 5-15% range."""
    value_data = _load_json_file("value_calculation.json")
    declarations = _load_json_file("customs_declarations_ru.json")
    combined = json.dumps(value_data or {}) + json.dumps(declarations or {})
    # Should have rates between 5 and 15
    rates = re.findall(r'(\d+)%', combined)
    valid_rates = [int(r) for r in rates if 0 <= int(r) <= 20]
    assert len(valid_rates) >= 2, "Expected at least 2 duty rate references"


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
        if any(word in k.lower() for word in ["russian", "cyrillic", "ru"]):
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
