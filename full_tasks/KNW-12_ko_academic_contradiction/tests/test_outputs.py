"""
Test suite for KNW-12: Korean-instruction Academic Paper Contradiction Analysis
Ground truth contradictions:
  1. Cycle life: KR=800 cycles, JA=1200 cycles, EN=800-1000 (NMC811)
  2. Optimal temperature: KR=25°C, JA=20-25°C, EN=15-25°C
  3. Charging rate: KR=>2C causes 40% acceleration, JA=>3C causes 40%, EN=>2C causes 30%
  4. Cathode recommendation: KR=NMC811, JA=LFP, EN=application-dependent
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
    def test_contradiction_report_exists(self):
        path = find_output_file("contradiction_report_ko.md")
        assert path is not None, "contradiction_report_ko.md not found"
        content = path.read_text(encoding="utf-8")
        assert len(content) > 500, "Report is too short"

    def test_citations_json_exists(self):
        path = find_output_file("citations.json")
        assert path is not None, "citations.json not found"

    def test_analysis_summary_exists(self):
        path = find_output_file("analysis_summary.json")
        assert path is not None, "analysis_summary.json not found"


class TestCitationsJSON:
    def setup_method(self):
        self.data = load_json_file("citations.json")
        if self.data is None:
            pytest.skip("citations.json not found")

    def test_contradiction_count(self):
        """Must find at least 3 of the 4 seeded contradictions."""
        contradictions = self.data.get("contradictions", [])
        assert len(contradictions) >= 3, f"Expected at least 3, found {len(contradictions)}"

    def test_cycle_life_contradiction(self):
        """Contradiction 1: KR=800, JA=1200, EN=800-1000."""
        contradictions = self.data.get("contradictions", [])
        found = False
        for c in contradictions:
            all_text = str(c).lower()
            if ("cycle" in all_text or "사이클" in all_text or "サイクル" in all_text) and \
               ("800" in all_text or "1200" in all_text):
                found = True
                break
        assert found, "Cycle life contradiction (800 vs 1200) not identified"

    def test_temperature_contradiction(self):
        """Contradiction 2: KR=25°C, JA=20-25°C, EN=15-25°C."""
        contradictions = self.data.get("contradictions", [])
        found = False
        for c in contradictions:
            all_text = str(c).lower()
            if ("temp" in all_text or "온도" in all_text or "温度" in all_text) and \
               ("25" in all_text or "20" in all_text or "15" in all_text):
                found = True
                break
        assert found, "Temperature contradiction not identified"

    def test_charging_rate_contradiction(self):
        """Contradiction 3: KR=>2C/40%, JA=>3C/40%, EN=>2C/30%."""
        contradictions = self.data.get("contradictions", [])
        found = False
        for c in contradictions:
            all_text = str(c).lower()
            if ("rate" in all_text or "charging" in all_text or "충전" in all_text or
                "充電" in all_text or "c-rate" in all_text or "2c" in all_text or "3c" in all_text):
                if ("30" in all_text or "40" in all_text):
                    found = True
                    break
        assert found, "Charging rate contradiction (2C/40% vs 3C vs 2C/30%) not identified"

    def test_cathode_recommendation_contradiction(self):
        """Contradiction 4: KR=NMC811, JA=LFP, EN=depends."""
        contradictions = self.data.get("contradictions", [])
        found = False
        for c in contradictions:
            all_text = str(c).lower()
            if ("cathode" in all_text or "양극" in all_text or "正極" in all_text or
                "material" in all_text or "nmc" in all_text or "lfp" in all_text):
                found = True
                break
        assert found, "Cathode material recommendation contradiction not identified"

    def test_citations_have_sections(self):
        """Each citation must reference specific sections."""
        contradictions = self.data.get("contradictions", [])
        for c in contradictions:
            papers = [c.get("korean_paper", {}), c.get("japanese_paper", {}), c.get("english_paper", {})]
            for paper in papers:
                if paper:
                    section = paper.get("section", "")
                    assert section != "", f"Missing section reference in contradiction {c.get('id', '?')}"


class TestAnalysisSummary:
    def setup_method(self):
        self.data = load_json_file("analysis_summary.json")
        if self.data is None:
            pytest.skip("analysis_summary.json not found")

    def test_total_contradictions_field(self):
        total = self.data.get("total_contradictions", 0)
        assert total >= 3, f"Expected at least 3 contradictions in summary, got {total}"

    def test_papers_analyzed_count(self):
        papers = self.data.get("papers_analyzed", 0)
        assert papers == 3, f"Expected 3 papers analyzed, got {papers}"


class TestReportQuality:
    def setup_method(self):
        self.content = load_text_file("contradiction_report_ko.md")
        if self.content is None:
            pytest.skip("contradiction_report_ko.md not found")

    def test_report_in_korean(self):
        """Report should contain Korean characters."""
        korean_chars = sum(1 for c in self.content if '가' <= c <= '힯')
        assert korean_chars > 100, "Report does not appear to be written in Korean"

    def test_report_mentions_key_values(self):
        """Report should mention the key contradictory values."""
        text = self.content
        key_values = ["800", "1200", "25", "NMC811", "LFP", "2C", "3C", "30%", "40%"]
        found = sum(1 for v in key_values if v in text)
        assert found >= 5, f"Report mentions only {found}/9 key values"



# === Standalone wrappers for class-based tests (P1 fix) ===

def test_OutputFilesExist_test_contradiction_report_exists():
    """Wrapper for TestOutputFilesExist.test_contradiction_report_exists"""
    instance = TestOutputFilesExist()
    instance.test_contradiction_report_exists()


def test_OutputFilesExist_test_citations_json_exists():
    """Wrapper for TestOutputFilesExist.test_citations_json_exists"""
    instance = TestOutputFilesExist()
    instance.test_citations_json_exists()


def test_OutputFilesExist_test_analysis_summary_exists():
    """Wrapper for TestOutputFilesExist.test_analysis_summary_exists"""
    instance = TestOutputFilesExist()
    instance.test_analysis_summary_exists()


def test_CitationsJSON_test_contradiction_count():
    """Wrapper for TestCitationsJSON.test_contradiction_count"""
    instance = TestCitationsJSON()
    instance.test_contradiction_count()


def test_CitationsJSON_test_cycle_life_contradiction():
    """Wrapper for TestCitationsJSON.test_cycle_life_contradiction"""
    instance = TestCitationsJSON()
    instance.test_cycle_life_contradiction()


def test_CitationsJSON_test_temperature_contradiction():
    """Wrapper for TestCitationsJSON.test_temperature_contradiction"""
    instance = TestCitationsJSON()
    instance.test_temperature_contradiction()


def test_CitationsJSON_test_charging_rate_contradiction():
    """Wrapper for TestCitationsJSON.test_charging_rate_contradiction"""
    instance = TestCitationsJSON()
    instance.test_charging_rate_contradiction()


def test_CitationsJSON_test_cathode_recommendation_contradiction():
    """Wrapper for TestCitationsJSON.test_cathode_recommendation_contradiction"""
    instance = TestCitationsJSON()
    instance.test_cathode_recommendation_contradiction()


def test_CitationsJSON_test_citations_have_sections():
    """Wrapper for TestCitationsJSON.test_citations_have_sections"""
    instance = TestCitationsJSON()
    instance.test_citations_have_sections()


def test_AnalysisSummary_test_total_contradictions_field():
    """Wrapper for TestAnalysisSummary.test_total_contradictions_field"""
    instance = TestAnalysisSummary()
    instance.test_total_contradictions_field()


def test_AnalysisSummary_test_papers_analyzed_count():
    """Wrapper for TestAnalysisSummary.test_papers_analyzed_count"""
    instance = TestAnalysisSummary()
    instance.test_papers_analyzed_count()


def test_ReportQuality_test_report_in_korean():
    """Wrapper for TestReportQuality.test_report_in_korean"""
    instance = TestReportQuality()
    instance.test_report_in_korean()


def test_ReportQuality_test_report_mentions_key_values():
    """Wrapper for TestReportQuality.test_report_mentions_key_values"""
    instance = TestReportQuality()
    instance.test_report_mentions_key_values()

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
