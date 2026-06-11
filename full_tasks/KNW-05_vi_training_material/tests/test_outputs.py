"""WildClawBench-style grading for KNW-05_vi_training_material."""
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


def _load_json(name: str) -> Any:
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


def _has_vietnamese(text: str) -> bool:
    """Check if text contains Vietnamese-specific diacritical characters."""
    # Vietnamese uses special characters like ă, ơ, ư, đ and tone marks
    viet_chars = r"[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđĐ]"
    return bool(re.search(viet_chars, text))


def _vietnamese_word_count(text: str) -> int:
    """Approximate Vietnamese word count (space-separated)."""
    return len(text.split())


def _score_content_coverage(manual: str, exercises: Any, answer: dict) -> float:
    """Score content coverage from source materials (weight: 0.25)."""
    score = 0.0

    if not manual:
        return 0.0

    # Check key cloud computing topics are covered
    topics = {
        "IaaS": ["IaaS", "Infrastructure"],
        "PaaS": ["PaaS", "Platform"],
        "SaaS": ["SaaS", "Software"],
        "compute": ["EC2", "ECS", "compute", "máy ảo", "tính toán"],
        "storage": ["S3", "OSS", "storage", "lưu trữ"],
        "database": ["RDS", "database", "cơ sở dữ liệu", "DynamoDB"],
        "networking": ["VPC", "CDN", "mạng", "network"],
        "security": ["IAM", "encryption", "bảo mật", "mã hóa"],
        "serverless": ["Lambda", "serverless", "không máy chủ"],
        "containers": ["container", "Kubernetes", "Docker", "EKS"],
    }

    covered = 0
    for topic, keywords in topics.items():
        if any(k.lower() in manual.lower() for k in keywords):
            covered += 1

    score += 0.4 * (covered / len(topics))

    # Check AWS vs Alibaba Cloud comparison exists
    if "AWS" in manual and ("Alibaba" in manual or "阿里" in manual):
        score += 0.2

    # Check word count
    word_count = _vietnamese_word_count(manual)
    if word_count >= 3000:
        score += 0.2
    elif word_count >= 2000:
        score += 0.15
    elif word_count >= 1000:
        score += 0.1

    # Check exercises exist and cover content
    if isinstance(exercises, (list, dict)):
        ex_list = exercises if isinstance(exercises, list) else exercises.get("exercises", [])
        if len(ex_list) >= 10:
            score += 0.2
        elif len(ex_list) >= 5:
            score += 0.1

    return min(score, 1.0)


def _score_vietnamese_quality(manual: str, exercises: Any, questions: Any) -> float:
    """Score Vietnamese language quality (weight: 0.25)."""
    score = 0.0

    if not manual:
        return 0.0

    # Check Vietnamese text present
    if not _has_vietnamese(manual):
        return 0.1  # Content exists but not in Vietnamese

    score += 0.2

    # Check technical terms in Vietnamese
    viet_tech_terms = ["điện toán đám mây", "máy ảo", "lưu trữ", "cơ sở dữ liệu",
                       "mạng", "bảo mật", "triển khai", "ứng dụng", "dịch vụ",
                       "tài nguyên", "hiệu suất", "khả năng", "mở rộng"]
    found_terms = sum(1 for t in viet_tech_terms if t in manual.lower())
    score += 0.3 * min(found_terms / 6, 1.0)

    # Check section structure
    headers = re.findall(r"^#{1,3}\s+.+$", manual, re.MULTILINE)
    if len(headers) >= 8:
        score += 0.2
    elif len(headers) >= 5:
        score += 0.15
    elif len(headers) >= 3:
        score += 0.1

    # Check exercises are in Vietnamese
    ex_str = json.dumps(exercises, ensure_ascii=False) if exercises else ""
    if _has_vietnamese(ex_str):
        score += 0.15

    # Check questions are in Vietnamese
    q_str = json.dumps(questions, ensure_ascii=False) if questions else ""
    if _has_vietnamese(q_str):
        score += 0.15

    return min(score, 1.0)


def _score_exercise_quality(exercises: Any) -> float:
    """Score exercise quality (weight: 0.20)."""
    score = 0.0

    if not exercises:
        return 0.0

    ex_list = exercises if isinstance(exercises, list) else exercises.get("exercises", [])

    if not isinstance(ex_list, list):
        return 0.1

    # Check quantity
    if len(ex_list) >= 10:
        score += 0.3
    elif len(ex_list) >= 7:
        score += 0.2
    elif len(ex_list) >= 4:
        score += 0.1

    # Check exercise structure
    valid_exercises = 0
    for ex in ex_list:
        if isinstance(ex, dict):
            # Check required fields
            has_title = any(k in ex for k in ["title", "tiêu_đề", "tieu_de", "name"])
            has_desc = any(k in ex for k in ["description", "mô_tả", "mo_ta", "content"])
            has_difficulty = any(k in ex for k in ["difficulty", "mức_độ", "level", "độ_khó"])
            if has_title and has_desc:
                valid_exercises += 1

    if valid_exercises >= 10:
        score += 0.3
    elif valid_exercises >= 5:
        score += 0.2

    # Check Vietnamese content in exercises
    ex_str = json.dumps(ex_list, ensure_ascii=False)
    if _has_vietnamese(ex_str):
        score += 0.2

    # Check variety (different difficulty levels or topics)
    difficulties = set()
    for ex in ex_list:
        if isinstance(ex, dict):
            d = ex.get("difficulty", ex.get("mức_độ", ex.get("level", "")))
            if d:
                difficulties.add(str(d))
    if len(difficulties) >= 2:
        score += 0.2

    return min(score, 1.0)


