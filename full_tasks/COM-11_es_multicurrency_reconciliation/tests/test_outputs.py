"""Test suite for COM-11: Multi-currency invoice reconciliation."""
import json
import os
import re
from pathlib import Path
from typing import Dict, Any

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR/"output"/name, OUTPUT_DIR/"outputs"/name, OUTPUT_DIR/name,
                  Path(f"/workspace/output/{name}"), Path(f"/workspace/outputs/{name}"), Path(f"/workspace/{name}")]
    for p in candidates:
        if p.exists(): return p
    return candidates[0]

def _load_json(name: str) -> Any:
    p = _find_file(name)
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8-sig"))
        except: pass
    return None

def _load_text(name: str) -> str:
    p = _find_file(name)
    if p.exists():
        try: return p.read_text(encoding="utf-8-sig")
        except: pass
    return ""

def _load_answer() -> dict:
    for p in [OUTPUT_DIR/"answer.json", OUTPUT_DIR/"output"/"answer.json", Path("/workspace/answer.json")]:
        if p.exists():
            try: return json.loads(p.read_text(encoding="utf-8-sig"))
            except: pass
    return {}

# Ground truth
TOTAL_USD = 47250.00
TOTAL_EUR_BANK = 38420.50  # approximate from bank debits
TOTAL_CNY = 312800.00
USD_TO_EUR = 0.92
CNY_TO_EUR = 0.13
EXPECTED_DISCREPANCIES = 3

def _score_conversion(answer: dict) -> float:
    score = 0.0
    if not answer: return 0.0
    
    # Check total_usd
    total_usd = answer.get("total_usd", 0)
    if isinstance(total_usd, (int, float)) and abs(total_usd - TOTAL_USD) < 100:
        score += 0.3
    
    # Check total_cny
    total_cny = answer.get("total_cny", 0)
    if isinstance(total_cny, (int, float)) and abs(total_cny - TOTAL_CNY) < 1000:
        score += 0.3
    
    # Check converted total (USD*0.92 + CNY*0.13 + EUR)
    expected_eur = TOTAL_USD * USD_TO_EUR + TOTAL_CNY * CNY_TO_EUR  # ~43470 + 40664 = ~84134
    total_conv = answer.get("total_converted_eur", 0)
    if isinstance(total_conv, (int, float)) and abs(total_conv - expected_eur) < 5000:
        score += 0.4
    
    return min(score, 1.0)

def _score_discrepancies() -> float:
    score = 0.0
    data = _load_json("discrepancies.json")
    if not data: return 0.0
    
    score += 0.2  # file exists
    
    content = json.dumps(data, ensure_ascii=False).lower()
    
    # Check for duplicate detection (ZF-0892)
    if "zf-0892" in content or "duplicate" in content or "duplica" in content:
        score += 0.3
    
    # Check for amount mismatch
    if "mismatch" in content or "discrepancia" in content or "diferencia" in content or "2340" in content or "2430" in content:
        score += 0.25
    
    # Check for missing invoice
    if "missing" in content or "faltante" in content or "us-inv-089" in content or "inv-017" in content:
        score += 0.25
    
    return min(score, 1.0)

def _score_spanish_report() -> float:
    score = 0.0
    report = _load_text("reconciliation_report_es.md")
    if not report: return 0.0
    
    score += 0.2  # exists
    
    # Check Spanish content
    spanish_markers = ["conciliación", "factura", "discrepancia", "importe", "moneda", "tipo de cambio", "total"]
    found = sum(1 for m in spanish_markers if m.lower() in report.lower())
    score += min(0.3, found * 0.05)
    
    # Check length
    if len(report) > 1000: score += 0.2
    elif len(report) > 500: score += 0.1
    
    # Check structure (headers)
    headers = re.findall(r"^#+\s+.+$", report, re.MULTILINE)
    if len(headers) >= 3: score += 0.15
    
    # Check for numbers/data in report
    numbers = re.findall(r"[\d,.]+", report)
    if len(numbers) > 10: score += 0.15
    
    return min(score, 1.0)

def _score_completeness(answer: dict) -> float:
    score = 0.0
    if not answer: return 0.0
    
    required = ["total_invoices", "total_usd", "total_eur", "total_cny", "total_converted_eur", "discrepancies_found"]
    present = sum(1 for f in required if f in answer)
    score += present / len(required) * 0.5
    
    # Check discrepancy count
    disc_count = answer.get("discrepancies_found", 0)
    if isinstance(disc_count, int) and disc_count == EXPECTED_DISCREPANCIES:
        score += 0.3
    elif isinstance(disc_count, int) and disc_count >= 2:
        score += 0.15
    
    # Check converted_totals.json exists
    totals = _load_json("converted_totals.json")
    if totals: score += 0.2
    
    return min(score, 1.0)

def grade() -> Dict[str, Any]:
    answer = _load_answer()
    dimensions = {
        "conversion_accuracy": {"score": _score_conversion(answer), "weight": 0.30},
        "discrepancy_detection": {"score": _score_discrepancies(), "weight": 0.30},
        "spanish_report": {"score": _score_spanish_report(), "weight": 0.20},
        "completeness": {"score": _score_completeness(answer), "weight": 0.20},
    }
    overall = sum(d["score"] * d["weight"] for d in dimensions.values())
    return {"overall_score": round(overall, 4), "dimensions": dimensions}

# Pytest tests
def test_answer_exists():
    answer = _load_answer()
    assert answer, "answer.json not found"
    assert "total_usd" in answer, "Missing total_usd"

def test_usd_total():
    answer = _load_answer()
    assert abs(answer.get("total_usd", 0) - TOTAL_USD) < 100, f"USD total should be ~{TOTAL_USD}"

def test_cny_total():
    answer = _load_answer()
    assert abs(answer.get("total_cny", 0) - TOTAL_CNY) < 1000, f"CNY total should be ~{TOTAL_CNY}"

def test_discrepancies_found():
    answer = _load_answer()
    assert answer.get("discrepancies_found", 0) >= 2, "Should find at least 2 discrepancies"

def test_discrepancies_json():
    data = _load_json("discrepancies.json")
    assert data, "discrepancies.json not found"

def test_spanish_report_exists():
    report = _load_text("reconciliation_report_es.md")
    assert report and len(report) > 200, "Spanish report too short or missing"

def test_spanish_language():
    report = _load_text("reconciliation_report_es.md")
    assert "conciliación" in report.lower() or "factura" in report.lower(), "Report should be in Spanish"

def test_grade_overall():
    result = grade()
    assert result["overall_score"] > 0.15, f"Score too low: {result['overall_score']}"

if __name__ == "__main__":
    print(json.dumps(grade(), indent=2, ensure_ascii=False))
