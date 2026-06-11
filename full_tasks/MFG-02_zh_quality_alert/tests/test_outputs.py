"""WildClawBench-style grading for MFG-02_zh_quality_alert."""
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


def _score_defect_detection(data: dict) -> Dict[str, Any]:
    """Score defect detection accuracy (weight: 0.30)."""
    score = 0.0
    details = []

    # Check answer.json
    if "total_defects" in data:
        total = data["total_defects"]
        # From QC data: sum of all defects = ~76
        if isinstance(total, (int, float)) and 60 <= total <= 90:
            score += 0.3
            details.append(f"Total defects {total} in expected range")
        else:
            details.append(f"Total defects {total} outside expected range (60-90)")

    if "critical_defects" in data:
        critical = data["critical_defects"]
        # Critical (Nghiêm trọng) defects: approximately 7-8 entries
        if isinstance(critical, (int, float)) and 5 <= critical <= 12:
            score += 0.2
            details.append(f"Critical defects {critical} in expected range")

    # Check defect_classification.json
    defect_file = _find_file("defect_classification.json")
    if defect_file.exists():
        try:
            defect_data = json.loads(defect_file.read_text(encoding="utf-8"))
            # Check for classification structure
            if isinstance(defect_data, (list, dict)):
                score += 0.2
                details.append("Defect classification file properly structured")

                # Check for severity levels
                content_str = json.dumps(defect_data)
                has_critical = any(kw in content_str for kw in ["Critical", "critical", "严重", "nghiêm trọng"])
                has_major = any(kw in content_str for kw in ["Major", "major", "主要", "chính"])
                has_minor = any(kw in content_str for kw in ["Minor", "minor", "次要", "phụ"])
                severity_score = sum([has_critical, has_major, has_minor]) / 3
                score += severity_score * 0.3
                details.append(f"Severity levels: {sum([has_critical, has_major, has_minor])}/3")
        except json.JSONDecodeError:
            details.append("defect_classification.json invalid JSON")
    else:
        details.append("defect_classification.json not found")

    return {"score": min(score, 1.0), "details": details}


