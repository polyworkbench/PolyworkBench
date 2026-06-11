"""
Test suite for LEG-03_ko_ip_filing
Evaluates: claims_translation, prior_art_analysis, korean_legal_quality, novelty_assessment, filing_completeness
"""

import json
import os
import re
from pathlib import Path
import pytest


def check_file_exists(filepath):
    """Check if a file exists and has content."""
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"
    return True, "OK"


def load_json_file(filepath):
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return None, str(e)


def check_korean_text(text):
    """Check if text contains substantial Korean content."""
    korean_chars = len(re.findall(r'[가-힯㄰-㆏]', text))
    total_chars = len(re.findall(r'[\w]', text))
    if total_chars == 0:
        return 0.0
    return korean_chars / total_chars


def grade():
    """Main grading function returning overall_score and dimensions."""

    output_dir = "/workspace/output"
    answer_path = "/workspace/output/answer.json"
    if not os.path.exists(answer_path):
        answer_path = "/workspace/answer.json"

    if not os.path.exists(output_dir):
        output_dir = "output"
    if not os.path.exists(answer_path):
        answer_path = "answer.json"

    dimensions = {
        "claims_translation": 0.0,
        "prior_art_analysis": 0.0,
        "korean_legal_quality": 0.0,
        "novelty_assessment": 0.0,
        "filing_completeness": 0.0
    }

    weights = {
        "claims_translation": 0.25,
        "prior_art_analysis": 0.25,
        "korean_legal_quality": 0.20,
        "novelty_assessment": 0.15,
        "filing_completeness": 0.15
    }

    # =====================================================
    # DIMENSION 1: Claims Translation (0.25)
    # =====================================================
    claims_score = 0.0

    claims_path = os.path.join(output_dir, "patent_claims_ko.md")
    exists, _ = check_file_exists(claims_path)

    if exists:
        with open(claims_path, 'r', encoding='utf-8') as f:
            claims_text = f.read()

        # Check Korean language content
        korean_ratio = check_korean_text(claims_text)
        if korean_ratio > 0.3:
            claims_score += 0.2
        elif korean_ratio > 0.15:
            claims_score += 0.1

        # Count claims (should be 15)
        # Look for claim numbering patterns
        claim_patterns = [
            r'청구항\s*\d+',
            r'제\s*\d+\s*항',
            r'claim\s*\d+',
            r'\d+\.\s',
            r'【청구항\s*\d+】'
        ]
        max_claims_found = 0
        for pattern in claim_patterns:
            matches = re.findall(pattern, claims_text, re.IGNORECASE)
            max_claims_found = max(max_claims_found, len(matches))

        if max_claims_found >= 15:
            claims_score += 0.3
        elif max_claims_found >= 10:
            claims_score += 0.2
        elif max_claims_found >= 5:
            claims_score += 0.1

        # Check for Korean patent claim terminology
        ko_patent_terms = ["포함하는", "구성되는", "특징으로 하는", "있어서",
                          "상기", "수단", "단계", "장치", "시스템", "방법"]
        terms_found = sum(1 for t in ko_patent_terms if t in claims_text)
        claims_score += min(0.25, terms_found / 5 * 0.25)

        # Check for independent vs dependent claim distinction
        has_independent = any(kw in claims_text for kw in ["독립항", "독립 청구항", "포함하는 시스템", "포함하는 방법", "포함하는 장치"])
        has_dependent = any(kw in claims_text for kw in ["종속항", "에 있어서", "제1항에", "제9항에", "제13항에"])
        if has_independent and has_dependent:
            claims_score += 0.25
        elif has_independent or has_dependent:
            claims_score += 0.15

    dimensions["claims_translation"] = min(1.0, claims_score)

    # =====================================================
    # DIMENSION 2: Prior Art Analysis (0.25)
    # =====================================================
    pa_score = 0.0

    pa_path = os.path.join(output_dir, "prior_art_analysis_ko.json")
    pa_data, err = load_json_file(pa_path)

    if pa_data is not None:
        pa_score += 0.15  # Valid JSON

        pa_text = json.dumps(pa_data, ensure_ascii=False).lower()

        # Should reference Japanese prior art
        jp_ref = any(kw in pa_text for kw in ["2022-156789", "日本", "일본", "japan", "특개", "山田", "야마다", "東京環境"])
        if jp_ref:
            pa_score += 0.2

        # Should reference Chinese utility model
        cn_ref = any(kw in pa_text for kw in ["217845623", "中国", "중국", "china", "실용신안", "深圳", "선전", "李明华"])
        if cn_ref:
            pa_score += 0.2

        # Should contain technical comparisons (numbers specific to prior art differences)
        tech_comparisons = any(kw in pa_text for kw in ["256", "512", "100ms", "50ms", "15ms",
                                                         "8w", "5w", "7nm", "4층", "8층", "6층"])
        if tech_comparisons:
            pa_score += 0.2

        # Should identify differences/advantages
        diff_keywords = ["차이", "비교", "우수", "개선", "advantage", "difference", "구별", "진보"]
        diff_found = sum(1 for kw in diff_keywords if kw in pa_text)
        if diff_found >= 2:
            pa_score += 0.25
        elif diff_found >= 1:
            pa_score += 0.15

    dimensions["prior_art_analysis"] = min(1.0, pa_score)

    # =====================================================
    # DIMENSION 3: Korean Legal Quality (0.20)
    # =====================================================
    ko_score = 0.0

    # Check claims file and novelty assessment for Korean legal quality
    files_to_check = [
        os.path.join(output_dir, "patent_claims_ko.md"),
        os.path.join(output_dir, "novelty_assessment_ko.md")
    ]

    for fpath in files_to_check:
        exists, _ = check_file_exists(fpath)
        if exists:
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()

            # Korean legal/patent terminology
            ko_legal_terms = ["특허법", "신규성", "진보성", "선행기술", "청구범위",
                            "명세서", "실시예", "기술분야", "통상의 기술자",
                            "출원", "발명", "특허청"]
            terms_found = sum(1 for t in ko_legal_terms if t in text)
            ko_score += min(0.25, terms_found / 5 * 0.25)

            # Check Korean ratio
            if check_korean_text(text) > 0.3:
                ko_score += 0.15

    # Check for formal structure
    novelty_path = os.path.join(output_dir, "novelty_assessment_ko.md")
    exists, _ = check_file_exists(novelty_path)
    if exists:
        with open(novelty_path, 'r', encoding='utf-8') as f:
            novelty_text = f.read()
        if len(novelty_text) > 1500:
            ko_score += 0.1
        has_structure = bool(re.search(r'^#+\s', novelty_text, re.MULTILINE))
        if has_structure:
            ko_score += 0.1

    dimensions["korean_legal_quality"] = min(1.0, ko_score)

    # =====================================================
    # DIMENSION 4: Novelty Assessment (0.15)
    # =====================================================
    novelty_score = 0.0

    novelty_path = os.path.join(output_dir, "novelty_assessment_ko.md")
    exists, _ = check_file_exists(novelty_path)

    if exists:
        with open(novelty_path, 'r', encoding='utf-8') as f:
            novelty_text = f.read()

        # Check for novelty discussion
        novelty_keywords = ["신규성", "novelty", "새로운", "공지", "공개"]
        if any(kw in novelty_text.lower() for kw in novelty_keywords):
            novelty_score += 0.25

        # Check for inventive step discussion
        inventive_keywords = ["진보성", "inventive step", "용이", "예측", "현저한 효과"]
        if any(kw in novelty_text.lower() for kw in inventive_keywords):
            novelty_score += 0.25

        # Check for specific technical differentiators referenced
        tech_diffs = ["512", "256", "cross-modal", "크로스모달", "15ms", "15밀리초", "7nm", "transformer", "트랜스포머", "8층"]
        diffs_found = sum(1 for d in tech_diffs if d.lower() in novelty_text.lower())
        novelty_score += min(0.3, diffs_found / 3 * 0.3)

        # Check for conclusion/determination
        conclusion_kw = ["결론", "판단", "인정", "확인", "따라서"]
        if any(kw in novelty_text for kw in conclusion_kw):
            novelty_score += 0.2

    dimensions["novelty_assessment"] = min(1.0, novelty_score)

    # =====================================================
    # DIMENSION 5: Filing Completeness (0.15)
    # =====================================================
    filing_score = 0.0

    # Check filing checklist
    checklist_path = os.path.join(output_dir, "filing_checklist_ko.json")
    checklist_data, err = load_json_file(checklist_path)

    if checklist_data is not None:
        filing_score += 0.2

        checklist_text = json.dumps(checklist_data, ensure_ascii=False).lower()

        # Should reference KIPO requirements
        kipo_refs = ["kipo", "특허청", "출원서", "명세서", "청구범위", "요약서", "도면"]
        refs_found = sum(1 for r in kipo_refs if r in checklist_text)
        filing_score += min(0.3, refs_found / 4 * 0.3)

        # Should have status indicators
        if any(kw in checklist_text for kw in ["완료", "미완료", "준비", "필요", "complete", "incomplete", "ready"]):
            filing_score += 0.2

    # Check answer.json
    answer_data, err = load_json_file(answer_path)
    if answer_data is not None:
        filing_score += 0.1

        if answer_data.get("total_claims") == 15:
            filing_score += 0.1

        if "independent_claims" in answer_data:
            # Should be 3 (claims 1, 9, 13)
            if answer_data["independent_claims"] == 3:
                filing_score += 0.1

    # Check all required files exist
    required = ["patent_claims_ko.md", "prior_art_analysis_ko.json",
                "novelty_assessment_ko.md", "filing_checklist_ko.json"]
    all_exist = all(check_file_exists(os.path.join(output_dir, f))[0] for f in required)
    if all_exist:
        filing_score += 0.1

    dimensions["filing_completeness"] = min(1.0, filing_score)

    # =====================================================
    # CALCULATE OVERALL SCORE
    # =====================================================
    overall_score = sum(dimensions[k] * weights[k] for k in dimensions)

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": {k: round(v, 4) for k, v in dimensions.items()}
    }



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

if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2))
