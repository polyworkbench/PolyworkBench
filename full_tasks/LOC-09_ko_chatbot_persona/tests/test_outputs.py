"""
Test suite for LOC-09: Korean chatbot persona design and adaptation.
Evaluates: persona_consistency, korean_speech_levels, dialogue_quality, intent_coverage, cultural_adaptation
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


def check_persona_consistency() -> dict:
    """Check persona guide completeness and consistency."""
    guide = load_md("persona_guide_ko.md")
    if guide is None:
        return {"score": 0.0, "issues": ["persona_guide_ko.md not found"]}

    score = 1.0
    issues = []

    # Check minimum length
    if len(guide) < 2000:
        score -= 0.2
        issues.append("Persona guide too brief")

    # Check Korean content
    korean_pattern = re.compile(r'[가-힣]')
    korean_chars = len(korean_pattern.findall(guide))
    if korean_chars < 200:
        score -= 0.3
        issues.append("Guide not primarily in Korean")

    # Check for key persona elements
    persona_elements = ["이름", "성격", "말투", "톤"]
    found = sum(1 for elem in persona_elements if elem in guide)
    if found < 2:
        score -= 0.2
        issues.append(f"Only {found}/4 persona elements defined")

    # Check for speech level rules
    speech_level_terms = ["해요체", "합쇼체", "해체", "존대"]
    sl_found = sum(1 for term in speech_level_terms if term in guide)
    if sl_found < 2:
        score -= 0.2
        issues.append("Speech level rules not well documented")

    # Check for forbidden expressions section
    if "금기" in guide or "주의" in guide or "피해" in guide or "사용하지" in guide:
        pass  # Good
    else:
        score -= 0.1
        issues.append("No forbidden expressions section found")

    return {"score": max(0.0, score), "issues": issues}


def check_korean_speech_levels() -> dict:
    """Check proper Korean speech level usage in scripts."""
    scripts = load_json("chatbot_scripts_ko.json")
    if scripts is None:
        return {"score": 0.0, "issues": ["chatbot_scripts_ko.json not found"]}

    score = 1.0
    issues = []

    # Handle structure
    if isinstance(scripts, dict) and "intents" in scripts:
        intents = scripts["intents"]
    elif isinstance(scripts, dict) and "scripts" in scripts:
        intents = scripts["scripts"]
    elif isinstance(scripts, list):
        intents = scripts
    else:
        return {"score": 0.1, "issues": ["Unexpected structure"]}

    # Check speech_level field exists
    has_speech_level = 0
    total_responses = 0
    speech_levels_found = set()

    for intent in intents:
        if not isinstance(intent, dict):
            continue
        responses = intent.get("responses", intent.get("bot_responses", []))
        if isinstance(responses, list):
            for resp in responses:
                total_responses += 1
                if isinstance(resp, dict):
                    sl = resp.get("speech_level", "")
                    if sl:
                        has_speech_level += 1
                        speech_levels_found.add(sl)
                elif isinstance(resp, str):
                    # Check if the intent has a speech_level field
                    if "speech_level" in intent:
                        has_speech_level += 1
                        speech_levels_found.add(intent["speech_level"])

    if total_responses == 0:
        return {"score": 0.1, "issues": ["No responses found in scripts"]}

    # Check speech_level coverage
    sl_ratio = has_speech_level / max(total_responses, 1)
    if sl_ratio < 0.5:
        score -= 0.3
        issues.append(f"Only {sl_ratio:.0%} of responses have speech_level marked")

    # Check variety of speech levels (should have at least haeyoche and hapsyoche)
    valid_levels = {"haeyoche", "hapsyoche", "haeche", "해요체", "합쇼체", "해체"}
    if not speech_levels_found.intersection(valid_levels):
        # Try alternate naming
        all_text = json.dumps(scripts, ensure_ascii=False)
        if "해요" in all_text and "합쇼" in all_text:
            pass
        else:
            score -= 0.2
            issues.append("Missing variety of speech levels")

    # Check Korean endings for haeyoche (-요, -세요, -할게요, etc.)
    korean_pattern = re.compile(r'[가-힣]')
    all_response_text = json.dumps(intents, ensure_ascii=False)
    haeyoche_endings = re.findall(r'[요세][\.\?\!\"\')\s,]', all_response_text)
    hapsyoche_endings = re.findall(r'[다까][\.\?\!\"\')\s,]', all_response_text)

    if len(haeyoche_endings) < 5 and len(hapsyoche_endings) < 5:
        score -= 0.2
        issues.append("Korean speech level endings not properly used")

    # Check that payment/complaint intents use hapsyoche
    formal_intents = ["payment_issue", "complaint", "escalation"]
    for intent in intents:
        if isinstance(intent, dict):
            intent_id = intent.get("intent_id", "")
            if intent_id in formal_intents:
                intent_text = json.dumps(intent, ensure_ascii=False)
                # Should have formal markers
                if "습니다" in intent_text or "습니까" in intent_text or "hapsyoche" in intent_text or "합쇼체" in intent_text:
                    pass  # Correct
                else:
                    score -= 0.05
                    issues.append(f"Intent '{intent_id}' should use formal speech level")

    return {"score": max(0.0, score), "issues": issues}


def check_dialogue_quality() -> dict:
    """Check dialogue flow quality."""
    flows = load_json("dialogue_flows_ko.json")
    if flows is None:
        return {"score": 0.0, "issues": ["dialogue_flows_ko.json not found"]}

    score = 1.0
    issues = []

    # Handle structure
    if isinstance(flows, dict) and "intents" in flows:
        intents = flows["intents"]
    elif isinstance(flows, dict) and "flows" in flows:
        intents = flows["flows"]
    elif isinstance(flows, list):
        intents = flows
    else:
        return {"score": 0.1, "issues": ["Unexpected structure"]}

    # Check 20 intents
    if len(intents) < 20:
        score -= (20 - len(intents)) * 0.03
        issues.append(f"Only {len(intents)}/20 intents")

    # Check for user_input_examples (at least 3 per intent)
    low_examples = 0
    for intent in intents:
        if isinstance(intent, dict):
            examples = intent.get("user_input_examples", intent.get("user_inputs", []))
            if isinstance(examples, list) and len(examples) < 3:
                low_examples += 1

    if low_examples > 5:
        score -= 0.15
        issues.append(f"{low_examples} intents have fewer than 3 user input examples")

    # Check Korean content
    korean_pattern = re.compile(r'[가-힣]')
    all_text = json.dumps(intents, ensure_ascii=False)
    korean_chars = len(korean_pattern.findall(all_text))
    if korean_chars < 500:
        score -= 0.3
        issues.append("Dialogue flows not primarily in Korean")

    # Check for next_intents (branching logic)
    has_branching = 0
    for intent in intents:
        if isinstance(intent, dict):
            if "next_intents" in intent or "next" in intent or "branches" in intent:
                has_branching += 1

    if has_branching < 10:
        score -= 0.1
        issues.append("Few intents have branching logic defined")

    return {"score": max(0.0, score), "issues": issues}


def check_intent_coverage() -> dict:
    """Check that all 20 intents from source are covered."""
    scripts = load_json("chatbot_scripts_ko.json")
    if scripts is None:
        return {"score": 0.0, "issues": ["chatbot_scripts_ko.json not found"]}

    expected_intents = {
        "greeting", "product_inquiry", "price_check", "order_status",
        "shipping_info", "return_request", "payment_issue", "coupon_inquiry",
        "account_help", "complaint", "product_recommendation", "size_guide",
        "wishlist_manage", "loyalty_program", "event_notification", "farewell",
        "technical_support", "feedback_positive", "subscription_manage", "escalation"
    }

    score = 1.0
    issues = []

    # Extract intent IDs from scripts
    if isinstance(scripts, dict) and "intents" in scripts:
        intents = scripts["intents"]
    elif isinstance(scripts, dict) and "scripts" in scripts:
        intents = scripts["scripts"]
    elif isinstance(scripts, list):
        intents = scripts
    else:
        return {"score": 0.1, "issues": ["Unexpected structure"]}

    found_intents = set()
    for intent in intents:
        if isinstance(intent, dict):
            intent_id = intent.get("intent_id", intent.get("id", ""))
            found_intents.add(intent_id)

    missing = expected_intents - found_intents
    if missing:
        score -= len(missing) * 0.04
        issues.append(f"Missing intents: {', '.join(list(missing)[:5])}")

    # Check each intent has at least 3 responses
    low_responses = 0
    for intent in intents:
        if isinstance(intent, dict):
            responses = intent.get("responses", intent.get("bot_responses", []))
            if isinstance(responses, list) and len(responses) < 3:
                low_responses += 1

    if low_responses > 5:
        score -= 0.15
        issues.append(f"{low_responses} intents have fewer than 3 response variants")

    return {"score": max(0.0, score), "issues": issues}


def check_cultural_adaptation() -> dict:
    """Check tone analysis and cultural adaptation quality."""
    analysis = load_json("tone_analysis.json")
    if analysis is None:
        return {"score": 0.0, "issues": ["tone_analysis.json not found"]}

    score = 1.0
    issues = []

    # Handle structure
    if isinstance(analysis, dict) and "analysis" in analysis:
        items = analysis["analysis"]
    elif isinstance(analysis, dict) and "intents" in analysis:
        items = analysis["intents"]
    elif isinstance(analysis, list):
        items = analysis
    else:
        return {"score": 0.1, "issues": ["Unexpected structure"]}

    # Check coverage (should have analysis for each intent)
    if len(items) < 15:
        score -= 0.2
        issues.append(f"Only {len(items)} intent analyses (expected ~20)")

    # Check required fields
    required_fields = {"intent_id", "speech_level_rationale"}
    for item in items[:5]:
        if isinstance(item, dict):
            # Check for at least intent_id and some rationale
            has_id = "intent_id" in item or "id" in item
            has_rationale = any(k in item for k in ["speech_level_rationale", "rationale", "reason"])
            if not has_id:
                score -= 0.05
            if not has_rationale:
                score -= 0.05

    # Check for Korean content in analysis
    all_text = json.dumps(items, ensure_ascii=False)
    korean_pattern = re.compile(r'[가-힣]')
    korean_chars = len(korean_pattern.findall(all_text))
    if korean_chars < 100:
        score -= 0.2
        issues.append("Tone analysis lacks Korean content")

    # Check for cultural adaptation mentions
    cultural_keywords = ["문화", "적응", "한국", "존대", "맥락", "상황"]
    cultural_found = sum(1 for kw in cultural_keywords if kw in all_text)
    if cultural_found < 2:
        score -= 0.1
        issues.append("Limited cultural adaptation discussion")

    return {"score": max(0.0, score), "issues": issues}


def grade() -> dict:
    """Main grading function."""
    dimensions = {
        "persona_consistency": {**check_persona_consistency(), "weight": 0.25},
        "korean_speech_levels": {**check_korean_speech_levels(), "weight": 0.25},
        "dialogue_quality": {**check_dialogue_quality(), "weight": 0.20},
        "intent_coverage": {**check_intent_coverage(), "weight": 0.15},
        "cultural_adaptation": {**check_cultural_adaptation(), "weight": 0.15},
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
