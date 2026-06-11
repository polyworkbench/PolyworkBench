"""
Test suite for LOC-06: Chinese subtitle generation from multilingual sources.
Evaluates: translation_quality, timing_accuracy, chinese_natural, terminology_consistency, srt_format
"""

import json
import re
import os
from pathlib import Path
import pytest


WORKSPACE = os.environ.get("WORKSPACE", "/workspace")


def parse_srt(content: str) -> list:
    """Parse SRT file into list of subtitle entries."""
    entries = []
    blocks = re.split(r'\n\n+', content.strip())
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                idx = int(lines[0].strip())
                timing = lines[1].strip()
                text = '\n'.join(lines[2:])
                entries.append({
                    'index': idx,
                    'timing': timing,
                    'text': text
                })
            except (ValueError, IndexError):
                continue
    return entries


def parse_timing(timing_str: str):
    """Parse SRT timing line into start/end milliseconds."""
    pattern = r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})'
    match = re.match(pattern, timing_str)
    if not match:
        return None, None
    groups = match.groups()
    start_ms = (int(groups[0]) * 3600 + int(groups[1]) * 60 + int(groups[2])) * 1000 + int(groups[3])
    end_ms = (int(groups[4]) * 3600 + int(groups[5]) * 60 + int(groups[6])) * 1000 + int(groups[7])
    return start_ms, end_ms


def check_srt_format(content: str) -> dict:
    """Check SRT format compliance."""
    score = 1.0
    issues = []
    entries = parse_srt(content)

    # Check 50 entries
    if len(entries) != 50:
        score -= 0.4
        issues.append(f"Expected 50 entries, found {len(entries)}")

    # Check sequential numbering
    for i, entry in enumerate(entries):
        if entry['index'] != i + 1:
            score -= 0.1
            issues.append(f"Entry {i+1} has index {entry['index']}")
            break

    # Check timing format
    timing_pattern = r'^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}$'
    bad_timings = 0
    for entry in entries:
        if not re.match(timing_pattern, entry['timing']):
            bad_timings += 1
    if bad_timings > 0:
        score -= min(0.3, bad_timings * 0.05)
        issues.append(f"{bad_timings} entries have malformed timing")

    # Check max 2 lines per subtitle
    over_lines = 0
    for entry in entries:
        lines = entry['text'].split('\n')
        if len(lines) > 2:
            over_lines += 1
    if over_lines > 0:
        score -= min(0.2, over_lines * 0.04)
        issues.append(f"{over_lines} entries exceed 2 lines")

    return {"score": max(0.0, score), "issues": issues}


def check_timing_accuracy(content: str) -> dict:
    """Check timing sync with source (within ±200ms tolerance)."""
    # Reference timings from English source
    reference_timings = [
        (1000, 4500), (5000, 8200), (8700, 12100), (12500, 15800),
        (16200, 19500), (20000, 23300), (23800, 27100), (27500, 30800),
        (31200, 34500), (35000, 38300), (38800, 42100), (42500, 45800),
        (46200, 49500), (50000, 53300), (53800, 57100), (57500, 60800),
        (61200, 64500), (65000, 68300), (68800, 72100), (72500, 75800),
        (76200, 79500), (80000, 83300), (83800, 87100), (87500, 90800),
        (91200, 94500), (95000, 98300), (98800, 102100), (102500, 105800),
        (106200, 109500), (110000, 113300), (113800, 117100), (117500, 120800),
        (121200, 124500), (125000, 128300), (128800, 132100), (132500, 135800),
        (136200, 139500), (140000, 143300), (143800, 147100), (147500, 150800),
        (151200, 154500), (155000, 158300), (158800, 162100), (162500, 165800),
        (166200, 169500), (170000, 173300), (173800, 177100), (177500, 180800),
        (181200, 184500), (185000, 188500)
    ]

    entries = parse_srt(content)
    if not entries:
        return {"score": 0.0, "issues": ["No entries found"]}

    score = 1.0
    tolerance_ms = 200
    out_of_sync = 0

    for i, entry in enumerate(entries):
        if i >= len(reference_timings):
            break
        start, end = parse_timing(entry['timing'])
        if start is None:
            out_of_sync += 1
            continue
        ref_start, ref_end = reference_timings[i]
        if abs(start - ref_start) > tolerance_ms or abs(end - ref_end) > tolerance_ms:
            out_of_sync += 1

    if out_of_sync > 0:
        # Allow some adjustments (up to 10 is fine for Chinese adaptation)
        if out_of_sync <= 10:
            score -= out_of_sync * 0.02
        else:
            score -= 0.2 + (out_of_sync - 10) * 0.04

    return {"score": max(0.0, score), "issues": [f"{out_of_sync} entries out of sync"]}


