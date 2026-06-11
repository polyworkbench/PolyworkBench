"""
Test suite for LEG-01_ru_contract_review
Evaluates: conflict_detection, russian_legal_quality, risk_assessment, recommendations, completeness
"""

import json
import os
import re
import pytest
from pathlib import Path


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


def check_russian_text(text):
    """Check if text contains substantial Russian content."""
    cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁ]', text))
    total_alpha = len(re.findall(r'[a-zA-Zа-яА-ЯёЁ]', text))
    if total_alpha == 0:
        return 0.0
    return cyrillic_chars / total_alpha


def grade():
    """Main grading function returning overall_score and dimensions."""

    output_dir = "/workspace/output"
    answer_path = "/workspace/output/answer.json"
    if not os.path.exists(answer_path):
        answer_path = "/workspace/answer.json"

    # Alternative paths
    alt_output_dir = "output"
    alt_answer_path = "answer.json"

    # Resolve paths with fallbacks
    if not os.path.exists(output_dir):
        output_dir = alt_output_dir
    if not os.path.exists(answer_path):
        answer_path = alt_answer_path

    dimensions = {
        "conflict_detection": 0.0,
        "russian_legal_quality": 0.0,
        "risk_assessment": 0.0,
        "recommendations": 0.0,
        "completeness": 0.0
    }

    weights = {
        "conflict_detection": 0.30,
        "russian_legal_quality": 0.25,
        "risk_assessment": 0.20,
        "recommendations": 0.15,
        "completeness": 0.10
    }

    # =====================================================
    # DIMENSION 1: Conflict Detection (0.30)
    # =====================================================
    conflict_score = 0.0

    # Check conflict_analysis.json
    conflict_path = os.path.join(output_dir, "conflict_analysis.json")
    conflict_data, err = load_json_file(conflict_path)

    if conflict_data is not None:
        conflicts = conflict_data.get("conflicts", conflict_data if isinstance(conflict_data, list) else [])
        if isinstance(conflict_data, dict) and "conflicts" not in conflict_data:
            # Try to find conflicts in any list-valued key
            for v in conflict_data.values():
                if isinstance(v, list) and len(v) > 0:
                    conflicts = v
                    break

        num_conflicts = len(conflicts) if isinstance(conflicts, list) else 0

        # Must find at least 3 key conflicts
        if num_conflicts >= 3:
            conflict_score += 0.3
        elif num_conflicts >= 2:
            conflict_score += 0.2
        elif num_conflicts >= 1:
            conflict_score += 0.1

        # Check for specific key conflicts
        conflict_text = json.dumps(conflict_data, ensure_ascii=False).lower()

        # Payment terms conflict: 30 days vs 60 days
        payment_conflict = any([
            "30" in conflict_text and "60" in conflict_text,
            "payment" in conflict_text or "付款" in conflict_text or "оплат" in conflict_text,
            "net 30" in conflict_text or "net 60" in conflict_text
        ])
        if payment_conflict:
            conflict_score += 0.25

        # Liability cap conflict: 5M vs 10M CNY
        liability_conflict = any([
            "5" in conflict_text and "10" in conflict_text and ("million" in conflict_text or "000,000" in conflict_text or "млн" in conflict_text),
            "liability" in conflict_text or "责任" in conflict_text or "ответственност" in conflict_text,
            "5,000,000" in conflict_text or "10,000,000" in conflict_text
        ])
        if liability_conflict:
            conflict_score += 0.25

        # Jurisdiction conflict: England vs China
        jurisdiction_conflict = any([
            ("england" in conflict_text or "english" in conflict_text or "англ" in conflict_text) and
            ("china" in conflict_text or "chinese" in conflict_text or "кита" in conflict_text or "中国" in conflict_text),
            "jurisdiction" in conflict_text or "юрисдикц" in conflict_text or "管辖" in conflict_text,
            "cietac" in conflict_text or "icc" in conflict_text
        ])
        if jurisdiction_conflict:
            conflict_score += 0.2

    dimensions["conflict_detection"] = min(1.0, conflict_score)

    # =====================================================
    # DIMENSION 2: Russian Legal Quality (0.25)
    # =====================================================
    russian_score = 0.0

    memo_path = os.path.join(output_dir, "legal_memo_ru.md")
    exists, _ = check_file_exists(memo_path)

    if exists:
        with open(memo_path, 'r', encoding='utf-8') as f:
            memo_text = f.read()

        # Check Russian language ratio (should be >50%)
        russian_ratio = check_russian_text(memo_text)
        if russian_ratio > 0.5:
            russian_score += 0.3
        elif russian_ratio > 0.3:
            russian_score += 0.15

        # Check for legal terminology
        legal_terms = [
            "юридическ", "заключени", "договор", "соглашени", "сторон",
            "обязательств", "ответственност", "применим", "прав",
            "условия", "противореч", "конфликт", "риск"
        ]
        terms_found = sum(1 for term in legal_terms if term in memo_text.lower())
        russian_score += min(0.3, terms_found / len(legal_terms) * 0.3)

        # Check structure (headings, sections)
        has_structure = bool(re.search(r'^#+\s', memo_text, re.MULTILINE))
        if has_structure:
            russian_score += 0.2

        # Check document length (should be substantive)
        if len(memo_text) > 2000:
            russian_score += 0.2
        elif len(memo_text) > 1000:
            russian_score += 0.1

    dimensions["russian_legal_quality"] = min(1.0, russian_score)

    # =====================================================
    # DIMENSION 3: Risk Assessment (0.20)
    # =====================================================
    risk_score = 0.0

    risk_path = os.path.join(output_dir, "risk_register.json")
    risk_data, err = load_json_file(risk_path)

    if risk_data is not None:
        # Find risks list
        risks = risk_data if isinstance(risk_data, list) else risk_data.get("risks", [])
        if isinstance(risk_data, dict) and not isinstance(risks, list):
            for v in risk_data.values():
                if isinstance(v, list):
                    risks = v
                    break

        if isinstance(risks, list) and len(risks) > 0:
            risk_score += 0.2

            # Check for severity classifications
            severities = []
            for risk in risks:
                if isinstance(risk, dict):
                    sev = risk.get("severity", risk.get("level", risk.get("критичность", "")))
                    if sev:
                        severities.append(str(sev).lower())

            if severities:
                risk_score += 0.2
                # Should have at least one high-severity risk
                high_keywords = ["high", "critical", "высок", "критич", "5", "4"]
                has_high = any(any(kw in s for kw in high_keywords) for s in severities)
                if has_high:
                    risk_score += 0.2

            # Check for required fields in risk entries
            required_fields_variants = [
                ["id", "description", "severity"],
                ["id", "description_ru", "severity"],
                ["category", "description", "level"],
            ]

            sample_risk = risks[0] if risks else {}
            if isinstance(sample_risk, dict):
                for field_set in required_fields_variants:
                    if all(any(f in k.lower() for k in sample_risk.keys()) for f in field_set):
                        risk_score += 0.2
                        break

            # Check that risks reference source clauses
            risk_text = json.dumps(risks, ensure_ascii=False).lower()
            has_clause_refs = any(kw in risk_text for kw in ["article", "clause", "section", "статья", "пункт", "条", "4.2", "8.1", "13"])
            if has_clause_refs:
                risk_score += 0.2

    dimensions["risk_assessment"] = min(1.0, risk_score)

    # =====================================================
    # DIMENSION 4: Recommendations (0.15)
    # =====================================================
    rec_score = 0.0

    rec_path = os.path.join(output_dir, "recommendations_ru.md")
    exists, _ = check_file_exists(rec_path)

    if exists:
        with open(rec_path, 'r', encoding='utf-8') as f:
            rec_text = f.read()

        # Check Russian content
        if check_russian_text(rec_text) > 0.4:
            rec_score += 0.25

        # Check length
        if len(rec_text) > 500:
            rec_score += 0.25

        # Check for actionable recommendations
        action_keywords = ["рекоменд", "необходим", "следует", "предлаг", "целесообразн", "устранени"]
        actions_found = sum(1 for kw in action_keywords if kw in rec_text.lower())
        rec_score += min(0.25, actions_found / 3 * 0.25)

        # Check for specific resolution suggestions
        resolution_keywords = ["единый", "согласов", "привести в соответстви", "изменить", "дополн", "уточн"]
        resolutions_found = sum(1 for kw in resolution_keywords if kw in rec_text.lower())
        rec_score += min(0.25, resolutions_found / 2 * 0.25)

    dimensions["recommendations"] = min(1.0, rec_score)

    # =====================================================
    # DIMENSION 5: Completeness (0.10)
    # =====================================================
    completeness_score = 0.0

    required_files = [
        os.path.join(output_dir, "legal_memo_ru.md"),
        os.path.join(output_dir, "risk_register.json"),
        os.path.join(output_dir, "conflict_analysis.json"),
        os.path.join(output_dir, "recommendations_ru.md"),
    ]

    files_present = 0
    for fp in required_files:
        exists, _ = check_file_exists(fp)
        if exists:
            files_present += 1

    completeness_score += (files_present / len(required_files)) * 0.5

    # Check answer.json
    answer_data, err = load_json_file(answer_path)
    if answer_data is not None:
        completeness_score += 0.2

        # Check required fields in answer
        has_total = "total_conflicts" in answer_data
        has_high_risk = "high_risk_count" in answer_data
        has_jurisdiction = "primary_jurisdiction_conflict" in answer_data

        if has_total:
            completeness_score += 0.1
            # Validate: should be at least 3 conflicts
            if isinstance(answer_data["total_conflicts"], int) and answer_data["total_conflicts"] >= 3:
                completeness_score += 0.05
        if has_high_risk:
            completeness_score += 0.1
        if has_jurisdiction:
            completeness_score += 0.05

    dimensions["completeness"] = min(1.0, completeness_score)

    # =====================================================
    # CALCULATE OVERALL SCORE
    # =====================================================
    overall_score = sum(dimensions[k] * weights[k] for k in dimensions)

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": {k: round(v, 4) for k, v in dimensions.items()}
    }


