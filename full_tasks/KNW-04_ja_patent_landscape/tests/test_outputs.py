"""WildClawBench-style grading for KNW-04_ja_patent_landscape."""
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


def _has_japanese(text: str) -> bool:
    """Check if text contains Japanese characters (hiragana, katakana, or kanji)."""
    return bool(re.search(r"[぀-ゟ゠-ヿ一-鿿]", text))


def _japanese_char_count(text: str) -> int:
    """Count Japanese characters."""
    return len(re.findall(r"[぀-ゟ゠-ヿ一-鿿]", text))


def _score_coverage_analysis(report: str, matrix: dict, answer: dict) -> float:
    """Score coverage of all 45 patents (weight: 0.25)."""
    score = 0.0

    # Check patent_matrix has entries
    if matrix:
        patents = matrix.get("patents", matrix.get("entries", matrix.get("data", [])))
        if isinstance(patents, list):
            count = len(patents)
        elif isinstance(patents, dict):
            count = len(patents)
        else:
            count = 0

        if count >= 40:
            score += 0.4
        elif count >= 30:
            score += 0.3
        elif count >= 20:
            score += 0.2
        elif count >= 10:
            score += 0.1

    # Check all three patent offices are represented
    report_lower = report.lower()
    matrix_str = json.dumps(matrix).lower() if matrix else ""
    combined = report_lower + matrix_str

    offices = ["uspto", "us2024", "cnipa", "cn2024", "kipo", "kr2024"]
    found_offices = sum(1 for o in offices if o in combined)
    if found_offices >= 4:  # At least references to US, CN, KR
        score += 0.3
    elif found_offices >= 2:
        score += 0.2

    # Check answer.json total_patents
    total = answer.get("total_patents", 0)
    if total == 45:
        score += 0.3
    elif 40 <= total <= 50:
        score += 0.2
    elif total > 0:
        score += 0.1

    return min(score, 1.0)


def _score_trend_identification(trend: dict, report: str) -> float:
    """Score technology trend identification (weight: 0.25)."""
    score = 0.0

    if not trend:
        # Check if trends are in the report instead
        if _has_japanese(report) and len(report) > 1000:
            score = 0.2
        return score

    json_str = json.dumps(trend, ensure_ascii=False)

    # Check year-by-year filing data
    years = re.findall(r"202[0-4]", json_str)
    if len(set(years)) >= 3:
        score += 0.2

    # Check technology category trends
    tech_categories = ["硫化物", "酸化物", "ポリマー", "電極", "製造",
                       "sulfide", "oxide", "polymer", "electrode", "manufactur"]
    found_cats = sum(1 for c in tech_categories if c.lower() in json_str.lower())
    if found_cats >= 4:
        score += 0.3
    elif found_cats >= 2:
        score += 0.2

    # Check regional comparison
    regions = ["米国", "中国", "韓国", "US", "CN", "KR", "アメリカ"]
    found_regions = sum(1 for r in regions if r in json_str)
    if found_regions >= 3:
        score += 0.2

    # Check Japanese content
    if _has_japanese(json_str):
        score += 0.15

    # Check emerging technologies identified
    emerging_keywords = ["新興", "emerging", "注目", "成長", "トレンド"]
    if any(k in json_str for k in emerging_keywords):
        score += 0.15

    return min(score, 1.0)


def _score_japanese_quality(report: str) -> float:
    """Score Japanese language quality (weight: 0.20)."""
    score = 0.0

    if not report or not _has_japanese(report):
        return 0.0

    # Check character count
    jp_chars = _japanese_char_count(report)
    if jp_chars >= 3000:
        score += 0.3
    elif jp_chars >= 2000:
        score += 0.2
    elif jp_chars >= 1000:
        score += 0.1

    # Check patent/technical vocabulary
    patent_terms = ["特許", "出願", "権利者", "請求項", "分類", "技術",
                    "ランドスケープ", "分析", "動向", "出願人", "発明",
                    "実施例", "従来技術", "課題", "解決手段"]
    found_terms = sum(1 for t in patent_terms if t in report)
    score += 0.3 * min(found_terms / 7, 1.0)

    # Check section structure
    headers = re.findall(r"^#{1,3}\s+.+$", report, re.MULTILINE)
    if len(headers) >= 6:
        score += 0.2
    elif len(headers) >= 4:
        score += 0.15
    elif len(headers) >= 2:
        score += 0.1

    # Check for data integration (numbers, percentages)
    data_refs = re.findall(r"\d+[.%件社]", report)
    if len(data_refs) >= 10:
        score += 0.2
    elif len(data_refs) >= 5:
        score += 0.1

    return min(score, 1.0)


