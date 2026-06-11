"""
WildClawBench-style grading for COM-01: Chinese product catalog → Russian marketplace listings.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

EXPECTED_PRODUCTS = 20
EXPECTED_KEYWORDS_PER_PRODUCT = 5
REQUIRED_FIELDS = ["title", "description", "category", "price_rub", "sku", "material", "weight"]


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
    # Fallback: assemble from individual files
    data = {}
    listings_path = _find_file("listings_ru.json")
    if listings_path.exists():
        try:
            data["listings"] = json.loads(listings_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass
    seo_path = _find_file("seo_keywords_ru.txt")
    if seo_path.exists():
        data["seo_keywords_text"] = seo_path.read_text(encoding="utf-8-sig")
    size_path = _find_file("size_conversion_table.json")
    if size_path.exists():
        try:
            data["size_conversion"] = json.loads(size_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass
    compliance_path = _find_file("compliance_tags.json")
    if compliance_path.exists():
        try:
            data["compliance_tags"] = json.loads(compliance_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass
    return data


def _is_russian(text: str) -> bool:
    """Check if text contains significant Russian characters."""
    if not text:
        return False
    cyrillic = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    return cyrillic / max(len(text), 1) > 0.3


def _score_listings(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the product listings quality."""
    scores = {}
    listings = data.get("listings", [])

    if isinstance(listings, dict):
        listings = list(listings.values())

    if not listings:
        return {"listings_present": 0.0, "listings_count": 0.0,
                "russian_quality": 0.0, "field_completeness": 0.0, "pricing_accuracy": 0.0}

    scores["listings_present"] = 1.0
    scores["listings_count"] = min(1.0, len(listings) / EXPECTED_PRODUCTS)

    # Check Russian language quality
    russian_scores = []
    for item in listings:
        title = item.get("title", item.get("name", ""))
        desc = item.get("description", "")
        if _is_russian(title) and _is_russian(desc):
            russian_scores.append(1.0)
        elif _is_russian(title) or _is_russian(desc):
            russian_scores.append(0.5)
        else:
            russian_scores.append(0.0)
    scores["russian_quality"] = sum(russian_scores) / max(len(russian_scores), 1)

    # Check field completeness
    field_scores = []
    for item in listings:
        present = sum(1 for f in REQUIRED_FIELDS
                      if f in item or f.replace("_", "") in str(item.keys()).lower())
        field_scores.append(present / len(REQUIRED_FIELDS))
    scores["field_completeness"] = sum(field_scores) / max(len(field_scores), 1)

    # Check pricing logic (should be in RUB, reasonable range)
    price_scores = []
    for item in listings:
        price = item.get("price_rub", item.get("price", 0))
        if isinstance(price, (int, float)) and 500 <= price <= 50000:
            price_scores.append(1.0)
        elif isinstance(price, (int, float)) and price > 0:
            price_scores.append(0.5)
        else:
            price_scores.append(0.0)
    scores["pricing_accuracy"] = sum(price_scores) / max(len(price_scores), 1)

    return scores


def _score_seo(data: Dict[str, Any]) -> Dict[str, float]:
    """Score SEO keywords generation."""
    scores = {}
    seo_text = data.get("seo_keywords_text", "")
    seo_data = data.get("seo_keywords", [])

    if not seo_text and not seo_data:
        seo_path = _find_file("seo_keywords_ru.txt")
        if seo_path.exists():
            seo_text = seo_path.read_text(encoding="utf-8-sig")

    if not seo_text and not seo_data:
        return {"seo_present": 0.0, "seo_russian": 0.0, "seo_coverage": 0.0}

    scores["seo_present"] = 1.0

    # Check if keywords are in Russian
    if seo_text:
        scores["seo_russian"] = 1.0 if _is_russian(seo_text) else 0.0
        # Count keyword lines/entries
        lines = [l.strip() for l in seo_text.split("\n") if l.strip()]
        scores["seo_coverage"] = min(1.0, len(lines) / (EXPECTED_PRODUCTS * 3))
    elif seo_data:
        all_keywords = str(seo_data)
        scores["seo_russian"] = 1.0 if _is_russian(all_keywords) else 0.0
        if isinstance(seo_data, list):
            scores["seo_coverage"] = min(1.0, len(seo_data) / EXPECTED_PRODUCTS)
        else:
            scores["seo_coverage"] = 0.5

    return scores


def _score_size_conversion(data: Dict[str, Any]) -> Dict[str, float]:
    """Score size conversion table."""
    scores = {}
    size_data = data.get("size_conversion", {})

    if not size_data:
        size_path = _find_file("size_conversion_table.json")
        if size_path.exists():
            try:
                size_data = json.loads(size_path.read_text(encoding="utf-8-sig"))
            except Exception:
                pass

    if not size_data:
        return {"size_table_present": 0.0, "size_table_quality": 0.0}

    scores["size_table_present"] = 1.0

    # Check if it has CN→RU mapping
    blob = json.dumps(size_data, ensure_ascii=False).lower()
    quality = 0.0
    if "cn" in blob or "中国" in blob or "china" in blob:
        quality += 0.3
    if "ru" in blob or "россия" in blob or "russia" in blob:
        quality += 0.3
    # Check for actual size values
    if any(str(s) in blob for s in ["40", "42", "44", "46", "48"]):
        quality += 0.4
    scores["size_table_quality"] = min(1.0, quality)

    return scores


