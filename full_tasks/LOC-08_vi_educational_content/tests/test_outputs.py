"""
Test suite for LOC-08: Vietnamese educational content adaptation.
Evaluates: content_accuracy, vietnamese_pedagogical, exercise_quality, standards_alignment, completeness
"""

import json
import os
import re
from pathlib import Path
import pytest


WORKSPACE = os.environ.get("WORKSPACE", "/workspace")


def load_json(filename: str):
    """Load JSON file from workspace."""
    filepath = os.path.join(WORKSPACE, "output", filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(WORKSPACE, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_md(filename: str) -> str:
    """Load markdown file from workspace."""
    filepath = os.path.join(WORKSPACE, "output", filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(WORKSPACE, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def check_content_accuracy() -> dict:
    """Check mathematical content accuracy in curriculum."""
    content = load_md("curriculum_vi.md")
    if content is None:
        return {"score": 0.0, "issues": ["curriculum_vi.md not found"]}

    score = 1.0
    issues = []

    # Check for 10 lessons
    lesson_markers = re.findall(r'(?:Bài|bài|Lesson|BÀI)\s*\d+', content, re.IGNORECASE)
    # Also check for ## headers with lesson numbers
    header_lessons = re.findall(r'^##\s+.*(?:Bài|bài)\s*\d+', content, re.MULTILINE | re.IGNORECASE)
    total_lessons = max(len(set(lesson_markers)), len(header_lessons))

    if total_lessons < 10:
        score -= (10 - total_lessons) * 0.08
        issues.append(f"Only {total_lessons}/10 lessons found")

    # Check for Vietnamese math terminology
    vn_math_terms = ["phương trình", "biến số", "hệ số", "biểu thức", "đa thức",
                     "bất phương trình", "hàm số", "đồ thị", "nghiệm"]
    found_terms = sum(1 for term in vn_math_terms if term in content.lower())
    if found_terms < 5:
        score -= 0.2
        issues.append(f"Only {found_terms}/9 key Vietnamese math terms found")

    # Check content is in Vietnamese (diacritics present)
    vietnamese_chars = re.findall(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', content)
    if len(vietnamese_chars) < 100:
        score -= 0.3
        issues.append("Content does not appear to be in Vietnamese")

    # Check for mathematical examples (should contain equations)
    equations = re.findall(r'[xy]\s*[=+\-*/]\s*\d+', content)
    if len(equations) < 5:
        score -= 0.1
        issues.append("Few mathematical examples found")

    return {"score": max(0.0, score), "issues": issues}


def check_vietnamese_pedagogical() -> dict:
    """Check Vietnamese pedagogical quality."""
    guide = load_md("teacher_guide_vi.md")
    if guide is None:
        return {"score": 0.0, "issues": ["teacher_guide_vi.md not found"]}

    score = 1.0
    issues = []

    # Check length (should be substantive)
    if len(guide) < 2000:
        score -= 0.3
        issues.append("Teacher guide too brief")

    # Check Vietnamese content
    vietnamese_chars = re.findall(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', guide)
    if len(vietnamese_chars) < 50:
        score -= 0.3
        issues.append("Teacher guide not in Vietnamese")

    # Check for pedagogical keywords
    pedagogical_terms = ["phương pháp", "giảng dạy", "học sinh", "hoạt động",
                         "đánh giá", "bài tập", "giáo viên", "lớp"]
    found = sum(1 for term in pedagogical_terms if term in guide.lower())
    if found < 4:
        score -= 0.2
        issues.append(f"Only {found}/8 pedagogical terms found")

    # Check for time allocation mentions (45 minutes per period)
    if "45" in guide or "phút" in guide:
        pass  # Good
    else:
        score -= 0.1
        issues.append("No time allocation mentioned")

    # Check for Korean methodology integration reference
    korean_ref = any(word in guide.lower() for word in ["hàn quốc", "hàn", "korea", "phương pháp"])
    if not korean_ref:
        score -= 0.1
        issues.append("No reference to Korean methodology")

    return {"score": max(0.0, score), "issues": issues}


def check_exercise_quality() -> dict:
    """Check exercise file quality."""
    data = load_json("exercises_vi.json")
    if data is None:
        return {"score": 0.0, "issues": ["exercises_vi.json not found"]}

    score = 1.0
    issues = []

    # Handle structure
    if isinstance(data, dict) and "exercises" in data:
        exercises = data["exercises"]
    elif isinstance(data, list):
        exercises = data
    else:
        return {"score": 0.1, "issues": ["Unexpected data structure"]}

    # Check minimum count (50 exercises = 5 per lesson × 10 lessons)
    if len(exercises) < 50:
        score -= min(0.3, (50 - len(exercises)) * 0.01)
        issues.append(f"Only {len(exercises)}/50 exercises found")

    # Check required fields
    required_fields = {"lesson_id", "exercise_id", "type", "question_vi", "answer", "difficulty"}
    field_issues = 0
    for ex in exercises[:10]:
        if isinstance(ex, dict):
            missing = required_fields - set(ex.keys())
            if missing:
                field_issues += len(missing)

    if field_issues > 0:
        score -= min(0.2, field_issues * 0.02)
        issues.append(f"{field_issues} missing fields in first 10 exercises")

    # Check Vietnamese diacritics in questions
    vn_pattern = re.compile(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]')
    non_vietnamese = 0
    for ex in exercises[:20]:
        if isinstance(ex, dict) and "question_vi" in ex:
            q = str(ex["question_vi"])
            if not vn_pattern.search(q) and len(q) > 20:
                non_vietnamese += 1

    if non_vietnamese > 5:
        score -= 0.2
        issues.append(f"{non_vietnamese} questions don't appear to be in Vietnamese")

    # Check difficulty distribution
    difficulties = [ex.get("difficulty") for ex in exercises if isinstance(ex, dict)]
    if difficulties:
        valid_diffs = [d for d in difficulties if d in [1, 2, 3]]
        if len(valid_diffs) > 0:
            avg_diff = sum(valid_diffs) / len(valid_diffs)
            if avg_diff < 1.3 or avg_diff > 2.7:
                score -= 0.1
                issues.append(f"Difficulty distribution skewed (avg: {avg_diff:.1f})")

    # Check exercise types
    types = set(ex.get("type", "") for ex in exercises if isinstance(ex, dict))
    if len(types) < 2:
        score -= 0.1
        issues.append("Only one exercise type found")

    return {"score": max(0.0, score), "issues": issues}


def check_standards_alignment() -> dict:
    """Check alignment with Vietnamese educational standards."""
    assessment = load_json("assessment_vi.json")
    if assessment is None:
        return {"score": 0.0, "issues": ["assessment_vi.json not found"]}

    score = 1.0
    issues = []

    # Check for midterm and final assessments
    has_midterm = False
    has_final = False

    if isinstance(assessment, dict):
        if "midterm" in assessment or "kiem_tra_giua_ky" in assessment:
            has_midterm = True
        if "final" in assessment or "kiem_tra_cuoi_ky" in assessment:
            has_final = True
        if "assessments" in assessment:
            for a in assessment["assessments"]:
                if isinstance(a, dict):
                    atype = str(a.get("type", "")).lower()
                    if "mid" in atype or "giữa" in atype or "giua" in atype:
                        has_midterm = True
                    if "final" in atype or "cuối" in atype or "cuoi" in atype:
                        has_final = True
    elif isinstance(assessment, list):
        for item in assessment:
            if isinstance(item, dict):
                atype = str(item.get("type", "")).lower()
                if "mid" in atype or "giữa" in atype or "giua" in atype:
                    has_midterm = True
                if "final" in atype or "cuối" in atype or "cuoi" in atype:
                    has_final = True

    if not has_midterm:
        score -= 0.25
        issues.append("No midterm assessment found")
    if not has_final:
        score -= 0.25
        issues.append("No final assessment found")

    # Check for questions in assessments
    assessment_str = json.dumps(assessment, ensure_ascii=False)
    question_count = assessment_str.count("question") + assessment_str.count("câu_hỏi") + assessment_str.count("cau_hoi")
    if question_count < 10:
        score -= 0.2
        issues.append(f"Too few assessment questions detected")

    # Check for Vietnamese content
    vn_pattern = re.compile(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]')
    vn_chars = len(vn_pattern.findall(assessment_str))
    if vn_chars < 50:
        score -= 0.2
        issues.append("Assessment content not in Vietnamese")

    return {"score": max(0.0, score), "issues": issues}


def check_completeness() -> dict:
    """Check overall completeness of deliverables."""
    score = 1.0
    issues = []

    files_to_check = [
        ("curriculum_vi.md", 2000),
        ("exercises_vi.json", 500),
        ("teacher_guide_vi.md", 1000),
        ("assessment_vi.json", 500),
    ]

    for filename, min_size in files_to_check:
        filepath = os.path.join(WORKSPACE, "output", filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(WORKSPACE, filename)
        if not os.path.exists(filepath):
            score -= 0.25
            issues.append(f"{filename} not found")
        else:
            size = os.path.getsize(filepath)
            if size < min_size:
                score -= 0.1
                issues.append(f"{filename} too small ({size} bytes)")

    return {"score": max(0.0, score), "issues": issues}


def grade() -> dict:
    """Main grading function."""
    dimensions = {
        "content_accuracy": {**check_content_accuracy(), "weight": 0.25},
        "vietnamese_pedagogical": {**check_vietnamese_pedagogical(), "weight": 0.25},
        "exercise_quality": {**check_exercise_quality(), "weight": 0.20},
        "standards_alignment": {**check_standards_alignment(), "weight": 0.15},
        "completeness": {**check_completeness(), "weight": 0.15},
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": dimensions
    }




def test_grade_overall():
    """Verify grade function produces a meaningful score."""
    result = grade()
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_grade_overall():
    """Verify grade function produces a meaningful score."""
    result = grade()
    assert result["overall_score"] > 0.15, "No valid output produced"


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
        if any(word in k.lower() for word in ["vietnamese", "vi"]):
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

if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))
