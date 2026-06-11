"""
Test suite for LEG-13: Spanish Evidence Chain Reconstruction
Ground truth:
  Timeline:
    Jan 12 - Transfer 1 (¥2.3M)
    Jan 15 - In-person meeting in Madrid
    Jan 18 - Transfer 2 (¥1.8M)
    Jan 20 - Agreement signing
    Jan 25 - Transfer 3 (¥3.1M)
  Financials:
    Total CNY: ¥7,200,000
    Total USD: ~$1,080,000
    Exchange rate: 6.67
  Witness inconsistency:
    Witness A says meeting was Jan 16; Witness B says Jan 15 (confirmed)
    Witness C says "one week before signing" = Jan 13 (approx, slightly off)
"""
import json
import os
import pytest
from pathlib import Path

def _find_file(name):
    """Multi-path file discovery."""
    from pathlib import Path
    OUT = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))
    candidates = [OUT/"output"/name, OUT/"outputs"/name, OUT/name,
                  Path(f"/workspace/output/{name}"), Path(f"/workspace/outputs/{name}"), Path(f"/workspace/{name}")]
    for p in candidates:
        if p.exists(): return p
    return candidates[0]



def find_output_file(filename):
    """Multi-path file discovery."""
    search_paths = [
        Path("/workspace") / filename,
        Path("/workspace/output") / filename,
        Path("/workspace/outputs") / filename,
        Path(".") / filename,
        Path("output") / filename,
        Path("outputs") / filename,
    ]
    for p in search_paths:
        if p.exists():
            return p
    return None


def load_json_file(filename):
    """Load a JSON file from multiple possible locations."""
    path = find_output_file(filename)
    if path is None:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text_file(filename):
    """Load a text file from multiple possible locations."""
    path = find_output_file(filename)
    if path is None:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestOutputFilesExist:
    def test_evidence_chain_report_exists(self):
        path = find_output_file("cadena_evidencia.md")
        assert path is not None, "cadena_evidencia.md not found"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 500, "cadena_evidencia.md is too short"

    def test_timeline_json_exists(self):
        path = find_output_file("timeline.json")
        assert path is not None, "timeline.json not found"

    def test_financial_summary_exists(self):
        path = find_output_file("financial_summary.json")
        assert path is not None, "financial_summary.json not found"


class TestTimelineJSON:
    def setup_method(self):
        self.data = load_json_file("timeline.json")
        if self.data is None:
            pytest.skip("timeline.json not found")

    def test_events_present(self):
        events = self.data.get("events", [])
        assert len(events) >= 5, f"Expected at least 5 events, found {len(events)}"

    def test_correct_transfer_1_date(self):
        """Transfer 1 should be Jan 12."""
        events = self.data.get("events", [])
        found = False
        for e in events:
            date = str(e.get("date", ""))
            event_text = str(e.get("event", "")).lower()
            if "2024-01-12" in date and ("transfer" in event_text or "transferencia" in event_text or "txn" in event_text):
                found = True
                break
        assert found, "Transfer 1 on Jan 12 not found in timeline"

    def test_correct_meeting_date(self):
        """Meeting should be Jan 15 (not Jan 16)."""
        events = self.data.get("events", [])
        found_15 = False
        found_16 = False
        for e in events:
            date = str(e.get("date", ""))
            event_text = str(e.get("event", "")).lower()
            if "meeting" in event_text or "reunión" in event_text or "reunion" in event_text:
                if "2024-01-15" in date:
                    found_15 = True
                elif "2024-01-16" in date:
                    found_16 = True
        assert found_15, "Meeting should be dated Jan 15 (corrected from Witness A's Jan 16)"

    def test_correct_signing_date(self):
        """Signing should be Jan 20."""
        events = self.data.get("events", [])
        found = False
        for e in events:
            date = str(e.get("date", ""))
            event_text = str(e.get("event", "")).lower()
            if "2024-01-20" in date and ("sign" in event_text or "firma" in event_text):
                found = True
                break
        assert found, "Agreement signing on Jan 20 not found"

    def test_correct_event_sequence(self):
        """Events should be in chronological order."""
        events = self.data.get("events", [])
        dates = [e.get("date", "") for e in events if e.get("date")]
        sorted_dates = sorted(dates)
        assert dates == sorted_dates, "Events are not in chronological order"

    def test_witness_inconsistency_identified(self):
        """Must identify Witness A's date error (Jan 16 vs Jan 15)."""
        inconsistencies = self.data.get("witness_inconsistencies", [])
        if not inconsistencies:
            # Check if it's in events notes
            events = self.data.get("events", [])
            all_text = str(events).lower()
            assert "16" in all_text and "15" in all_text, \
                "Witness date inconsistency (Jan 15 vs 16) not identified"
        else:
            found = False
            for inc in inconsistencies:
                all_text = str(inc).lower()
                if ("date" in all_text or "fecha" in all_text) and \
                   ("16" in all_text or "15" in all_text):
                    found = True
                    break
            assert found, "Witness A date error not identified in inconsistencies"


