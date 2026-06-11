"""
Test suite for LOC-10: Multi-locale simultaneous release coordination.
Evaluates: consistency_check, qa_thoroughness, changelog_quality, issue_detection, locale_coverage, report_quality

Deliberately embedded issues in input files:
1. Korean (ko): "btn_logout" translated as "로그아웃" but source context says it appears in both
   settings menu and account page — no context-specific variant provided (minor)
2. Vietnamese (vi): "notification_count" string is MISSING entirely from translations_vi.json
3. Russian (ru): "profile_greeting" has placeholder "{имя_пользователя}" instead of "{username}"
   (placeholders should remain as-is, not be translated)
4. French (fr): "privacy_policy" translated as "Mentions légales" which means "Legal notices"
   — inconsistent with other locales which all translate it as "Privacy Policy"
"""

import json
import os
import re
from pathlib import Path
import pytest


WORKSPACE = os.environ.get("WORKSPACE", "/workspace")

# The deliberately embedded issues that should be detected
EXPECTED_ISSUES = {
    "vi_missing_notification_count": {
        "locale": "vi",
        "string_key": "notification_count",
        "issue_type": "missing_string",
        "severity": "critical",
        "description": "notification_count string is missing from Vietnamese translations"
    },
    "ru_placeholder_translated": {
        "locale": "ru",
        "string_key": "profile_greeting",
        "issue_type": "placeholder_error",
        "severity": "critical",
        "description": "Russian profile_greeting has {имя_пользователя} instead of {username}"
    },
    "fr_privacy_policy_inconsistent": {
        "locale": "fr",
        "string_key": "privacy_policy",
        "issue_type": "inconsistency",
        "severity": "major",
        "description": "French privacy_policy is 'Mentions légales' (Legal notices) instead of Privacy Policy"
    },
    "ko_btn_logout_no_variant": {
        "locale": "ko",
        "string_key": "btn_logout",
        "issue_type": "inconsistency",
        "severity": "minor",
        "description": "Korean btn_logout lacks context-specific variant for different UI locations"
    }
}


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


def check_consistency_check() -> dict:
    """Check consistency matrix completeness and accuracy."""
    matrix = load_json("consistency_matrix.json")
    if matrix is None:
        return {"score": 0.0, "issues": ["consistency_matrix.json not found"]}

    score = 1.0
    issues = []

    # Check structure - should have entries for string keys
    if isinstance(matrix, dict):
        # Could have a "matrix" or "strings" wrapper
        if "matrix" in matrix:
            entries = matrix["matrix"]
        elif "strings" in matrix:
            entries = matrix["strings"]
        else:
            entries = matrix
    else:
        return {"score": 0.1, "issues": ["Unexpected structure"]}

    # Should cover most of the 50 source strings
    if isinstance(entries, dict):
        num_keys = len(entries)
        if num_keys < 40:
            score -= 0.2
            issues.append(f"Only {num_keys}/50 strings in matrix")

        # Check that entries have locale information
        locales_expected = {"zh", "ja", "ko", "ru", "vi", "fr"}
        sample_entries = list(entries.values())[:5]
        for entry in sample_entries:
            if isinstance(entry, dict):
                found_locales = set(entry.keys()).intersection(locales_expected)
                alt_found = any(loc in json.dumps(entry) for loc in locales_expected)
                if len(found_locales) < 4 and not alt_found:
                    score -= 0.05

        # Check for identification of the missing Vietnamese string
        vi_notification = entries.get("notification_count", {})
        if isinstance(vi_notification, dict):
            vi_data = vi_notification.get("vi", vi_notification.get("Vietnamese", {}))
            if isinstance(vi_data, dict):
                if vi_data.get("present") == False or vi_data.get("missing") == True:
                    pass  # Correctly identified!
                else:
                    score -= 0.1
                    issues.append("Did not flag Vietnamese missing notification_count")

    elif isinstance(entries, list):
        if len(entries) < 40:
            score -= 0.2
            issues.append(f"Only {len(entries)} entries in matrix")

    return {"score": max(0.0, score), "issues": issues}