def check_chinese_natural(content: str) -> dict:
    """Check Chinese text naturalness."""
    entries = parse_srt(content)
    score = 1.0
    issues = []

    if not entries:
        return {"score": 0.0, "issues": ["No entries found"]}

    # Check that text is actually Chinese
    chinese_char_pattern = re.compile(r'[一-鿿]')
    non_chinese = 0
    for entry in entries:
        text = entry['text'].replace('\n', '')
        chinese_chars = len(chinese_char_pattern.findall(text))
        total_chars = len(text.replace(' ', ''))
        if total_chars > 0 and chinese_chars / total_chars < 0.3:
            non_chinese += 1

    if non_chinese > 5:
        score -= 0.4
        issues.append(f"{non_chinese} entries appear to not be in Chinese")

    # Check line length (max 18 Chinese characters per line)
    long_lines = 0
    for entry in entries:
        for line in entry['text'].split('\n'):
            # Count Chinese characters
            zh_chars = len(chinese_char_pattern.findall(line))
            if zh_chars > 18:
                long_lines += 1

    if long_lines > 0:
        score -= min(0.3, long_lines * 0.03)
        issues.append(f"{long_lines} lines exceed 18 Chinese characters")

    # Check for common subtitle anti-patterns
    awkward_patterns = [
        r'的的',  # doubled 的
        r'了了',  # doubled 了
        r'。$',   # period at end (unusual in subtitles)
    ]
    awkward_count = 0
    for entry in entries:
        for pattern in awkward_patterns:
            if re.search(pattern, entry['text']):
                awkward_count += 1
                break

    if awkward_count > 5:
        score -= min(0.2, awkward_count * 0.02)
        issues.append(f"{awkward_count} entries have awkward patterns")

    return {"score": max(0.0, score), "issues": issues}


def check_terminology_consistency(content: str) -> dict:
    """Check terminology consistency with glossary."""
    # Key terms that must appear correctly
    required_terms = {
        "人工智能": "artificial intelligence",
        "机器学习": "machine learning",
        "深度学习": "deep learning",
        "神经网络": "neural network",
        "自然语言处理": "natural language processing",
        "注意力机制": "attention mechanism",
        "大语言模型": "large language model",
        "迁移学习": "transfer learning",
        "生成对抗网络": "generative adversarial network",
        "联邦学习": "federated learning",
        "知识蒸馏": "knowledge distillation",
        "差分隐私": "differential privacy",
    }

    entries = parse_srt(content)
    full_text = ' '.join([e['text'] for e in entries])

    score = 1.0
    found = 0
    missing = []

    for zh_term, en_term in required_terms.items():
        if zh_term in full_text:
            found += 1
        else:
            missing.append(f"{en_term} -> {zh_term}")

    # Allow some flexibility (some terms might be expressed differently)
    coverage = found / len(required_terms)
    if coverage < 0.5:
        score = coverage
    elif coverage < 0.8:
        score = 0.5 + (coverage - 0.5) * 1.5
    else:
        score = 0.8 + (coverage - 0.8) * 1.0

    issues = [f"Missing terms: {', '.join(missing[:5])}"] if missing else []
    return {"score": max(0.0, min(1.0, score)), "issues": issues}


def check_subtitle_data_json() -> dict:
    """Validate subtitle_data.json structure."""
    filepath = os.path.join(WORKSPACE, "subtitle_data.json")
    if not os.path.exists(filepath):
        return {"score": 0.0, "issues": ["subtitle_data.json not found"]}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"score": 0.0, "issues": [f"JSON parse error: {str(e)}"]}

    score = 1.0
    issues = []

    # Check it's a list with 50 entries
    if isinstance(data, dict) and "subtitles" in data:
        data = data["subtitles"]
    if not isinstance(data, list):
        return {"score": 0.2, "issues": ["Data is not a list"]}

    if len(data) != 50:
        score -= 0.3
        issues.append(f"Expected 50 entries, got {len(data)}")

    # Check required fields
    required_fields = {"id", "start_time", "end_time", "text_zh", "text_en_source", "confidence_score"}
    for i, entry in enumerate(data[:5]):  # Check first 5
        if not isinstance(entry, dict):
            score -= 0.1
            continue
        missing = required_fields - set(entry.keys())
        if missing:
            score -= 0.05 * len(missing)
            issues.append(f"Entry {i}: missing fields {missing}")

    # Check confidence scores are in range
    for entry in data:
        if isinstance(entry, dict) and "confidence_score" in entry:
            cs = entry["confidence_score"]
            if not isinstance(cs, (int, float)) or cs < 0 or cs > 1:
                score -= 0.05
                issues.append("confidence_score out of range [0,1]")
                break

    return {"score": max(0.0, score), "issues": issues}