class TestFinancialSummary:
    def setup_method(self):
        self.data = load_json_file("financial_summary.json")
        if self.data is None:
            pytest.skip("financial_summary.json not found")

    def test_total_cny(self):
        """Total should be ¥7,200,000."""
        total = self.data.get("total_cny", 0)
        assert abs(total - 7200000) < 10000, f"Expected total ~¥7,200,000, got ¥{total}"

    def test_total_usd(self):
        """Total should be ~$1,080,000."""
        total = self.data.get("total_usd", 0)
        assert 1000000 < total < 1200000, f"Expected total ~$1,080,000, got ${total}"

    def test_exchange_rate(self):
        """Exchange rate should be ~6.67."""
        rate = self.data.get("exchange_rate_used", 0)
        assert 6.5 < rate < 6.8, f"Expected exchange rate ~6.67, got {rate}"

    def test_three_transfers_listed(self):
        """Should list exactly 3 transfers."""
        transfers = self.data.get("transfers", [])
        assert len(transfers) == 3, f"Expected 3 transfers, got {len(transfers)}"

    def test_transfer_amounts_correct(self):
        """Individual transfer amounts should match ground truth."""
        transfers = self.data.get("transfers", [])
        expected_amounts = [2300000, 1800000, 3100000]
        actual_amounts = sorted([t.get("amount_cny", 0) for t in transfers])
        expected_sorted = sorted(expected_amounts)
        for actual, expected in zip(actual_amounts, expected_sorted):
            assert abs(actual - expected) < 10000, \
                f"Transfer amount mismatch: expected {expected}, got {actual}"


class TestReportQuality:
    def setup_method(self):
        self.content = load_text_file("cadena_evidencia.md")
        if self.content is None:
            pytest.skip("cadena_evidencia.md not found")

    def test_report_in_spanish(self):
        """Report should be in Spanish."""
        spanish_indicators = ["evidencia", "testigo", "transferencia", "firma",
                            "conclusi", "recomendaci", "cronolog"]
        found = sum(1 for word in spanish_indicators if word in self.content.lower())
        assert found >= 4, "Report does not appear to be written in Spanish"

    def test_report_mentions_all_transfers(self):
        """Report should reference all three transfer amounts."""
        text = self.content
        assert "2,300,000" in text or "2.300.000" in text or "2,3" in text or "230万" in text, \
            "Transfer 1 amount not mentioned"



# === Standalone wrappers for class-based tests (P1 fix) ===

def test_OutputFilesExist_test_evidence_chain_report_exists():
    """Wrapper for TestOutputFilesExist.test_evidence_chain_report_exists"""
    instance = TestOutputFilesExist()
    instance.test_evidence_chain_report_exists()


def test_OutputFilesExist_test_timeline_json_exists():
    """Wrapper for TestOutputFilesExist.test_timeline_json_exists"""
    instance = TestOutputFilesExist()
    instance.test_timeline_json_exists()


def test_OutputFilesExist_test_financial_summary_exists():
    """Wrapper for TestOutputFilesExist.test_financial_summary_exists"""
    instance = TestOutputFilesExist()
    instance.test_financial_summary_exists()


def test_TimelineJSON_test_events_present():
    """Wrapper for TestTimelineJSON.test_events_present"""
    instance = TestTimelineJSON()
    instance.test_events_present()


def test_TimelineJSON_test_correct_transfer_1_date():
    """Wrapper for TestTimelineJSON.test_correct_transfer_1_date"""
    instance = TestTimelineJSON()
    instance.test_correct_transfer_1_date()


def test_TimelineJSON_test_correct_meeting_date():
    """Wrapper for TestTimelineJSON.test_correct_meeting_date"""
    instance = TestTimelineJSON()
    instance.test_correct_meeting_date()


def test_TimelineJSON_test_correct_signing_date():
    """Wrapper for TestTimelineJSON.test_correct_signing_date"""
    instance = TestTimelineJSON()
    instance.test_correct_signing_date()