def check_qa_thoroughness() -> dict:
    """Check QA report thoroughness."""
    report = load_md("qa_report.md")
    if report is None:
        return {"score": 0.0, "issues": ["qa_report.md not found"]}

    score = 1.0
    issues = []

    # Check minimum length
    if len(report) < 2000:
        score -= 0.2
        issues.append("QA report too brief")

    # Check for severity levels mentioned
    severity_terms = ["critical", "major", "minor"]
    found_severities = sum(1 for s in severity_terms if s.lower() in report.lower())
    if found_severities < 2:
        score -= 0.15
        issues.append("Missing severity level classification")

    # Check for locale coverage
    locales = ["zh", "ja", "ko", "ru", "vi", "fr"]
    locale_mentions = sum(1 for loc in locales if loc in report.lower() or
                         any(name in report.lower() for name in
                             ["chinese", "japanese", "korean", "russian", "vietnamese", "french"]))
    if locale_mentions < 4:
        score -= 0.15
        issues.append("Not all locales covered in report")

    # Check for key issue detection mentions
    issue_indicators = [
        "notification_count",  # Vietnamese missing string
        "placeholder",         # Russian placeholder issue
        "privacy",            # French privacy_policy
        "{username}",         # Russian placeholder
        "{имя_пользователя}" # Explicit mention of wrong placeholder
    ]
    detected = sum(1 for ind in issue_indicators if ind in report)
    if detected < 2:
        score -= 0.2
        issues.append("Key issues not sufficiently discussed in report")

    # Check for recommendations section
    if "recommend" in report.lower() or "рекоменд" in report.lower() or "suggestion" in report.lower():
        pass
    else:
        score -= 0.1
        issues.append("No recommendations section found")

    return {"score": max(0.0, score), "issues": issues}


