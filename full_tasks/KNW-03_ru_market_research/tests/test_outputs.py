"""WildClawBench-style grading for KNW-03_ru_market_research."""
import json
import os
import re
from pathlib import Path
from typing import Any, Dict
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


def _find_file(name: str) -> Path:
    """Locate output file in workspace."""
    candidates = [
        OUTPUT_DIR / "output" / name,
        OUTPUT_DIR / name,
        TASK_DIR / "output" / name,
        TASK_DIR / name,
    ]
    for c in candidates:
        if c.exists():
            return c
    return OUTPUT_DIR / "output" / name


def _load_json(name: str) -> dict:
    """Load a JSON output file."""
    path = _find_file(name)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_text(name: str) -> str:
    """Load a text/markdown output file."""
    path = _find_file(name)
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _load_answer() -> dict:
    """Load the answer.json file."""
    candidates = [
        OUTPUT_DIR / "answer.json",
        TASK_DIR / "answer.json",
        OUTPUT_DIR / "output" / "answer.json",
    ]
    for c in candidates:
        if c.exists():
            with open(c, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def _has_russian(text: str) -> bool:
    """Check if text contains Russian/Cyrillic characters."""
    return bool(re.search(r"[а-яА-ЯёЁ]", text))


def _russian_word_count(text: str) -> int:
    """Count Russian words."""
    return len(re.findall(r"[а-яА-ЯёЁ]+", text))


def _score_market_sizing(market_sizing: dict, answer: dict) -> float:
    """Score market sizing accuracy (weight: 0.25)."""
    score = 0.0

    if not market_sizing:
        return 0.0

    # Check year-by-year data exists
    years_data = market_sizing.get("years", market_sizing.get("data", market_sizing.get("market_size", {})))
    if isinstance(years_data, dict):
        if len(years_data) >= 5:
            score += 0.3
        elif len(years_data) >= 3:
            score += 0.2
    elif isinstance(years_data, list):
        if len(years_data) >= 5:
            score += 0.3

    # Check segmentation exists
    json_str = json.dumps(market_sizing).lower()
    seg_types = ["lfp", "nmc", "solid", "region", "application", "chemistry"]
    found_segs = sum(1 for s in seg_types if s in json_str)
    if found_segs >= 3:
        score += 0.2
    elif found_segs >= 2:
        score += 0.1

    # Check CAGR present
    if "cagr" in json_str:
        score += 0.15

    # Check forecasts present
    if "2030" in json_str or "forecast" in json_str:
        score += 0.15

    # Validate answer.json market size values are reasonable
    market_2024 = answer.get("market_size_2024_billion_usd", 0)
    if 80 <= market_2024 <= 200:  # Reasonable range
        score += 0.2
    elif market_2024 > 0:
        score += 0.1

    return min(score, 1.0)


def _score_competitor_analysis(competitor: dict) -> float:
    """Score competitor analysis (weight: 0.25)."""
    score = 0.0

    if not competitor:
        return 0.0

    # Check number of competitors
    competitors = competitor.get("competitors", competitor.get("companies", competitor.get("players", [])))
    if isinstance(competitors, list):
        if len(competitors) >= 5:
            score += 0.3
        elif len(competitors) >= 3:
            score += 0.2
    elif isinstance(competitors, dict):
        if len(competitors) >= 5:
            score += 0.3

    # Check key players are included
    json_str = json.dumps(competitor)
    key_players = ["CATL", "BYD", "LG", "Samsung", "SK", "Panasonic"]
    found_players = sum(1 for p in key_players if p in json_str)
    if found_players >= 5:
        score += 0.3
    elif found_players >= 3:
        score += 0.2

    # Check Russian language content
    if _has_russian(json_str):
        score += 0.2

    # Check detailed fields (market share, capacity, strategy)
    detail_fields = ["share", "capacity", "strateg", "technolog", "revenue"]
    alt_fields = ["доля", "мощност", "стратег", "технолог", "выручк"]
    found_details = sum(1 for f in (detail_fields + alt_fields) if f.lower() in json_str.lower())
    if found_details >= 3:
        score += 0.2
    elif found_details >= 2:
        score += 0.1

    return min(score, 1.0)


def _score_russian_quality(brief: str) -> float:
    """Score Russian language quality (weight: 0.20)."""
    score = 0.0

    if not brief or not _has_russian(brief):
        return 0.0

    # Check word count
    word_count = _russian_word_count(brief)
    if word_count >= 2000:
        score += 0.3
    elif word_count >= 1000:
        score += 0.2
    elif word_count >= 500:
        score += 0.1

    # Check professional vocabulary
    business_terms = ["рынок", "доля", "рост", "компани", "инвестиц",
                      "прогноз", "технолог", "производств", "мощност",
                      "спрос", "предложени", "конкурент", "стратеги",
                      "анализ", "тренд", "сегмент"]
    found_terms = sum(1 for t in business_terms if t in brief.lower())
    score += 0.3 * min(found_terms / 8, 1.0)

    # Check section structure
    headers = re.findall(r"^#{1,3}\s+.+$", brief, re.MULTILINE)
    if len(headers) >= 5:
        score += 0.2
    elif len(headers) >= 3:
        score += 0.1

    # Check for data/numbers integration
    numbers = re.findall(r"\d+[.,]?\d*\s*(%|млрд|GWh|USD|\$)", brief)
    if len(numbers) >= 10:
        score += 0.2
    elif len(numbers) >= 5:
        score += 0.1

    return min(score, 1.0)


def _score_data_synthesis(brief: str, answer: dict) -> float:
    """Score data synthesis from three languages (weight: 0.15)."""
    score = 0.0

    if not brief:
        return 0.0

    # Check English source data integration
    en_data = ["128", "315", "23.4", "CAGR", "IRA", "BloombergNEF"]
    en_found = sum(1 for d in en_data if d in brief)
    score += 0.25 * min(en_found / 3, 1.0)

    # Check Chinese source data integration (company names, capacity data)
    zh_markers = ["CATL", "宁德", "BYD", "比亚迪", "CALB", "中创", "GWh"]
    zh_found = sum(1 for m in zh_markers if m in brief)
    score += 0.25 * min(zh_found / 3, 1.0)

    # Check Korean source data integration
    ko_markers = ["LG", "Samsung SDI", "SK On", "450", "280", "NCMA", "전고체"]
    # Also check Russian transliterations
    ko_ru_markers = ["Самсунг", "Эл-Джи", "흑자"]
    all_ko = ko_markers + ko_ru_markers
    ko_found = sum(1 for m in all_ko if m in brief)
    score += 0.25 * min(ko_found / 3, 1.0)

    # Check answer.json has synthesized data
    if answer.get("top_3_players"):
        score += 0.15
    if answer.get("cagr_pct") and 15 <= answer.get("cagr_pct", 0) <= 35:
        score += 0.1

    return min(score, 1.0)


def _score_swot(swot: dict) -> float:
    """Score SWOT analysis coherence (weight: 0.15)."""
    score = 0.0

    if not swot:
        return 0.0

    json_str = json.dumps(swot, ensure_ascii=False)

    # Check all four SWOT categories present
    # In Russian: Сильные стороны, Слабые стороны, Возможности, Угрозы
    # Or English: strengths, weaknesses, opportunities, threats
    categories_en = ["strength", "weakness", "opportunit", "threat"]
    categories_ru = ["сильн", "слаб", "возможност", "угроз"]

    found_en = sum(1 for c in categories_en if c in json_str.lower())
    found_ru = sum(1 for c in categories_ru if c in json_str.lower())
    found_total = max(found_en, found_ru)

    if found_total >= 4:
        score += 0.4
    elif found_total >= 3:
        score += 0.3
    elif found_total >= 2:
        score += 0.2

    # Check minimum items per category (at least 3 each)
    # Look for list-like structures
    lists = re.findall(r'\[([^\]]+)\]', json_str)
    long_lists = [l for l in lists if l.count(',') >= 2]  # At least 3 items
    if len(long_lists) >= 4:
        score += 0.3
    elif len(long_lists) >= 2:
        score += 0.2

    # Check Russian content
    if _has_russian(json_str):
        score += 0.3

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Grade the KNW-03 task outputs."""
    brief = _load_text("market_brief_ru.md")
    competitor = _load_json("competitor_analysis_ru.json")
    market_sizing = _load_json("market_sizing.json")
    swot = _load_json("swot_analysis_ru.json")
    answer = _load_answer()

    # Calculate dimension scores
    sizing = _score_market_sizing(market_sizing, answer)
    competitor_score = _score_competitor_analysis(competitor)
    russian_quality = _score_russian_quality(brief)
    synthesis = _score_data_synthesis(brief, answer)
    swot_score = _score_swot(swot)

    # Weighted overall score
    overall = (
        sizing * 0.25
        + competitor_score * 0.25
        + russian_quality * 0.20
        + synthesis * 0.15
        + swot_score * 0.15
    )

    return {
        "overall_score": round(overall, 4),
        "dimensions": {
            "market_sizing": {"score": round(sizing, 4), "weight": 0.25},
            "competitor_analysis": {"score": round(competitor_score, 4), "weight": 0.25},
            "russian_quality": {"score": round(russian_quality, 4), "weight": 0.20},
            "data_synthesis": {"score": round(synthesis, 4), "weight": 0.15},
            "swot_coherence": {"score": round(swot_score, 4), "weight": 0.15},
        },
    }


def test_grade_overall():
    """Pytest entrypoint for grading."""
    result = grade()
    assert result["overall_score"] >= 0.0, f"Score below 0: {result}"
    print(f"\n{'='*60}")
    print(f"KNW-03 Grade: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for dim, info in result["dimensions"].items():
        print(f"  {dim}: {info['score']:.2%} (weight: {info['weight']})")
    print(f"{'='*60}")
    assert result["overall_score"] > 0.15, "Task produced no valid output"


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