def _score_compliance(data: Dict[str, Any]) -> Dict[str, float]:
    """Score compliance tags generation."""
    scores = {}
    compliance = data.get("compliance_tags", {})

    if not compliance:
        comp_path = _find_file("compliance_tags.json")
        if comp_path.exists():
            try:
                compliance = json.loads(comp_path.read_text(encoding="utf-8-sig"))
            except Exception:
                pass

    if not compliance:
        return {"compliance_present": 0.0, "compliance_quality": 0.0}

    scores["compliance_present"] = 1.0

    # Check for TR TS / EAC references
    blob = json.dumps(compliance, ensure_ascii=False)
    quality = 0.0
    if "ТР ТС" in blob or "TR TS" in blob.upper():
        quality += 0.4
    if "EAC" in blob.upper():
        quality += 0.3
    if "017" in blob or "004" in blob or "021" in blob:  # Specific regulation numbers
        quality += 0.3
    scores["compliance_quality"] = min(1.0, quality)

    return scores


def _score_script(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the validation script existence."""
    scores = {}
    script_candidates = [
        _find_file("validate_listings.py"),
        _find_file("validation.py"),
        _find_file("check_listings.py"),
    ]
    script_exists = any(p.exists() for p in script_candidates)
    scores["validation_script"] = 1.0 if script_exists else 0.0
    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for COM-01."""
    data = _load_answer()

    if not data:
        return {"overall_score": 0.0, "dimensions": {}, "error": "No answer found."}

    dimensions = {}

    # Dimension 1: Listings Quality (weight: 0.35)
    listing_scores = _score_listings(data)
    dimensions["listings"] = {
        "score": sum(listing_scores.values()) / max(len(listing_scores), 1),
        "weight": 0.35,
        "details": listing_scores
    }

    # Dimension 2: SEO Keywords (weight: 0.20)
    seo_scores = _score_seo(data)
    dimensions["seo_keywords"] = {
        "score": sum(seo_scores.values()) / max(len(seo_scores), 1),
        "weight": 0.20,
        "details": seo_scores
    }

    # Dimension 3: Size Conversion (weight: 0.15)
    size_scores = _score_size_conversion(data)
    dimensions["size_conversion"] = {
        "score": sum(size_scores.values()) / max(len(size_scores), 1),
        "weight": 0.15,
        "details": size_scores
    }

    # Dimension 4: Compliance Tags (weight: 0.20)
    comp_scores = _score_compliance(data)
    dimensions["compliance"] = {
        "score": sum(comp_scores.values()) / max(len(comp_scores), 1),
        "weight": 0.20,
        "details": comp_scores
    }

    # Dimension 5: Validation Script (weight: 0.10)
    script_scores = _score_script(data)
    dimensions["validation"] = {
        "score": sum(script_scores.values()) / max(len(script_scores), 1),
        "weight": 0.10,
        "details": script_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-01 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_listings_in_russian():
    result = grade()
    listings = result["dimensions"].get("listings", {})
    details = listings.get("details", {})
    assert details.get("russian_quality", 0) >= 0.5, (
        "Listings must be primarily in Russian"
    )


def test_pricing_reasonable():
    result = grade()
    listings = result["dimensions"].get("listings", {})
    details = listings.get("details", {})
    assert details.get("pricing_accuracy", 0) >= 0.3, (
        "Pricing should be in RUB within reasonable range"
    )


def test_compliance_tags_present():
    result = grade()
    comp = result["dimensions"].get("compliance", {})
    assert comp.get("score", 0) >= 0.3, (
        "Compliance tags (TR TS / EAC) should be generated"
    )


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["listings_ru.json", "seo_keywords_ru.txt",
                          "size_conversion_table.json", "compliance_tags.json"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify output is in Russian (Cyrillic), not English fallback."""
    data = _load_answer()
    listings = data.get("listings", [])
    if isinstance(listings, dict):
        listings = list(listings.values())
    if not listings:
        # Try loading from file
        listings_path = _find_file("listings_ru.json")
        if listings_path.exists():
            listings = json.loads(listings_path.read_text(encoding="utf-8-sig"))
            if isinstance(listings, dict):
                listings = list(listings.values())
    assert listings, "No listings data found to check language"
    blob = json.dumps(listings, ensure_ascii=False)
    cyrillic_chars = sum(1 for c in blob if 'Ѐ' <= c <= 'ӿ')
    ratio = cyrillic_chars / max(len(blob), 1)
    assert ratio > 0.15, f"Output Cyrillic ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    blob = json.dumps(data, ensure_ascii=False)
    assert len(blob) > 500, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify primary output isn't in English."""
    data = _load_answer()
    if not data:
        return
    listings = data.get("listings", [])
    if isinstance(listings, dict):
        listings = list(listings.values())
    if not listings:
        return
    blob = json.dumps(listings, ensure_ascii=False)
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', blob))
    total_chars = len(blob)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Output appears to be mostly English ({english_ratio:.0%})"


def test_item_count_sufficient():
    """Verify at least 20 listings are produced."""
    data = _load_answer()
    listings = data.get("listings", [])
    if isinstance(listings, dict):
        listings = list(listings.values())
    if not listings:
        listings_path = _find_file("listings_ru.json")
        if listings_path.exists():
            try:
                listings = json.loads(listings_path.read_text(encoding="utf-8-sig"))
                if isinstance(listings, dict):
                    listings = list(listings.values())
            except Exception:
                pass
    assert len(listings) >= 15, f"Only {len(listings)} listings produced, expected ~20"


def test_pricing_plausibility():
    """Verify prices are in RUB plausible range (500-50000)."""
    data = _load_answer()
    listings = data.get("listings", [])
    if isinstance(listings, dict):
        listings = list(listings.values())
    if not listings:
        return
    plausible = 0
    for item in listings:
        price = item.get("price_rub", item.get("price", 0))
        if isinstance(price, (int, float)) and 500 <= price <= 50000:
            plausible += 1
    ratio = plausible / max(len(listings), 1)
    assert ratio >= 0.5, f"Only {ratio:.0%} of prices in plausible RUB range (500-50000)"