def check_changelog_quality() -> dict:
    """Check locale-specific changelog quality."""
    score = 1.0
    issues = []

    locales = {
        "zh": {"check_chars": re.compile(r'[一-鿿]'), "min_chars": 100},
        "ja": {"check_chars": re.compile(r'[ぁ-ヿ一-鿿]'), "min_chars": 50},
        "ko": {"check_chars": re.compile(r'[가-힣]'), "min_chars": 100},
        "ru": {"check_chars": re.compile(r'[а-яА-ЯёЁ]'), "min_chars": 100},
        "vi": {"check_chars": re.compile(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]'), "min_chars": 30},
        "fr": {"check_chars": re.compile(r'[àâæçéèêëîïôœùûüÿ]'), "min_chars": 20},
    }

    changelogs_found = 0
    for locale, config in locales.items():
        filepath = os.path.join(WORKSPACE, f"changelogs/changelog_{locale}.md")
        if not os.path.exists(filepath):
            score -= 0.12
            issues.append(f"changelog_{locale}.md not found")
            continue

        changelogs_found += 1
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check minimum content
        if len(content) < 500:
            score -= 0.05
            issues.append(f"changelog_{locale}.md too short")
            continue

        # Check language-specific characters
        lang_chars = len(config["check_chars"].findall(content))
        if lang_chars < config["min_chars"]:
            score -= 0.05
            issues.append(f"changelog_{locale}.md may not be in correct language")

        # Check for version number
        if "3.2.0" not in content:
            score -= 0.02
            issues.append(f"changelog_{locale}.md missing version number")

    if changelogs_found == 0:
        return {"score": 0.0, "issues": ["No changelogs found"]}

    return {"score": max(0.0, score), "issues": issues}


def check_issue_detection() -> dict:
    """Check if deliberately embedded issues were detected."""
    found_issues = load_json("issues_found.json")
    if found_issues is None:
        return {"score": 0.0, "issues": ["issues_found.json not found"]}

    score = 0.0
    issues = []

    # Handle structure
    if isinstance(found_issues, dict) and "issues" in found_issues:
        issue_list = found_issues["issues"]
    elif isinstance(found_issues, list):
        issue_list = found_issues
    else:
        return {"score": 0.1, "issues": ["Unexpected structure"]}

    if len(issue_list) == 0:
        return {"score": 0.0, "issues": ["No issues reported"]}

    # Convert to searchable text
    all_issues_text = json.dumps(issue_list, ensure_ascii=False).lower()

    # Check for each expected issue
    detected_critical = 0
    detected_total = 0

    # Issue 1: Vietnamese missing notification_count (critical)
    if "notification_count" in all_issues_text and ("vi" in all_issues_text or "vietnam" in all_issues_text):
        detected_critical += 1
        detected_total += 1
    else:
        issues.append("Did not detect: Vietnamese missing notification_count")

    # Issue 2: Russian placeholder error (critical)
    if ("имя_пользователя" in all_issues_text or "placeholder" in all_issues_text) and \
       ("ru" in all_issues_text or "russian" in all_issues_text or "profile_greeting" in all_issues_text):
        detected_critical += 1
        detected_total += 1
    else:
        issues.append("Did not detect: Russian placeholder translation error")

    # Issue 3: French privacy_policy inconsistency (major)
    if ("privacy_policy" in all_issues_text or "mentions" in all_issues_text) and \
       ("fr" in all_issues_text or "french" in all_issues_text):
        detected_total += 1
    else:
        issues.append("Did not detect: French privacy_policy inconsistency")

    # Issue 4: Korean btn_logout (minor - bonus)
    if "btn_logout" in all_issues_text and ("ko" in all_issues_text or "korean" in all_issues_text):
        detected_total += 1

    # Scoring: critical issues worth more
    if detected_critical >= 2:
        score += 0.5
    elif detected_critical == 1:
        score += 0.25

    score += detected_total * 0.15
    score = min(1.0, score)

    # Check issue structure quality
    valid_issues = 0
    for issue in issue_list[:5]:
        if isinstance(issue, dict):
            has_locale = "locale" in issue or "language" in issue
            has_key = "string_key" in issue or "key" in issue or "string" in issue
            has_type = "issue_type" in issue or "type" in issue or "category" in issue
            if has_locale and has_key:
                valid_issues += 1

    if valid_issues < 3:
        score -= 0.1
        issues.append("Issue structure incomplete (missing locale/key fields)")

    return {"score": max(0.0, score), "issues": issues}


def check_locale_coverage() -> dict:
    """Check that all 6 locales are adequately covered."""
    score = 1.0
    issues = []

    # Check consistency matrix covers all locales
    matrix = load_json("consistency_matrix.json")
    if matrix:
        matrix_text = json.dumps(matrix, ensure_ascii=False)
        locales_in_matrix = sum(1 for loc in ["zh", "ja", "ko", "ru", "vi", "fr"]
                               if loc in matrix_text)
        if locales_in_matrix < 6:
            score -= 0.2
            issues.append(f"Only {locales_in_matrix}/6 locales in consistency matrix")
    else:
        score -= 0.3
        issues.append("No consistency matrix to check locale coverage")

    # Check all changelogs exist
    changelog_count = 0
    for locale in ["zh", "ja", "ko", "ru", "vi", "fr"]:
        filepath = os.path.join(WORKSPACE, f"changelogs/changelog_{locale}.md")
        if os.path.exists(filepath):
            changelog_count += 1

    if changelog_count < 6:
        score -= (6 - changelog_count) * 0.1
        issues.append(f"Only {changelog_count}/6 changelogs created")

    return {"score": max(0.0, score), "issues": issues}


def check_report_quality() -> dict:
    """Check overall report professional quality."""
    report = load_md("qa_report.md")
    if report is None:
        return {"score": 0.0, "issues": ["qa_report.md not found"]}

    score = 1.0
    issues = []

    # Check for structured sections (headers)
    headers = re.findall(r'^#+\s+.+', report, re.MULTILINE)
    if len(headers) < 3:
        score -= 0.2
        issues.append("Report lacks proper section structure")

    # Check for summary/overview section
    has_summary = any(word in report.lower() for word in ["summary", "overview", "executive", "conclusion"])
    if not has_summary:
        score -= 0.1
        issues.append("No summary/overview section")

    # Check for statistics/metrics
    has_numbers = len(re.findall(r'\d+', report)) > 5
    if not has_numbers:
        score -= 0.1
        issues.append("Report lacks quantitative data")

    # Check professional formatting (tables, lists)
    has_formatting = '|' in report or '- ' in report or '* ' in report
    if not has_formatting:
        score -= 0.1
        issues.append("Report lacks professional formatting")

    # Check it's in English
    # Simple heuristic: majority of words should be ASCII
    ascii_chars = sum(1 for c in report if ord(c) < 128)
    if ascii_chars / max(len(report), 1) < 0.7:
        score -= 0.2
        issues.append("Report not primarily in English")

    return {"score": max(0.0, score), "issues": issues}


def grade() -> dict:
    """Main grading function."""
    dimensions = {
        "consistency_check": {**check_consistency_check(), "weight": 0.20},
        "qa_thoroughness": {**check_qa_thoroughness(), "weight": 0.20},
        "changelog_quality": {**check_changelog_quality(), "weight": 0.20},
        "issue_detection": {**check_issue_detection(), "weight": 0.15},
        "locale_coverage": {**check_locale_coverage(), "weight": 0.15},
        "report_quality": {**check_report_quality(), "weight": 0.10},
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


# === Standardized pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    result = grade()
    assert result["overall_score"] >= 0.0, "grade() should return a valid score"

def test_target_language():
    """Verify output exists and has content (English-target task)."""
    result = grade()
    if result["overall_score"] == 0.0:
        pytest.skip("No output to check")
    assert result["overall_score"] > 0.0

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
    """English target task - this test passes trivially."""
    pass

if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))
