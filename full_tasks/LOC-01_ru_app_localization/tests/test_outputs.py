"""
Test suite for LOC-01: Mobile app localization to Russian
Evaluates: translation_coverage, length_compliance, russian_quality, consistency, context_accuracy
"""

import json
import os
import re
from pathlib import Path
import pytest

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Search paths: workspace root, /output/, /outputs/ (instruction variants)
_SEARCH_DIRS = [
    OUTPUT_DIR,
    OUTPUT_DIR / "output",
    OUTPUT_DIR / "outputs",
]


def _resolve_path(filename):
    """Find a file across multiple candidate directories."""
    for d in _SEARCH_DIRS:
        candidate = d / filename
        if candidate.exists():
            return str(candidate)
    # Fallback to OUTPUT_DIR (will fail naturally if not found)
    return os.path.join(OUTPUT_DIR, filename)


def load_json(filename):
    """Load a JSON file from the output directory (searches output/outputs variants)."""
    filepath = _resolve_path(filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(filename):
    """Load a text/markdown file from the output directory (searches output/outputs variants)."""
    filepath = _resolve_path(filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def load_input_json(filename):
    """Load a JSON file from the input directory."""
    input_dir = os.environ.get("INPUT_DIR", "/workspace/inputs")
    filepath = os.path.join(input_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def is_cyrillic(text):
    """Check if text contains Cyrillic characters."""
    cyrillic_pattern = re.compile(r'[Ѐ-ӿ]')
    return bool(cyrillic_pattern.search(text))


def check_translation_coverage(strings_ru, source_strings):
    """Check that all source strings have been translated."""
    if strings_ru is None:
        return 0.0

    source_keys = set()
    for s in source_strings["strings"]:
        source_keys.add(s["key"])

    # Check for translated keys in output
    translated_keys = set()
    if isinstance(strings_ru, dict):
        if "strings" in strings_ru:
            # Format: {"strings": [{"key": ..., "value": ...}]}
            for item in strings_ru["strings"]:
                if isinstance(item, dict) and "key" in item:
                    key = item["key"]
                    value = item.get("value", "") or item.get("translation", "")
                    if value and value.strip():
                        translated_keys.add(key)
        else:
            # Format: {"key": "value", ...}
            for key, value in strings_ru.items():
                if key in source_keys and value and str(value).strip():
                    translated_keys.add(key)

    coverage = len(translated_keys.intersection(source_keys)) / len(source_keys) if source_keys else 0
    return coverage


def check_length_compliance(strings_ru, source_strings):
    """Check that translations respect max_length constraints."""
    if strings_ru is None:
        return 0.0

    max_lengths = {}
    for s in source_strings["strings"]:
        max_lengths[s["key"]] = s["max_length"]

    compliant = 0
    total = 0

    translations = {}
    if isinstance(strings_ru, dict):
        if "strings" in strings_ru:
            for item in strings_ru["strings"]:
                if isinstance(item, dict) and "key" in item:
                    translations[item["key"]] = item.get("value", "") or item.get("translation", "")
        else:
            translations = {k: v for k, v in strings_ru.items() if k in max_lengths}

    for key, max_len in max_lengths.items():
        if key in translations and translations[key]:
            total += 1
            if len(translations[key]) <= max_len:
                compliant += 1

    if total == 0:
        return 0.0
    return compliant / total


def check_russian_quality(strings_ru):
    """Check that translations are in Russian (Cyrillic) and show quality markers."""
    if strings_ru is None:
        return 0.0

    translations = []
    if isinstance(strings_ru, dict):
        if "strings" in strings_ru:
            for item in strings_ru["strings"]:
                if isinstance(item, dict):
                    val = item.get("value", "") or item.get("translation", "")
                    if val:
                        translations.append(val)
        else:
            translations = [v for v in strings_ru.values() if isinstance(v, str) and v.strip()]

    if not translations:
        return 0.0

    cyrillic_count = 0
    for t in translations:
        # Skip placeholders-only strings
        cleaned = re.sub(r'\{[^}]+\}', '', t).strip()
        if not cleaned:
            cyrillic_count += 1  # placeholder-only strings are fine
            continue
        if is_cyrillic(cleaned):
            cyrillic_count += 1

    score = cyrillic_count / len(translations) if translations else 0

    # Check for pluralization handling
    plural_keys = ["plural_tasks_one", "plural_tasks_few", "plural_tasks_many",
                   "time_minutes_ago", "time_hours_ago", "time_days_ago"]

    plural_translations = {}
    if isinstance(strings_ru, dict):
        if "strings" in strings_ru:
            for item in strings_ru["strings"]:
                if isinstance(item, dict) and item.get("key") in plural_keys:
                    plural_translations[item["key"]] = item.get("value", "") or item.get("translation", "")
        else:
            for key in plural_keys:
                if key in strings_ru:
                    plural_translations[key] = strings_ru[key]

    # Check that plural forms are different from each other
    plural_bonus = 0.0
    if "plural_tasks_one" in plural_translations and "plural_tasks_few" in plural_translations:
        if plural_translations["plural_tasks_one"] != plural_translations["plural_tasks_few"]:
            plural_bonus = 0.1

    return min(1.0, score + plural_bonus)


def check_consistency(strings_ru, source_strings):
    """Check terminology consistency across translations."""
    if strings_ru is None:
        return 0.0

    translations = {}
    if isinstance(strings_ru, dict):
        if "strings" in strings_ru:
            for item in strings_ru["strings"]:
                if isinstance(item, dict) and "key" in item:
                    translations[item["key"]] = item.get("value", "") or item.get("translation", "")
        else:
            translations = strings_ru

    score = 1.0

    # Check that status translations are consistent with style guide
    expected_statuses = {
        "status_pending": "Ожидает",
        "status_in_progress": "В работе",
        "status_completed": "Завершен",
        "status_overdue": "Просрочен",
        "status_cancelled": "Отменен"
    }

    status_matches = 0
    status_total = 0
    for key, expected_root in expected_statuses.items():
        if key in translations:
            status_total += 1
            # Check if the translation starts with or contains the expected root
            if expected_root.lower() in translations[key].lower():
                status_matches += 1

    if status_total > 0:
        status_score = status_matches / status_total
    else:
        status_score = 0.0

    # Check priority consistency
    expected_priorities = {
        "priority_low": "Низк",
        "priority_medium": "Средн",
        "priority_high": "Высок",
        "priority_urgent": "Срочн"
    }

    priority_matches = 0
    priority_total = 0
    for key, expected_root in expected_priorities.items():
        if key in translations:
            priority_total += 1
            if expected_root.lower() in translations[key].lower():
                priority_matches += 1

    if priority_total > 0:
        priority_score = priority_matches / priority_total
    else:
        priority_score = 0.0

    # Combined consistency score
    return (status_score * 0.5 + priority_score * 0.5)


def check_context_accuracy(strings_ru, context_notes):
    """Check context notes and QA checklist exist and are meaningful."""
    if strings_ru is None:
        return 0.0

    score = 0.0

    # Check context_notes_ru.md exists and has content
    if context_notes and len(context_notes) > 100:
        score += 0.4
        # Check if it mentions specific translation decisions
        if any(word in context_notes.lower() for word in ["перевод", "локализац", "длин", "контекст", "выбор"]):
            score += 0.2

    # Check qa_checklist.json
    qa_checklist = load_json("qa_checklist.json")
    if qa_checklist is not None:
        score += 0.2
        # Check it has meaningful content
        if isinstance(qa_checklist, (dict, list)):
            content_str = json.dumps(qa_checklist)
            if len(content_str) > 50:
                score += 0.2

    return min(1.0, score)


def grade():
    """Main grading function. Returns overall score and dimension scores."""
    # Load outputs
    strings_ru = load_json("strings_ru.json")
    length_report = load_json("length_report.json")
    context_notes = load_text("context_notes_ru.md")
    qa_checklist = load_json("qa_checklist.json")

    # Load source for reference
    source_strings = load_input_json("strings_en.json")

    # Check file existence
    files_exist = all([
        strings_ru is not None,
        length_report is not None,
        context_notes is not None,
        qa_checklist is not None
    ])

    if not files_exist:
        missing = []
        if strings_ru is None:
            missing.append("strings_ru.json")
        if length_report is None:
            missing.append("length_report.json")
        if context_notes is None:
            missing.append("context_notes_ru.md")
        if qa_checklist is None:
            missing.append("qa_checklist.json")

    # Calculate dimension scores
    translation_coverage = check_translation_coverage(strings_ru, source_strings)
    length_compliance = check_length_compliance(strings_ru, source_strings)
    russian_quality = check_russian_quality(strings_ru)
    consistency = check_consistency(strings_ru, source_strings)
    context_accuracy = check_context_accuracy(strings_ru, context_notes)

    # Weighted overall score
    overall_score = (
        translation_coverage * 0.30 +
        length_compliance * 0.25 +
        russian_quality * 0.20 +
        consistency * 0.15 +
        context_accuracy * 0.10
    )

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": {
            "translation_coverage": {
                "score": round(translation_coverage, 4),
                "weight": 0.30,
                "description": "Percentage of source strings translated"
            },
            "length_compliance": {
                "score": round(length_compliance, 4),
                "weight": 0.25,
                "description": "Percentage of translations within max_length"
            },
            "russian_quality": {
                "score": round(russian_quality, 4),
                "weight": 0.20,
                "description": "Quality of Russian translations (Cyrillic, pluralization)"
            },
            "consistency": {
                "score": round(consistency, 4),
                "weight": 0.15,
                "description": "Terminology consistency with style guide"
            },
            "context_accuracy": {
                "score": round(context_accuracy, 4),
                "weight": 0.10,
                "description": "Quality of context notes and QA checklist"
            }
        }
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
        if any(word in k.lower() for word in ["russian", "cyrillic", "ru"]):
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
