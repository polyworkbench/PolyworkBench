"""
WildClawBench-style grading for LEG-06: Chinese litigation strategy brief from English-Russian sources.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Key facts that must appear in the outputs
ARBITRATION_SEAT = "Singapore"
APPLICABLE_LAW = "English"  # English law / England and Wales
DISPUTE_AMOUNT = 2350000  # USD 2.3M (actually 2,350,000)
COUNTERPARTY_CLAIMS_FORCE_MAJEURE = True
ICC_CASE_NUMBER = "ICC-ARB/2024/1247"
CONTRACT_NUMBER = "SC-2023-0847"
CONTRACT_VALUE = 4500000


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _is_chinese(text: str) -> bool:
    """Check if text contains significant Chinese characters."""
    if not text:
        return False
    chinese_chars = sum(1 for c in text if '一' <= c <= '鿿')
    return chinese_chars / max(len(text.replace(" ", "")), 1) > 0.15


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


def _score_legal_analysis(brief: str, strategy: Dict) -> Dict[str, float]:
    """Score legal analysis quality (weight: 0.30)."""
    scores = {}

    if not brief and not strategy:
        return {"brief_exists": 0.0, "seat_identified": 0.0, "law_identified": 0.0,
                "amount_identified": 0.0, "force_majeure_analysis": 0.0,
                "defense_strategy": 0.0}

    scores["brief_exists"] = 1.0 if brief else 0.0

    # Check if arbitration seat is correctly identified
    strategy_str = json.dumps(strategy, ensure_ascii=False) if strategy else ""
    combined = brief + " " + strategy_str

    # Singapore as seat
    seat_found = any(term in combined.lower() for term in [
        "singapore", "新加坡"
    ])
    scores["seat_identified"] = 1.0 if seat_found else 0.0

    # English law
    law_found = any(term in combined for term in [
        "English", "英国法", "英格兰", "England", "英国", "英格兰和威尔士"
    ])
    scores["law_identified"] = 1.0 if law_found else 0.0

    # Dispute amount (2.3M or 2,350,000 or 235万)
    amount_found = any(term in combined for term in [
        "2,350,000", "2350000", "2.35", "235万", "230万", "2.3M", "$2.3"
    ])
    scores["amount_identified"] = 1.0 if amount_found else 0.0

    # Force majeure analysis
    fm_found = any(term in combined for term in [
        "不可抗力", "force majeure", "форс-мажор", "免责"
    ])
    scores["force_majeure_analysis"] = 1.0 if fm_found else 0.0

    # Defense strategy present
    defense_terms = ["抗辩", "答辩", "defense", "反驳", "策略", "建议"]
    defense_found = sum(1 for term in defense_terms if term in combined)
    scores["defense_strategy"] = min(1.0, defense_found / 2)

    return scores


def _score_chinese_quality(brief: str, evidence: Any, timeline: Any) -> Dict[str, float]:
    """Score Chinese language quality (weight: 0.25)."""
    scores = {}

    # Brief in Chinese
    scores["brief_in_chinese"] = 1.0 if _is_chinese(brief) else 0.0

    # Evidence list in Chinese
    evidence_str = json.dumps(evidence, ensure_ascii=False) if evidence else ""
    scores["evidence_in_chinese"] = 1.0 if _is_chinese(evidence_str) else 0.0

    # Timeline in Chinese
    timeline_str = json.dumps(timeline, ensure_ascii=False) if timeline else ""
    scores["timeline_in_chinese"] = 1.0 if _is_chinese(timeline_str) else 0.0

    # Legal terminology usage
    legal_terms = ["仲裁", "管辖", "适用法律", "争议", "违约", "损害赔偿",
                   "证据", "时效", "裁决", "申请人", "被申请人", "诉讼"]
    term_count = sum(1 for term in legal_terms if term in brief)
    scores["legal_terminology"] = min(1.0, term_count / 5)

    # Structure and formatting (headings, sections)
    has_headings = bool(re.search(r'[#＃]+\s', brief)) or bool(re.search(r'[一二三四五六七八九十]+[、.]', brief))
    scores["document_structure"] = 1.0 if has_headings else 0.0

    return scores


def _score_strategy_coherence(strategy: Dict) -> Dict[str, float]:
    """Score strategy analysis coherence (weight: 0.20)."""
    scores = {}

    if not strategy:
        return {"strategy_exists": 0.0, "required_fields": 0.0,
                "seat_correct": 0.0, "law_correct": 0.0, "amount_correct": 0.0}

    scores["strategy_exists"] = 1.0

    # Check required fields
    required_fields = ["arbitration_seat", "applicable_law", "dispute_amount",
                       "counterparty_claims", "defense_points"]
    alt_fields = {
        "arbitration_seat": ["seat", "仲裁地", "arbitration_venue"],
        "applicable_law": ["governing_law", "适用法律", "law"],
        "dispute_amount": ["amount", "争议金额", "claim_amount", "total_amount"],
        "counterparty_claims": ["claims", "对方主张", "claimant_claims", "opponent_claims"],
        "defense_points": ["defense", "抗辩要点", "our_defense", "defense_strategy"]
    }

    found_fields = 0
    strategy_str = json.dumps(strategy, ensure_ascii=False).lower()
    for field in required_fields:
        if field in strategy_str:
            found_fields += 1
        else:
            for alt in alt_fields.get(field, []):
                if alt.lower() in strategy_str:
                    found_fields += 1
                    break
    scores["required_fields"] = found_fields / len(required_fields)

    # Verify key facts
    strategy_text = json.dumps(strategy, ensure_ascii=False)

    # Seat = Singapore
    scores["seat_correct"] = 1.0 if any(
        s in strategy_text for s in ["Singapore", "singapore", "新加坡"]
    ) else 0.0

    # Law = English
    scores["law_correct"] = 1.0 if any(
        s in strategy_text for s in ["English", "english", "英国", "英格兰"]
    ) else 0.0

    # Amount ~= 2,350,000 or 2.3M
    scores["amount_correct"] = 1.0 if any(
        s in strategy_text for s in ["2350000", "2,350,000", "2.35", "235"]
    ) else 0.0

    return scores


def _score_evidence_organization(evidence: Any) -> Dict[str, float]:
    """Score evidence list organization (weight: 0.15)."""
    scores = {}

    if not evidence:
        return {"evidence_exists": 0.0, "evidence_count": 0.0,
                "evidence_structure": 0.0, "purpose_included": 0.0}

    scores["evidence_exists"] = 1.0

    # Check if it's a list/array
    if isinstance(evidence, list):
        scores["evidence_count"] = min(1.0, len(evidence) / 5)  # Expect at least 5 items

        # Check structure of evidence items
        structured = 0
        has_purpose = 0
        for item in evidence:
            if isinstance(item, dict):
                structured += 1
                # Check for purpose/description field
                if any(k in str(item.keys()).lower() for k in
                       ["purpose", "目的", "证明", "description", "说明", "relevance"]):
                    has_purpose += 1
        scores["evidence_structure"] = structured / max(len(evidence), 1)
        scores["purpose_included"] = has_purpose / max(len(evidence), 1)
    elif isinstance(evidence, dict):
        items = list(evidence.values()) if evidence else []
        scores["evidence_count"] = min(1.0, len(items) / 5)
        scores["evidence_structure"] = 0.7  # Dict format is acceptable
        blob = json.dumps(evidence, ensure_ascii=False)
        scores["purpose_included"] = 1.0 if any(
            t in blob for t in ["purpose", "目的", "证明", "说明"]
        ) else 0.0
    else:
        scores["evidence_count"] = 0.0
        scores["evidence_structure"] = 0.0
        scores["purpose_included"] = 0.0

    return scores


def _score_timeline_accuracy(timeline: Any) -> Dict[str, float]:
    """Score timeline accuracy (weight: 0.10)."""
    scores = {}

    if not timeline:
        return {"timeline_exists": 0.0, "date_format": 0.0,
                "key_events": 0.0, "chronological": 0.0}

    scores["timeline_exists"] = 1.0

    timeline_str = json.dumps(timeline, ensure_ascii=False)

    # Check for dates
    date_pattern = re.findall(r'20[23][0-9][-/年][0-9]{1,2}[-/月]?[0-9]{0,2}', timeline_str)
    scores["date_format"] = min(1.0, len(date_pattern) / 5)

    # Key events that should appear
    key_events = [
        "2023-03",   # Contract signing
        "2023-09",   # Force majeure notice
        "2024-03",   # Batch 7 non-delivery
        "2024-04",   # Default notice
        "2024-06",   # Filing
    ]
    events_found = sum(1 for event in key_events
                       if event in timeline_str or event.replace("-", "/") in timeline_str
                       or event.replace("-", "年", 1).replace("-", "月") in timeline_str)
    scores["key_events"] = events_found / len(key_events)

    # Check chronological order (basic check)
    if isinstance(timeline, list) and len(timeline) >= 2:
        dates_in_order = True
        prev_date = ""
        for entry in timeline:
            if isinstance(entry, dict):
                date = str(entry.get("date", entry.get("日期", entry.get("time", ""))))
                if date and prev_date and date < prev_date:
                    dates_in_order = False
                    break
                if date:
                    prev_date = date
        scores["chronological"] = 1.0 if dates_in_order else 0.5
    else:
        scores["chronological"] = 0.5  # Can't verify order easily

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for LEG-06."""
    brief = _load_md_file("litigation_brief_zh.md")
    strategy = _load_json_file("strategy_analysis.json") or {}
    evidence = _load_json_file("evidence_list_zh.json")
    timeline = _load_json_file("timeline_zh.json")

    if not brief and not strategy and not evidence and not timeline:
        return {"overall_score": 0.0, "dimensions": {}, "error": "No output files found."}

    dimensions = {}

    # Dimension 1: Legal Analysis (weight: 0.30)
    legal_scores = _score_legal_analysis(brief, strategy)
    dimensions["legal_analysis"] = {
        "score": sum(legal_scores.values()) / max(len(legal_scores), 1),
        "weight": 0.30,
        "details": legal_scores
    }

    # Dimension 2: Chinese Quality (weight: 0.25)
    chinese_scores = _score_chinese_quality(brief, evidence, timeline)
    dimensions["chinese_quality"] = {
        "score": sum(chinese_scores.values()) / max(len(chinese_scores), 1),
        "weight": 0.25,
        "details": chinese_scores
    }

    # Dimension 3: Strategy Coherence (weight: 0.20)
    strategy_scores = _score_strategy_coherence(strategy)
    dimensions["strategy_coherence"] = {
        "score": sum(strategy_scores.values()) / max(len(strategy_scores), 1),
        "weight": 0.20,
        "details": strategy_scores
    }

    # Dimension 4: Evidence Organization (weight: 0.15)
    evidence_scores = _score_evidence_organization(evidence)
    dimensions["evidence_organization"] = {
        "score": sum(evidence_scores.values()) / max(len(evidence_scores), 1),
        "weight": 0.15,
        "details": evidence_scores
    }

    # Dimension 5: Timeline Accuracy (weight: 0.10)
    timeline_scores = _score_timeline_accuracy(timeline)
    dimensions["timeline_accuracy"] = {
        "score": sum(timeline_scores.values()) / max(len(timeline_scores), 1),
        "weight": 0.10,
        "details": timeline_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"LEG-06 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
        for k, v in dim.get("details", {}).items():
            print(f"    {k}: {v:.2f}")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_arbitration_seat_identified():
    """Verify the agent correctly identifies Singapore as the arbitration seat."""
    strategy = _load_json_file("strategy_analysis.json") or {}
    brief = _load_md_file("litigation_brief_zh.md")
    combined = brief + json.dumps(strategy, ensure_ascii=False)
    assert any(s in combined for s in ["Singapore", "新加坡"]), \
        "Arbitration seat (Singapore) not identified"


def test_applicable_law_identified():
    """Verify the agent correctly identifies English law as applicable."""
    strategy = _load_json_file("strategy_analysis.json") or {}
    brief = _load_md_file("litigation_brief_zh.md")
    combined = brief + json.dumps(strategy, ensure_ascii=False)
    assert any(s in combined for s in ["English", "英国法", "英格兰", "英国"]), \
        "Applicable law (English law) not identified"


def test_dispute_amount():
    """Verify the agent correctly identifies the dispute amount as ~$2.3M."""
    strategy = _load_json_file("strategy_analysis.json") or {}
    brief = _load_md_file("litigation_brief_zh.md")
    combined = brief + json.dumps(strategy, ensure_ascii=False)
    assert any(s in combined for s in [
        "2,350,000", "2350000", "2.35", "235万", "230万", "2.3"
    ]), "Dispute amount ($2.35M) not identified"


def test_force_majeure_addressed():
    """Verify the agent addresses the force majeure claim."""
    brief = _load_md_file("litigation_brief_zh.md")
    assert any(s in brief for s in ["不可抗力", "force majeure"]), \
        "Force majeure defense not addressed in brief"


def test_brief_in_chinese():
    """Verify the litigation brief is written in Chinese."""
    brief = _load_md_file("litigation_brief_zh.md")
    assert _is_chinese(brief), "Litigation brief must be in Chinese"


def test_timeline_exists():
    """Verify timeline file exists and has content."""
    timeline = _load_json_file("timeline_zh.json")
    assert timeline is not None, "timeline_zh.json not found or invalid"
    if isinstance(timeline, list):
        assert len(timeline) >= 3, "Timeline should have at least 3 events"


def test_evidence_list_exists():
    """Verify evidence list file exists and has content."""
    evidence = _load_json_file("evidence_list_zh.json")
    assert evidence is not None, "evidence_list_zh.json not found or invalid"


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
