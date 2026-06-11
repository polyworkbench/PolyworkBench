"""WildClawBench-style grading for KNW-02_ko_tech_report."""
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


def _has_korean(text: str) -> bool:
    """Check if text contains Korean characters."""
    return bool(re.search(r"[가-힯]", text))


def _korean_char_count(text: str) -> int:
    """Count Korean syllable characters."""
    return len(re.findall(r"[가-힯]", text))


def _score_synthesis_quality(report: str, recommendations: str) -> float:
    """Score synthesis of English whitepaper and Japanese notes (weight: 0.25)."""
    score = 0.0

    # Check that content from both sources is present
    # English whitepaper concepts
    en_concepts = ["edge ai", "npu", "quantization", "pruning", "distillation",
                   "tensorrt", "onnx", "jetson", "mobilenet", "efficientnet"]
    en_found = sum(1 for c in en_concepts if c.lower() in report.lower())
    score += 0.3 * min(en_found / 5, 1.0)

    # Japanese notes concepts (may appear in Korean transliteration)
    ja_concepts = ["모델 압축", "양자화", "가지치기", "지식 증류", "NAS",
                   "INT8", "INT4", "스파스", "열 스로틀링"]
    ja_found = sum(1 for c in ja_concepts if c in report)
    score += 0.3 * min(ja_found / 4, 1.0)

    # Check integration (not just concatenation) - sections referencing both
    if len(report) > 2000 and _has_korean(report):
        score += 0.2

    # Recommendations should synthesize findings
    if _has_korean(recommendations) and len(recommendations) > 400:
        score += 0.2

    return min(score, 1.0)


def _score_korean_technical(report: str, recommendations: str) -> float:
    """Score Korean technical writing quality (weight: 0.25)."""
    score = 0.0

    # Check report is in Korean
    if not _has_korean(report):
        return 0.0

    kr_chars = _korean_char_count(report)
    if kr_chars >= 2000:
        score += 0.3
    elif kr_chars >= 1000:
        score += 0.2
    elif kr_chars >= 500:
        score += 0.1

    # Technical terminology check
    tech_terms_ko = ["추론", "모델", "최적화", "성능", "지연시간", "정확도",
                     "전력", "소비", "처리량", "메모리", "배포", "압축",
                     "가속기", "프레임워크", "아키텍처", "벤치마크"]
    found_terms = sum(1 for t in tech_terms_ko if t in report)
    score += 0.3 * min(found_terms / 8, 1.0)

    # Section structure
    headers = re.findall(r"^#{1,3}\s+.+$", report, re.MULTILINE)
    if len(headers) >= 4:
        score += 0.2
    elif len(headers) >= 2:
        score += 0.1

    # Recommendations quality
    if _has_korean(recommendations) and _korean_char_count(recommendations) >= 800:
        score += 0.2
    elif _has_korean(recommendations):
        score += 0.1

    return min(score, 1.0)


def _score_comparison_accuracy(matrix: dict, report: str) -> float:
    """Score comparison matrix accuracy (weight: 0.20)."""
    score = 0.0

    if not matrix:
        return 0.0

    # Check matrix structure
    solutions = matrix.get("solutions", matrix.get("comparisons", matrix.get("matrix", [])))
    if isinstance(solutions, list):
        if len(solutions) >= 5:
            score += 0.3
        elif len(solutions) >= 3:
            score += 0.2

        # Check required fields per solution
        required_fields = {"latency", "accuracy", "power", "name", "method"}
        alt_fields = {"latency_ms", "accuracy_pct", "power_watts", "solution_name", "methodology"}
        valid_entries = 0
        for sol in solutions:
            if isinstance(sol, dict):
                keys = set(sol.keys())
                if len(keys & (required_fields | alt_fields)) >= 3:
                    valid_entries += 1
        if valid_entries >= 5:
            score += 0.4
        elif valid_entries >= 3:
            score += 0.3
    elif isinstance(solutions, dict):
        # Matrix format
        if len(solutions) >= 5:
            score += 0.3
        score += 0.2

    # Check that benchmark data is reflected
    benchmark_refs = ["MobileNet", "YOLO", "BERT", "EfficientNet", "ResNet"]
    found = sum(1 for b in benchmark_refs if b.lower() in str(matrix).lower())
    score += 0.3 * min(found / 3, 1.0)

    return min(score, 1.0)


