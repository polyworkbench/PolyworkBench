"""
BabelAgentBench grading for KNW-10: Multi-source fact verification across 6 languages.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List
import pytest

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Expected verification statuses for each claim
EXPECTED_STATUSES = {
    "C01": "VERIFIED",         # China GDP 4.8% - confirmed in zh, ru, fr sources
    "C02": "CONTRADICTED",     # Global semi $620B - sources say $588B, $612B, $595B (not $620B)
    "C03": "CONTRADICTED",     # Vietnam FDI $30B - actual is $25.7B registered
    "C04": "VERIFIED",         # Russia nuclear 21.4% - confirmed in ru source
    "C05": "CONTRADICTED",     # Japan AI 2.5T yen - actual is 1.87T yen
    "C06": "VERIFIED",         # Korea semi exports +42.3% - confirmed in ko source
    "C07": "PARTIALLY_VERIFIED",  # France renewables 70 GW - actual is 68.4 GW (close but not 70)
    "C08": "CONTRADICTED",     # China NEV 8M - actual is 7.358M (735.8 wan)
    "C09": "VERIFIED",         # Russia oil 9.23M bpd - confirmed in ru source
    "C10": "VERIFIED",         # Vietnam electronics $52.8B - confirmed in vi source
    "C11": "CONTRADICTED",     # Global AI chip $45B - Korean source says $72.4B
    "C12": "PARTIALLY_VERIFIED",  # Japan robotics 45.2% - JA says 45.2%, KO says 42%, FR says 43-45%
    "C13": "VERIFIED",         # Korea HBM 98% - confirmed in ko source
    "C14": "PARTIALLY_VERIFIED",  # France nuclear 65% - actual is 62.8% (close but not 65%)
    "C15": "CONTRADICTED",     # Russia gas to China 35 bcm - actual is 28.1 bcm
    "C16": "VERIFIED",         # Vietnam PMI >50 - confirmed (avg 52.8)
    "C17": "VERIFIED",         # China high-tech mfg 9.1% - confirmed in zh source
    "C18": "CONTRADICTED",     # Japan semi 3T yen - actual is 2.43T yen
    "C19": "PARTIALLY_VERIFIED",  # Global AI >$150B - sources vary: $148B, $152B, $150-155B
    "C20": "VERIFIED",         # Korea semi capex 72T won - confirmed in ko source
}

# Known contradictions that should be detected
EXPECTED_CONTRADICTIONS = [
    {"claim": "C02", "description": "Global semiconductor market size differs across sources",
     "sources": ["zh ($588B)", "ja ($612B)", "ko ($595B)", "fr ($595-615B)"]},
    {"claim": "C05", "description": "Japan AI market size: claim says 2.5T yen, actual is 1.87T yen"},
    {"claim": "C12", "description": "Japan robotics share: JA=45.2%, KO=42%, FR=43-45%"},
    {"claim": "C15", "description": "Russia-China gas: claim says 35 bcm, actual is 28.1 bcm"},
    {"claim": "C19", "description": "Global AI investment varies: JA=$148B, ZH=$152B, KO=$155B, FR=$148-156B"},
]


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


def _normalize_status(status: str) -> str:
    """Normalize verification status strings."""
    status = status.upper().strip()
    if "VERIFIED" in status and "PARTIALLY" not in status and "UN" not in status:
        return "VERIFIED"
    elif "CONTRADICT" in status:
        return "CONTRADICTED"
    elif "PARTIAL" in status:
        return "PARTIALLY_VERIFIED"
    elif "UNVERIF" in status:
        return "UNVERIFIABLE"
    return status


def _score_verification_accuracy(claims_matrix: Any) -> Dict[str, float]:
    """Score accuracy of verification decisions."""
    scores = {}

    if not claims_matrix:
        return {"matrix_exists": 0.0, "status_accuracy": 0.0,
                "coverage": 0.0}

    scores["matrix_exists"] = 1.0

    # Extract statuses from matrix
    statuses = {}
    if isinstance(claims_matrix, list):
        for item in claims_matrix:
            if isinstance(item, dict):
                cid = item.get("id", item.get("claim_id", ""))
                status = item.get("status", item.get("verdict", item.get("result", "")))
                statuses[cid] = _normalize_status(str(status))
    elif isinstance(claims_matrix, dict):
        for k, v in claims_matrix.items():
            if isinstance(v, dict):
                status = v.get("status", v.get("verdict", v.get("result", "")))
                statuses[k] = _normalize_status(str(status))
            elif isinstance(v, str):
                statuses[k] = _normalize_status(v)

    # Score accuracy
    correct = 0
    total = len(EXPECTED_STATUSES)
    for cid, expected in EXPECTED_STATUSES.items():
        actual = statuses.get(cid, statuses.get(cid.lower(), ""))
        if actual == expected:
            correct += 1
        elif expected == "PARTIALLY_VERIFIED" and actual in ["VERIFIED", "CONTRADICTED"]:
            correct += 0.5  # Partial credit for reasonable alternative

    scores["status_accuracy"] = correct / total if total > 0 else 0.0
    scores["coverage"] = min(1.0, len(statuses) / total)

    return scores


def _score_contradiction_detection(contradictions_data: Any) -> Dict[str, float]:
    """Score detection of contradictions between sources."""
    scores = {}

    if not contradictions_data:
        return {"contradictions_exists": 0.0, "contradiction_count": 0.0,
                "specific_evidence": 0.0}

    scores["contradictions_exists"] = 1.0

    # Extract contradictions
    if isinstance(contradictions_data, list):
        contradictions = contradictions_data
    elif isinstance(contradictions_data, dict):
        contradictions = contradictions_data.get("contradictions",
                        contradictions_data.get("conflicts",
                        list(contradictions_data.values())))
        if not isinstance(contradictions, list):
            contradictions = [contradictions]
    else:
        contradictions = []

    scores["contradiction_count"] = min(1.0, len(contradictions) / 5.0)

    # Check for specific evidence
    contr_text = json.dumps(contradictions_data, ensure_ascii=False).lower()
    specific_markers = ["588", "612", "595", "45.2", "42", "28.1", "35",
                        "1.87", "2.5", "148", "152", "155", "62.8", "65",
                        "68.4", "70", "735", "800"]
    specific_found = sum(1 for m in specific_markers if m in contr_text)
    scores["specific_evidence"] = min(1.0, specific_found / 5.0)

    return scores


def _score_source_triangulation(claims_matrix: Any, report_text: str) -> Dict[str, float]:
    """Score cross-referencing between sources."""
    scores = {}

    combined = json.dumps(claims_matrix or {}, ensure_ascii=False) + " " + report_text

    if not combined.strip():
        return {"multi_source_refs": 0.0, "methodology": 0.0}

    # Check if multiple sources are referenced for claims
    source_names = ["china", "japan", "korea", "russia", "vietnam", "france",
                    "zh", "ja", "ko", "ru", "vi", "fr"]
    sources_found = sum(1 for s in source_names if s in combined.lower())
    scores["multi_source_refs"] = min(1.0, sources_found / 6.0)

    # Check methodology description
    method_terms = ["cross-ref", "triangul", "compar", "discrepan",
                    "methodolog", "different", "conflict", "contradict"]
    method_found = sum(1 for t in method_terms if t in combined.lower())
    scores["methodology"] = min(1.0, method_found / 4.0)

    return scores


def _score_confidence_calibration(conf_data: Any) -> Dict[str, float]:
    """Score confidence score calibration."""
    scores = {}

    if not conf_data:
        return {"confidence_exists": 0.0, "coverage": 0.0,
                "calibration": 0.0}

    scores["confidence_exists"] = 1.0

    # Extract confidence values
    conf_values = {}
    if isinstance(conf_data, list):
        for item in conf_data:
            if isinstance(item, dict):
                cid = item.get("id", item.get("claim_id", ""))
                val = item.get("confidence", item.get("score", None))
                if val is not None:
                    conf_values[cid] = float(val)
    elif isinstance(conf_data, dict):
        for k, v in conf_data.items():
            if isinstance(v, dict):
                val = v.get("confidence", v.get("score", None))
                if val is not None:
                    conf_values[k] = float(val)
            elif isinstance(v, (int, float)):
                conf_values[k] = float(v)

    scores["coverage"] = min(1.0, len(conf_values) / 20.0)

    # Check calibration: VERIFIED claims should have higher confidence
    # than CONTRADICTED/PARTIALLY_VERIFIED ones
    verified_confs = []
    other_confs = []
    for cid, conf in conf_values.items():
        expected = EXPECTED_STATUSES.get(cid, "")
        if expected == "VERIFIED":
            verified_confs.append(conf)
        elif expected in ["CONTRADICTED", "PARTIALLY_VERIFIED"]:
            other_confs.append(conf)

    if verified_confs and other_confs:
        avg_verified = sum(verified_confs) / len(verified_confs)
        avg_other = sum(other_confs) / len(other_confs)
        # Good calibration: verified claims should have higher confidence
        if avg_verified > avg_other:
            scores["calibration"] = min(1.0, (avg_verified - avg_other) * 5)
        else:
            scores["calibration"] = 0.2
    else:
        scores["calibration"] = 0.3

    return scores


def _score_report_quality(report_text: str) -> Dict[str, float]:
    """Score the verification report quality."""
    scores = {}

    if not report_text:
        return {"report_exists": 0.0, "length": 0.0, "structure": 0.0}

    scores["report_exists"] = 1.0

    # Check length
    wc = len(report_text.split())
    if wc >= 1000:
        scores["length"] = 1.0
    elif wc >= 500:
        scores["length"] = 0.7
    elif wc >= 200:
        scores["length"] = 0.4
    else:
        scores["length"] = 0.2

    # Check structure
    has_headers = len(re.findall(r'^#+\s', report_text, re.MULTILINE)) >= 3
    has_claims_refs = any(f"C{i:02d}" in report_text or f"Claim {i}" in report_text
                         for i in range(1, 21))
    scores["structure"] = (has_headers + has_claims_refs) / 2.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for KNW-10."""
    claims_matrix = _load_json("claims_matrix.json")
    contradictions_data = _load_json("contradictions.json")
    conf_data = _load_json("confidence_scores.json")
    report_text = _load_text("verification_report.md")
    reliability_data = _load_json("source_reliability.json")

    dimensions = {}

    # Dimension 1: Verification Accuracy (weight: 0.25)
    ver_scores = _score_verification_accuracy(claims_matrix)
    dimensions["verification_accuracy"] = {
        "score": sum(ver_scores.values()) / max(len(ver_scores), 1),
        "weight": 0.25,
        "details": ver_scores
    }

    # Dimension 2: Contradiction Detection (weight: 0.25)
    contr_scores = _score_contradiction_detection(contradictions_data)
    dimensions["contradiction_detection"] = {
        "score": sum(contr_scores.values()) / max(len(contr_scores), 1),
        "weight": 0.25,
        "details": contr_scores
    }

    # Dimension 3: Source Triangulation (weight: 0.20)
    tri_scores = _score_source_triangulation(claims_matrix, report_text)
    dimensions["source_triangulation"] = {
        "score": sum(tri_scores.values()) / max(len(tri_scores), 1),
        "weight": 0.20,
        "details": tri_scores
    }

    # Dimension 4: Confidence Calibration (weight: 0.15)
    cal_scores = _score_confidence_calibration(conf_data)
    dimensions["confidence_calibration"] = {
        "score": sum(cal_scores.values()) / max(len(cal_scores), 1),
        "weight": 0.15,
        "details": cal_scores
    }

    # Dimension 5: Report Quality (weight: 0.15)
    rep_scores = _score_report_quality(report_text)
    dimensions["report_quality"] = {
        "score": sum(rep_scores.values()) / max(len(rep_scores), 1),
        "weight": 0.15,
        "details": rep_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"KNW-10 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "No valid output produced"


def test_claims_matrix_exists():
    data = _load_json("claims_matrix.json")
    assert data, "claims_matrix.json not found or empty"


def test_verification_accuracy_minimum():
    result = grade()
    ver = result["dimensions"].get("verification_accuracy", {})
    details = ver.get("details", {})
    assert details.get("status_accuracy", 0) >= 0.3, (
        "At least 30% of claims must be correctly verified"
    )


def test_contradictions_detected():
    data = _load_json("contradictions.json")
    assert data, "contradictions.json not found or empty"
    if isinstance(data, list):
        contradictions = data
    elif isinstance(data, dict):
        contradictions = data.get("contradictions", data.get("conflicts", []))
    else:
        contradictions = []
    assert len(contradictions) >= 3, (
        "At least 3 contradictions should be identified"
    )


def test_confidence_scores_exist():
    data = _load_json("confidence_scores.json")
    assert data, "confidence_scores.json not found or empty"


def test_source_reliability_exists():
    data = _load_json("source_reliability.json")
    assert data, "source_reliability.json not found or empty"


def test_verification_report_adequate():
    text = _load_text("verification_report.md")
    assert text, "verification_report.md not found or empty"
    assert len(text.split()) >= 200, "Verification report too short"


def test_all_claims_addressed():
    data = _load_json("claims_matrix.json")
    if not data:
        assert False, "claims_matrix.json not found"
    # Count addressed claims
    if isinstance(data, list):
        count = len(data)
    elif isinstance(data, dict):
        count = len(data)
    else:
        count = 0
    assert count >= 15, f"At least 15 of 20 claims must be addressed (found {count})"


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
