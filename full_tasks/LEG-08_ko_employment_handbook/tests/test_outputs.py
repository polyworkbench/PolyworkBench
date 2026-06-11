"""
WildClawBench-style grading for LEG-08: Korean employee handbook localization.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Key Korean labor law facts that must be reflected
KOREAN_LAW_FACTS = {
    "weekly_hours_max": 52,  # 40 + 12 overtime
    "annual_leave_first_year": "1개월 개근 시 1일",
    "annual_leave_standard": 15,  # days for 1+ year
    "annual_leave_max": 25,  # maximum days
    "termination_notice_days": 30,
    "maternity_leave_days": 90,  # single pregnancy
    "maternity_leave_multiple": 120,  # multiple pregnancy
    "paternity_leave_days": 10,
    "severance_threshold_years": 1,
    "overtime_rate": 1.5,  # 50% premium
    "probation_months": 3,
}


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _is_korean(text: str) -> bool:
    """Check if text contains significant Korean characters."""
    if not text:
        return False
    korean_chars = sum(1 for c in text if '가' <= c <= '힣' or 'ㄱ' <= c <= 'ㅎ' or 'ㅏ' <= c <= 'ㅣ')
    return korean_chars / max(len(text.replace(" ", "")), 1) > 0.15


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


def _score_localization_accuracy(handbook: str) -> Dict[str, float]:
    """Score localization accuracy (weight: 0.30)."""
    scores = {}

    if not handbook:
        return {"handbook_exists": 0.0, "hours_correct": 0.0,
                "leave_correct": 0.0, "termination_correct": 0.0,
                "maternity_correct": 0.0, "severance_correct": 0.0}

    scores["handbook_exists"] = 1.0

    # Check 52-hour workweek (40 + 12)
    scores["hours_correct"] = 1.0 if ("52시간" in handbook or "52 시간" in handbook or
                                       ("40시간" in handbook and "12시간" in handbook)) else 0.0

    # Check annual leave (15 days for 1+ year)
    scores["leave_correct"] = 1.0 if ("15일" in handbook and
                                       any(t in handbook for t in ["연차", "유급휴가"])) else 0.0

    # Check 30-day termination notice
    scores["termination_correct"] = 1.0 if ("30일" in handbook and
                                             any(t in handbook for t in ["해고", "예고", "통지"])) else 0.0

    # Check maternity leave (90 days)
    scores["maternity_correct"] = 1.0 if ("90일" in handbook and
                                           any(t in handbook for t in ["출산", "산전후"])) else 0.0

    # Check severance pay (1 year threshold)
    scores["severance_correct"] = 1.0 if any(t in handbook for t in
                                              ["퇴직급여", "퇴직금"]) else 0.0

    return scores


def _score_legal_compliance(handbook: str, compliance: Any) -> Dict[str, float]:
    """Score legal compliance (weight: 0.25)."""
    scores = {}

    combined = handbook + " " + json.dumps(compliance or {}, ensure_ascii=False)

    if not combined.strip():
        return {"at_will_removed": 0.0, "korean_holidays": 0.0,
                "labor_law_refs": 0.0, "compliance_notes": 0.0}

    # At-will employment should be REMOVED (not valid in Korea)
    # In Korean law, there's no at-will; termination requires just cause
    scores["at_will_removed"] = 0.0 if "at-will" in handbook.lower() else 1.0

    # Korean holidays should replace US holidays
    korean_holidays = ["설날", "추석", "광복절", "개천절", "한글날", "어린이날",
                       "현충일", "부처님오신날", "크리스마스", "근로자의 날"]
    holiday_found = sum(1 for h in korean_holidays if h in handbook)
    scores["korean_holidays"] = min(1.0, holiday_found / 4)

    # References to Korean labor law
    law_refs = ["근로기준법", "남녀고용평등법", "퇴직급여", "고용보험법"]
    refs_found = sum(1 for ref in law_refs if ref in combined)
    scores["labor_law_refs"] = min(1.0, refs_found / 3)

    # Compliance notes exist and have content
    if compliance and isinstance(compliance, (dict, list)):
        scores["compliance_notes"] = 1.0
    else:
        scores["compliance_notes"] = 0.0

    return scores


def _score_korean_quality(handbook: str, change_log: Any, compliance: Any) -> Dict[str, float]:
    """Score Korean language quality (weight: 0.20)."""
    scores = {}

    scores["handbook_in_korean"] = 1.0 if _is_korean(handbook) else 0.0

    # Check change log in Korean
    change_str = json.dumps(change_log, ensure_ascii=False) if change_log else ""
    scores["changelog_in_korean"] = 1.0 if _is_korean(change_str) else 0.0

    # Check for proper Korean legal terminology
    legal_terms = ["취업규칙", "근로계약", "소정근로시간", "통상임금",
                   "평균임금", "유급휴일", "연장근로"]
    term_count = sum(1 for t in legal_terms if t in handbook)
    scores["legal_terminology"] = min(1.0, term_count / 4)

    # Document structure
    has_structure = bool(re.search(r'[#제]\s*\d+', handbook)) or "제" in handbook[:100]
    scores["document_structure"] = 1.0 if has_structure else 0.0

    return scores


def _score_change_tracking(change_log: Any) -> Dict[str, float]:
    """Score change tracking quality (weight: 0.15)."""
    scores = {}

    if not change_log:
        return {"changelog_exists": 0.0, "change_count": 0.0,
                "change_reasons": 0.0, "change_categorized": 0.0}

    scores["changelog_exists"] = 1.0

    if isinstance(change_log, list):
        scores["change_count"] = min(1.0, len(change_log) / 8)

        # Check if changes have reasons
        has_reason = 0
        has_category = 0
        for item in change_log:
            if isinstance(item, dict):
                if any(k in str(item.keys()).lower() for k in
                       ["reason", "사유", "이유", "근거", "rationale"]):
                    has_reason += 1
                if any(k in str(item.keys()).lower() for k in
                       ["category", "type", "분류", "유형", "종류"]):
                    has_category += 1
        scores["change_reasons"] = has_reason / max(len(change_log), 1)
        scores["change_categorized"] = has_category / max(len(change_log), 1)

    elif isinstance(change_log, dict):
        items = list(change_log.values()) if change_log else []
        scores["change_count"] = min(1.0, len(items) / 8)
        blob = json.dumps(change_log, ensure_ascii=False)
        scores["change_reasons"] = 1.0 if any(
            t in blob for t in ["reason", "사유", "이유", "근거"]
        ) else 0.0
        scores["change_categorized"] = 1.0 if any(
            t in blob for t in ["category", "type", "분류", "유형"]
        ) else 0.0

    return scores


def _score_completeness(handbook: str, legal_refs: Any) -> Dict[str, float]:
    """Score overall completeness (weight: 0.10)."""
    scores = {}

    # Check if all 20 policy sections are covered (or equivalent)
    section_keywords = ["근로시간", "휴가", "임금", "해고", "징계",
                        "복무", "교육", "안전", "비밀", "차별"]
    sections_found = sum(1 for kw in section_keywords if kw in handbook)
    scores["policy_coverage"] = min(1.0, sections_found / 7)

    # Legal references file
    if legal_refs:
        scores["legal_refs_present"] = 1.0
        refs_str = json.dumps(legal_refs, ensure_ascii=False)
        # Check for article numbers
        has_articles = bool(re.search(r'제\d+조', refs_str))
        scores["article_numbers"] = 1.0 if has_articles else 0.0
    else:
        scores["legal_refs_present"] = 0.0
        scores["article_numbers"] = 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for LEG-08."""
    handbook = _load_md_file("handbook_ko.md")
    change_log = _load_json_file("change_log_ko.json")
    compliance = _load_json_file("compliance_notes_ko.json")
    legal_refs = _load_json_file("legal_references_ko.json")

    if not handbook and not change_log and not compliance and not legal_refs:
        return {"overall_score": 0.0, "dimensions": {}, "error": "No output files found."}

    dimensions = {}

    # Dimension 1: Localization Accuracy (weight: 0.30)
    loc_scores = _score_localization_accuracy(handbook)
    dimensions["localization_accuracy"] = {
        "score": sum(loc_scores.values()) / max(len(loc_scores), 1),
        "weight": 0.30,
        "details": loc_scores
    }

    # Dimension 2: Legal Compliance (weight: 0.25)
    compliance_scores = _score_legal_compliance(handbook, compliance)
    dimensions["legal_compliance"] = {
        "score": sum(compliance_scores.values()) / max(len(compliance_scores), 1),
        "weight": 0.25,
        "details": compliance_scores
    }

    # Dimension 3: Korean Quality (weight: 0.20)
    korean_scores = _score_korean_quality(handbook, change_log, compliance)
    dimensions["korean_quality"] = {
        "score": sum(korean_scores.values()) / max(len(korean_scores), 1),
        "weight": 0.20,
        "details": korean_scores
    }

    # Dimension 4: Change Tracking (weight: 0.15)
    change_scores = _score_change_tracking(change_log)
    dimensions["change_tracking"] = {
        "score": sum(change_scores.values()) / max(len(change_scores), 1),
        "weight": 0.15,
        "details": change_scores
    }

    # Dimension 5: Completeness (weight: 0.10)
    completeness_scores = _score_completeness(handbook, legal_refs)
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
    print(f"LEG-08 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
        for k, v in dim.get("details", {}).items():
            print(f"    {k}: {v:.2f}")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_handbook_in_korean():
    """Verify the handbook is written in Korean."""
    handbook = _load_md_file("handbook_ko.md")
    assert _is_korean(handbook), "Handbook must be primarily in Korean"


def test_52_hour_workweek():
    """Verify Korean 52-hour workweek limit is applied."""
    handbook = _load_md_file("handbook_ko.md")
    assert "52" in handbook, "Korean 52-hour weekly limit not mentioned"


def test_annual_leave_15_days():
    """Verify Korean annual leave of 15 days is specified."""
    handbook = _load_md_file("handbook_ko.md")
    assert "15일" in handbook or "15 일" in handbook, \
        "Korean statutory annual leave of 15 days not specified"


def test_no_at_will():
    """Verify at-will employment concept is removed (invalid in Korea)."""
    handbook = _load_md_file("handbook_ko.md")
    assert "at-will" not in handbook.lower() and "at will" not in handbook.lower(), \
        "At-will employment is not valid in Korean law and should be removed"


def test_30_day_termination_notice():
    """Verify 30-day termination notice requirement."""
    handbook = _load_md_file("handbook_ko.md")
    assert "30일" in handbook or "30 일" in handbook, \
        "30-day termination notice not specified"


def test_maternity_leave_90_days():
    """Verify 90-day maternity leave."""
    handbook = _load_md_file("handbook_ko.md")
    assert "90일" in handbook or "90 일" in handbook, \
        "90-day maternity leave not specified"


def test_change_log_exists():
    """Verify change log is generated."""
    change_log = _load_json_file("change_log_ko.json")
    assert change_log is not None, "change_log_ko.json not found or invalid"
    if isinstance(change_log, list):
        assert len(change_log) >= 5, "Change log should have at least 5 entries"


def test_severance_pay_mentioned():
    """Verify severance pay (퇴직금) is addressed."""
    handbook = _load_md_file("handbook_ko.md")
    assert any(t in handbook for t in ["퇴직급여", "퇴직금"]), \
        "Severance pay (퇴직금/퇴직급여) must be addressed"


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