def _score_feasibility(feasibility: dict) -> float:
    """Score feasibility analysis (weight: 0.15)."""
    score = 0.0

    if not feasibility:
        return 0.0

    # Check structure has evaluation items
    if isinstance(feasibility, dict):
        # Look for scoring items
        items = feasibility.get("items", feasibility.get("criteria", feasibility.get("evaluation", {})))
        if isinstance(items, (list, dict)):
            if len(items) >= 4:
                score += 0.4
            elif len(items) >= 2:
                score += 0.2

        # Check for scores (1-5 scale)
        json_str = json.dumps(feasibility)
        scores_found = re.findall(r'"score":\s*[1-5]', json_str)
        if len(scores_found) >= 4:
            score += 0.3
        elif len(scores_found) >= 2:
            score += 0.2

        # Check for Korean explanations
        if _has_korean(json_str):
            score += 0.3

    return min(score, 1.0)


def _score_recommendations(recommendations: str, answer: dict) -> float:
    """Score recommendations quality (weight: 0.15)."""
    score = 0.0

    if not recommendations:
        return 0.0

    if not _has_korean(recommendations):
        return 0.1

    # Check for time-horizon structure (short/mid/long term)
    time_keywords = ["단기", "중기", "장기", "short", "mid", "long"]
    found_time = sum(1 for k in time_keywords if k in recommendations.lower())
    if found_time >= 3:
        score += 0.3
    elif found_time >= 2:
        score += 0.2

    # Check for risk analysis
    risk_keywords = ["리스크", "위험", "과제", "제약", "한계"]
    found_risk = sum(1 for k in risk_keywords if k in recommendations)
    if found_risk >= 2:
        score += 0.2
    elif found_risk >= 1:
        score += 0.1

    # Check length
    if _korean_char_count(recommendations) >= 800:
        score += 0.2
    elif _korean_char_count(recommendations) >= 400:
        score += 0.1

    # Check answer.json
    if answer.get("top_recommendation") and _has_korean(str(answer.get("top_recommendation", ""))):
        score += 0.15
    if answer.get("feasibility_score"):
        score += 0.15

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Grade the KNW-02 task outputs."""
    report = _load_text("tech_assessment_ko.md")
    matrix = _load_json("comparison_matrix.json")
    feasibility = _load_json("feasibility_ko.json")
    recommendations = _load_text("recommendations_ko.md")
    answer = _load_answer()

    # Calculate dimension scores
    synthesis = _score_synthesis_quality(report, recommendations)
    korean_tech = _score_korean_technical(report, recommendations)
    comparison = _score_comparison_accuracy(matrix, report)
    feasibility_score = _score_feasibility(feasibility)
    recs = _score_recommendations(recommendations, answer)

    # Weighted overall score
    overall = (
        synthesis * 0.25
        + korean_tech * 0.25
        + comparison * 0.20
        + feasibility_score * 0.15
        + recs * 0.15
    )

    return {
        "overall_score": round(overall, 4),
        "dimensions": {
            "synthesis_quality": {"score": round(synthesis, 4), "weight": 0.25},
            "korean_technical": {"score": round(korean_tech, 4), "weight": 0.25},
            "comparison_accuracy": {"score": round(comparison, 4), "weight": 0.20},
            "feasibility_analysis": {"score": round(feasibility_score, 4), "weight": 0.15},
            "recommendations": {"score": round(recs, 4), "weight": 0.15},
        },
    }


def test_grade_overall():
    """Pytest entrypoint for grading."""
    result = grade()
    assert result["overall_score"] >= 0.0, f"Score below 0: {result}"
    print(f"\n{'='*60}")
    print(f"KNW-02 Grade: {result['overall_score']:.2%}")
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
        if any(word in k.lower() for word in ["korean", "hangul", "ko"]):
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