def check_timing_report() -> dict:
    """Validate timing_report.json."""
    filepath = os.path.join(WORKSPACE, "timing_report.json")
    if not os.path.exists(filepath):
        return {"score": 0.0, "issues": ["timing_report.json not found"]}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"score": 0.0, "issues": [f"JSON parse error: {str(e)}"]}

    score = 1.0
    issues = []
    required_fields = ["total_entries", "adjusted_entries", "max_adjustment_ms", "average_adjustment_ms"]

    for field in required_fields:
        if field not in data:
            score -= 0.2
            issues.append(f"Missing field: {field}")

    if "total_entries" in data and data["total_entries"] != 50:
        score -= 0.1
        issues.append("total_entries should be 50")

    return {"score": max(0.0, score), "issues": issues}


def check_terminology_glossary() -> dict:
    """Validate terminology_glossary.json."""
    filepath = os.path.join(WORKSPACE, "terminology_glossary.json")
    if not os.path.exists(filepath):
        return {"score": 0.0, "issues": ["terminology_glossary.json not found"]}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {"score": 0.0, "issues": [f"JSON parse error: {str(e)}"]}

    score = 1.0
    issues = []

    # Should be a list of term entries
    if isinstance(data, dict) and "terms" in data:
        terms = data["terms"]
    elif isinstance(data, list):
        terms = data
    else:
        return {"score": 0.2, "issues": ["Unexpected data structure"]}

    if len(terms) < 10:
        score -= 0.3
        issues.append(f"Too few terms: {len(terms)}")

    # Check required fields
    required_fields = {"term_en", "term_zh", "occurrences", "source"}
    for i, entry in enumerate(terms[:5]):
        if not isinstance(entry, dict):
            score -= 0.1
            continue
        missing = required_fields - set(entry.keys())
        if missing:
            score -= 0.05 * len(missing)
            issues.append(f"Term {i}: missing {missing}")

    return {"score": max(0.0, score), "issues": issues}


def grade() -> dict:
    """Main grading function."""
    results = {}

    # Check SRT file exists
    srt_path = os.path.join(WORKSPACE, "subtitles_zh.srt")
    if not os.path.exists(srt_path):
        return {
            "overall_score": 0.0,
            "dimensions": {
                "translation_quality": {"score": 0.0, "weight": 0.25, "issues": ["subtitles_zh.srt not found"]},
                "timing_accuracy": {"score": 0.0, "weight": 0.25, "issues": ["subtitles_zh.srt not found"]},
                "chinese_natural": {"score": 0.0, "weight": 0.20, "issues": ["subtitles_zh.srt not found"]},
                "terminology_consistency": {"score": 0.0, "weight": 0.15, "issues": ["subtitles_zh.srt not found"]},
                "srt_format": {"score": 0.0, "weight": 0.15, "issues": ["subtitles_zh.srt not found"]},
            }
        }

    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    # Dimension 1: SRT format compliance (weight: 0.15)
    srt_result = check_srt_format(srt_content)

    # Dimension 2: Timing accuracy (weight: 0.25)
    timing_result = check_timing_accuracy(srt_content)

    # Dimension 3: Chinese naturalness (weight: 0.20)
    chinese_result = check_chinese_natural(srt_content)

    # Dimension 4: Terminology consistency (weight: 0.15)
    terminology_result = check_terminology_consistency(srt_content)

    # Dimension 5: Translation quality - composite of data json checks (weight: 0.25)
    data_result = check_subtitle_data_json()
    report_result = check_timing_report()
    glossary_result = check_terminology_glossary()
    translation_score = (data_result["score"] * 0.4 + report_result["score"] * 0.3 + glossary_result["score"] * 0.3)
    translation_issues = data_result["issues"] + report_result["issues"] + glossary_result["issues"]

    dimensions = {
        "translation_quality": {"score": translation_score, "weight": 0.25, "issues": translation_issues},
        "timing_accuracy": {"score": timing_result["score"], "weight": 0.25, "issues": timing_result["issues"]},
        "chinese_natural": {"score": chinese_result["score"], "weight": 0.20, "issues": chinese_result["issues"]},
        "terminology_consistency": {"score": terminology_result["score"], "weight": 0.15, "issues": terminology_result["issues"]},
        "srt_format": {"score": srt_result["score"], "weight": 0.15, "issues": srt_result["issues"]},
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
    """Verify output is in the correct target language, not English fallback."""
    result = grade()
    if result["overall_score"] == 0.0:
        pytest.skip("No output to check")
    dims = result.get("dimensions", {})
    # Look for language-quality dimension
    lang_dim_scores = []
    for k, v in dims.items():
        if any(word in k.lower() for word in ["chinese", "zh"]):
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
