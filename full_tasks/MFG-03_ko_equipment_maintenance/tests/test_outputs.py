"""WildClawBench-style grading for MFG-03_ko_equipment_maintenance."""
import json
import os
import re
from pathlib import Path
from typing import Any, Dict

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


def _find_file(name: str) -> Path:
    """Search for a file in common output locations."""
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


def _load_answer() -> dict:
    """Load answer.json with fallback paths."""
    candidates = [
        OUTPUT_DIR / "answer.json",
        OUTPUT_DIR / "output" / "answer.json",
        TASK_DIR / "answer.json",
    ]
    for c in candidates:
        if c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    return {}


def _score_schedule_accuracy(data: dict) -> Dict[str, Any]:
    """Score PM schedule accuracy (weight: 0.25)."""
    score = 0.0
    details = []

    schedule_file = _find_file("pm_schedule_ko.json")
    if not schedule_file.exists():
        return {"score": 0.0, "details": ["pm_schedule_ko.json not found"]}

    try:
        schedule_data = json.loads(schedule_file.read_text(encoding="utf-8"))
        content_str = json.dumps(schedule_data, ensure_ascii=False)

        # Check for frequency categories
        frequencies = {
            "daily": any(kw in content_str for kw in ["일일", "매일", "daily", "始業"]),
            "weekly": any(kw in content_str for kw in ["주간", "매주", "weekly", "週次"]),
            "monthly": any(kw in content_str for kw in ["월간", "매월", "monthly", "月次"]),
            "quarterly": any(kw in content_str for kw in ["분기", "3개월", "quarterly", "四半期"]),
            "annual": any(kw in content_str for kw in ["연간", "매년", "annual", "年次"]),
        }
        found_freq = sum(frequencies.values())
        score += (found_freq / len(frequencies)) * 0.4
        details.append(f"Frequency categories: {found_freq}/{len(frequencies)}")

        # Check for priority levels
        has_priority = any(kw in content_str for kw in ["Critical", "High", "Medium", "Low",
                                                         "긴급", "높음", "보통", "낮음"])
        if has_priority:
            score += 0.2
            details.append("Priority levels included")

        # Check for parts and time estimates
        has_parts = any(kw in content_str for kw in ["부품", "parts", "部品", "노즐", "nozzle"])
        has_time = any(kw in content_str for kw in ["시간", "분", "time", "소요", "duration"])
        if has_parts:
            score += 0.2
            details.append("Parts requirements included")
        if has_time:
            score += 0.2
            details.append("Time estimates included")

    except json.JSONDecodeError:
        details.append("pm_schedule_ko.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def _score_korean_translation(data: dict) -> Dict[str, Any]:
    """Score Korean translation quality (weight: 0.25)."""
    score = 0.0
    details = []

    guide_file = _find_file("maintenance_guide_ko.md")
    if not guide_file.exists():
        return {"score": 0.0, "details": ["maintenance_guide_ko.md not found"]}

    content = guide_file.read_text(encoding="utf-8")

    # Check for Korean characters (Hangul)
    hangul_chars = re.findall(r'[가-힣]', content)
    if len(hangul_chars) > 200:
        score += 0.35
        details.append(f"Rich Korean content: {len(hangul_chars)} Hangul chars")
    elif len(hangul_chars) > 50:
        score += 0.2
        details.append(f"Some Korean content: {len(hangul_chars)} Hangul chars")
    else:
        details.append(f"Few Korean characters: {len(hangul_chars)}")

    # Check for Korean maintenance terminology
    ko_terms = ["장비", "보전", "점검", "교체", "윤활", "노즐", "벨트", "베어링",
                "정비", "세척", "예방", "고장"]
    found_terms = [t for t in ko_terms if t in content]
    term_score = len(found_terms) / len(ko_terms)
    score += term_score * 0.35
    details.append(f"Korean maintenance terms: {len(found_terms)}/{len(ko_terms)}")

    # Check document structure/completeness
    if len(content) > 1500:
        score += 0.15
        details.append(f"Guide length adequate: {len(content)} chars")

    # Check for sections/headers
    headers = re.findall(r'^#+\s+.+', content, re.MULTILINE)
    if len(headers) >= 3:
        score += 0.15
        details.append(f"Well-structured: {len(headers)} sections")

    return {"score": min(score, 1.0), "details": details}


def _score_parts_mapping(data: dict) -> Dict[str, Any]:
    """Score parts mapping quality (weight: 0.20)."""
    score = 0.0
    details = []

    parts_file = _find_file("parts_mapping.json")
    if not parts_file.exists():
        return {"score": 0.0, "details": ["parts_mapping.json not found"]}

    try:
        parts_data = json.loads(parts_file.read_text(encoding="utf-8"))
        content_str = json.dumps(parts_data, ensure_ascii=False)

        # Check for multilingual mapping
        has_japanese = bool(re.findall(r'[ぁ-んァ-ヶ一-龥]', content_str))
        has_english = bool(re.findall(r'[A-Z]{3}', content_str))  # Part numbers
        has_korean = bool(re.findall(r'[가-힣]', content_str))

        lang_score = sum([has_japanese, has_english, has_korean]) / 3
        score += lang_score * 0.4
        details.append(f"Languages in mapping: JA={has_japanese}, EN={has_english}, KO={has_korean}")

        # Check for part numbers from spare_parts_en.csv
        part_numbers = ["NZL-H24", "SPK-NXT", "BLT-", "FLT-", "LED-CAM", "BRG-SRV", "BSC-"]
        found_parts = sum(1 for pn in part_numbers if pn in content_str)
        parts_score = found_parts / len(part_numbers)
        score += parts_score * 0.3
        details.append(f"Part numbers mapped: {found_parts}/{len(part_numbers)}")

        # Check for safety stock recommendations
        if any(kw in content_str for kw in ["안전재고", "safety stock", "安全在庫", "재고"]):
            score += 0.15
            details.append("Safety stock recommendations included")

        # Check for cost information
        if any(kw in content_str for kw in ["가격", "비용", "USD", "price", "cost", "원"]):
            score += 0.15
            details.append("Cost information included")

    except json.JSONDecodeError:
        details.append("parts_mapping.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def _score_history_analysis(data: dict) -> Dict[str, Any]:
    """Score maintenance history analysis (weight: 0.15)."""
    score = 0.0
    details = []

    history_file = _find_file("maintenance_history_analysis.json")
    if not history_file.exists():
        return {"score": 0.0, "details": ["maintenance_history_analysis.json not found"]}

    try:
        history_data = json.loads(history_file.read_text(encoding="utf-8"))
        content_str = json.dumps(history_data, ensure_ascii=False)

        # Check for MTBF calculation
        if any(kw in content_str for kw in ["MTBF", "mtbf", "평균고장간격"]):
            score += 0.25
            details.append("MTBF included")

        # Check for MTTR calculation
        if any(kw in content_str for kw in ["MTTR", "mttr", "평균수리시간"]):
            score += 0.25
            details.append("MTTR included")

        # Check for failure pattern analysis
        if any(kw in content_str for kw in ["패턴", "pattern", "故障", "고장", "유형"]):
            score += 0.25
            details.append("Failure patterns analyzed")

        # Check answer.json for MTBF/MTTR values
        if "avg_mtbf_hours" in data:
            mtbf = data["avg_mtbf_hours"]
            if isinstance(mtbf, (int, float)) and 200 <= mtbf <= 2000:
                score += 0.125
                details.append(f"MTBF value {mtbf:.1f}h reasonable")
        if "avg_mttr_hours" in data:
            mttr = data["avg_mttr_hours"]
            if isinstance(mttr, (int, float)) and 0.5 <= mttr <= 10:
                score += 0.125
                details.append(f"MTTR value {mttr:.1f}h reasonable")

    except json.JSONDecodeError:
        details.append("maintenance_history_analysis.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def _score_completeness(data: dict) -> Dict[str, Any]:
    """Score overall completeness (weight: 0.15)."""
    score = 0.0
    details = []

    # Check all output files exist
    required_files = ["pm_schedule_ko.json", "maintenance_guide_ko.md",
                      "parts_mapping.json", "maintenance_history_analysis.json"]
    existing = [f for f in required_files if _find_file(f).exists()]
    file_score = len(existing) / len(required_files)
    score += file_score * 0.4
    details.append(f"Output files: {len(existing)}/{len(required_files)}")

    # Check answer.json completeness
    required_answer_fields = ["total_pm_items", "annual_cost_estimate_usd",
                              "critical_items", "avg_mtbf_hours", "avg_mttr_hours", "total_spare_parts"]
    present = [f for f in required_answer_fields if f in data]
    answer_score = len(present) / len(required_answer_fields)
    score += answer_score * 0.3
    details.append(f"Answer fields: {len(present)}/{len(required_answer_fields)}")

    # Check for cost analysis
    if "annual_cost_estimate_usd" in data:
        cost = data["annual_cost_estimate_usd"]
        if isinstance(cost, (int, float)) and cost > 0:
            score += 0.15
            details.append(f"Annual cost estimate: ${cost:,.2f}")

    # Check total PM items is reasonable
    if "total_pm_items" in data:
        items = data["total_pm_items"]
        if isinstance(items, int) and 10 <= items <= 100:
            score += 0.15
            details.append(f"Total PM items: {items}")

    return {"score": min(score, 1.0), "details": details}


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading. Returns {overall_score, dimensions}."""
    data = _load_answer()

    dimensions = {
        "schedule_accuracy": _score_schedule_accuracy(data),
        "korean_translation": _score_korean_translation(data),
        "parts_mapping": _score_parts_mapping(data),
        "history_analysis": _score_history_analysis(data),
        "completeness": _score_completeness(data),
    }

    weights = {
        "schedule_accuracy": 0.25,
        "korean_translation": 0.25,
        "parts_mapping": 0.20,
        "history_analysis": 0.15,
        "completeness": 0.15,
    }

    overall = sum(dimensions[k]["score"] * weights[k] for k in dimensions)

    return {
        "overall_score": round(overall, 4),
        "dimensions": dimensions,
    }


def test_grade_overall():
    """Pytest entry point."""
    result = grade()
    assert result["overall_score"] >= 0.15, f"Score too low: {result['overall_score']}"
    print(f"\n{'='*60}")
    print(f"OVERALL SCORE: {result['overall_score']:.4f}")
    print(f"{'='*60}")
    for dim, info in result["dimensions"].items():
        print(f"  {dim}: {info['score']:.4f}")
        for detail in info["details"]:
            print(f"    - {detail}")
    assert result["overall_score"] >= 0.2, f"Score too low: {result['overall_score']}"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["pm_schedule_ko.json", "maintenance_guide_ko.md",
                          "parts_mapping.json", "maintenance_history_analysis.json"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify maintenance guide is in Korean (Hangul), not English fallback."""
    guide_file = _find_file("maintenance_guide_ko.md")
    if not guide_file.exists():
        return
    content = guide_file.read_text(encoding="utf-8")
    hangul_chars = sum(1 for c in content if '가' <= c <= '힣')
    total_chars = len(content.replace(" ", "").replace("\n", ""))
    ratio = hangul_chars / max(total_chars, 1)
    assert ratio > 0.2, f"Korean guide Hangul ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    blob = json.dumps(data, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Korean guide isn't in English."""
    guide_file = _find_file("maintenance_guide_ko.md")
    if not guide_file.exists():
        return
    text = guide_file.read_text(encoding="utf-8")
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Guide appears to be mostly English ({english_ratio:.0%})"


def test_maintenance_schedule_items():
    """Verify PM schedule has sufficient items."""
    schedule_file = _find_file("pm_schedule_ko.json")
    if not schedule_file.exists():
        return
    try:
        schedule_data = json.loads(schedule_file.read_text(encoding="utf-8"))
    except Exception:
        return
    # Should have multiple PM items
    if isinstance(schedule_data, list):
        count = len(schedule_data)
    elif isinstance(schedule_data, dict):
        count = len(schedule_data.get("items", schedule_data.get("schedule", schedule_data)))
        if isinstance(count, dict):
            count = len(count)
    else:
        count = 0
    assert count >= 5, f"Only {count} PM schedule items, expected at least 5"
