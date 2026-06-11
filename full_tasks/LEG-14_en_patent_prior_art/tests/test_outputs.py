"""
Test suite for LEG-14: Patent Prior Art Analysis
Ground truth claim mapping:
  Claim 1: Anticipated by Prior Art Paper 1, Section 3.2 (silicone + BN/Al2O3/AlN, 30-70wt%, 5+ W/mK)
  Claim 2: NOVEL (microcapsule self-healing specific to TIM with performance retention)
  Claim 3: Anticipated by DIN 12345 §4.1 (identical measurement method)
  Claim 4: Anticipated by Prior Art Paper 2, Figure 4 (DA-based PU interlayer)
  Claim 5: NOVEL (specific 5-layer architecture with graded fillers)
  Claim 6: Anticipated by Paper 1 §5.1 (oriented BN) + Paper 3 Abstract (through-thickness)
  Claim 7: Anticipated by DIN 12345 §6.2 (self-healing test method)
  Claim 8: Anticipated by Prior Art Paper 3, Section 2 (chitin-templated BN)
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
    def test_prior_art_report_exists(self):
        path = find_output_file("prior_art_report.md")
        assert path is not None, "prior_art_report.md not found"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 500, "prior_art_report.md is too short"

    def test_claim_mapping_json_exists(self):
        path = find_output_file("claim_mapping.json")
        assert path is not None, "claim_mapping.json not found"

    def test_novelty_assessment_json_exists(self):
        path = find_output_file("novelty_assessment.json")
        assert path is not None, "novelty_assessment.json not found"


class TestClaimMapping:
    def setup_method(self):
        self.data = load_json_file("claim_mapping.json")
        if self.data is None:
            pytest.skip("claim_mapping.json not found")

    def test_total_claims_is_8(self):
        total = self.data.get("total_claims", 0)
        assert total == 8, f"Expected 8 total claims, got {total}"

    def test_novel_claims_identified(self):
        """Claims 2 and 5 should be identified as novel."""
        novel = self.data.get("novel_claims", [])
        assert 2 in novel, "Claim 2 should be identified as novel"
        assert 5 in novel, "Claim 5 should be identified as novel"

    def test_anticipated_claims_identified(self):
        """Claims 1, 3, 4, 6, 7, 8 should be anticipated."""
        anticipated = self.data.get("anticipated_claims", [])
        for claim_num in [1, 3, 4, 6, 7, 8]:
            assert claim_num in anticipated, f"Claim {claim_num} should be anticipated"

    def test_claim_1_mapping(self):
        """Claim 1 → Prior Art Paper 1, Section 3.2."""
        mappings = self.data.get("mappings", [])
        claim_1 = next((m for m in mappings if m.get("claim_number") == 1), None)
        assert claim_1 is not None, "Claim 1 mapping not found"
        refs = claim_1.get("prior_art_references", [])
        assert len(refs) > 0, "Claim 1 should have prior art references"
        all_text = str(refs).lower()
        assert "paper 1" in all_text or "paper_1" in all_text or "thompson" in all_text or \
               "filler" in all_text or "3.2" in all_text, \
            "Claim 1 should reference Paper 1 Section 3.2"

    def test_claim_3_mapping(self):
        """Claim 3 → DIN 12345 §4.1."""
        mappings = self.data.get("mappings", [])
        claim_3 = next((m for m in mappings if m.get("claim_number") == 3), None)
        assert claim_3 is not None, "Claim 3 mapping not found"
        refs = claim_3.get("prior_art_references", [])
        all_text = str(refs).lower()
        assert "din" in all_text or "12345" in all_text or "standard" in all_text, \
            "Claim 3 should reference DIN 12345"

    def test_claim_4_mapping(self):
        """Claim 4 → Prior Art Paper 2, Figure 4."""
        mappings = self.data.get("mappings", [])
        claim_4 = next((m for m in mappings if m.get("claim_number") == 4), None)
        assert claim_4 is not None, "Claim 4 mapping not found"
        refs = claim_4.get("prior_art_references", [])
        all_text = str(refs).lower()
        assert "paper 2" in all_text or "paper_2" in all_text or "rodriguez" in all_text or \
               "self-healing" in all_text or "figure 4" in all_text or "fig" in all_text, \
            "Claim 4 should reference Paper 2"

    def test_claim_8_mapping(self):
        """Claim 8 → Prior Art Paper 3, Section 2."""
        mappings = self.data.get("mappings", [])
        claim_8 = next((m for m in mappings if m.get("claim_number") == 8), None)
        assert claim_8 is not None, "Claim 8 mapping not found"
        refs = claim_8.get("prior_art_references", [])
        all_text = str(refs).lower()
        assert "paper 3" in all_text or "paper_3" in all_text or "tanaka" in all_text or \
               "bio" in all_text or "chitin" in all_text or "section 2" in all_text, \
            "Claim 8 should reference Paper 3 Section 2"

    def test_mappings_have_structure(self):
        """All mappings should have required fields."""
        mappings = self.data.get("mappings", [])
        assert len(mappings) == 8, f"Expected 8 mappings, got {len(mappings)}"
        for m in mappings:
            assert "claim_number" in m, "Mapping missing claim_number"
            assert "status" in m, "Mapping missing status"


class TestNoveltyAssessment:
    def setup_method(self):
        self.data = load_json_file("novelty_assessment.json")
        if self.data is None:
            pytest.skip("novelty_assessment.json not found")

    def test_novel_claim_count(self):
        """Should have exactly 2 novel claims."""
        count = self.data.get("novel_claim_count", 0)
        assert count == 2, f"Expected 2 novel claims, got {count}"

    def test_anticipated_claim_count(self):
        """Should have 6 anticipated claims."""
        count = self.data.get("anticipated_claim_count", 0)
        assert count == 6, f"Expected 6 anticipated claims, got {count}"

    def test_novel_claims_are_2_and_5(self):
        """Novel claims should be 2 and 5."""
        novel = self.data.get("novel_claims", [])
        assert sorted(novel) == [2, 5], f"Expected novel claims [2, 5], got {sorted(novel)}"

    def test_overall_novelty_assessment(self):
        """Overall novelty should be low or medium (only 2/8 claims novel)."""
        novelty = self.data.get("overall_novelty", "").lower()
        assert novelty in ["low", "medium"], f"Expected low/medium overall novelty, got {novelty}"


class TestReportQuality:
    def setup_method(self):
        self.content = load_text_file("prior_art_report.md")
        if self.content is None:
            pytest.skip("prior_art_report.md not found")

    def test_report_discusses_all_claims(self):
        """Report should discuss all 8 claims."""
        for i in range(1, 9):
            assert f"claim {i}" in self.content.lower() or f"claim{i}" in self.content.lower() or \
                   f"#{i}" in self.content or f"no. {i}" in self.content.lower() or \
                   f"number {i}" in self.content.lower(), \
                f"Report should discuss claim {i}"

    def test_report_references_prior_art(self):
        """Report should reference the prior art documents."""
        text = self.content.lower()
        assert "din" in text or "12345" in text, "Report should reference DIN standard"
        assert "paper" in text or "thompson" in text or "rodriguez" in text or "tanaka" in text, \
            "Report should reference prior art papers"



# === Standalone wrappers for class-based tests (P1 fix) ===

def test_OutputFilesExist_test_prior_art_report_exists():
    """Wrapper for TestOutputFilesExist.test_prior_art_report_exists"""
    instance = TestOutputFilesExist()
    instance.test_prior_art_report_exists()


def test_OutputFilesExist_test_claim_mapping_json_exists():
    """Wrapper for TestOutputFilesExist.test_claim_mapping_json_exists"""
    instance = TestOutputFilesExist()
    instance.test_claim_mapping_json_exists()


def test_OutputFilesExist_test_novelty_assessment_json_exists():
    """Wrapper for TestOutputFilesExist.test_novelty_assessment_json_exists"""
    instance = TestOutputFilesExist()
    instance.test_novelty_assessment_json_exists()


def test_ClaimMapping_test_total_claims_is_8():
    """Wrapper for TestClaimMapping.test_total_claims_is_8"""
    instance = TestClaimMapping()
    instance.test_total_claims_is_8()


def test_ClaimMapping_test_novel_claims_identified():
    """Wrapper for TestClaimMapping.test_novel_claims_identified"""
    instance = TestClaimMapping()
    instance.test_novel_claims_identified()


def test_ClaimMapping_test_anticipated_claims_identified():
    """Wrapper for TestClaimMapping.test_anticipated_claims_identified"""
    instance = TestClaimMapping()
    instance.test_anticipated_claims_identified()


def test_ClaimMapping_test_claim_1_mapping():
    """Wrapper for TestClaimMapping.test_claim_1_mapping"""
    instance = TestClaimMapping()
    instance.test_claim_1_mapping()


def test_ClaimMapping_test_claim_3_mapping():
    """Wrapper for TestClaimMapping.test_claim_3_mapping"""
    instance = TestClaimMapping()
    instance.test_claim_3_mapping()


def test_ClaimMapping_test_claim_4_mapping():
    """Wrapper for TestClaimMapping.test_claim_4_mapping"""
    instance = TestClaimMapping()
    instance.test_claim_4_mapping()


def test_ClaimMapping_test_claim_8_mapping():
    """Wrapper for TestClaimMapping.test_claim_8_mapping"""
    instance = TestClaimMapping()
    instance.test_claim_8_mapping()


def test_ClaimMapping_test_mappings_have_structure():
    """Wrapper for TestClaimMapping.test_mappings_have_structure"""
    instance = TestClaimMapping()
    instance.test_mappings_have_structure()


def test_NoveltyAssessment_test_novel_claim_count():
    """Wrapper for TestNoveltyAssessment.test_novel_claim_count"""
    instance = TestNoveltyAssessment()
    instance.test_novel_claim_count()


def test_NoveltyAssessment_test_anticipated_claim_count():
    """Wrapper for TestNoveltyAssessment.test_anticipated_claim_count"""
    instance = TestNoveltyAssessment()
    instance.test_anticipated_claim_count()


def test_NoveltyAssessment_test_novel_claims_are_2_and_5():
    """Wrapper for TestNoveltyAssessment.test_novel_claims_are_2_and_5"""
    instance = TestNoveltyAssessment()
    instance.test_novel_claims_are_2_and_5()


def test_NoveltyAssessment_test_overall_novelty_assessment():
    """Wrapper for TestNoveltyAssessment.test_overall_novelty_assessment"""
    instance = TestNoveltyAssessment()
    instance.test_overall_novelty_assessment()


def test_ReportQuality_test_report_discusses_all_claims():
    """Wrapper for TestReportQuality.test_report_discusses_all_claims"""
    instance = TestReportQuality()
    instance.test_report_discusses_all_claims()


def test_ReportQuality_test_report_references_prior_art():
    """Wrapper for TestReportQuality.test_report_references_prior_art"""
    instance = TestReportQuality()
    instance.test_report_references_prior_art()

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
