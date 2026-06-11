"""
WildClawBench-style grading for MFG-09: Korean lean manufacturing analysis.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


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


def _is_korean(text: str) -> bool:
    """Check if text contains significant Korean characters."""
    if not text:
        return False
    korean = sum(1 for c in text if '가' <= c <= '힣' or 'ㄱ' <= c <= 'ㅎ' or 'ㅏ' <= c <= 'ㅣ')
    return korean / max(len(text.replace(" ", "").replace("\n", "")), 1) > 0.15


def _score_tps_application() -> Dict[str, float]:
    """Score TPS principles application (weight: 0.25)."""
    scores = {}
    report_path = _find_file("lean_analysis_ko.md")

    if not report_path.exists():
        return {"report_exists": 0.0, "jit_discussed": 0.0,
                "jidoka_discussed": 0.0, "waste_analysis": 0.0, "kaizen_approach": 0.0}

    content = report_path.read_text(encoding="utf-8-sig")
    content_combined = content.lower()
    scores["report_exists"] = 1.0

    # Check JIT concepts discussed (Korean terms)
    jit_terms = ["적시생산", "저스트인타임", "jit", "just-in-time", "택트타임",
                 "takt", "풀 시스템", "간판", "かんばん", "pull"]
    scores["jit_discussed"] = 1.0 if sum(1 for t in jit_terms if t in content_combined) >= 2 else 0.0

    # Check Jidoka concepts
    jidoka_terms = ["자동화", "지도카", "자働화", "이상감지", "라인스톱",
                    "포카요케", "poka-yoke", "andon", "안돈"]
    scores["jidoka_discussed"] = 1.0 if sum(1 for t in jidoka_terms if t in content_combined) >= 1 else 0.0

    # Check 7 wastes analysis
    waste_terms_ko = ["과잉생산", "대기", "운반", "과잉가공", "재고", "동작", "불량",
                      "낭비", "무다", "muda", "7대 낭비"]
    waste_found = sum(1 for t in waste_terms_ko if t in content_combined)
    scores["waste_analysis"] = min(1.0, waste_found / 4)

    # Check kaizen/improvement approach
    kaizen_terms = ["카이젠", "개선", "kaizen", "pdca", "지속적 개선",
                    "현상분석", "문제점", "대책"]
    scores["kaizen_approach"] = 1.0 if sum(1 for t in kaizen_terms if t in content_combined) >= 2 else 0.0

    return scores


def _score_metrics_analysis() -> Dict[str, float]:
    """Score metrics analysis quality (weight: 0.25)."""
    scores = {}
    comparison = _load_json("metrics_comparison.json")
    report_path = _find_file("lean_analysis_ko.md")

    if not comparison and not (report_path.exists()):
        return {"metrics_exists": 0.0, "oee_analyzed": 0.0,
                "bottleneck_identified": 0.0, "targets_defined": 0.0}

    if comparison:
        scores["metrics_exists"] = 1.0
        blob = json.dumps(comparison, ensure_ascii=False).lower()

        # Check OEE analysis
        oee_terms = ["oee", "설비종합효율", "가동률", "availability", "performance", "quality"]
        scores["oee_analyzed"] = min(1.0, sum(1 for t in oee_terms if t in blob) / 3)

        # Check bottleneck identification (welding and painting are bottlenecks)
        bottleneck_terms = ["bottleneck", "병목", "welding", "painting", "용접", "도장",
                           "焊接", "喷涂"]
        scores["bottleneck_identified"] = 1.0 if sum(1 for t in bottleneck_terms if t in blob) >= 1 else 0.0

        # Check current vs target values
        has_comparison = any(k in blob for k in ["current", "target", "현재", "목표",
                                                  "benchmark", "벤치마크", "before", "after"])
        scores["targets_defined"] = 1.0 if has_comparison else 0.0
    else:
        scores["metrics_exists"] = 0.0
        # Fallback: check report
        if report_path.exists():
            content = report_path.read_text(encoding="utf-8-sig").lower()
            scores["oee_analyzed"] = 1.0 if "oee" in content else 0.0
            scores["bottleneck_identified"] = 1.0 if any(k in content for k in ["병목", "bottleneck"]) else 0.0
            scores["targets_defined"] = 0.0
        else:
            scores["oee_analyzed"] = 0.0
            scores["bottleneck_identified"] = 0.0
            scores["targets_defined"] = 0.0

    return scores


def _score_korean_quality() -> Dict[str, float]:
    """Score Korean language quality (weight: 0.20)."""
    scores = {}

    report_path = _find_file("lean_analysis_ko.md")
    plan = _load_json("improvement_plan_ko.json")

    # Check report is in Korean
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8-sig")
        scores["report_is_korean"] = 1.0 if _is_korean(content) else 0.0

        # Check for Korean manufacturing terminology
        ko_mfg_terms = ["생산라인", "공정", "개선", "효율", "품질", "설비",
                        "작업자", "생산성", "리드타임", "재공품"]
        terms_found = sum(1 for t in ko_mfg_terms if t in content)
        scores["korean_terminology"] = min(1.0, terms_found / 5)
    else:
        scores["report_is_korean"] = 0.0
        scores["korean_terminology"] = 0.0

    # Check improvement plan has Korean content
    if plan:
        plan_blob = json.dumps(plan, ensure_ascii=False)
        scores["plan_korean_content"] = 1.0 if _is_korean(plan_blob) else 0.0
    else:
        scores["plan_korean_content"] = 0.0

    return scores


def _score_improvement_feasibility() -> Dict[str, float]:
    """Score improvement plan feasibility (weight: 0.15)."""
    scores = {}
    plan = _load_json("improvement_plan_ko.json")

    if not plan:
        return {"plan_exists": 0.0, "time_phased": 0.0,
                "actionable_items": 0.0, "cost_estimates": 0.0}

    scores["plan_exists"] = 1.0
    blob = json.dumps(plan, ensure_ascii=False).lower()

    # Check time-phased structure (short/medium/long term)
    time_terms = ["단기", "중기", "장기", "short", "medium", "long",
                  "1-3", "3-6", "6-12", "개월", "month"]
    scores["time_phased"] = 1.0 if sum(1 for t in time_terms if t in blob) >= 2 else 0.0

    # Check for actionable items
    if isinstance(plan, dict):
        # Count total improvement items
        all_items = []
        for key, value in plan.items():
            if isinstance(value, list):
                all_items.extend(value)
            elif isinstance(value, dict):
                for sub_value in value.values():
                    if isinstance(sub_value, list):
                        all_items.extend(sub_value)
        scores["actionable_items"] = min(1.0, len(all_items) / 5) if all_items else 0.5
    elif isinstance(plan, list):
        scores["actionable_items"] = min(1.0, len(plan) / 5)
    else:
        scores["actionable_items"] = 0.0

    # Check for cost/investment references
    cost_terms = ["비용", "투자", "cost", "investment", "원", "만원", "억"]
    scores["cost_estimates"] = 1.0 if any(t in blob for t in cost_terms) else 0.0

    return scores


def _score_vsm_accuracy() -> Dict[str, float]:
    """Score value stream map accuracy (weight: 0.15)."""
    scores = {}
    vsm = _load_json("value_stream_map.json")

    if not vsm:
        return {"vsm_exists": 0.0, "process_steps": 0.0,
                "timing_data": 0.0, "wip_data": 0.0, "lead_time": 0.0}

    scores["vsm_exists"] = 1.0
    blob = json.dumps(vsm, ensure_ascii=False).lower()

    # Check process steps are included
    process_terms = ["stamping", "welding", "painting", "assembly", "inspection",
                     "冲压", "焊接", "喷涂", "装配", "检验",
                     "프레스", "용접", "도장", "조립", "검사"]
    steps_found = sum(1 for t in process_terms if t in blob)
    scores["process_steps"] = min(1.0, steps_found / 4)

    # Check timing data
    timing_terms = ["cycle_time", "cycle time", "사이클타임", "takt", "택트",
                    "wait", "대기", "lead_time", "리드타임"]
    scores["timing_data"] = min(1.0, sum(1 for t in timing_terms if t in blob) / 2)

    # Check WIP data
    wip_terms = ["wip", "재공", "在制品", "inventory", "재고", "buffer"]
    scores["wip_data"] = 1.0 if any(t in blob for t in wip_terms) else 0.0

    # Check lead time calculation
    lead_terms = ["lead_time", "lead time", "리드타임", "total_time", "value_add",
                  "가치부가", "value added", "부가가치"]
    scores["lead_time"] = 1.0 if sum(1 for t in lead_terms if t in blob) >= 1 else 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for MFG-09."""
    dimensions = {}

    # Dimension 1: TPS Application (weight: 0.25)
    tps_scores = _score_tps_application()
    dimensions["tps_application"] = {
        "score": sum(tps_scores.values()) / max(len(tps_scores), 1),
        "weight": 0.25,
        "details": tps_scores
    }

    # Dimension 2: Metrics Analysis (weight: 0.25)
    metrics_scores = _score_metrics_analysis()
    dimensions["metrics_analysis"] = {
        "score": sum(metrics_scores.values()) / max(len(metrics_scores), 1),
        "weight": 0.25,
        "details": metrics_scores
    }

    # Dimension 3: Korean Quality (weight: 0.20)
    korean_scores = _score_korean_quality()
    dimensions["korean_quality"] = {
        "score": sum(korean_scores.values()) / max(len(korean_scores), 1),
        "weight": 0.20,
        "details": korean_scores
    }

    # Dimension 4: Improvement Feasibility (weight: 0.15)
    feasibility_scores = _score_improvement_feasibility()
    dimensions["improvement_feasibility"] = {
        "score": sum(feasibility_scores.values()) / max(len(feasibility_scores), 1),
        "weight": 0.15,
        "details": feasibility_scores
    }

    # Dimension 5: VSM Accuracy (weight: 0.15)
    vsm_scores = _score_vsm_accuracy()
    dimensions["vsm_accuracy"] = {
        "score": sum(vsm_scores.values()) / max(len(vsm_scores), 1),
        "weight": 0.15,
        "details": vsm_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"MFG-09 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_report_exists_and_korean():
    report_path = _find_file("lean_analysis_ko.md")
    assert report_path.exists(), "lean_analysis_ko.md must exist"
    content = report_path.read_text(encoding="utf-8-sig")
    assert _is_korean(content), "Report must be primarily in Korean"


def test_tps_principles_applied():
    result = grade()
    tps = result["dimensions"].get("tps_application", {})
    details = tps.get("details", {})
    assert details.get("waste_analysis", 0) >= 0.5, (
        "7 wastes analysis should be present"
    )


def test_vsm_exists():
    vsm = _load_json("value_stream_map.json")
    assert vsm is not None, "value_stream_map.json must exist and be valid JSON"


def test_improvement_plan_exists():
    plan = _load_json("improvement_plan_ko.json")
    assert plan is not None, "improvement_plan_ko.json must exist and be valid JSON"


def test_metrics_comparison_exists():
    metrics = _load_json("metrics_comparison.json")
    assert metrics is not None, "metrics_comparison.json must exist and be valid JSON"


def test_bottleneck_identified():
    result = grade()
    metrics = result["dimensions"].get("metrics_analysis", {})
    details = metrics.get("details", {})
    assert details.get("bottleneck_identified", 0) > 0, (
        "Bottleneck processes (welding/painting) should be identified"
    )


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["lean_analysis_ko.md", "metrics_comparison.json",
                          "improvement_plan_ko.json", "value_stream_map.json"]
    # answer.json check
    answer_candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    answer_exists = any(p.exists() for p in answer_candidates)
    assert answer_exists, "Required output file missing: answer.json"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify lean analysis report is in Korean (Hangul), not English fallback."""
    report_path = _find_file("lean_analysis_ko.md")
    if not report_path.exists():
        return
    content = report_path.read_text(encoding="utf-8-sig")
    hangul_chars = sum(1 for c in content if '가' <= c <= '힣')
    total_chars = len(content.replace(" ", "").replace("\n", ""))
    ratio = hangul_chars / max(total_chars, 1)
    assert ratio > 0.15, f"Korean report Hangul ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    report_path = _find_file("lean_analysis_ko.md")
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8-sig")
        assert len(content) > 500, f"Lean analysis too short ({len(content)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Korean report isn't in English."""
    report_path = _find_file("lean_analysis_ko.md")
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8-sig")
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Report appears to be mostly English ({english_ratio:.0%})"


def test_lean_metrics_present():
    """Verify lean metrics comparison has quantitative data."""
    comparison = _load_json("metrics_comparison.json")
    if not comparison:
        return
    blob = json.dumps(comparison, ensure_ascii=False).lower()
    # Should have OEE or similar metric
    assert any(t in blob for t in ["oee", "설비종합효율", "가동률"]), \
        "Metrics comparison should include OEE or equivalent"
    # Should have numeric values
    numbers = re.findall(r'\d+\.?\d*', blob)
    assert len(numbers) >= 5, f"Only {len(numbers)} numeric values in metrics, expected quantitative data"


def test_improvement_plan_korean():
    """Verify improvement plan is in Korean."""
    plan = _load_json("improvement_plan_ko.json")
    if not plan:
        return
    plan_blob = json.dumps(plan, ensure_ascii=False)
    assert _is_korean(plan_blob), "Improvement plan should contain Korean text"