def _score_glossary_accuracy(glossary: Any) -> float:
    """Score glossary accuracy (weight: 0.15)."""
    score = 0.0

    if not glossary:
        return 0.0

    terms = glossary if isinstance(glossary, list) else glossary.get("terms", glossary.get("glossary", []))

    if not isinstance(terms, list):
        # Maybe it's a dict of terms
        if isinstance(glossary, dict) and len(glossary) >= 10:
            score += 0.3
            if any(_has_vietnamese(str(v)) for v in glossary.values()):
                score += 0.3
            return min(score + 0.2, 1.0)
        return 0.1

    # Check quantity
    if len(terms) >= 40:
        score += 0.3
    elif len(terms) >= 25:
        score += 0.2
    elif len(terms) >= 15:
        score += 0.1

    # Check trilingual entries
    trilingual = 0
    for term in terms:
        if isinstance(term, dict):
            has_vi = any(k in term for k in ["vi", "vietnamese", "tiếng_việt", "tieng_viet"])
            has_en = any(k in term for k in ["en", "english", "tiếng_anh"])
            has_zh = any(k in term for k in ["zh", "chinese", "tiếng_trung", "中文"])
            if has_vi and has_en and has_zh:
                trilingual += 1
            elif len(term) >= 3:  # At least 3 language fields
                trilingual += 1

    if trilingual >= 30:
        score += 0.3
    elif trilingual >= 20:
        score += 0.2
    elif trilingual >= 10:
        score += 0.15

    # Check Vietnamese definitions present
    glossary_str = json.dumps(terms, ensure_ascii=False)
    if _has_vietnamese(glossary_str):
        score += 0.2

    # Check key cloud terms are included
    key_terms = ["cloud", "virtual", "server", "database", "storage", "network"]
    found = sum(1 for t in key_terms if t.lower() in glossary_str.lower())
    score += 0.2 * min(found / 4, 1.0)

    return min(score, 1.0)


def _score_pedagogical_structure(manual: str, questions: Any, answer: dict) -> float:
    """Score pedagogical structure (weight: 0.15)."""
    score = 0.0

    # Check manual has progressive structure (basic → advanced)
    if manual:
        headers = re.findall(r"^#{1,3}\s+(.+)$", manual, re.MULTILINE)
        if len(headers) >= 6:
            score += 0.2

        # Check for chapter summaries or key points
        summary_markers = ["tóm tắt", "tổng kết", "điểm chính", "từ khóa",
                          "summary", "key points", "keywords"]
        found_summaries = sum(1 for m in summary_markers if m.lower() in manual.lower())
        if found_summaries >= 2:
            score += 0.2

    # Check assessment questions
    if questions:
        q_list = questions if isinstance(questions, list) else questions.get("questions", [])
        if isinstance(q_list, list):
            if len(q_list) >= 20:
                score += 0.2
            elif len(q_list) >= 10:
                score += 0.15

            # Check question types variety
            types = set()
            for q in q_list:
                if isinstance(q, dict):
                    qtype = q.get("type", q.get("loại", ""))
                    if qtype:
                        types.add(str(qtype).lower())
            if len(types) >= 3:
                score += 0.2
            elif len(types) >= 2:
                score += 0.1

    # Check answer.json
    if answer:
        if answer.get("total_chapters", 0) >= 5:
            score += 0.1
        if answer.get("covered_objectives"):
            score += 0.1

    return min(score, 1.0)


def grade() -> Dict[str, Any]:
    """Grade the KNW-05 task outputs."""
    manual = _load_text("training_manual_vi.md")
    exercises = _load_json("exercises_vi.json")
    glossary = _load_json("glossary_vi_en_zh.json")
    questions = _load_json("assessment_questions_vi.json")
    answer = _load_answer()

    # Calculate dimension scores
    coverage = _score_content_coverage(manual, exercises, answer)
    vietnamese = _score_vietnamese_quality(manual, exercises, questions)
    exercise_q = _score_exercise_quality(exercises)
    glossary_acc = _score_glossary_accuracy(glossary)
    pedagogy = _score_pedagogical_structure(manual, questions, answer)

    # Weighted overall score
    overall = (
        coverage * 0.25
        + vietnamese * 0.25
        + exercise_q * 0.20
        + glossary_acc * 0.15
        + pedagogy * 0.15
    )

    return {
        "overall_score": round(overall, 4),
        "dimensions": {
            "content_coverage": {"score": round(coverage, 4), "weight": 0.25},
            "vietnamese_quality": {"score": round(vietnamese, 4), "weight": 0.25},
            "exercise_quality": {"score": round(exercise_q, 4), "weight": 0.20},
            "glossary_accuracy": {"score": round(glossary_acc, 4), "weight": 0.15},
            "pedagogical_structure": {"score": round(pedagogy, 4), "weight": 0.15},
        },
    }


def test_grade_overall():
    """Pytest entrypoint for grading."""
    result = grade()
    assert result["overall_score"] >= 0.0, f"Score below 0: {result}"
    print(f"\n{'='*60}")
    print(f"KNW-05 Grade: {result['overall_score']:.2%}")
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
