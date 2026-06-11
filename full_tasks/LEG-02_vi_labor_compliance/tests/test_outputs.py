"""
Test suite for LEG-02_vi_labor_compliance
Evaluates: compliance_identification, gap_analysis, vietnamese_quality, remediation, legal_accuracy
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


def check_vietnamese_text(text):
    """Check if text contains Vietnamese diacritics."""
    vietnamese_chars = re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower())
    return len(vietnamese_chars) > 0


def grade():
    """Main grading function returning overall_score and dimensions."""

    output_dir = "/workspace/output"
    answer_path = "/workspace/output/answer.json"
    if not os.path.exists(answer_path):
        answer_path = "/workspace/answer.json"

    # Alternative paths
    if not os.path.exists(output_dir):
        output_dir = "output"
    if not os.path.exists(answer_path):
        answer_path = "answer.json"

    dimensions = {
        "compliance_identification": 0.0,
        "gap_analysis": 0.0,
        "vietnamese_quality": 0.0,
        "remediation": 0.0,
        "legal_accuracy": 0.0
    }

    weights = {
        "compliance_identification": 0.30,
        "gap_analysis": 0.25,
        "vietnamese_quality": 0.20,
        "remediation": 0.15,
        "legal_accuracy": 0.10
    }

    # =====================================================
    # DIMENSION 1: Compliance Identification (0.30)
    # =====================================================
    compliance_score = 0.0

    checklist_path = os.path.join(output_dir, "compliance_checklist_vi.md")
    exists, _ = check_file_exists(checklist_path)

    if exists:
        with open(checklist_path, 'r', encoding='utf-8') as f:
            checklist_text = f.read()

        # Check that checklist covers all 3 contracts
        contract_refs = 0
        for marker in ["001", "015", "022", "hợp đồng 1", "hợp đồng 2", "hợp đồng 3", "contract 1", "contract 2", "contract 3", "HĐ 1", "HĐ 2", "HĐ 3"]:
            if marker.lower() in checklist_text.lower():
                contract_refs += 1
        if contract_refs >= 3:
            compliance_score += 0.25
        elif contract_refs >= 2:
            compliance_score += 0.15

        # Check for compliance status markers
        status_markers = ["tuân thủ", "không tuân thủ", "vi phạm", "cần xem xét", "compliant", "non-compliant"]
        markers_found = sum(1 for m in status_markers if m.lower() in checklist_text.lower())
        if markers_found >= 2:
            compliance_score += 0.25

        # Check for key violation areas
        key_violations = {
            "overtime": ["làm thêm", "giờ làm thêm", "overtime", "60 giờ", "50 giờ", "40 giờ"],
            "probation": ["thử việc", "probation", "90 ngày", "60 ngày"],
            "rest_period": ["nghỉ ngơi", "nghỉ giữa ca", "12 giờ", "rest period"],
        }

        violations_found = 0
        for area, keywords in key_violations.items():
            if any(kw.lower() in checklist_text.lower() for kw in keywords):
                violations_found += 1

        compliance_score += min(0.5, violations_found / 3 * 0.5)

    dimensions["compliance_identification"] = min(1.0, compliance_score)

    # =====================================================
    # DIMENSION 2: Gap Analysis (0.25)
    # =====================================================
    gap_score = 0.0

    gap_path = os.path.join(output_dir, "gap_analysis_vi.json")
    gap_data, err = load_json_file(gap_path)

    if gap_data is not None:
        # Find gaps list
        gaps = gap_data if isinstance(gap_data, list) else gap_data.get("gaps", gap_data.get("gap_analysis", []))
        if isinstance(gap_data, dict) and not isinstance(gaps, list):
            for v in gap_data.values():
                if isinstance(v, list):
                    gaps = v
                    break

        if isinstance(gaps, list) and len(gaps) > 0:
            gap_score += 0.2

            # Check number of gaps identified (should be at least 5)
            if len(gaps) >= 5:
                gap_score += 0.2
            elif len(gaps) >= 3:
                gap_score += 0.1

            # Check for specific references to articles/clauses
            gap_text = json.dumps(gap_data, ensure_ascii=False).lower()

            # Should reference ILO conventions
            ilo_refs = ["c001", "c014", "c029", "c158", "ilo"]
            ilo_found = sum(1 for ref in ilo_refs if ref in gap_text)
            if ilo_found >= 2:
                gap_score += 0.2
            elif ilo_found >= 1:
                gap_score += 0.1

            # Should reference Vietnamese Labor Code articles
            vn_refs = ["điều 107", "điều 108", "điều 109", "điều 25", "điều 122", "điều 36", "article 107", "art. 107"]
            vn_found = sum(1 for ref in vn_refs if ref.lower() in gap_text)
            if vn_found >= 2:
                gap_score += 0.2
            elif vn_found >= 1:
                gap_score += 0.1

            # Check for overtime violation specifically (key testable fact)
            overtime_gap = any(kw in gap_text for kw in ["60 giờ", "50 giờ", "40 giờ", "overtime", "làm thêm"])
            if overtime_gap:
                gap_score += 0.2

    dimensions["gap_analysis"] = min(1.0, gap_score)

    # =====================================================
    # DIMENSION 3: Vietnamese Quality (0.20)
    # =====================================================
    vn_score = 0.0

    # Check multiple output files for Vietnamese content
    vi_files = [
        os.path.join(output_dir, "compliance_checklist_vi.md"),
        os.path.join(output_dir, "remediation_plan_vi.md")
    ]

    for vf in vi_files:
        exists, _ = check_file_exists(vf)
        if exists:
            with open(vf, 'r', encoding='utf-8') as f:
                text = f.read()

            if check_vietnamese_text(text):
                vn_score += 0.25

            # Check for Vietnamese legal terminology
            vn_legal_terms = ["bộ luật lao động", "hợp đồng lao động", "người lao động",
                            "người sử dụng lao động", "vi phạm", "tuân thủ", "quy định"]
            terms_found = sum(1 for t in vn_legal_terms if t in text.lower())
            vn_score += min(0.25, terms_found / 4 * 0.25)

    dimensions["vietnamese_quality"] = min(1.0, vn_score)

    # =====================================================
    # DIMENSION 4: Remediation (0.15)
    # =====================================================
    rem_score = 0.0

    rem_path = os.path.join(output_dir, "remediation_plan_vi.md")
    exists, _ = check_file_exists(rem_path)

    if exists:
        with open(rem_path, 'r', encoding='utf-8') as f:
            rem_text = f.read()

        # Check length (should be substantive)
        if len(rem_text) > 1000:
            rem_score += 0.25
        elif len(rem_text) > 500:
            rem_score += 0.15

        # Check for actionable items
        action_keywords = ["sửa đổi", "điều chỉnh", "bổ sung", "thay đổi", "khắc phục",
                          "giảm", "tăng", "thêm", "bỏ", "cần"]
        actions_found = sum(1 for kw in action_keywords if kw in rem_text.lower())
        rem_score += min(0.35, actions_found / 4 * 0.35)

        # Check for specific remediation per contract
        contract_specific = sum(1 for m in ["001", "015", "022", "hợp đồng 1", "hợp đồng 2", "hợp đồng 3"]
                              if m.lower() in rem_text.lower())
        if contract_specific >= 3:
            rem_score += 0.2
        elif contract_specific >= 2:
            rem_score += 0.1

        # Check for structure
        has_structure = bool(re.search(r'^#+\s|^\d+\.|\*\*|^-\s', rem_text, re.MULTILINE))
        if has_structure:
            rem_score += 0.2

    dimensions["remediation"] = min(1.0, rem_score)

    # =====================================================
    # DIMENSION 5: Legal Accuracy (0.10)
    # =====================================================
    accuracy_score = 0.0

    risk_path = os.path.join(output_dir, "risk_items_vi.json")
    risk_data, err = load_json_file(risk_path)

    if risk_data is not None:
        risk_text = json.dumps(risk_data, ensure_ascii=False).lower()

        # Key testable fact 1: Overtime exceeds 40h/month limit (contracts specify 60h and 50h)
        if any(kw in risk_text for kw in ["60", "50", "40", "giờ làm thêm", "overtime"]):
            accuracy_score += 0.3

        # Key testable fact 2: Probation period violations
        # Contract 1: 90 days for production worker (should be max 6 days for "other work")
        # Contract 2: 60 days for technician (at limit but acceptable)
        if any(kw in risk_text for kw in ["90 ngày", "thử việc", "probation", "60 ngày", "30 ngày"]):
            accuracy_score += 0.25

        # Key testable fact 3: Rest period between shifts not guaranteed
        if any(kw in risk_text for kw in ["nghỉ", "12 giờ", "rest", "chuyển ca"]):
            accuracy_score += 0.25

        # Check severity levels exist
        if any(kw in risk_text for kw in ["cao", "high", "trung bình", "medium", "thấp", "low"]):
            accuracy_score += 0.2

    # Check answer.json
    answer_data, err = load_json_file(answer_path)
    if answer_data is not None:
        if "total_violations" in answer_data:
            if isinstance(answer_data["total_violations"], int) and answer_data["total_violations"] >= 5:
                accuracy_score += 0.0  # Already at max area
        if answer_data.get("contracts_reviewed") == 3:
            accuracy_score += 0.0

    dimensions["legal_accuracy"] = min(1.0, accuracy_score)

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
    print(json.dumps(result, indent=2))
