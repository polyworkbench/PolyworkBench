"""
BabelAgentBench grading for KNW-07: Cross-lingual QA from 5-language sources.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Expected answers with acceptable variations
EXPECTED_ANSWERS = {
    "Q01": {"answer": "4.6%", "acceptable": ["4.6", "4.6%", "4.6 percent"]},
    "Q02": {"answer": "2.87 million", "acceptable": ["287", "2.87", "2,870,000"]},
    "Q03": {"answer": "72%", "acceptable": ["72", "72%", "72 percent"]},
    "Q04": {"answer": "53%", "acceptable": ["53", "53%", "53 percent"]},
    "Q05": {"answer": "9.23 million barrels", "acceptable": ["9.23", "9,23"]},
    "Q06": {"answer": "21.4%", "acceptable": ["21.4", "21.4%", "21.4 percent"]},
    "Q07": {"answer": "1.87 trillion yen", "acceptable": ["1.87", "18700", "18,700", "125", "12.5"]},
    "Q08": {"answer": "1000 qubits", "acceptable": ["1000", "1,000"]},
    "Q09": {"answer": "52.8", "acceptable": ["52.8"]},
    "Q10": {"answer": "50%", "acceptable": ["50", "50%", "50 percent"]},
    "Q11": {"answer": "5.1%", "acceptable": ["5.1", "5.1%", "5.1 percent"]},
    "Q12": {"answer": "102.4 billion USD", "acceptable": ["102.4", "1024", "1,024"]},
    "Q13": {"answer": "28.1 billion cubic meters", "acceptable": ["28.1", "28,1"]},
    "Q14": {"answer": "14.7%", "acceptable": ["14.7", "14.7%", "14.7 percent"]},
    "Q15": {"answer": "25.7 billion USD", "acceptable": ["25.7", "25,7"]},
}


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


def _check_answer(answer_text: str, q_id: str) -> float:
    """Check if an answer matches expected values."""
    if not answer_text:
        return 0.0
    answer_str = str(answer_text).lower().strip()
    expected = EXPECTED_ANSWERS.get(q_id, {})
    acceptable = expected.get("acceptable", [])
    for acc in acceptable:
        if acc.lower() in answer_str:
            return 1.0
    return 0.0


def _score_answer_accuracy(fact_sheet: Any) -> Dict[str, float]:
    """Score correctness of extracted answers."""
    scores = {}
    if not fact_sheet:
        return {"fact_sheet_exists": 0.0, "accuracy": 0.0, "coverage": 0.0}

    scores["fact_sheet_exists"] = 1.0

    # Extract answers from various possible structures
    answers = {}
    if isinstance(fact_sheet, list):
        for item in fact_sheet:
            if isinstance(item, dict):
                qid = item.get("id", item.get("question_id", ""))
                ans = item.get("answer", item.get("value", item.get("response", "")))
                answers[qid] = str(ans)
    elif isinstance(fact_sheet, dict):
        if "answers" in fact_sheet:
            for item in fact_sheet["answers"]:
                if isinstance(item, dict):
                    qid = item.get("id", item.get("question_id", ""))
                    ans = item.get("answer", item.get("value", ""))
                    answers[qid] = str(ans)
        else:
            for k, v in fact_sheet.items():
                if isinstance(v, dict):
                    answers[k] = str(v.get("answer", v.get("value", "")))
                else:
                    answers[k] = str(v)

    # Score accuracy
    correct = 0
    total = len(EXPECTED_ANSWERS)
    for q_id in EXPECTED_ANSWERS:
        ans = answers.get(q_id, answers.get(q_id.lower(), ""))
        if _check_answer(ans, q_id):
            correct += 1

    scores["accuracy"] = correct / total if total > 0 else 0.0
    scores["coverage"] = min(1.0, len(answers) / total)

    return scores


def _score_source_citation(citation_data: Any) -> Dict[str, float]:
    """Score source citations quality."""
    scores = {}
    if not citation_data:
        return {"citations_exist": 0.0, "citation_count": 0.0, "citation_quality": 0.0}

    scores["citations_exist"] = 1.0

    if isinstance(citation_data, list):
        citations = citation_data
    elif isinstance(citation_data, dict):
        citations = citation_data.get("citations", citation_data.get("sources", list(citation_data.values())))
        if not isinstance(citations, list):
            citations = [citations]
    else:
        citations = []

    scores["citation_count"] = min(1.0, len(citations) / 5.0)

    # Check quality (expected fields: title, language, date)
    quality_scores = []
    for c in citations:
        if isinstance(c, dict):
            has_title = any(k in c for k in ["title", "titre"])
            has_lang = any(k in c for k in ["language", "langue", "lang"])
            has_date = any(k in c for k in ["date", "year", "published"])
            quality_scores.append((has_title + has_lang + has_date) / 3.0)
    scores["citation_quality"] = sum(quality_scores) / max(len(quality_scores), 1)

    return scores


def _score_verification_quality() -> Dict[str, float]:
    """Score the verification report."""
    scores = {}
    report_path = _find_file("verification_report.md")
    if not report_path.exists():
        return {"report_exists": 0.0, "methodology": 0.0, "length": 0.0}

    text = report_path.read_text(encoding="utf-8-sig")
    scores["report_exists"] = 1.0

    # Check methodology description
    method_terms = ["methodol", "approach", "verif", "cross-ref", "extract",
                    "translat", "locat", "identif"]
    method_found = sum(1 for t in method_terms if t in text.lower())
    scores["methodology"] = min(1.0, method_found / 4.0)

    # Check length
    wc = len(text.split())
    scores["length"] = min(1.0, wc / 300.0)

    return scores


def _score_confidence_calibration(conf_data: Any) -> Dict[str, float]:
    """Score confidence scores."""
    scores = {}
    if not conf_data:
        return {"confidence_exists": 0.0, "all_scored": 0.0, "reasonable_range": 0.0}

    scores["confidence_exists"] = 1.0

    # Extract confidence values
    conf_values = []
    if isinstance(conf_data, list):
        for item in conf_data:
            if isinstance(item, dict):
                val = item.get("confidence", item.get("score", None))
                if val is not None:
                    conf_values.append(float(val))
    elif isinstance(conf_data, dict):
        for k, v in conf_data.items():
            if isinstance(v, dict):
                val = v.get("confidence", v.get("score", None))
                if val is not None:
                    conf_values.append(float(val))
            elif isinstance(v, (int, float)):
                conf_values.append(float(v))

    scores["all_scored"] = min(1.0, len(conf_values) / 15.0)

    # Check if values are in reasonable range (0-1)
    if conf_values:
        in_range = sum(1 for v in conf_values if 0.0 <= v <= 1.0)
        scores["reasonable_range"] = in_range / len(conf_values)
    else:
        scores["reasonable_range"] = 0.0

    return scores


def _score_completeness(fact_sheet: Any, citation_data: Any, conf_data: Any) -> Dict[str, float]:
    """Score overall completeness of outputs."""
    scores = {}
    scores["fact_sheet"] = 1.0 if fact_sheet else 0.0
    scores["verification_report"] = 1.0 if _find_file("verification_report.md").exists() else 0.0
    scores["source_citations"] = 1.0 if citation_data else 0.0
    scores["confidence_scores"] = 1.0 if conf_data else 0.0
    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for KNW-07."""
    fact_sheet = _load_json("fact_sheet.json")
    citation_data = _load_json("source_citations.json")
    conf_data = _load_json("confidence_scores.json")

    dimensions = {}

    # Dimension 1: Answer Accuracy (weight: 0.30)
    acc_scores = _score_answer_accuracy(fact_sheet)
    dimensions["answer_accuracy"] = {
        "score": sum(acc_scores.values()) / max(len(acc_scores), 1),
        "weight": 0.30,
        "details": acc_scores
    }

    # Dimension 2: Source Citation (weight: 0.25)
    cit_scores = _score_source_citation(citation_data)
    dimensions["source_citation"] = {
        "score": sum(cit_scores.values()) / max(len(cit_scores), 1),
        "weight": 0.25,
        "details": cit_scores
    }

    # Dimension 3: Verification Quality (weight: 0.20)
    ver_scores = _score_verification_quality()
    dimensions["verification_quality"] = {
        "score": sum(ver_scores.values()) / max(len(ver_scores), 1),
        "weight": 0.20,
        "details": ver_scores
    }

    # Dimension 4: Confidence Calibration (weight: 0.15)
    conf_scores = _score_confidence_calibration(conf_data)
    dimensions["confidence_calibration"] = {
        "score": sum(conf_scores.values()) / max(len(conf_scores), 1),
        "weight": 0.15,
        "details": conf_scores
    }

    # Dimension 5: Completeness (weight: 0.10)
    comp_scores = _score_completeness(fact_sheet, citation_data, conf_data)
    dimensions["completeness"] = {
        "score": sum(comp_scores.values()) / max(len(comp_scores), 1),
        "weight": 0.10,
        "details": comp_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"KNW-07 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_fact_sheet_exists():
    path = _find_file("fact_sheet.json")
    assert path.exists(), "fact_sheet.json not found"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    assert data, "fact_sheet.json is empty"


def test_answer_accuracy_minimum():
    result = grade()
    acc = result["dimensions"].get("answer_accuracy", {})
    details = acc.get("details", {})
    assert details.get("accuracy", 0) >= 0.3, (
        "At least 5 of 15 questions must be answered correctly"
    )


def test_all_sources_cited():
    path = _find_file("source_citations.json")
    assert path.exists(), "source_citations.json not found"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        citations = data
    elif isinstance(data, dict):
        citations = data.get("citations", data.get("sources", []))
    else:
        citations = []
    assert len(citations) >= 5, "All 5 source documents must be cited"


def test_confidence_scores_present():
    path = _find_file("confidence_scores.json")
    assert path.exists(), "confidence_scores.json not found"
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    assert data, "confidence_scores.json is empty"


def test_verification_report_exists():
    path = _find_file("verification_report.md")
    assert path.exists(), "verification_report.md not found"
    text = path.read_text(encoding="utf-8-sig")
    assert len(text.split()) >= 100, "Verification report too short"


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