def _score_root_cause(data: dict) -> Dict[str, Any]:
    """Score root cause analysis (weight: 0.25)."""
    score = 0.0
    details = []

    rca_file = _find_file("root_cause_analysis.json")
    if not rca_file.exists():
        return {"score": 0.0, "details": ["root_cause_analysis.json not found"]}

    try:
        rca_data = json.loads(rca_file.read_text(encoding="utf-8"))
        content_str = json.dumps(rca_data, ensure_ascii=False)

        # Check for 5M1E methodology
        categories_5m1e = {
            "man": any(kw in content_str for kw in ["Man", "人", "人员", "operator", "người"]),
            "machine": any(kw in content_str for kw in ["Machine", "机", "机器", "设备", "máy"]),
            "material": any(kw in content_str for kw in ["Material", "料", "物料", "材料", "vật liệu"]),
            "method": any(kw in content_str for kw in ["Method", "法", "方法", "工艺", "phương pháp"]),
            "measurement": any(kw in content_str for kw in ["Measurement", "测", "测量", "检测", "đo"]),
            "environment": any(kw in content_str for kw in ["Environment", "环", "环境", "môi trường"]),
        }
        found_categories = sum(categories_5m1e.values())
        score += (found_categories / 6) * 0.5
        details.append(f"5M1E categories: {found_categories}/6")

        # Check for specific root causes related to the data
        key_causes = [
            any(kw in content_str for kw in ["温度", "temperature", "reflow", "nhiệt"]),
            any(kw in content_str for kw in ["吸嘴", "nozzle", "đầu hút"]),
            any(kw in content_str for kw in ["飞达", "feeder", "送料"]),
        ]
        cause_score = sum(key_causes) / len(key_causes)
        score += cause_score * 0.3
        details.append(f"Key root causes identified: {sum(key_causes)}/3")

        # Check answer.json top_root_cause
        if "top_root_cause" in data and data["top_root_cause"]:
            score += 0.2
            details.append(f"Top root cause identified: {data['top_root_cause'][:50]}")

    except json.JSONDecodeError:
        details.append("root_cause_analysis.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def _score_chinese_alert(data: dict) -> Dict[str, Any]:
    """Score Chinese quality alert document (weight: 0.20)."""
    score = 0.0
    details = []

    alert_file = _find_file("quality_alert_zh.md")
    if not alert_file.exists():
        return {"score": 0.0, "details": ["quality_alert_zh.md not found"]}

    content = alert_file.read_text(encoding="utf-8")

    # Check for Chinese characters
    chinese_chars = re.findall(r'[一-鿿]', content)
    if len(chinese_chars) > 100:
        score += 0.3
        details.append(f"Rich Chinese content: {len(chinese_chars)} chars")
    elif len(chinese_chars) > 30:
        score += 0.15
        details.append(f"Some Chinese content: {len(chinese_chars)} chars")

    # Check for quality alert sections
    sections = {
        "alert_level": any(kw in content for kw in ["警报级别", "等级", "紧急程度"]),
        "scope": any(kw in content for kw in ["影响范围", "涉及", "影响产品"]),
        "description": any(kw in content for kw in ["缺陷描述", "问题描述", "不良描述"]),
        "containment": any(kw in content for kw in ["围堵", "遏制", "紧急措施", "临时措施"]),
        "root_cause": any(kw in content for kw in ["根本原因", "原因分析", "根因"]),
        "corrective": any(kw in content for kw in ["纠正措施", "改善措施", "整改"]),
    }
    found_sections = sum(sections.values())
    score += (found_sections / len(sections)) * 0.5
    details.append(f"Alert sections: {found_sections}/{len(sections)}")

    # Check document length
    if len(content) > 800:
        score += 0.2
        details.append(f"Document length adequate: {len(content)} chars")

    return {"score": min(score, 1.0), "details": details}


def _score_classification(data: dict) -> Dict[str, Any]:
    """Score defect classification quality (weight: 0.15)."""
    score = 0.0
    details = []

    defect_file = _find_file("defect_classification.json")
    if not defect_file.exists():
        return {"score": 0.0, "details": ["defect_classification.json not found"]}

    try:
        defect_data = json.loads(defect_file.read_text(encoding="utf-8"))
        content_str = json.dumps(defect_data, ensure_ascii=False)

        # Check for defect type categories from the QC data
        defect_types = {
            "solder": any(kw in content_str for kw in ["焊接", "hàn", "solder", "虚焊", "冷焊"]),
            "misalignment": any(kw in content_str for kw in ["偏移", "lệch", "misalign", "位移"]),
            "missing": any(kw in content_str for kw in ["缺件", "thiếu", "missing", "漏件"]),
            "bridge": any(kw in content_str for kw in ["桥接", "cầu", "bridge", "连锡"]),
            "cosmetic": any(kw in content_str for kw in ["外观", "ngoại quan", "cosmetic", "表面"]),
        }
        found_types = sum(defect_types.values())
        score += (found_types / len(defect_types)) * 0.5
        details.append(f"Defect types classified: {found_types}/{len(defect_types)}")

        # Check for batch information
        if "affected_batches" in data and isinstance(data["affected_batches"], list):
            if len(data["affected_batches"]) > 0:
                score += 0.3
                details.append(f"Affected batches listed: {len(data['affected_batches'])}")

        # Check for frequency/count data
        if any(kw in content_str for kw in ["频率", "次数", "count", "frequency", "数量"]):
            score += 0.2
            details.append("Frequency data included")

    except json.JSONDecodeError:
        details.append("defect_classification.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def _score_corrective_actions(data: dict) -> Dict[str, Any]:
    """Score corrective actions plan (weight: 0.10)."""
    score = 0.0
    details = []

    actions_file = _find_file("corrective_actions_zh.json")
    if not actions_file.exists():
        return {"score": 0.0, "details": ["corrective_actions_zh.json not found"]}

    try:
        actions_data = json.loads(actions_file.read_text(encoding="utf-8"))
        content_str = json.dumps(actions_data, ensure_ascii=False)

        # Check for short-term vs long-term actions
        has_short = any(kw in content_str for kw in ["短期", "临时", "immediate", "short"])
        has_long = any(kw in content_str for kw in ["长期", "永久", "long-term", "permanent"])
        if has_short:
            score += 0.25
            details.append("Short-term actions included")
        if has_long:
            score += 0.25
            details.append("Long-term actions included")

        # Check for responsibility assignment
        if any(kw in content_str for kw in ["责任人", "负责", "responsible", "owner"]):
            score += 0.25
            details.append("Responsibility assigned")

        # Check for timeline/deadline
        if any(kw in content_str for kw in ["期限", "日期", "deadline", "完成时间", "目标日期"]):
            score += 0.25
            details.append("Deadlines specified")

    except json.JSONDecodeError:
        details.append("corrective_actions_zh.json invalid JSON")

    return {"score": min(score, 1.0), "details": details}


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading. Returns {overall_score, dimensions}."""
    data = _load_answer()

    dimensions = {
        "defect_detection": _score_defect_detection(data),
        "root_cause": _score_root_cause(data),
        "chinese_alert": _score_chinese_alert(data),
        "classification": _score_classification(data),
        "corrective_actions": _score_corrective_actions(data),
    }

    weights = {
        "defect_detection": 0.30,
        "root_cause": 0.25,
        "chinese_alert": 0.20,
        "classification": 0.15,
        "corrective_actions": 0.10,
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
    optional_important = ["quality_alert_zh.md", "defect_classification.json",
                          "root_cause_analysis.json", "corrective_actions_zh.json"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify quality alert is in Chinese (CJK), not English fallback."""
    alert_file = _find_file("quality_alert_zh.md")
    if not alert_file.exists():
        return
    content = alert_file.read_text(encoding="utf-8")
    chinese_chars = sum(1 for c in content if '一' <= c <= '鿿')
    total_chars = len(content.replace(" ", "").replace("\n", ""))
    ratio = chinese_chars / max(total_chars, 1)
    assert ratio > 0.2, f"Chinese alert CJK ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    blob = json.dumps(data, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Chinese alert isn't in English."""
    alert_file = _find_file("quality_alert_zh.md")
    if not alert_file.exists():
        return
    text = alert_file.read_text(encoding="utf-8")
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Alert appears to be mostly English ({english_ratio:.0%})"


def test_defect_counts_plausible():
    """Verify defect counts are in plausible range."""
    data = _load_answer()
    if "total_defects" in data:
        total = data["total_defects"]
        assert isinstance(total, (int, float)) and 40 <= total <= 120, \
            f"Total defects {total} outside plausible range (40-120)"
    if "critical_defects" in data:
        critical = data["critical_defects"]
        assert isinstance(critical, (int, float)) and 3 <= critical <= 20, \
            f"Critical defects {critical} outside plausible range (3-20)"