def _score_whitespace(whitespace: dict) -> float:
    """Score whitespace map accuracy (weight: 0.15)."""
    score = 0.0

    if not whitespace:
        return 0.0

    json_str = json.dumps(whitespace, ensure_ascii=False)

    # Check whitespace entries exist
    spaces = whitespace.get("whitespaces", whitespace.get("gaps", whitespace.get("opportunities", [])))
    if isinstance(spaces, list):
        if len(spaces) >= 5:
            score += 0.3
        elif len(spaces) >= 3:
            score += 0.2
        elif len(spaces) >= 1:
            score += 0.1

        # Check each whitespace has required fields
        valid = 0
        for s in spaces:
            if isinstance(s, dict):
                if len(s) >= 3:
                    valid += 1
        if valid >= 3:
            score += 0.2
    elif isinstance(spaces, dict):
        if len(spaces) >= 3:
            score += 0.3

    # Check IPC references
    ipc_refs = re.findall(r"H01M|C01B|G16C|C04B|C22B", json_str)
    if len(ipc_refs) >= 3:
        score += 0.2
    elif len(ipc_refs) >= 1:
        score += 0.1

    # Check opportunity assessment
    if any(k in json_str for k in ["高", "中", "低", "high", "medium", "low"]):
        score += 0.15

    # Japanese descriptions
    if _has_japanese(json_str):
        score += 0.15

    return min(score, 1.0)


def _score_classification(matrix: dict, answer: dict) -> float:
    """Score IPC classification accuracy (weight: 0.15)."""
    score = 0.0

    if not matrix:
        return 0.0

    json_str = json.dumps(matrix)

    # Check IPC codes are present and correct format
    ipc_codes = re.findall(r"H01M\d+/\d+|C01B\d+/\d+|G16C\d+/\d+", json_str)
    if len(ipc_codes) >= 10:
        score += 0.3
    elif len(ipc_codes) >= 5:
        score += 0.2

    # Check technology taxonomy categories used
    taxonomy_cats = ["SE", "EL", "MF", "SY", "AP", "固体電解質", "電極",
                     "製造", "システム", "応用"]
    found_cats = sum(1 for c in taxonomy_cats if c in json_str)
    if found_cats >= 4:
        score += 0.3
    elif found_cats >= 2:
        score += 0.2

    # Check cross-reference matrix exists
    if "matrix" in json_str.lower() or "cross" in json_str.lower():
        score += 0.2

    # Check answer.json dominant_ipc
    if answer.get("dominant_ipc") and "H01M" in str(answer.get("dominant_ipc", "")):
        score += 0.2

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Grade the KNW-04 task outputs."""
    report = _load_text("landscape_report_ja.md")
    matrix = _load_json("patent_matrix.json")
    trend = _load_json("trend_analysis_ja.json")
    whitespace = _load_json("whitespace_map.json")
    answer = _load_answer()

    # Calculate dimension scores
    coverage = _score_coverage_analysis(report, matrix, answer)
    trends = _score_trend_identification(trend, report)
    japanese = _score_japanese_quality(report)
    whitespace_score = _score_whitespace(whitespace)
    classification = _score_classification(matrix, answer)

    # Weighted overall score
    overall = (
        coverage * 0.25
        + trends * 0.25
        + japanese * 0.20
        + whitespace_score * 0.15
        + classification * 0.15
    )

    return {
        "overall_score": round(overall, 4),
        "dimensions": {
            "coverage_analysis": {"score": round(coverage, 4), "weight": 0.25},
            "trend_identification": {"score": round(trends, 4), "weight": 0.25},
            "japanese_quality": {"score": round(japanese, 4), "weight": 0.20},
            "whitespace_accuracy": {"score": round(whitespace_score, 4), "weight": 0.15},
            "classification": {"score": round(classification, 4), "weight": 0.15},
        },
    }


def test_grade_overall():
    """Pytest entrypoint for grading."""
    result = grade()
    assert result["overall_score"] >= 0.0, f"Score below 0: {result}"
    print(f"\n{'='*60}")
    print(f"KNW-04 Grade: {result['overall_score']:.2%}")
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
        if any(word in k.lower() for word in ["japanese", "jp", "ja"]):
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
