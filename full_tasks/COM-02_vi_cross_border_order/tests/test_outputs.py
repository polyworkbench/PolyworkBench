"""
BabelAgentBench grading for COM-02: Cross-border order reconciliation (Vietnamese).
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

EXPECTED_ORDERS = 10
EXCHANGE_RATE = 3450  # 1 CNY = 3450 VND

# Known discrepancies embedded in the input data:
# ORD-VN-001: value mismatch (invoice 17000 CNY = 58,650,000 VND vs customs declared 55,200,000 VND)
# ORD-VN-003: quantity mismatch (invoice: 500, customs: 480) - noted in customs form
# ORD-VN-005: HS code mismatch (invoice: 6911.10.11 vs customs: 6911.10.19) - noted in customs form
# ORD-VN-006: value underreporting (~16% below actual) - noted in customs form
# ORD-VN-007: product mismatch (invoice: leather shoes 6403.59.90 vs other HS codes)
KNOWN_DISCREPANCIES = ["ORD-VN-001", "ORD-VN-003", "ORD-VN-005", "ORD-VN-006", "ORD-VN-007"]


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_answer() -> Dict[str, Any]:
    candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    for path in candidates:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    return {}


def _is_vietnamese(text: str) -> bool:
    """Check if text contains Vietnamese diacritical characters."""
    if not text:
        return False
    vietnamese_chars = set("ăắằẳẵặâấầẩẫậđêếềểễệôốồổỗộơớờởỡợưứừửữựíìỉĩịúùủũụóòỏõọéèẻẽẹáàảãạýỳỷỹỵ")
    vn_count = sum(1 for c in text.lower() if c in vietnamese_chars)
    return vn_count >= 3


def _score_reconciliation(data: Dict[str, Any]) -> Dict[str, float]:
    """Score order reconciliation accuracy."""
    scores = {}
    reconciled_path = _find_file("orders_reconciled.json")

    reconciled = None
    if reconciled_path.exists():
        try:
            reconciled = json.loads(reconciled_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not reconciled:
        reconciled = data.get("orders_reconciled", data.get("reconciled", []))

    if not reconciled:
        return {"file_present": 0.0, "order_count": 0.0, "fields_complete": 0.0, "currency_conversion": 0.0}

    scores["file_present"] = 1.0

    # Check if it's a list or dict with orders
    orders = reconciled if isinstance(reconciled, list) else reconciled.get("orders", list(reconciled.values()) if isinstance(reconciled, dict) else [])

    scores["order_count"] = min(1.0, len(orders) / EXPECTED_ORDERS)

    # Check field completeness
    required_fields = ["order_id", "quantity", "hs_code"]
    field_scores = []
    for order in orders:
        if isinstance(order, dict):
            present = sum(1 for f in required_fields if any(f in k.lower().replace("_", "") or k.lower().replace("_", "") in f for k in order.keys()))
            field_scores.append(present / len(required_fields))
    scores["fields_complete"] = sum(field_scores) / max(len(field_scores), 1) if field_scores else 0.0

    # Check currency conversion (VND values should be present)
    vnd_found = 0
    for order in orders:
        if isinstance(order, dict):
            blob = json.dumps(order).lower()
            if "vnd" in blob or any(isinstance(v, (int, float)) and v > 1000000 for v in order.values() if isinstance(v, (int, float))):
                vnd_found += 1
    scores["currency_conversion"] = min(1.0, vnd_found / max(len(orders), 1))

    return scores


def _score_customs_compliance(data: Dict[str, Any]) -> Dict[str, float]:
    """Score customs declarations quality."""
    scores = {}
    customs_path = _find_file("customs_declarations_vi.json")

    customs = None
    if customs_path.exists():
        try:
            customs = json.loads(customs_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not customs:
        return {"file_present": 0.0, "declarations_count": 0.0, "hs_codes_valid": 0.0, "vietnamese_content": 0.0}

    scores["file_present"] = 1.0

    # Get declarations list
    declarations = customs if isinstance(customs, list) else customs.get("declarations", list(customs.values()) if isinstance(customs, dict) else [])

    scores["declarations_count"] = min(1.0, len(declarations) / EXPECTED_ORDERS)

    # Check HS code format (should be XX.XX or XXXX.XX.XX pattern)
    valid_hs = 0
    for decl in declarations:
        if isinstance(decl, dict):
            hs = str(decl.get("hs_code", decl.get("ma_hs", "")))
            if re.match(r'\d{4}[\.\s]?\d{2}', hs):
                valid_hs += 1
    scores["hs_codes_valid"] = valid_hs / max(len(declarations), 1) if declarations else 0.0

    # Check Vietnamese content
    vn_count = 0
    for decl in declarations:
        if isinstance(decl, dict):
            text = json.dumps(decl, ensure_ascii=False)
            if _is_vietnamese(text):
                vn_count += 1
    scores["vietnamese_content"] = vn_count / max(len(declarations), 1) if declarations else 0.0

    return scores


def _score_shipping_labels(data: Dict[str, Any]) -> Dict[str, float]:
    """Score shipping labels quality."""
    scores = {}
    labels_path = _find_file("shipping_labels_vi.json")

    labels = None
    if labels_path.exists():
        try:
            labels = json.loads(labels_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not labels:
        return {"file_present": 0.0, "label_count": 0.0, "address_complete": 0.0, "vietnamese_names": 0.0}

    scores["file_present"] = 1.0

    # Get labels list
    label_list = labels if isinstance(labels, list) else labels.get("labels", labels.get("shipping_labels", list(labels.values()) if isinstance(labels, dict) else []))

    scores["label_count"] = min(1.0, len(label_list) / EXPECTED_ORDERS)

    # Check address completeness
    address_fields = ["recipient", "address", "phone", "postal"]
    complete_count = 0
    for label in label_list:
        if isinstance(label, dict):
            blob = json.dumps(label).lower()
            found = sum(1 for f in address_fields if any(f in k.lower() for k in label.keys()) or f in blob)
            if found >= 3:
                complete_count += 1
    scores["address_complete"] = complete_count / max(len(label_list), 1) if label_list else 0.0

    # Check Vietnamese names/addresses
    vn_name_count = 0
    for label in label_list:
        if isinstance(label, dict):
            text = json.dumps(label, ensure_ascii=False)
            if _is_vietnamese(text):
                vn_name_count += 1
    scores["vietnamese_names"] = vn_name_count / max(len(label_list), 1) if label_list else 0.0

    return scores


def _score_discrepancy_detection(data: Dict[str, Any]) -> Dict[str, float]:
    """Score discrepancy detection accuracy."""
    scores = {}
    report_path = _find_file("discrepancy_report.md")

    report_text = ""
    if report_path.exists():
        report_text = report_path.read_text(encoding="utf-8-sig")

    if not report_text:
        return {"file_present": 0.0, "discrepancies_found": 0.0, "detail_quality": 0.0}

    scores["file_present"] = 1.0

    # Check how many known discrepancies are detected
    found = 0
    for order_id in KNOWN_DISCREPANCIES:
        if order_id in report_text:
            found += 1
    scores["discrepancies_found"] = found / len(KNOWN_DISCREPANCIES)

    # Check detail quality (mentions of quantity, HS code, value issues)
    detail_keywords = ["số lượng", "mã hs", "giá trị", "chênh lệch", "sai", "khác", "quantity", "hs code", "value", "mismatch"]
    detail_found = sum(1 for kw in detail_keywords if kw.lower() in report_text.lower())
    scores["detail_quality"] = min(1.0, detail_found / 4)

    return scores


def _score_vietnamese_quality(data: Dict[str, Any]) -> Dict[str, float]:
    """Score overall Vietnamese language quality across outputs."""
    scores = {}

    # Check discrepancy report Vietnamese
    report_path = _find_file("discrepancy_report.md")
    if report_path.exists():
        text = report_path.read_text(encoding="utf-8-sig")
        scores["report_vietnamese"] = 1.0 if _is_vietnamese(text) and len(text) > 100 else 0.5 if len(text) > 50 else 0.0
    else:
        scores["report_vietnamese"] = 0.0

    # Check customs declarations Vietnamese
    customs_path = _find_file("customs_declarations_vi.json")
    if customs_path.exists():
        text = customs_path.read_text(encoding="utf-8-sig")
        scores["customs_vietnamese"] = 1.0 if _is_vietnamese(text) else 0.0
    else:
        scores["customs_vietnamese"] = 0.0

    # Check shipping labels Vietnamese
    labels_path = _find_file("shipping_labels_vi.json")
    if labels_path.exists():
        text = labels_path.read_text(encoding="utf-8-sig")
        scores["labels_vietnamese"] = 1.0 if _is_vietnamese(text) else 0.0
    else:
        scores["labels_vietnamese"] = 0.0

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for COM-02."""
    data = _load_answer()

    dimensions = {}

    # Dimension 1: Reconciliation Accuracy (weight: 0.30)
    recon_scores = _score_reconciliation(data)
    dimensions["reconciliation_accuracy"] = {
        "score": sum(recon_scores.values()) / max(len(recon_scores), 1),
        "weight": 0.30,
        "details": recon_scores
    }

    # Dimension 2: Customs Compliance (weight: 0.25)
    customs_scores = _score_customs_compliance(data)
    dimensions["customs_compliance"] = {
        "score": sum(customs_scores.values()) / max(len(customs_scores), 1),
        "weight": 0.25,
        "details": customs_scores
    }

    # Dimension 3: Shipping Labels (weight: 0.20)
    label_scores = _score_shipping_labels(data)
    dimensions["shipping_labels"] = {
        "score": sum(label_scores.values()) / max(len(label_scores), 1),
        "weight": 0.20,
        "details": label_scores
    }

    # Dimension 4: Discrepancy Detection (weight: 0.15)
    disc_scores = _score_discrepancy_detection(data)
    dimensions["discrepancy_detection"] = {
        "score": sum(disc_scores.values()) / max(len(disc_scores), 1),
        "weight": 0.15,
        "details": disc_scores
    }

    # Dimension 5: Vietnamese Quality (weight: 0.10)
    vn_scores = _score_vietnamese_quality(data)
    dimensions["vietnamese_quality"] = {
        "score": sum(vn_scores.values()) / max(len(vn_scores), 1),
        "weight": 0.10,
        "details": vn_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-02 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_reconciliation_present():
    result = grade()
    recon = result["dimensions"].get("reconciliation_accuracy", {})
    details = recon.get("details", {})
    assert details.get("file_present", 0) == 1.0, "orders_reconciled.json must be present"


def test_customs_vietnamese():
    result = grade()
    customs = result["dimensions"].get("customs_compliance", {})
    details = customs.get("details", {})
    assert details.get("vietnamese_content", 0) >= 0.5, "Customs declarations must contain Vietnamese text"


def test_discrepancies_detected():
    result = grade()
    disc = result["dimensions"].get("discrepancy_detection", {})
    details = disc.get("details", {})
    assert details.get("discrepancies_found", 0) >= 0.4, "At least 2 of 5 known discrepancies should be detected"


def test_shipping_labels_complete():
    result = grade()
    labels = result["dimensions"].get("shipping_labels", {})
    details = labels.get("details", {})
    assert details.get("label_count", 0) >= 0.8, "At least 8 of 10 shipping labels should be generated"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["orders_reconciled.json", "customs_declarations_vi.json",
                          "shipping_labels_vi.json", "discrepancy_report.md"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify output contains Vietnamese diacritics, not English fallback."""
    customs_path = _find_file("customs_declarations_vi.json")
    labels_path = _find_file("shipping_labels_vi.json")
    report_path = _find_file("discrepancy_report.md")

    texts = []
    for p in [customs_path, labels_path, report_path]:
        if p.exists():
            texts.append(p.read_text(encoding="utf-8-sig"))

    assert texts, "No Vietnamese output files found"
    combined = " ".join(texts)
    assert _is_vietnamese(combined), "Output files don't contain Vietnamese diacritical marks"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    blob = json.dumps(data, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify primary output isn't in English."""
    report_path = _find_file("discrepancy_report.md")
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8-sig")
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Discrepancy report appears to be mostly English ({english_ratio:.0%})"


def test_item_count_sufficient():
    """Verify at least 10 orders are reconciled."""
    reconciled_path = _find_file("orders_reconciled.json")
    if not reconciled_path.exists():
        data = _load_answer()
        orders = data.get("orders_reconciled", data.get("reconciled", []))
    else:
        try:
            reconciled = json.loads(reconciled_path.read_text(encoding="utf-8-sig"))
            orders = reconciled if isinstance(reconciled, list) else reconciled.get("orders", list(reconciled.values()) if isinstance(reconciled, dict) else [])
        except Exception:
            orders = []
    assert len(orders) >= 8, f"Only {len(orders)} orders reconciled, expected ~10"
