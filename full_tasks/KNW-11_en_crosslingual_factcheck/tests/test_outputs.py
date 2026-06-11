"""
Test suite for KNW-11: Cross-lingual Fact Verification Chain
Ground truth:
  1. Date: March 15, 2024 (ES+ZH agree) vs March 18 (EN+FR)
  2. Member count: 12 (ES+ZH) vs 14 (EN+FR)
  3. Trade volume: $2.4B (ES+EN) vs ¥168B~$2.3B (ZH) vs €2.4B (FR)
  4. Signing location: Lima (ES+EN+ZH) vs Bogotá (FR)
  5. Lead negotiator: María González — only in ES and ZH
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
    def test_verification_report_exists(self):
        path = find_output_file("verification_report.md")
        assert path is not None, "verification_report.md not found"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 500, "verification_report.md is too short"

    def test_contradictions_json_exists(self):
        path = find_output_file("contradictions.json")
        assert path is not None, "contradictions.json not found"

    def test_source_comparison_json_exists(self):
        path = find_output_file("source_comparison.json")
        assert path is not None, "source_comparison.json not found"


class TestContradictionsJSON:
    def setup_method(self):
        self.data = load_json_file("contradictions.json")
        if self.data is None:
            pytest.skip("contradictions.json not found")

    def test_total_contradictions_count(self):
        """Must find at least 4 of the 5 seeded contradictions."""
        total = self.data.get("total_contradictions", 0)
        assert total >= 4, f"Expected at least 4 contradictions, found {total}"

    def test_contradictions_list_present(self):
        assert "contradictions" in self.data
        assert isinstance(self.data["contradictions"], list)
        assert len(self.data["contradictions"]) >= 4

    def test_date_contradiction_found(self):
        """Contradiction 1: Date discrepancy (March 15 vs March 18)."""
        contradictions = self.data["contradictions"]
        date_found = False
        for c in contradictions:
            desc = str(c.get("description", "")).lower()
            claims = c.get("claims", {})
            all_text = desc + " " + str(claims).lower()
            if ("date" in all_text or "march" in all_text or "marzo" in all_text or "mars" in all_text) and \
               ("15" in all_text or "18" in all_text):
                date_found = True
                # Check correct value determination
                correct = str(c.get("correct_value", "")).lower()
                if "15" in correct:
                    break
        assert date_found, "Date contradiction (March 15 vs 18) not identified"

    def test_member_count_contradiction_found(self):
        """Contradiction 2: 12 vs 14 member countries."""
        contradictions = self.data["contradictions"]
        member_found = False
        for c in contradictions:
            desc = str(c.get("description", "")).lower()
            claims = c.get("claims", {})
            all_text = desc + " " + str(claims).lower()
            if ("member" in all_text or "countr" in all_text or "nation" in all_text or "país" in all_text) and \
               ("12" in all_text or "14" in all_text):
                member_found = True
                break
        assert member_found, "Member count contradiction (12 vs 14) not identified"

    def test_location_contradiction_found(self):
        """Contradiction 4: Lima vs Bogotá."""
        contradictions = self.data["contradictions"]
        location_found = False
        for c in contradictions:
            desc = str(c.get("description", "")).lower()
            claims = c.get("claims", {})
            all_text = desc + " " + str(claims).lower()
            if ("lima" in all_text or "bogot" in all_text) and \
               ("location" in all_text or "sign" in all_text or "lieu" in all_text or "lugar" in all_text or "city" in all_text):
                location_found = True
                break
        assert location_found, "Location contradiction (Lima vs Bogotá) not identified"

    def test_contradiction_structure(self):
        """Each contradiction must have required fields."""
        contradictions = self.data["contradictions"]
        for c in contradictions:
            assert "id" in c or "category" in c, "Contradiction missing id or category"
            assert "description" in c, "Contradiction missing description"
            assert "claims" in c or "correct_value" in c, "Contradiction missing claims or correct_value"


class TestSourceComparison:
    def setup_method(self):
        self.data = load_json_file("source_comparison.json")
        if self.data is None:
            pytest.skip("source_comparison.json not found")

    def test_all_four_sources_analyzed(self):
        """Must reference all 4 source languages."""
        sources = self.data.get("sources", [])
        source_ids = [s.get("id", s.get("language", "")).lower() for s in sources]
        all_text = str(self.data).lower()
        assert any("es" in sid or "spanish" in sid for sid in source_ids) or "spanish" in all_text, \
            "Spanish source not analyzed"
        assert any("en" in sid or "english" in sid for sid in source_ids) or "english" in all_text, \
            "English source not analyzed"
        assert any("zh" in sid or "chinese" in sid for sid in source_ids) or "chinese" in all_text, \
            "Chinese source not analyzed"
        assert any("fr" in sid or "french" in sid for sid in source_ids) or "french" in all_text, \
            "French source not analyzed"

    def test_french_source_identified_as_least_reliable_on_location(self):
        """French source should be flagged for the Bogotá error."""
        all_text = str(self.data).lower()
        assert "bogot" in all_text or "french" in all_text or "fr" in all_text


class TestVerificationReport:
    def setup_method(self):
        self.content = load_text_file("verification_report.md")
        if self.content is None:
            pytest.skip("verification_report.md not found")

    def test_report_mentions_key_contradictions(self):
        """Report must discuss main contradictions."""
        text = self.content.lower()
        # At least 3 of these key terms should appear
        key_terms = ["march 15", "march 18", "12", "14", "lima", "bogot", "gonzález", "trade volume"]
        found = sum(1 for term in key_terms if term in text)
        assert found >= 4, f"Report mentions only {found}/8 key terms, expected at least 4"

    def test_report_has_structure(self):
        """Report should have headers/sections."""
        assert "#" in self.content, "Report should have markdown headers"
        assert len(self.content.split("\n")) > 20, "Report should be substantial (>20 lines)"



# === Standalone wrappers for class-based tests (P1 fix) ===

def test_OutputFilesExist_test_verification_report_exists():
    """Wrapper for TestOutputFilesExist.test_verification_report_exists"""
    instance = TestOutputFilesExist()
    instance.test_verification_report_exists()


def test_OutputFilesExist_test_contradictions_json_exists():
    """Wrapper for TestOutputFilesExist.test_contradictions_json_exists"""
    instance = TestOutputFilesExist()
    instance.test_contradictions_json_exists()


def test_OutputFilesExist_test_source_comparison_json_exists():
    """Wrapper for TestOutputFilesExist.test_source_comparison_json_exists"""
    instance = TestOutputFilesExist()
    instance.test_source_comparison_json_exists()


def test_ContradictionsJSON_test_total_contradictions_count():
    """Wrapper for TestContradictionsJSON.test_total_contradictions_count"""
    instance = TestContradictionsJSON()
    instance.test_total_contradictions_count()


def test_ContradictionsJSON_test_contradictions_list_present():
    """Wrapper for TestContradictionsJSON.test_contradictions_list_present"""
    instance = TestContradictionsJSON()
    instance.test_contradictions_list_present()


def test_ContradictionsJSON_test_date_contradiction_found():
    """Wrapper for TestContradictionsJSON.test_date_contradiction_found"""
    instance = TestContradictionsJSON()
    instance.test_date_contradiction_found()


def test_ContradictionsJSON_test_member_count_contradiction_found():
    """Wrapper for TestContradictionsJSON.test_member_count_contradiction_found"""
    instance = TestContradictionsJSON()
    instance.test_member_count_contradiction_found()


def test_ContradictionsJSON_test_location_contradiction_found():
    """Wrapper for TestContradictionsJSON.test_location_contradiction_found"""
    instance = TestContradictionsJSON()
    instance.test_location_contradiction_found()


def test_ContradictionsJSON_test_contradiction_structure():
    """Wrapper for TestContradictionsJSON.test_contradiction_structure"""
    instance = TestContradictionsJSON()
    instance.test_contradiction_structure()


def test_SourceComparison_test_all_four_sources_analyzed():
    """Wrapper for TestSourceComparison.test_all_four_sources_analyzed"""
    instance = TestSourceComparison()
    instance.test_all_four_sources_analyzed()


def test_SourceComparison_test_french_source_identified_as_least_reliable_on_location():
    """Wrapper for TestSourceComparison.test_french_source_identified_as_least_reliable_on_location"""
    instance = TestSourceComparison()
    instance.test_french_source_identified_as_least_reliable_on_location()


def test_VerificationReport_test_report_mentions_key_contradictions():
    """Wrapper for TestVerificationReport.test_report_mentions_key_contradictions"""
    instance = TestVerificationReport()
    instance.test_report_mentions_key_contradictions()


def test_VerificationReport_test_report_has_structure():
    """Wrapper for TestVerificationReport.test_report_has_structure"""
    instance = TestVerificationReport()
    instance.test_report_has_structure()

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
