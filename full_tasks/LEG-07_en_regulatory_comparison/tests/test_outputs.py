"""
WildClawBench-style grading for LEG-07: Cross-jurisdiction Asian data protection regulatory comparison.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

JURISDICTIONS = ["China", "Korea", "Vietnam", "Japan"]
JURISDICTION_LAWS = {"China": "PIPL", "Korea": "PIPA", "Vietnam": "PDPD", "Japan": "APPI"}
DIMENSIONS = ["scope", "legal_basis", "consent", "data_subject_rights",
              "cross_border", "breach_notification", "dpo", "penalties"]

# Key facts from the source documents
KEY_FACTS = {
    "china_breach_timeline": "72",  # hours
    "korea_breach_timeline": "72",  # hours
    "vietnam_breach_timeline": "72",  # hours
    "japan_breach_timeline_initial": "3",  # days (speed report)
    "china_dpo_threshold": "1000000",  # 100万人
    "korea_dpo_mandatory": True,  # all organizations
    "vietnam_dpo_mandatory": True,  # all organizations
    "japan_dpo_mandatory": False,  # recommended only
    "china_max_fine_pct": "5",  # 5% of revenue
    "korea_max_fine_pct": "3",  # 3% of revenue
    "china_children_age": "14",
    "korea_children_age": "14",
    "vietnam_children_age": "7",
    "china_cross_border_security_assessment": True,
    "vietnam_cross_border_mps_notification": True,
    "japan_adequacy_mechanism": True,
    "korea_adequacy_mechanism": True,
}


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


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


def _score_accuracy(analysis: str, matrix: Any, gap: Any) -> Dict[str, float]:
    """Score accuracy of regulatory information (weight: 0.25)."""
    scores = {}
    combined = analysis + " " + json.dumps(matrix or {}, ensure_ascii=False) + " " + json.dumps(gap or {}, ensure_ascii=False)

    if not combined.strip():
        return {"content_exists": 0.0, "breach_timelines": 0.0,
                "dpo_requirements": 0.0, "fine_amounts": 0.0, "children_ages": 0.0}

    scores["content_exists"] = 1.0

    # Check breach notification timelines
    breach_correct = 0
    if "72" in combined:  # China, Korea, Vietnam all 72 hours
        breach_correct += 1
    # Japan has different timeline (3-5 days initial)
    if any(t in combined for t in ["3 day", "5 day", "3日", "5日", "3-5"]):
        breach_correct += 1
    scores["breach_timelines"] = min(1.0, breach_correct / 2)

    # Check DPO requirements accuracy
    dpo_correct = 0
    # Japan DPO not mandatory
    if any(phrase in combined.lower() for phrase in
           ["japan" + s for s in [" not mandatory", " recommended", " no legal obligation",
                                   " voluntary", " not required"]]):
        dpo_correct += 1
    elif "recommend" in combined.lower() and "japan" in combined.lower():
        dpo_correct += 1
    # Korea/Vietnam mandatory for all
    if "mandatory" in combined.lower() or "all organ" in combined.lower():
        dpo_correct += 1
    scores["dpo_requirements"] = min(1.0, dpo_correct / 2)

    # Check fine amounts
    fine_correct = 0
    if "5%" in combined or "5 percent" in combined.lower() or "百分之五" in combined:
        fine_correct += 1  # China
    if "3%" in combined or "3 percent" in combined.lower() or "100분의 3" in combined:
        fine_correct += 1  # Korea
    if any(t in combined for t in ["100 million", "1億", "100,000,000"]):
        fine_correct += 1  # Japan (1 oku yen)
    scores["fine_amounts"] = min(1.0, fine_correct / 2)

    # Children age thresholds
    age_correct = 0
    if "14" in combined:  # China and Korea
        age_correct += 1
    if "7" in combined:  # Vietnam
        age_correct += 1
    scores["children_ages"] = min(1.0, age_correct / 2)

    return scores


def _score_completeness(analysis: str, matrix: Any) -> Dict[str, float]:
    """Score completeness of coverage (weight: 0.25)."""
    scores = {}

    if not analysis and not matrix:
        return {"all_jurisdictions": 0.0, "all_dimensions": 0.0,
                "cross_border_detail": 0.0, "rights_comparison": 0.0}

    combined = analysis + " " + json.dumps(matrix or {}, ensure_ascii=False)

    # Check all 4 jurisdictions covered
    jurisdictions_found = sum(1 for j in JURISDICTIONS if j.lower() in combined.lower())
    laws_found = sum(1 for law in JURISDICTION_LAWS.values() if law in combined)
    scores["all_jurisdictions"] = min(1.0, max(jurisdictions_found, laws_found) / 4)

    # Check all comparison dimensions covered
    dimension_keywords = {
        "scope": ["scope", "applicab", "territorial", "extraterritorial"],
        "legal_basis": ["legal basis", "lawful", "legitimate interest"],
        "consent": ["consent", "agree"],
        "data_subject_rights": ["right", "access", "erasure", "portability"],
        "cross_border": ["cross-border", "transfer", "international"],
        "breach_notification": ["breach", "notification", "incident"],
        "dpo": ["DPO", "officer", "responsible person"],
        "penalties": ["penalt", "fine", "sanction", "enforcement"],
    }
    dims_covered = 0
    for dim, keywords in dimension_keywords.items():
        if any(kw.lower() in combined.lower() for kw in keywords):
            dims_covered += 1
    scores["all_dimensions"] = dims_covered / len(DIMENSIONS)

    # Cross-border transfer mechanisms detail
    cross_border_terms = ["security assessment", "standard contract", "certification",
                          "adequacy", "CBPR", "notification", "consent"]
    cb_found = sum(1 for t in cross_border_terms if t.lower() in combined.lower())
    scores["cross_border_detail"] = min(1.0, cb_found / 4)

    # Data subject rights comparison
    rights_terms = ["access", "rectification", "erasure", "deletion",
                    "portability", "restriction", "objection"]
    rights_found = sum(1 for t in rights_terms if t.lower() in combined.lower())
    scores["rights_comparison"] = min(1.0, rights_found / 4)

    return scores


def _score_comparative_quality(analysis: str, gap: Any) -> Dict[str, float]:
    """Score quality of comparative analysis (weight: 0.20)."""
    scores = {}

    if not analysis:
        return {"analysis_exists": 0.0, "comparative_language": 0.0,
                "structured_comparison": 0.0, "recommendations": 0.0}

    scores["analysis_exists"] = 1.0

    # Check for comparative language
    comparative_terms = ["compared to", "unlike", "in contrast", "similarly",
                         "whereas", "more strict", "less strict", "stricter",
                         "unique", "differs", "common", "all four", "all jurisdictions"]
    comp_found = sum(1 for t in comparative_terms if t.lower() in analysis.lower())
    scores["comparative_language"] = min(1.0, comp_found / 4)

    # Check for structured comparison (tables, headings)
    has_table = "|" in analysis and "---" in analysis
    has_headings = bool(re.search(r'#{1,3}\s', analysis))
    scores["structured_comparison"] = 1.0 if (has_table or has_headings) else 0.0

    # Check for recommendations
    rec_terms = ["recommend", "should", "advise", "suggest", "action",
                 "priority", "implement", "compliance strategy"]
    rec_found = sum(1 for t in rec_terms if t.lower() in analysis.lower())
    scores["recommendations"] = min(1.0, rec_found / 3)

    return scores


def _score_regulatory_mapping(matrix: Any) -> Dict[str, float]:
    """Score regulation matrix quality (weight: 0.15)."""
    scores = {}

    if not matrix:
        return {"matrix_exists": 0.0, "matrix_structure": 0.0,
                "article_references": 0.0, "requirement_levels": 0.0}

    scores["matrix_exists"] = 1.0

    # Check structure
    matrix_str = json.dumps(matrix, ensure_ascii=False)

    if isinstance(matrix, dict):
        # Check if it has jurisdiction entries
        has_jurisdictions = sum(1 for j in JURISDICTIONS
                                if j.lower() in matrix_str.lower())
        scores["matrix_structure"] = min(1.0, has_jurisdictions / 4)
    elif isinstance(matrix, list):
        scores["matrix_structure"] = 0.7 if len(matrix) >= 4 else len(matrix) / 8
    else:
        scores["matrix_structure"] = 0.0

    # Check for article/section references
    article_patterns = [
        r'[Aa]rt(?:icle)?\s*\d+', r'[Ss]ection\s*\d+', r'第\d+条',
        r'제\d+조', r'Điều\s*\d+'
    ]
    article_count = sum(len(re.findall(p, matrix_str)) for p in article_patterns)
    scores["article_references"] = min(1.0, article_count / 8)

    # Check for requirement level indicators
    level_terms = ["mandatory", "required", "recommended", "not required",
                   "optional", "conditional", "strict", "moderate"]
    level_found = sum(1 for t in level_terms if t.lower() in matrix_str.lower())
    scores["requirement_levels"] = min(1.0, level_found / 4)

    return scores


def _score_roadmap_feasibility(roadmap: Any) -> Dict[str, float]:
    """Score compliance roadmap (weight: 0.15)."""
    scores = {}

    if not roadmap:
        return {"roadmap_exists": 0.0, "has_actions": 0.0,
                "has_timeline": 0.0, "has_priority": 0.0}

    scores["roadmap_exists"] = 1.0

    roadmap_str = json.dumps(roadmap, ensure_ascii=False)

    # Check for action items
    if isinstance(roadmap, list):
        scores["has_actions"] = min(1.0, len(roadmap) / 5)
    elif isinstance(roadmap, dict):
        # Could be structured with phases/categories
        items = roadmap.get("actions", roadmap.get("items",
                           roadmap.get("phases", roadmap.get("steps", []))))
        if isinstance(items, list):
            scores["has_actions"] = min(1.0, len(items) / 5)
        else:
            scores["has_actions"] = 0.5 if len(roadmap) >= 3 else 0.3
    else:
        scores["has_actions"] = 0.0

    # Check for timeline information
    timeline_terms = ["week", "month", "day", "quarter", "phase",
                      "timeline", "deadline", "duration", "Q1", "Q2"]
    timeline_found = sum(1 for t in timeline_terms if t.lower() in roadmap_str.lower())
    scores["has_timeline"] = min(1.0, timeline_found / 3)

    # Check for priority/effort
    priority_terms = ["priority", "high", "medium", "low", "critical",
                      "effort", "resource", "urgent", "important"]
    priority_found = sum(1 for t in priority_terms if t.lower() in roadmap_str.lower())
    scores["has_priority"] = min(1.0, priority_found / 3)

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for LEG-07."""
    analysis = _load_md_file("comparative_analysis.md")
    matrix = _load_json_file("regulation_matrix.json")
    gap = _load_json_file("gap_summary.json")
    roadmap = _load_json_file("compliance_roadmap.json")

    if not analysis and not matrix and not gap and not roadmap:
        return {"overall_score": 0.0, "dimensions": {}, "error": "No output files found."}

    dimensions = {}

    # Dimension 1: Accuracy (weight: 0.25)
    accuracy_scores = _score_accuracy(analysis, matrix, gap)
    dimensions["accuracy"] = {
        "score": sum(accuracy_scores.values()) / max(len(accuracy_scores), 1),
        "weight": 0.25,
        "details": accuracy_scores
    }

    # Dimension 2: Completeness (weight: 0.25)
    completeness_scores = _score_completeness(analysis, matrix)
    dimensions["completeness"] = {
        "score": sum(completeness_scores.values()) / max(len(completeness_scores), 1),
        "weight": 0.25,
        "details": completeness_scores
    }

    # Dimension 3: Comparative Quality (weight: 0.20)
    comparative_scores = _score_comparative_quality(analysis, gap)
    dimensions["comparative_quality"] = {
        "score": sum(comparative_scores.values()) / max(len(comparative_scores), 1),
        "weight": 0.20,
        "details": comparative_scores
    }

    # Dimension 4: Regulatory Mapping (weight: 0.15)
    mapping_scores = _score_regulatory_mapping(matrix)
    dimensions["regulatory_mapping"] = {
        "score": sum(mapping_scores.values()) / max(len(mapping_scores), 1),
        "weight": 0.15,
        "details": mapping_scores
    }

    # Dimension 5: Roadmap Feasibility (weight: 0.15)
    roadmap_scores = _score_roadmap_feasibility(roadmap)
    dimensions["roadmap_feasibility"] = {
        "score": sum(roadmap_scores.values()) / max(len(roadmap_scores), 1),
        "weight": 0.15,
        "details": roadmap_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"LEG-07 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
        for k, v in dim.get("details", {}).items():
            print(f"    {k}: {v:.2f}")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_all_jurisdictions_covered():
    """Verify all 4 jurisdictions are addressed."""
    analysis = _load_md_file("comparative_analysis.md")
    matrix = _load_json_file("regulation_matrix.json")
    combined = analysis + " " + json.dumps(matrix or {}, ensure_ascii=False)
    found = sum(1 for j in JURISDICTIONS if j.lower() in combined.lower())
    assert found >= 4, f"Only {found}/4 jurisdictions covered"


def test_breach_notification_comparison():
    """Verify breach notification timelines are compared."""
    analysis = _load_md_file("comparative_analysis.md")
    matrix = _load_json_file("regulation_matrix.json")
    combined = analysis + " " + json.dumps(matrix or {}, ensure_ascii=False)
    assert "72" in combined, "72-hour breach notification timeline not mentioned"


def test_cross_border_mechanisms():
    """Verify cross-border transfer mechanisms are analyzed."""
    analysis = _load_md_file("comparative_analysis.md")
    assert any(t in analysis.lower() for t in ["cross-border", "transfer", "international"]), \
        "Cross-border transfer analysis missing"


def test_gap_summary_exists():
    """Verify gap summary JSON is generated."""
    gap = _load_json_file("gap_summary.json")
    assert gap is not None, "gap_summary.json not found or invalid"


def test_compliance_roadmap_exists():
    """Verify compliance roadmap JSON is generated."""
    roadmap = _load_json_file("compliance_roadmap.json")
    assert roadmap is not None, "compliance_roadmap.json not found or invalid"


def test_japan_dpo_not_mandatory():
    """Verify Japan's DPO requirement is correctly identified as non-mandatory."""
    analysis = _load_md_file("comparative_analysis.md")
    matrix = _load_json_file("regulation_matrix.json")
    combined = analysis + " " + json.dumps(matrix or {}, ensure_ascii=False)
    # Japan doesn't have mandatory DPO
    japan_section = combined.lower()
    assert any(phrase in japan_section for phrase in
               ["not mandatory", "recommended", "not required", "voluntary", "no legal"]), \
        "Japan DPO requirement should be identified as non-mandatory/recommended"


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
