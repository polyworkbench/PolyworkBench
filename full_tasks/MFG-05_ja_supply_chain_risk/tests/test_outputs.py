"""WildClawBench-style grading for MFG-05_ja_supply_chain_risk."""
import json
import os
import re
from pathlib import Path
from typing import Any, Dict

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


def _find_file(name: str) -> Path:
    """Search for a file in common output locations."""
    candidates = [
        OUTPUT_DIR / "output" / name,
        OUTPUT_DIR / name,
        TASK_DIR / "output" / name,
        TASK_DIR / name,
    ]
    for c in candidates:
        if c.exists():
            return c
    return OUTPUT_DIR / "output" / name


def _load_answer() -> dict:
    """Load answer.json with fallback paths."""
    candidates = [
        OUTPUT_DIR / "answer.json",
        OUTPUT_DIR / "output" / "answer.json",
        TASK_DIR / "answer.json",
    ]
    for c in candidates:
        if c.exists():
            return json.loads(c.read_text(encoding="utf-8"))
    return {}


def _score_risk_identification(data: dict) -> Dict[str, Any]:
    """Score risk identification quality (weight: 0.25)."""
    score = 0.0
    details = []

    risk_file = _find_file("risk_register_ja.json")
    if not risk_file.exists():
        return {"score": 0.0, "details": ["risk_register_ja.json not found"]}

    try:
        risk_data = json.loads(risk_file.read_text(encoding="utf-8"))
        content_str = json.dumps(risk_data, ensure_ascii=False)

        # Check for risk categories from framework
        risk_categories = {
            "supply_disruption": any(kw in content_str for kw in ["供給途絶", "供給中断", "disruption", "途絶"]),
            "quality": any(kw in content_str for kw in ["品質リスク", "品質", "quality", "不良"]),
            "logistics": any(kw in content_str for kw in ["物流", "logistics", "納期", "配送"]),
            "financial": any(kw in content_str for kw in ["財務", "financial", "倒産", "為替"]),
            "geopolitical": any(kw in content_str for kw in ["地政学", "geopolitical", "政治", "貿易"]),
        }
        found_cats = sum(risk_categories.values())
        score += (found_cats / len(risk_categories)) * 0.4
        details.append(f"Risk categories: {found_cats}/{len(risk_categories)}")

        # Check for likelihood and impact scoring
        has_likelihood = any(kw in content_str for kw in ["可能性", "likelihood", "発生確率"])
        has_impact = any(kw in content_str for kw in ["影響度", "impact", "影響"])
        has_score = any(kw in content_str for kw in ["スコア", "score", "リスク値", "評点"])
        scoring_elements = sum([has_likelihood, has_impact, has_score])
        score += (scoring_elements / 3) * 0.3
        details.append(f"Scoring elements: {scoring_elements}/3")

        # Check for single source identification
        if any(kw in content_str for kw in ["単一", "single source", "一社依存", "集中リスク"]):
            score += 0.15
            details.append("Single source risks identified")

        # Check answer.json
        if "critical_risks" in data and isinstance(data["critical_risks"], int):
            if data["critical_risks"] > 0:
                score += 0.15
                details.append(f"Critical risks identified: {data['critical_risks']}")

    except json.JSONDecodeError:
        details.append("risk_register_ja.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def _score_supplier_scoring(data: dict) -> Dict[str, Any]:
    """Score supplier scorecard quality (weight: 0.25)."""
    score = 0.0
    details = []

    scorecard_file = _find_file("supplier_scorecard.json")
    if not scorecard_file.exists():
        return {"score": 0.0, "details": ["supplier_scorecard.json not found"]}

    try:
        scorecard_data = json.loads(scorecard_file.read_text(encoding="utf-8"))
        content_str = json.dumps(scorecard_data, ensure_ascii=False)

        # Check for 5-axis evaluation
        dimensions = {
            "quality": any(kw in content_str for kw in ["品質", "quality", "Quality"]),
            "delivery": any(kw in content_str for kw in ["納期", "delivery", "Delivery", "配送"]),
            "cost": any(kw in content_str for kw in ["コスト", "cost", "Cost", "価格"]),
            "flexibility": any(kw in content_str for kw in ["柔軟性", "flexibility", "Flexibility", "対応力"]),
            "financial": any(kw in content_str for kw in ["財務", "financial", "Financial", "安定性"]),
        }
        found_dims = sum(dimensions.values())
        score += (found_dims / len(dimensions)) * 0.4
        details.append(f"Scorecard dimensions: {found_dims}/{len(dimensions)}")

        # Check for all three countries' suppliers
        has_china = any(kw in content_str for kw in ["CN", "中国", "China", "SUP-CN"])
        has_korea = any(kw in content_str for kw in ["KR", "韓国", "Korea", "SUP-KR"])
        has_vietnam = any(kw in content_str for kw in ["VN", "ベトナム", "Vietnam", "SUP-VN"])
        countries = sum([has_china, has_korea, has_vietnam])
        score += (countries / 3) * 0.3
        details.append(f"Countries covered: {countries}/3")

        # Check total suppliers count
        if "total_suppliers" in data:
            total = data["total_suppliers"]
            # 7 China + 5 Korea + 6 Vietnam = 18
            if total == 18:
                score += 0.15
                details.append(f"Correct supplier count: {total}")
            elif isinstance(total, int) and 15 <= total <= 20:
                score += 0.1
                details.append(f"Approximate supplier count: {total}")

        # Check for scoring values (numeric scores present)
        numbers = re.findall(r'\d+\.?\d*', content_str)
        if len(numbers) > 20:
            score += 0.15
            details.append("Quantitative scoring present")

    except json.JSONDecodeError:
        details.append("supplier_scorecard.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def _score_japanese_report(data: dict) -> Dict[str, Any]:
    """Score Japanese report quality (weight: 0.20)."""
    score = 0.0
    details = []

    report_file = _find_file("assessment_report_ja.md")
    if not report_file.exists():
        return {"score": 0.0, "details": ["assessment_report_ja.md not found"]}

    content = report_file.read_text(encoding="utf-8")

    # Check for Japanese characters (kanji + hiragana + katakana)
    jp_chars = re.findall(r'[ぁ-んァ-ヶ一-龥]', content)
    if len(jp_chars) > 200:
        score += 0.3
        details.append(f"Rich Japanese content: {len(jp_chars)} chars")
    elif len(jp_chars) > 50:
        score += 0.15
        details.append(f"Some Japanese content: {len(jp_chars)} chars")

    # Check for Japanese supply chain terminology
    jp_terms = ["サプライチェーン", "リスク", "サプライヤー", "評価", "地政学",
                "調達", "供給", "品質", "納期", "対策", "軽減"]
    found_terms = [t for t in jp_terms if t in content]
    term_score = len(found_terms) / len(jp_terms)
    score += term_score * 0.35
    details.append(f"Japanese SC terms: {len(found_terms)}/{len(jp_terms)}")

    # Check report structure
    sections = {
        "summary": any(kw in content for kw in ["サマリー", "概要", "まとめ", "総括"]),
        "country_analysis": any(kw in content for kw in ["国別", "中国", "韓国", "ベトナム"]),
        "comparison": any(kw in content for kw in ["比較", "ランキング", "スコア"]),
        "geopolitical": any(kw in content for kw in ["地政学", "政治", "貿易摩擦"]),
    }
    found_sections = sum(sections.values())
    score += (found_sections / len(sections)) * 0.2
    details.append(f"Report sections: {found_sections}/{len(sections)}")

    # Check document length
    if len(content) > 2000:
        score += 0.15
        details.append(f"Report length: {len(content)} chars")

    return {"score": min(score, 1.0), "details": details}


def _score_mitigation_quality(data: dict) -> Dict[str, Any]:
    """Score mitigation plan quality (weight: 0.15)."""
    score = 0.0
    details = []

    mitigation_file = _find_file("mitigation_plan_ja.md")
    if not mitigation_file.exists():
        return {"score": 0.0, "details": ["mitigation_plan_ja.md not found"]}

    content = mitigation_file.read_text(encoding="utf-8")

    # Check for Japanese content
    jp_chars = re.findall(r'[ぁ-んァ-ヶ一-龥]', content)
    if len(jp_chars) > 100:
        score += 0.2
        details.append(f"Japanese mitigation content: {len(jp_chars)} chars")

    # Check for mitigation strategies
    strategies = {
        "dual_source": any(kw in content for kw in ["二社購買", "複数社", "代替", "マルチソース", "セカンドソース"]),
        "safety_stock": any(kw in content for kw in ["安全在庫", "バッファ", "在庫"]),
        "monitoring": any(kw in content for kw in ["モニタリング", "監視", "定期"]),
        "diversification": any(kw in content for kw in ["分散", "多角化", "diversif"]),
        "contracts": any(kw in content for kw in ["契約", "合意", "保証"]),
    }
    found_strategies = sum(strategies.values())
    score += (found_strategies / len(strategies)) * 0.5
    details.append(f"Mitigation strategies: {found_strategies}/{len(strategies)}")

    # Check for actionable recommendations
    if "recommended_actions" in data and isinstance(data["recommended_actions"], int):
        if data["recommended_actions"] >= 5:
            score += 0.15
            details.append(f"Recommended actions: {data['recommended_actions']}")

    # Check document substance
    if len(content) > 1000:
        score += 0.15
        details.append(f"Mitigation plan length: {len(content)} chars")

    return {"score": min(score, 1.0), "details": details}


def _score_framework_compliance(data: dict) -> Dict[str, Any]:
    """Score ISO 31000 framework compliance (weight: 0.15)."""
    score = 0.0
    details = []

    # Check risk register for framework elements
    risk_file = _find_file("risk_register_ja.json")
    if risk_file.exists():
        try:
            risk_data = json.loads(risk_file.read_text(encoding="utf-8"))
            content_str = json.dumps(risk_data, ensure_ascii=False)

            # Check for 5-point scales
            has_scale = any(kw in content_str for kw in ["1", "2", "3", "4", "5"])
            if has_scale:
                score += 0.2
                details.append("Risk scoring scale used")

            # Check for risk matrix thresholds
            thresholds = {
                "low": any(kw in content_str.lower() for kw in ["low", "低", "低リスク"]),
                "medium": any(kw in content_str.lower() for kw in ["medium", "中", "中リスク"]),
                "high": any(kw in content_str.lower() for kw in ["high", "高", "高リスク"]),
                "critical": any(kw in content_str.lower() for kw in ["critical", "重大", "クリティカル"]),
            }
            found_thresholds = sum(thresholds.values())
            score += (found_thresholds / len(thresholds)) * 0.3
            details.append(f"Risk thresholds: {found_thresholds}/{len(thresholds)}")

        except json.JSONDecodeError:
            details.append("risk_register_ja.json invalid JSON")

    # Check for ISO 31000 reference in report
    report_file = _find_file("assessment_report_ja.md")
    if report_file.exists():
        content = report_file.read_text(encoding="utf-8")
        if "31000" in content or "ISO" in content:
            score += 0.2
            details.append("ISO 31000 referenced in report")

    # Check answer.json metrics
    if "avg_risk_score" in data:
        avg_score = data["avg_risk_score"]
        if isinstance(avg_score, (int, float)) and 1 <= avg_score <= 25:
            score += 0.15
            details.append(f"Average risk score: {avg_score:.2f}")

    if "highest_risk_country" in data and data["highest_risk_country"]:
        score += 0.15
        details.append(f"Highest risk country: {data['highest_risk_country']}")

    return {"score": min(score, 1.0), "details": details}


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading. Returns {overall_score, dimensions}."""
    data = _load_answer()

    dimensions = {
        "risk_identification": _score_risk_identification(data),
        "supplier_scoring": _score_supplier_scoring(data),
        "japanese_report": _score_japanese_report(data),
        "mitigation_quality": _score_mitigation_quality(data),
        "framework_compliance": _score_framework_compliance(data),
    }

    weights = {
        "risk_identification": 0.25,
        "supplier_scoring": 0.25,
        "japanese_report": 0.20,
        "mitigation_quality": 0.15,
        "framework_compliance": 0.15,
    }

    overall = sum(dimensions[k]["score"] * weights[k] for k in dimensions)

    return {
        "overall_score": round(overall, 4),
        "dimensions": dimensions,
    }


def test_grade_overall():
    """Pytest entry point."""
    result = grade()
    assert result["overall_score"] >= 0.15, f"Score too low: {result['overall_score']}"
    print(f"\n{'='*60}")
    print(f"OVERALL SCORE: {result['overall_score']:.4f}")
    print(f"{'='*60}")
    for dim, info in result["dimensions"].items():
        print(f"  {dim}: {info['score']:.4f}")
        for detail in info["details"]:
            print(f"    - {detail}")
    assert result["overall_score"] >= 0.2, f"Score too low: {result['overall_score']}"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["risk_register_ja.json", "supplier_scorecard.json",
                          "assessment_report_ja.md", "mitigation_plan_ja.md"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify assessment report is in Japanese, not English fallback."""
    report_file = _find_file("assessment_report_ja.md")
    if not report_file.exists():
        return
    content = report_file.read_text(encoding="utf-8")
    jp_chars = sum(1 for c in content if 'ぁ' <= c <= 'ヿ' or '一' <= c <= '鿿')
    total_chars = len(content.replace(" ", "").replace("\n", ""))
    ratio = jp_chars / max(total_chars, 1)
    assert ratio > 0.2, f"Japanese report char ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    blob = json.dumps(data, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Japanese report isn't in English."""
    report_file = _find_file("assessment_report_ja.md")
    if not report_file.exists():
        return
    text = report_file.read_text(encoding="utf-8")
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Report appears to be mostly English ({english_ratio:.0%})"


def test_risk_register_entries():
    """Verify risk register has sufficient entries."""
    risk_file = _find_file("risk_register_ja.json")
    if not risk_file.exists():
        return
    try:
        risk_data = json.loads(risk_file.read_text(encoding="utf-8"))
    except Exception:
        return
    if isinstance(risk_data, list):
        count = len(risk_data)
    elif isinstance(risk_data, dict):
        risks = risk_data.get("risks", risk_data.get("register", risk_data))
        count = len(risks) if isinstance(risks, list) else len(risks) if isinstance(risks, dict) else 0
    else:
        count = 0
    assert count >= 5, f"Only {count} risk entries, expected at least 5"