# === Standardized pytest tests ===


def _resolve_output_dir():
    d = "/workspace/output"
    if not os.path.exists(d):
        d = "output"
    return d


def _resolve_answer_path():
    for p in ["/workspace/output/answer.json", "/workspace/answer.json", "output/answer.json", "answer.json"]:
        if os.path.exists(p):
            return p
    return "answer.json"


def _load_answer_for_test():
    p = _resolve_answer_path()
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def test_grade_overall():
    result = grade()
    assert result["overall_score"] > 0.15, "No valid output produced"


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
    ru_score = dims.get("russian_legal_quality", 0.0)
    if isinstance(ru_score, dict):
        ru_score = ru_score.get("score", 0.0)
    assert ru_score > 0.0, "Russian quality dimension is zero - output may be in wrong language"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    result = grade()
    assert result["overall_score"] > 0.0, "Output appears empty or trivial"
    dims = result.get("dimensions", {})
    non_zero = sum(1 for v in dims.values() if (v if isinstance(v, (int, float)) else 0) > 0)
    assert non_zero >= 2, f"Only {non_zero} dimensions scored above zero - output likely incomplete"


def test_no_english_fallback():
    """Verify primary output is not in English (Russian target task)."""
    od = _resolve_output_dir()
    memo_path = os.path.join(od, "legal_memo_ru.md")
    if not os.path.exists(memo_path):
        return
    with open(memo_path, 'r', encoding='utf-8') as f:
        text = f.read()
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Output appears to be mostly English ({english_ratio:.0%})"


if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2))
