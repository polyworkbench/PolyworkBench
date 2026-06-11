"""
Test suite for LEG-12: German Contract Conflict Analysis
Ground truth conflicts:
  1. Payment terms: Master §3(2) "30 Tage netto" vs Amendment 2 "net 45 days"
  2. Liability cap: Master §7(2) "€500,000" vs Amendment 3 "$750,000" (currency mismatch)
  3. Jurisdiction: Master §10(2) "Landgericht München I" vs Amendment 1 "LCIA London"
  4. Termination notice: Master §8(1) "6 Monate" vs Amendment 2 "90 days"
  5. IP ownership: Master §12(1) "Auftragnehmer" vs Amendment 3 §4 "jointly owned"
  6. Force majeure: Master §9(2) includes "Pandemie" vs Amendment 1 §2.3 excludes it
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
    def test_konfliktanalyse_exists(self):
        path = find_output_file("konfliktanalyse.md")
        assert path is not None, "konfliktanalyse.md not found"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 500, "konfliktanalyse.md is too short"

    def test_conflicts_json_exists(self):
        path = find_output_file("conflicts.json")
        assert path is not None, "conflicts.json not found"

    def test_resolution_matrix_exists(self):
        path = find_output_file("resolution_matrix.json")
        assert path is not None, "resolution_matrix.json not found"


class TestConflictsJSON:
    def setup_method(self):
        self.data = load_json_file("conflicts.json")
        if self.data is None:
            pytest.skip("conflicts.json not found")

    def test_total_conflicts_count(self):
        """Must find at least 5 of the 6 seeded conflicts."""
        total = self.data.get("total_conflicts", 0)
        assert total >= 5, f"Expected at least 5 conflicts, found {total}"

    def test_conflicts_list_structure(self):
        conflicts = self.data.get("conflicts", [])
        assert len(conflicts) >= 5, f"Expected at least 5 conflict entries"

    def test_payment_terms_conflict(self):
        """Conflict 1: 30 days vs 45 days."""
        conflicts = self.data.get("conflicts", [])
        found = False
        for c in conflicts:
            all_text = str(c).lower()
            if ("payment" in all_text or "zahlung" in all_text or "invoice" in all_text) and \
               ("30" in all_text or "45" in all_text):
                found = True
                break
        assert found, "Payment terms conflict (30 days vs 45 days) not identified"

    def test_liability_cap_conflict(self):
        """Conflict 2: €500,000 vs $750,000."""
        conflicts = self.data.get("conflicts", [])
        found = False
        for c in conflicts:
            all_text = str(c).lower()
            if ("liab" in all_text or "haftung" in all_text) and \
               ("500" in all_text or "750" in all_text):
                found = True
                break
        assert found, "Liability cap conflict (€500k vs $750k) not identified"

    def test_jurisdiction_conflict(self):
        """Conflict 3: Landgericht München vs LCIA."""
        conflicts = self.data.get("conflicts", [])
        found = False
        for c in conflicts:
            all_text = str(c).lower()
            if ("jurisdic" in all_text or "gerichtsstand" in all_text or "dispute" in all_text or
                "arbitr" in all_text) and \
               ("münchen" in all_text or "munich" in all_text or "lcia" in all_text or "london" in all_text):
                found = True
                break
        assert found, "Jurisdiction conflict (München vs LCIA) not identified"

    def test_termination_notice_conflict(self):
        """Conflict 4: 6 months vs 90 days."""
        conflicts = self.data.get("conflicts", [])
        found = False
        for c in conflicts:
            all_text = str(c).lower()
            if ("terminat" in all_text or "kündig" in all_text) and \
               ("6" in all_text or "90" in all_text or "month" in all_text or "monat" in all_text):
                found = True
                break
        assert found, "Termination notice conflict (6 months vs 90 days) not identified"

    def test_ip_ownership_conflict(self):
        """Conflict 5: Auftragnehmer vs jointly owned."""
        conflicts = self.data.get("conflicts", [])
        found = False
        for c in conflicts:
            all_text = str(c).lower()
            if ("ip" in all_text or "intellect" in all_text or "eigentum" in all_text or "ownership" in all_text) and \
               ("joint" in all_text or "auftragnehmer" in all_text or "contractor" in all_text):
                found = True
                break
        assert found, "IP ownership conflict (Auftragnehmer vs jointly owned) not identified"

    def test_force_majeure_conflict(self):
        """Conflict 6: Pandemie included vs excluded."""
        conflicts = self.data.get("conflicts", [])
        found = False
        for c in conflicts:
            all_text = str(c).lower()
            if ("force majeure" in all_text or "höhere gewalt" in all_text) and \
               ("pandemic" in all_text or "pandemie" in all_text):
                found = True
                break
        assert found, "Force majeure conflict (pandemic included vs excluded) not identified"

    def test_clause_references_present(self):
        """Each conflict should reference specific clauses."""
        conflicts = self.data.get("conflicts", [])
        refs_found = 0
        for c in conflicts:
            master_clause = str(c.get("master_clause", ""))
            amendment_clause = str(c.get("amendment_clause", ""))
            if ("§" in master_clause or "section" in master_clause.lower()) and \
               (amendment_clause != ""):
                refs_found += 1
        assert refs_found >= 4, f"Expected at least 4 conflicts with clause refs, found {refs_found}"


class TestResolutionMatrix:
    def setup_method(self):
        self.data = load_json_file("resolution_matrix.json")
        if self.data is None:
            pytest.skip("resolution_matrix.json not found")

    def test_priority_ranking_exists(self):
        ranking = self.data.get("priority_ranking", [])
        assert len(ranking) >= 4, "Priority ranking should have at least 4 entries"

    def test_recommended_actions_present(self):
        actions = self.data.get("recommended_actions", [])
        assert len(actions) >= 4, "Should have at least 4 recommended actions"


class TestReportQuality:
    def setup_method(self):
        self.content = load_text_file("konfliktanalyse.md")
        if self.content is None:
            pytest.skip("konfliktanalyse.md not found")

    def test_report_in_german(self):
        """Report should be in German."""
        german_indicators = ["und", "der", "die", "das", "ist", "werden", "Vertrag",
                           "Konflikt", "Analyse", "Empfehlung"]
        found = sum(1 for word in german_indicators if word in self.content)
        assert found >= 5, "Report does not appear to be written in German"

    def test_report_references_paragraphs(self):
        """Report should reference § numbers."""
        assert "§" in self.content, "Report should reference paragraph numbers (§)"



# === Standalone wrappers for class-based tests (P1 fix) ===

def test_OutputFilesExist_test_konfliktanalyse_exists():
    """Wrapper for TestOutputFilesExist.test_konfliktanalyse_exists"""
    instance = TestOutputFilesExist()
    instance.test_konfliktanalyse_exists()


def test_OutputFilesExist_test_conflicts_json_exists():
    """Wrapper for TestOutputFilesExist.test_conflicts_json_exists"""
    instance = TestOutputFilesExist()
    instance.test_conflicts_json_exists()


def test_OutputFilesExist_test_resolution_matrix_exists():
    """Wrapper for TestOutputFilesExist.test_resolution_matrix_exists"""
    instance = TestOutputFilesExist()
    instance.test_resolution_matrix_exists()


def test_ConflictsJSON_test_total_conflicts_count():
    """Wrapper for TestConflictsJSON.test_total_conflicts_count"""
    instance = TestConflictsJSON()
    instance.test_total_conflicts_count()


def test_ConflictsJSON_test_conflicts_list_structure():
    """Wrapper for TestConflictsJSON.test_conflicts_list_structure"""
    instance = TestConflictsJSON()
    instance.test_conflicts_list_structure()


def test_ConflictsJSON_test_payment_terms_conflict():
    """Wrapper for TestConflictsJSON.test_payment_terms_conflict"""
    instance = TestConflictsJSON()
    instance.test_payment_terms_conflict()


def test_ConflictsJSON_test_liability_cap_conflict():
    """Wrapper for TestConflictsJSON.test_liability_cap_conflict"""
    instance = TestConflictsJSON()
    instance.test_liability_cap_conflict()


def test_ConflictsJSON_test_jurisdiction_conflict():
    """Wrapper for TestConflictsJSON.test_jurisdiction_conflict"""
    instance = TestConflictsJSON()
    instance.test_jurisdiction_conflict()


def test_ConflictsJSON_test_termination_notice_conflict():
    """Wrapper for TestConflictsJSON.test_termination_notice_conflict"""
    instance = TestConflictsJSON()
    instance.test_termination_notice_conflict()


def test_ConflictsJSON_test_ip_ownership_conflict():
    """Wrapper for TestConflictsJSON.test_ip_ownership_conflict"""
    instance = TestConflictsJSON()
    instance.test_ip_ownership_conflict()


def test_ConflictsJSON_test_force_majeure_conflict():
    """Wrapper for TestConflictsJSON.test_force_majeure_conflict"""
    instance = TestConflictsJSON()
    instance.test_force_majeure_conflict()


def test_ConflictsJSON_test_clause_references_present():
    """Wrapper for TestConflictsJSON.test_clause_references_present"""
    instance = TestConflictsJSON()
    instance.test_clause_references_present()


def test_ResolutionMatrix_test_priority_ranking_exists():
    """Wrapper for TestResolutionMatrix.test_priority_ranking_exists"""
    instance = TestResolutionMatrix()
    instance.test_priority_ranking_exists()


def test_ResolutionMatrix_test_recommended_actions_present():
    """Wrapper for TestResolutionMatrix.test_recommended_actions_present"""
    instance = TestResolutionMatrix()
    instance.test_recommended_actions_present()


def test_ReportQuality_test_report_in_german():
    """Wrapper for TestReportQuality.test_report_in_german"""
    instance = TestReportQuality()
    instance.test_report_in_german()


def test_ReportQuality_test_report_references_paragraphs():
    """Wrapper for TestReportQuality.test_report_references_paragraphs"""
    instance = TestReportQuality()
    instance.test_report_references_paragraphs()

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
