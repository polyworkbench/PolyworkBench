"""
BabelAgentBench grading for KNW-09: Korean academic peer review simulation.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

REVIEW_CRITERIA = ["novelty", "methodology", "clarity", "significance"]
MIN_REVISION_SUGGESTIONS = 8

KOREAN_ACADEMIC_MARKERS = [
    "논문", "연구", "제안", "방법론", "실험",
    "결과", "기여", "한계", "개선", "평가",
    "분석", "비교", "성능", "모델"
]


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_json(name: str) -> Any:
    path = _find_file(name)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return None


def _load_text(name: str) -> str:
    path = _find_file(name)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            pass
    return ""


def _is_korean(text: str) -> bool:
    """Check if text contains significant Korean characters."""
    if not text:
        return False
    hangul_count = sum(1 for c in text if '가' <= c <= '힯' or
                       'ᄀ' <= c <= 'ᇿ' or '㄰' <= c <= '㆏')
    return hangul_count / max(len(text), 1) > 0.15


def _score_review_quality(review_text: str) -> Dict[str, float]:
    """Score the quality of review comments."""
    scores = {}

    if not review_text:
        return {"review_exists": 0.0, "length": 0.0,
                "strengths_weaknesses": 0.0, "specificity": 0.0}

    scores["review_exists"] = 1.0

    # Check length
    char_count = len(review_text)
    if char_count >= 2000:
        scores["length"] = 1.0
    elif char_count >= 1000:
        scores["length"] = 0.7
    elif char_count >= 500:
        scores["length"] = 0.4
    else:
        scores["length"] = 0.2

    # Check for strengths and weaknesses sections
    text_lower = review_text.lower()
    has_strengths = any(m in review_text for m in
                        ["strengths", "strong", "strength",
                         "Strengths", "Strong"]) or \
                   any(m in review_text for m in
                       ["강점", "장점", "우수"])
    has_weaknesses = any(m in review_text for m in
                         ["weakness", "weak", "limitation",
                          "Weakness", "Limitation"]) or \
                    any(m in review_text for m in
                        ["약점", "단점", "한계", "부족"])
    scores["strengths_weaknesses"] = (has_strengths + has_weaknesses) / 2.0

    # Check specificity (references to specific sections, numbers, methods)
    specific_refs = 0
    if re.search(r'(section|table|figure|equation|\d+\.\d+)', text_lower):
        specific_refs += 1
    if re.search(r'(4\.7|8\.2|73\.1|47|1\.05|86)', review_text):
        specific_refs += 1
    if any(m in review_text for m in ["MultiX-Transfer", "MBA", "modality-bridging",
                                       "VisAnchor", "MKD"]):
        specific_refs += 1
    scores["specificity"] = min(1.0, specific_refs / 2.0)

    return scores


def _score_korean_academic_style(review_text: str, suggestions_data: Any) -> Dict[str, float]:
    """Score Korean academic writing style."""
    scores = {}

    if not review_text:
        return {"is_korean": 0.0, "academic_vocabulary": 0.0, "formal_tone": 0.0}

    scores["is_korean"] = 1.0 if _is_korean(review_text) else 0.0

    # Check academic vocabulary
    kr_found = sum(1 for m in KOREAN_ACADEMIC_MARKERS if m in review_text)
    scores["academic_vocabulary"] = min(1.0, kr_found / 7.0)

    # Check formal tone (Korean formal endings)
    formal_endings = ["입니다", "습니다", "됩니다",
                      "있습니다", "바랍니다", "것입니다",
                      "필요합니다", "보입니다"]
    formal_count = sum(1 for e in formal_endings if e in review_text)
    scores["formal_tone"] = min(1.0, formal_count / 4.0)

    return scores


def _score_reference_integration(ref_comparison: Any) -> Dict[str, float]:
    """Score reference paper integration."""
    scores = {}

    if not ref_comparison:
        return {"comparison_exists": 0.0, "both_refs_covered": 0.0,
                "method_comparison": 0.0}

    scores["comparison_exists"] = 1.0

    # Check if both reference papers are covered
    ref_str = json.dumps(ref_comparison, ensure_ascii=False)
    has_zh_ref = any(m in ref_str for m in ["VisAnchor", "Wang", "ACL 2024",
                                             "visual-anchor", "446M"])
    has_ja_ref = any(m in ref_str for m in ["MKD", "Sato", "EMNLP 2024",
                                             "distillation", "4800"])
    scores["both_refs_covered"] = (has_zh_ref + has_ja_ref) / 2.0

    # Check for methodological comparison
    comparison_keys = ["method", "approach", "architecture", "performance",
                       "compute", "parameter", "dataset", "training"]
    kr_comparison_keys = ["방법", "성능", "파라미터", "데이터",
                          "훈련", "비교", "차이"]
    found = sum(1 for k in comparison_keys + kr_comparison_keys
                if k in ref_str.lower())
    scores["method_comparison"] = min(1.0, found / 4.0)

    return scores


def _score_constructiveness(suggestions_data: Any) -> Dict[str, float]:
    """Score constructiveness of revision suggestions."""
    scores = {}

    if not suggestions_data:
        return {"suggestions_exist": 0.0, "suggestion_count": 0.0,
                "priority_assigned": 0.0}

    scores["suggestions_exist"] = 1.0

    # Extract suggestions list
    if isinstance(suggestions_data, list):
        suggestions = suggestions_data
    elif isinstance(suggestions_data, dict):
        suggestions = suggestions_data.get("suggestions",
                     suggestions_data.get("revision_suggestions",
                     suggestions_data.get("revisions", list(suggestions_data.values()))))
        if not isinstance(suggestions, list):
            suggestions = [suggestions]
    else:
        suggestions = []

    scores["suggestion_count"] = min(1.0, len(suggestions) / MIN_REVISION_SUGGESTIONS)

    # Check priority assignment
    prioritized = 0
    for s in suggestions:
        if isinstance(s, dict):
            if any(k in s for k in ["priority", "importance",
                                     "urgency"]):
                prioritized += 1
            elif any(k in s for k in ["우선순위", "중요도"]):
                prioritized += 1
    scores["priority_assigned"] = min(1.0, prioritized / max(len(suggestions), 1))

    return scores


def _score_criteria_coverage(eval_matrix: Any) -> Dict[str, float]:
    """Score coverage of evaluation criteria."""
    scores = {}

    if not eval_matrix:
        return {"matrix_exists": 0.0, "criteria_covered": 0.0,
                "scores_valid": 0.0}

    scores["matrix_exists"] = 1.0

    # Check if all criteria are covered
    matrix_str = json.dumps(eval_matrix, ensure_ascii=False).lower()
    covered = sum(1 for c in REVIEW_CRITERIA if c in matrix_str)
    # Also check Korean equivalents
    kr_criteria = ["참신성", "방법론", "명확성", "중요성"]
    kr_covered = sum(1 for c in kr_criteria if c in matrix_str)
    scores["criteria_covered"] = min(1.0, max(covered, kr_covered) / 4.0)

    # Check if scores are valid (1-10 range)
    numbers = re.findall(r'(?:score|점수|rating).*?(\d+)', matrix_str)
    if not numbers:
        # Try to find any numbers in range
        all_numbers = re.findall(r'\b(\d+)\b', matrix_str)
        numbers = [n for n in all_numbers if 1 <= int(n) <= 10]
    if numbers:
        valid = sum(1 for n in numbers if 1 <= int(n) <= 10)
        scores["scores_valid"] = min(1.0, valid / 4.0)
    else:
        scores["scores_valid"] = 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for KNW-09."""
    review_text = _load_text("review_comments_ko.md")
    eval_matrix = _load_json("evaluation_matrix.json")
    suggestions_data = _load_json("revision_suggestions_ko.json")
    ref_comparison = _load_json("reference_comparison.json")

    dimensions = {}

    # Dimension 1: Review Quality (weight: 0.25)
    review_scores = _score_review_quality(review_text)
    dimensions["review_quality"] = {
        "score": sum(review_scores.values()) / max(len(review_scores), 1),
        "weight": 0.25,
        "details": review_scores
    }

    # Dimension 2: Korean Academic Style (weight: 0.25)
    style_scores = _score_korean_academic_style(review_text, suggestions_data)
    dimensions["korean_academic_style"] = {
        "score": sum(style_scores.values()) / max(len(style_scores), 1),
        "weight": 0.25,
        "details": style_scores
    }

    # Dimension 3: Reference Integration (weight: 0.20)
    ref_scores = _score_reference_integration(ref_comparison)
    dimensions["reference_integration"] = {
        "score": sum(ref_scores.values()) / max(len(ref_scores), 1),
        "weight": 0.20,
        "details": ref_scores
    }

    # Dimension 4: Constructiveness (weight: 0.15)
    const_scores = _score_constructiveness(suggestions_data)
    dimensions["constructiveness"] = {
        "score": sum(const_scores.values()) / max(len(const_scores), 1),
        "weight": 0.15,
        "details": const_scores
    }

    # Dimension 5: Criteria Coverage (weight: 0.15)
    crit_scores = _score_criteria_coverage(eval_matrix)
    dimensions["criteria_coverage"] = {
        "score": sum(crit_scores.values()) / max(len(crit_scores), 1),
        "weight": 0.15,
        "details": crit_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"KNW-09 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_review_in_korean():
    text = _load_text("review_comments_ko.md")
    assert text, "review_comments_ko.md not found or empty"
    assert _is_korean(text), "Review comments must be in Korean"


def test_evaluation_matrix_covers_criteria():
    data = _load_json("evaluation_matrix.json")
    assert data, "evaluation_matrix.json not found or empty"
    matrix_str = json.dumps(data, ensure_ascii=False).lower()
    # Check at least 3 of 4 criteria
    criteria_found = sum(1 for c in REVIEW_CRITERIA if c in matrix_str)
    kr_criteria = ["참신성", "방법론", "명확성", "중요성"]
    kr_found = sum(1 for c in kr_criteria if c in matrix_str)
    assert max(criteria_found, kr_found) >= 3, (
        "Evaluation matrix must cover at least 3 of 4 review criteria"
    )


def test_revision_suggestions_minimum():
    data = _load_json("revision_suggestions_ko.json")
    assert data, "revision_suggestions_ko.json not found or empty"
    if isinstance(data, list):
        suggestions = data
    elif isinstance(data, dict):
        suggestions = data.get("suggestions", data.get("revision_suggestions",
                      data.get("revisions", list(data.values()))))
    else:
        suggestions = []
    assert len(suggestions) >= 5, (
        f"Expected at least 5 revision suggestions, got {len(suggestions)}"
    )


def test_reference_comparison_exists():
    data = _load_json("reference_comparison.json")
    assert data, "reference_comparison.json not found or empty"
    ref_str = json.dumps(data, ensure_ascii=False)
    assert ("VisAnchor" in ref_str or "Wang" in ref_str or
            "ACL" in ref_str), "Must reference Chinese paper"
    assert ("MKD" in ref_str or "Sato" in ref_str or
            "EMNLP" in ref_str), "Must reference Japanese paper"


def test_review_mentions_paper_specifics():
    text = _load_text("review_comments_ko.md")
    assert text, "review_comments_ko.md not found"
    # Should mention specific elements from the paper
    has_specific = any(m in text for m in
                       ["MultiX-Transfer", "MBA", "modality-bridging",
                        "47", "4.7", "73.1", "86,000",
                        "1.05"])
    assert has_specific, "Review should reference specific paper content"


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