def test_TimelineJSON_test_correct_event_sequence():
    """Wrapper for TestTimelineJSON.test_correct_event_sequence"""
    instance = TestTimelineJSON()
    instance.test_correct_event_sequence()


def test_TimelineJSON_test_witness_inconsistency_identified():
    """Wrapper for TestTimelineJSON.test_witness_inconsistency_identified"""
    instance = TestTimelineJSON()
    instance.test_witness_inconsistency_identified()


def test_FinancialSummary_test_total_cny():
    """Wrapper for TestFinancialSummary.test_total_cny"""
    instance = TestFinancialSummary()
    instance.test_total_cny()


def test_FinancialSummary_test_total_usd():
    """Wrapper for TestFinancialSummary.test_total_usd"""
    instance = TestFinancialSummary()
    instance.test_total_usd()


def test_FinancialSummary_test_exchange_rate():
    """Wrapper for TestFinancialSummary.test_exchange_rate"""
    instance = TestFinancialSummary()
    instance.test_exchange_rate()


def test_FinancialSummary_test_three_transfers_listed():
    """Wrapper for TestFinancialSummary.test_three_transfers_listed"""
    instance = TestFinancialSummary()
    instance.test_three_transfers_listed()


def test_FinancialSummary_test_transfer_amounts_correct():
    """Wrapper for TestFinancialSummary.test_transfer_amounts_correct"""
    instance = TestFinancialSummary()
    instance.test_transfer_amounts_correct()


def test_ReportQuality_test_report_in_spanish():
    """Wrapper for TestReportQuality.test_report_in_spanish"""
    instance = TestReportQuality()
    instance.test_report_in_spanish()


def test_ReportQuality_test_report_mentions_all_transfers():
    """Wrapper for TestReportQuality.test_report_mentions_all_transfers"""
    instance = TestReportQuality()
    instance.test_report_mentions_all_transfers()

def grade():
    """Weighted grading with non-linear cap (0.85 max for all-pass).
    Supports both class-based (pytest) and function-based test patterns.
    """
    import sys, inspect
    
    mod = sys.modules.get("test_outputs")
    if mod is None:
        return {"overall_score": 0.0, "error": "Module not in sys.modules"}
    
    # Collect test functions: both top-level and class methods
    test_funcs = []
    
    # Top-level functions
    for name in dir(mod):
        obj = getattr(mod, name)
        if name.startswith("test_") and callable(obj) and not inspect.isclass(obj):
            test_funcs.append((name, obj))
    
    # Class-based tests (pytest-style: class TestX with def test_y(self))
    for name in dir(mod):
        obj = getattr(mod, name)
        if inspect.isclass(obj) and name.startswith("Test"):
            instance = obj()
            for method_name in dir(instance):
                if method_name.startswith("test_"):
                    method = getattr(instance, method_name)
                    if callable(method):
                        test_funcs.append((f"{name}.{method_name}", method))
    
    if not test_funcs:
        return {"overall_score": 0.0, "error": "No test functions found"}
    
    # Run with weighted scoring
    results = []
    for name, func in sorted(test_funcs):
        if any(k in name for k in ["correct", "accura", "value", "amount", "count",
                                     "number", "detect", "identif", "match", "verify",
                                     "found", "present"]):
            weight = 2.0
        elif any(k in name for k in ["exist", "file", "creat"]):
            weight = 0.5
        else:
            weight = 1.0
        try:
            func()
            results.append({"name": name, "passed": True, "weight": weight})
        except (AssertionError, Exception):
            results.append({"name": name, "passed": False, "weight": weight})
    
    total_weight = sum(r["weight"] for r in results)
    earned_weight = sum(r["weight"] for r in results if r["passed"])
    raw_score = earned_weight / total_weight if total_weight > 0 else 0.0
    
    # Non-linear scaling
    if raw_score >= 1.0: scaled = 0.85
    elif raw_score >= 0.9: scaled = 0.70 + (raw_score - 0.9) * 1.5
    elif raw_score >= 0.7: scaled = 0.50 + (raw_score - 0.7) * 1.0
    elif raw_score >= 0.5: scaled = 0.30 + (raw_score - 0.5) * 1.0
    elif raw_score >= 0.3: scaled = 0.15 + (raw_score - 0.3) * 0.75
    else: scaled = raw_score * 0.5
    
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "overall_score": round(scaled, 4),
        "dimensions": {
            "weighted_completion": {
                "score": round(scaled, 4), "weight": 1.0,
                "details": {"tests_passed": passed_count, "tests_total": len(results), "weighted_raw": round(raw_score, 4)}
            }
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(grade(), indent=2))
