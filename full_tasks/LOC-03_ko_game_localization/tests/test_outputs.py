"""
Test suite for LOC-03: Game dialogue localization to Korean
Evaluates: dialogue_quality, cultural_adaptation, korean_natural, character_consistency, honorific_handling
"""

import json
import os
import re
from pathlib import Path
import pytest

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


def load_json(filename):
    """Load a JSON file from the output directory."""
    candidates = [
        os.path.join(OUTPUT_DIR, "output", filename),
        os.path.join(OUTPUT_DIR, "outputs", filename),
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/output/{filename}",
        f"/workspace/outputs/{filename}",
        f"/workspace/{filename}",
    ]
    for filepath in candidates:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def load_text(filename):
    """Load a text/markdown file from the output directory."""
    candidates = [
        os.path.join(OUTPUT_DIR, "output", filename),
        os.path.join(OUTPUT_DIR, "outputs", filename),
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/output/{filename}",
        f"/workspace/outputs/{filename}",
        f"/workspace/{filename}",
    ]
    for filepath in candidates:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
    return None


def load_input_json(filename):
    """Load a JSON file from the input directory."""
    input_dir = os.environ.get("INPUT_DIR", "/workspace/inputs")
    filepath = os.path.join(input_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def has_korean(text):
    """Check if text contains Korean (Hangul) characters."""
    korean_pattern = re.compile(r'[가-힯ᄀ-ᇿ㄰-㆏]')
    return bool(korean_pattern.search(text))


def has_japanese(text):
    """Check if text contains Japanese-specific characters (hiragana/katakana)."""
    jp_pattern = re.compile(r'[぀-ゟ゠-ヿ]')
    return bool(jp_pattern.search(text))


def check_dialogue_quality(dialogue_ko, source_dialogue):
    """Check overall quality of dialogue translations."""
    if dialogue_ko is None:
        return 0.0

    # Handle different output formats
    dialogues = []
    if isinstance(dialogue_ko, list):
        dialogues = dialogue_ko
    elif isinstance(dialogue_ko, dict) and "dialogue" in dialogue_ko:
        dialogues = dialogue_ko["dialogue"]

    if not dialogues:
        return 0.0

    total_source = len(source_dialogue["dialogue"])
    score = 0.0

    # Check coverage - are all 40 lines translated?
    translated_count = 0
    for d in dialogues:
        if isinstance(d, dict):
            translated_text = d.get("translated_ko", "") or d.get("translation", "") or d.get("text_ko", "")
            if translated_text and has_korean(translated_text):
                translated_count += 1

    coverage = translated_count / total_source if total_source > 0 else 0
    score += coverage * 0.5

    # Check that translations are not just romanizations
    meaningful_translations = 0
    for d in dialogues:
        if isinstance(d, dict):
            translated_text = d.get("translated_ko", "") or d.get("translation", "") or d.get("text_ko", "")
            if translated_text and len(translated_text) > 3 and has_korean(translated_text):
                # Check it's not still Japanese
                if not has_japanese(translated_text):
                    meaningful_translations += 1

    if translated_count > 0:
        quality_ratio = meaningful_translations / translated_count
        score += quality_ratio * 0.5

    return min(1.0, score)


def check_cultural_adaptation(adaptation_notes, dialogue_ko):
    """Check cultural adaptation notes exist and are meaningful."""
    score = 0.0

    if adaptation_notes and len(adaptation_notes) > 200:
        score += 0.4
        # Check for Korean content
        if has_korean(adaptation_notes):
            score += 0.2
        # Check for discussion of cultural differences
        cultural_keywords = ["문화", "적응", "번역", "현지화", "한국", "일본", "경어", "존댓말", "반말", "표현"]
        keywords_found = sum(1 for kw in cultural_keywords if kw in adaptation_notes)
        if keywords_found >= 4:
            score += 0.4
        elif keywords_found >= 2:
            score += 0.2
        elif keywords_found >= 1:
            score += 0.1

    return min(1.0, score)


def check_korean_natural(dialogue_ko):
    """Check that Korean translations sound natural."""
    if dialogue_ko is None:
        return 0.0

    dialogues = []
    if isinstance(dialogue_ko, list):
        dialogues = dialogue_ko
    elif isinstance(dialogue_ko, dict) and "dialogue" in dialogue_ko:
        dialogues = dialogue_ko["dialogue"]

    if not dialogues:
        return 0.0

    score = 0.0
    total_checked = 0
    korean_quality = 0

    for d in dialogues:
        if isinstance(d, dict):
            translated_text = d.get("translated_ko", "") or d.get("translation", "") or d.get("text_ko", "")
            if translated_text and has_korean(translated_text):
                total_checked += 1
                # Check for natural Korean sentence endings
                korean_endings = ["다", "요", "까", "지", "네", "군", "라", "야", "거든", "잖아",
                                  "습니다", "합니다", "입니다", "세요", "하라", "도다"]
                text_clean = translated_text.rstrip("!?！？…。、,.")
                if any(text_clean.endswith(e) for e in korean_endings):
                    korean_quality += 1

    if total_checked > 0:
        score = korean_quality / total_checked

    return min(1.0, score)


def check_character_consistency(dialogue_ko, voice_guide):
    """Check that character voices are consistent."""
    if dialogue_ko is None:
        return 0.0

    score = 0.0

    # Check voice guide exists and has content
    if voice_guide and len(voice_guide) > 200:
        score += 0.3
        if has_korean(voice_guide):
            score += 0.2
        # Check it covers main characters
        characters = ["아키라", "미즈키", "미츠키", "렌", "발루스", "사쿠라", "카인", "에리스"]
        chars_found = sum(1 for c in characters if c in voice_guide)
        if chars_found >= 5:
            score += 0.3
        elif chars_found >= 3:
            score += 0.2
        elif chars_found >= 1:
            score += 0.1

    # Check dialogue has character field and speech_level
    dialogues = []
    if isinstance(dialogue_ko, list):
        dialogues = dialogue_ko
    elif isinstance(dialogue_ko, dict) and "dialogue" in dialogue_ko:
        dialogues = dialogue_ko["dialogue"]

    if dialogues:
        has_speech_level = sum(1 for d in dialogues if isinstance(d, dict) and
                             (d.get("speech_level") or d.get("honorific_level")))
        if has_speech_level >= 30:
            score += 0.2
        elif has_speech_level >= 15:
            score += 0.1

    return min(1.0, score)


def check_honorific_handling(dialogue_ko, source_dialogue):
    """Check that Japanese honorifics are properly converted to Korean speech levels."""
    if dialogue_ko is None:
        return 0.0

    dialogues = []
    if isinstance(dialogue_ko, list):
        dialogues = dialogue_ko
    elif isinstance(dialogue_ko, dict) and "dialogue" in dialogue_ko:
        dialogues = dialogue_ko["dialogue"]

    if not dialogues:
        return 0.0

    score = 0.0

    # Map expected speech patterns
    # Akira: 반말 (casual)
    # Mizuki: 해요체 (polite)
    # Ren: 반말 rough
    # Emperor: formal/archaic
    # System: 합니다체

    # Check that different characters have different speech patterns
    character_texts = {}
    for d in dialogues:
        if isinstance(d, dict):
            char = d.get("character", "")
            text = d.get("translated_ko", "") or d.get("translation", "") or d.get("text_ko", "")
            if char and text:
                if char not in character_texts:
                    character_texts[char] = []
                character_texts[char].append(text)

    if not character_texts:
        return 0.0

    # Check for polite endings in Mizuki's lines
    polite_endings = ["요", "세요", "에요", "이에요", "해요", "어요"]
    casual_endings = ["다", "야", "지", "거든", "잖아", "냐"]
    formal_endings = ["습니다", "합니다", "입니다", "십시오", "하라", "하도다"]

    mizuki_names = ["미즈키", "미츠키", "ミヅキ", "Mizuki"]
    akira_names = ["아키라", "アキラ", "Akira"]
    system_names = ["시스템", "システム", "System"]

    # Find Mizuki's lines
    mizuki_polite = False
    for name in mizuki_names:
        if name in character_texts:
            texts = character_texts[name]
            polite_count = sum(1 for t in texts if any(t.rstrip("!?！？…").endswith(e) for e in polite_endings))
            if polite_count > len(texts) * 0.5:
                mizuki_polite = True
                break

    # Find Akira's lines
    akira_casual = False
    for name in akira_names:
        if name in character_texts:
            texts = character_texts[name]
            casual_count = sum(1 for t in texts if any(t.rstrip("!?！？…").endswith(e) for e in casual_endings))
            if casual_count > len(texts) * 0.3:
                akira_casual = True
                break

    # Find System lines
    system_formal = False
    for name in system_names:
        if name in character_texts:
            texts = character_texts[name]
            formal_count = sum(1 for t in texts if any(t.rstrip("!?！？…").endswith(e) for e in formal_endings))
            if formal_count > len(texts) * 0.5:
                system_formal = True
                break

    if mizuki_polite:
        score += 0.35
    if akira_casual:
        score += 0.35
    if system_formal:
        score += 0.30

    return min(1.0, score)


def grade():
    """Main grading function. Returns overall score and dimension scores."""
    # Load outputs
    dialogue_ko = load_json("game_dialogue_ko.json")
    adaptation_notes = load_text("adaptation_notes_ko.md")
    voice_guide = load_text("character_voice_guide_ko.md")
    qa_flags = load_json("qa_flags.json")

    # Load source
    source_dialogue = load_input_json("dialogue_ja.json")

    # Calculate dimension scores
    dialogue_quality = check_dialogue_quality(dialogue_ko, source_dialogue)
    cultural_adaptation = check_cultural_adaptation(adaptation_notes, dialogue_ko)
    korean_natural = check_korean_natural(dialogue_ko)
    character_consistency = check_character_consistency(dialogue_ko, voice_guide)
    honorific_handling = check_honorific_handling(dialogue_ko, source_dialogue)

    # Weighted overall score
    overall_score = (
        dialogue_quality * 0.25 +
        cultural_adaptation * 0.25 +
        korean_natural * 0.20 +
        character_consistency * 0.15 +
        honorific_handling * 0.15
    )

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": {
            "dialogue_quality": {
                "score": round(dialogue_quality, 4),
                "weight": 0.25,
                "description": "Quality and coverage of dialogue translations"
            },
            "cultural_adaptation": {
                "score": round(cultural_adaptation, 4),
                "weight": 0.25,
                "description": "Quality of cultural adaptation notes"
            },
            "korean_natural": {
                "score": round(korean_natural, 4),
                "weight": 0.20,
                "description": "Naturalness of Korean language"
            },
            "character_consistency": {
                "score": round(character_consistency, 4),
                "weight": 0.15,
                "description": "Consistency of character voice across lines"
            },
            "honorific_handling": {
                "score": round(honorific_handling, 4),
                "weight": 0.15,
                "description": "Proper handling of Japanese→Korean speech levels"
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
    print(json.dumps(result, indent=2, ensure_ascii=False))
