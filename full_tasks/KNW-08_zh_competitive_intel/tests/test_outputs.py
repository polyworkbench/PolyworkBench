"""
BabelAgentBench grading for KNW-08: Chinese competitive intelligence from EN/KO/JA sources.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Key facts that should be extracted from competitor sources
COMPETITOR_A_FACTS = ["NovaTech", "Nova-7", "3nm", "3200", "18.4", "67%", "32000"]
COMPETITOR_B_FACTS = ["SiliconWave", "Wave-5", "4800", "6.8", "142%", "15000"]
COMPETITOR_C_FACTS = ["QuantumCore", "QC-X4", "280", "4.7", "58%", "480"]


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_json(name: str) -> Any:
    path = _find_file(name)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return None


def _load_text(name: str) -> str:
    path = _find_file(name)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            pass
    return ""


def _is_chinese(text: str) -> bool:
    """Check if text contains significant Chinese characters."""
    if not text:
        return False
    cjk_count = sum(1 for c in text if '一' <= c <= '鿿')
    return cjk_count / max(len(text), 1) > 0.15


def _score_extraction_accuracy(digest_text: str, profiles: Any) -> Dict[str, float]:
    """Score accuracy of extracted competitor information."""
    scores = {}

    if not digest_text and not profiles:
        return {"digest_exists": 0.0, "competitor_a_facts": 0.0,
                "competitor_b_facts": 0.0, "competitor_c_facts": 0.0}

    combined_text = digest_text + " " + json.dumps(profiles or {}, ensure_ascii=False)

    scores["digest_exists"] = 1.0 if digest_text else 0.0

    # Check competitor A facts
    a_found = sum(1 for f in COMPETITOR_A_FACTS if f in combined_text)
    scores["competitor_a_facts"] = min(1.0, a_found / 4.0)

    # Check competitor B facts
    b_found = sum(1 for f in COMPETITOR_B_FACTS if f in combined_text)
    scores["competitor_b_facts"] = min(1.0, b_found / 4.0)

    # Check competitor C facts
    c_found = sum(1 for f in COMPETITOR_C_FACTS if f in combined_text)
    scores["competitor_c_facts"] = min(1.0, c_found / 4.0)

    return scores


def _score_analysis_depth(digest_text: str, threat_data: Any) -> Dict[str, float]:
    """Score the depth of competitive analysis."""
    scores = {}

    if not digest_text and not threat_data:
        return {"threat_analysis_exists": 0.0, "comparative_analysis": 0.0,
                "actionable_insights": 0.0}

    scores["threat_analysis_exists"] = 1.0 if threat_data else 0.0

    # Check for comparative analysis elements
    combined = digest_text + " " + json.dumps(threat_data or {}, ensure_ascii=False)
    comparison_markers = ["vs", "compared", "advantage", "disadvantage",
                          "stronger", "weaker", "threat", "opportunity"]
    cn_markers = ["对比", "优势", "劣势", "威胁",
                  "机会", "竞争", "超越", "领先",
                  "差距", "应对"]
    markers_found = sum(1 for m in comparison_markers + cn_markers if m in combined.lower())
    scores["comparative_analysis"] = min(1.0, markers_found / 5.0)

    # Check for actionable insights
    action_markers = ["建议", "应当", "需要",
                      "加快", "加强", "提升",
                      "应对措施", "战略"]
    action_found = sum(1 for m in action_markers if m in combined)
    scores["actionable_insights"] = min(1.0, action_found / 4.0)

    return scores


def _score_chinese_quality(digest_text: str, implications_text: str) -> Dict[str, float]:
    """Score Chinese language quality."""
    scores = {}

    if not digest_text and not implications_text:
        return {"digest_chinese": 0.0, "implications_chinese": 0.0, "length_adequate": 0.0}

    scores["digest_chinese"] = 1.0 if _is_chinese(digest_text) else 0.0
    scores["implications_chinese"] = 1.0 if _is_chinese(implications_text) else 0.0

    # Check length
    total_chars = len(digest_text) + len(implications_text)
    if total_chars >= 2000:
        scores["length_adequate"] = 1.0
    elif total_chars >= 1000:
        scores["length_adequate"] = 0.7
    elif total_chars >= 500:
        scores["length_adequate"] = 0.4
    else:
        scores["length_adequate"] = 0.1

    return scores


def _score_strategic_insight(implications_text: str) -> Dict[str, float]:
    """Score strategic implications quality."""
    scores = {}

    if not implications_text:
        return {"implications_exists": 0.0, "strategy_count": 0.0, "forward_looking": 0.0}

    scores["implications_exists"] = 1.0

    # Count strategic recommendations (look for numbered items or bullets)
    lines = implications_text.split('\n')
    strategy_lines = [l for l in lines if re.match(r'^\s*[\d\-\*•]', l.strip())]
    scores["strategy_count"] = min(1.0, len(strategy_lines) / 5.0)

    # Check forward-looking elements
    forward_markers = ["2025", "2026", "2027", "未来",
                       "长期", "短期", "中期",
                       "趋势", "前景", "规划"]
    forward_found = sum(1 for m in forward_markers if m in implications_text)
    scores["forward_looking"] = min(1.0, forward_found / 3.0)

    return scores


def _score_completeness(digest_text: str, profiles: Any,
                        threat_data: Any, implications_text: str) -> Dict[str, float]:
    """Score completeness of all output files."""
    scores = {}
    scores["digest"] = 1.0 if digest_text else 0.0
    scores["profiles"] = 1.0 if profiles else 0.0
    scores["threat_analysis"] = 1.0 if threat_data else 0.0
    scores["implications"] = 1.0 if implications_text else 0.0
    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for KNW-08."""
    digest_text = _load_text("competitive_digest_zh.md")
    profiles = _load_json("competitor_profiles.json")
    threat_data = _load_json("threat_analysis_zh.json")
    implications_text = _load_text("strategic_implications_zh.md")

    dimensions = {}

    # Dimension 1: Extraction Accuracy (weight: 0.25)
    ext_scores = _score_extraction_accuracy(digest_text, profiles)
    dimensions["extraction_accuracy"] = {
        "score": sum(ext_scores.values()) / max(len(ext_scores), 1),
        "weight": 0.25,
        "details": ext_scores
    }

    # Dimension 2: Analysis Depth (weight: 0.25)
    depth_scores = _score_analysis_depth(digest_text, threat_data)
    dimensions["analysis_depth"] = {
        "score": sum(depth_scores.values()) / max(len(depth_scores), 1),
        "weight": 0.25,
        "details": depth_scores
    }

    # Dimension 3: Chinese Quality (weight: 0.20)
    cn_scores = _score_chinese_quality(digest_text, implications_text)
    dimensions["chinese_quality"] = {
        "score": sum(cn_scores.values()) / max(len(cn_scores), 1),
        "weight": 0.20,
        "details": cn_scores
    }

    # Dimension 4: Strategic Insight (weight: 0.15)
    strat_scores = _score_strategic_insight(implications_text)
    dimensions["strategic_insight"] = {
        "score": sum(strat_scores.values()) / max(len(strat_scores), 1),
        "weight": 0.15,
        "details": strat_scores
    }

    # Dimension 5: Completeness (weight: 0.15)
    comp_scores = _score_completeness(digest_text, profiles, threat_data, implications_text)
    dimensions["completeness"] = {
        "score": sum(comp_scores.values()) / max(len(comp_scores), 1),
        "weight": 0.15,
        "details": comp_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"KNW-08 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_digest_in_chinese():
    text = _load_text("competitive_digest_zh.md")
    assert text, "competitive_digest_zh.md not found or empty"
    assert _is_chinese(text), "Digest must be written in Chinese"


def test_all_competitors_covered():
    text = _load_text("competitive_digest_zh.md")
    profiles = _load_json("competitor_profiles.json")
    combined = text + " " + json.dumps(profiles or {}, ensure_ascii=False)
    assert "NovaTech" in combined, "Competitor A (NovaTech) not covered"
    assert "SiliconWave" in combined, "Competitor B (SiliconWave) not covered"
    assert "QuantumCore" in combined, "Competitor C (QuantumCore) not covered"


def test_threat_analysis_exists():
    data = _load_json("threat_analysis_zh.json")
    assert data, "threat_analysis_zh.json not found or empty"


def test_strategic_implications_exist():
    text = _load_text("strategic_implications_zh.md")
    assert text, "strategic_implications_zh.md not found or empty"
    assert _is_chinese(text), "Strategic implications must be in Chinese"
    assert len(text) >= 300, "Strategic implications too short"


def test_competitor_profiles_structured():
    data = _load_json("competitor_profiles.json")
    assert data, "competitor_profiles.json not found or empty"
    if isinstance(data, list):
        profiles = data
    elif isinstance(data, dict):
        profiles = data.get("competitors", data.get("profiles", list(data.values())))
    else:
        profiles = []
    assert len(profiles) >= 3, "Must have profiles for at least 3 competitors"


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
