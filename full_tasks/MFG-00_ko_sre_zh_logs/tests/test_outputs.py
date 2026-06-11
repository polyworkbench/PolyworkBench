"""
WildClawBench-style grading for HQ-03: Korean SRE Incident Analysis.
Returns multi-dimensional scores (0.0–1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

# Ground truth facts about the incident
INCIDENT_FACTS = {
    "root_cause": "redis",  # Redis master failover
    "key_terms": ["redis", "redlock", "sentinel", "failover", "ttl", "kafka"],
    "timeline_events_kst": {
        "23:00": "redis latency / incident start",
        "23:00:12": "redis master-0 down",
        "23:00:31": "sentinel elected new master",
        "23:05": "lowest success rate (45%)",
        "23:15": "hotpatch TTL 30→60",
        "23:18": "first successful order after fix",
        "23:25": "kafka lag drained",
        "23:30": "service restored",
    },
    "impact": {
        "duration_minutes_approx": 30,  # ~23:00 to ~23:30 KST
        "lowest_success_rate": 0.45,
        "peak_kafka_lag": 18900,
    },
    "operator": "zhang.wei",
    "fix": "lock TTL 30s → 60s",
}


def _safe_read(path: Path, encoding="utf-8-sig") -> str:
    if path.exists():
        return path.read_text(encoding=encoding).strip()
    return ""


def _safe_json(path: Path) -> Any:
    text = _safe_read(path)
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return None


def _find_file(name: str) -> Path:
    candidates = [OUTPUT_DIR / "output" / name, OUTPUT_DIR / name,
                  OUTPUT_DIR / "scripts" / name]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


def _load_answer() -> Dict[str, Any]:
    # Try multiple paths for answer.json
    candidates = [OUTPUT_DIR / "answer.json", OUTPUT_DIR / "output" / "answer.json"]
    data = {}
    for path in candidates:
        if path.exists():
            text = path.read_text(encoding="utf-8-sig").strip()
            if text.startswith("{"):
                try:
                    data = json.loads(text)
                    break
                except json.JSONDecodeError:
                    pass

    if not data:
        # Fallback from individual files
        rca_path = _find_file("rca.md")
        if rca_path.exists():
            data["rca_md"] = rca_path.read_text(encoding="utf-8-sig")

        summary_path = _find_file("summary_ko.md")
        if summary_path.exists():
            data["summary_ko_md"] = summary_path.read_text(encoding="utf-8-sig")

        timeline = _safe_json(_find_file("unified_timeline_raw.json"))
        if timeline:
            data["timeline_kst"] = timeline

        correlation = _safe_json(_find_file("correlation_analysis.json"))
        if correlation:
            data["correlation_analysis"] = correlation

        impact = _safe_json(_find_file("impact_metrics.json"))
        if impact:
            data["impact_metrics"] = impact

        actions_path = _find_file("action_items.json")
        if actions_path.exists():
            try:
                data["action_items"] = json.loads(actions_path.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError:
                pass

    # Normalize key names for grading compatibility
    # rca_md: agent may use "rca" (dict) or "rca_md" (string)
    if "rca_md" not in data:
        rca = data.get("rca", {})
        if isinstance(rca, dict) and rca:
            data["rca_md"] = json.dumps(rca, ensure_ascii=False)
        elif isinstance(rca, str) and rca:
            data["rca_md"] = rca
        # Also check for RCA_report.md file
        for fname in ["RCA_report.md", "rca_report.md", "RCA.md"]:
            rca_file = _find_file(fname)
            if rca_file.exists():
                data["rca_md"] = rca_file.read_text(encoding="utf-8-sig")
                break

    # summary_ko_md: agent may use "executive_summary_korean" or "summary_ko"
    if "summary_ko_md" not in data:
        for alt_key in ["executive_summary_korean", "summary_ko", "korean_summary"]:
            if alt_key in data and data[alt_key]:
                data["summary_ko_md"] = data[alt_key]
                break

    # impact_metrics: agent may use "impact" key
    if "impact_metrics" not in data and "impact" in data:
        data["impact_metrics"] = data["impact"]

    return data


def _score_timeline_and_timezone(data: Dict[str, Any]) -> Dict[str, float]:
    """Score timeline construction and timezone normalization."""
    scores = {}

    # Check for normalization script (accept multiple naming conventions)
    script_path = _find_file("normalize_timestamps.py")
    if not script_path.exists():
        script_path = _find_file("normalize_timezones.py")
    if not script_path.exists():
        script_path = _find_file("timezone_normalize.py")
    scores["script_exists"] = 1.0 if script_path.exists() else 0.0

    # Check unified timeline
    timeline = data.get("timeline_kst", [])
    if not timeline:
        timeline_raw = _safe_json(_find_file("unified_timeline_raw.json"))
        if timeline_raw:
            timeline = timeline_raw

    if not timeline:
        scores["timeline_present"] = 0.0
        scores["timeline_count"] = 0.0
        scores["timezone_correct"] = 0.0
        return scores

    scores["timeline_present"] = 1.0

    # Count events
    if isinstance(timeline, list):
        event_count = len(timeline)
    else:
        event_count = 0
    scores["timeline_count"] = min(1.0, event_count / 8.0)

    # Check timezone correctness: events should be in KST (23:xx range)
    kst_correct = 0
    total_checked = 0
    for item in (timeline if isinstance(timeline, list) else []):
        time_str = str(item.get("time_kst", item.get("time", item.get("timestamp", ""))))
        if "23:" in time_str or "2024-11-19 23" in time_str:
            kst_correct += 1
        total_checked += 1

    if total_checked > 0:
        scores["timezone_correct"] = kst_correct / total_checked
    else:
        scores["timezone_correct"] = 0.0

    # Check sources are attributed
    sourced = sum(1 for item in (timeline if isinstance(timeline, list) else [])
                  if "source" in item or "source" in str(item))
    scores["source_attribution"] = min(1.0, sourced / max(total_checked, 1))

    return scores


def _score_rca_structure(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the RCA document structure and content."""
    scores = {}
    rca = data.get("rca_md", "")

    if not rca:
        return {"rca_present": 0.0, "rca_sections": 0.0, "rca_sources": 0.0,
                "rca_technical_depth": 0.0}

    scores["rca_present"] = 1.0

    # Check required sections
    required_sections = [
        "Summary", "Impact", "Timeline", "Root Cause",
        "Contributing Factor", "Detection", "Resolution",
        "Lessons Learned", "Action Item"
    ]
    rca_lower = rca.lower()
    found_sections = [s for s in required_sections if s.lower() in rca_lower]
    scores["rca_sections"] = len(found_sections) / len(required_sections)

    # Check source citations [source: filename, line N]
    source_refs = re.findall(r'\[source:.*?\]', rca, re.IGNORECASE)
    if len(source_refs) >= 8:
        scores["rca_sources"] = 1.0
    elif len(source_refs) >= 5:
        scores["rca_sources"] = 0.7
    elif len(source_refs) >= 2:
        scores["rca_sources"] = 0.4
    elif source_refs:
        scores["rca_sources"] = 0.2
    else:
        # Check for alternative citation formats
        alt_refs = re.findall(r'\[.*?\.(?:log|txt|md).*?\]', rca)
        scores["rca_sources"] = min(0.5, len(alt_refs) * 0.1)

    # Technical depth: check key terms mentioned
    key_terms_found = sum(1 for term in INCIDENT_FACTS["key_terms"]
                          if term.lower() in rca_lower)
    scores["rca_technical_depth"] = min(1.0, key_terms_found / 4.0)

    # Check that resolution mentions the actual fix
    if "ttl" in rca_lower and ("30" in rca or "60" in rca):
        scores["rca_fix_accuracy"] = 1.0
    elif "ttl" in rca_lower or "lock" in rca_lower:
        scores["rca_fix_accuracy"] = 0.5
    else:
        scores["rca_fix_accuracy"] = 0.0

    return scores


def _score_impact_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the impact quantification."""
    scores = {}

    impact = data.get("impact_metrics", {})
    if not impact:
        impact = data.get("impact", {})
    if not impact:
        impact = _safe_json(_find_file("impact_metrics.json")) or {}

    # Check compute script exists (accept multiple naming conventions)
    script_path = _find_file("compute_impact.py")
    if not script_path.exists():
        script_path = _find_file("normalize_timezones.py")
    if not script_path.exists():
        script_path = _find_file("normalize_timestamps.py")
    scores["compute_script"] = 1.0 if script_path.exists() else 0.0

    if not impact:
        scores["metrics_present"] = 0.0
        scores["metrics_accuracy"] = 0.0
        return scores

    scores["metrics_present"] = 1.0

    # Check accuracy of key metrics
    accuracy_checks = []

    # Duration: should be ~20-35 minutes
    duration = impact.get("incident_duration_minutes", 0)
    if not duration:
        # Agent may use seconds
        dur_sec = impact.get("incident_duration_seconds", 0)
        if isinstance(dur_sec, (int, float)) and dur_sec > 0:
            duration = dur_sec / 60.0
    if isinstance(duration, (int, float)):
        if 20 <= duration <= 35:
            accuracy_checks.append(1.0)
        elif 15 <= duration <= 45:
            accuracy_checks.append(0.5)
        else:
            accuracy_checks.append(0.2)

    # Lowest success rate: should be ~0.45 (45%)
    lowest = impact.get("lowest_success_rate", 0)
    if not lowest:
        lowest = impact.get("success_rate_nadir", 0)
    if isinstance(lowest, str):
        # Handle "45.0%" format
        try:
            lowest = float(lowest.replace("%", "")) / 100.0
        except (ValueError, TypeError):
            lowest = 0
    if isinstance(lowest, (int, float)):
        # Handle both 0.45 and 45.0 formats
        if lowest > 1:
            lowest = lowest / 100.0
        if 0.40 <= lowest <= 0.50:
            accuracy_checks.append(1.0)
        elif 0.30 <= lowest <= 0.60:
            accuracy_checks.append(0.5)
        else:
            accuracy_checks.append(0.2)

    # Kafka lag peak: should be ~18900
    lag = impact.get("peak_kafka_lag", 0)
    if not lag:
        lag = impact.get("kafka_lag_peak", 0)
    if isinstance(lag, (int, float)):
        if 18000 <= lag <= 19500:
            accuracy_checks.append(1.0)
        elif 12000 <= lag <= 20000:
            accuracy_checks.append(0.5)
        else:
            accuracy_checks.append(0.2)

    scores["metrics_accuracy"] = sum(accuracy_checks) / max(len(accuracy_checks), 1) if accuracy_checks else 0.0

    return scores


def _score_correlation_analysis(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the correlation/causal analysis."""
    scores = {}

    correlation = data.get("correlation_analysis", {})
    if not correlation:
        correlation = _safe_json(_find_file("correlation_analysis.json")) or {}

    if not correlation:
        return {"correlation_present": 0.0, "causal_chain": 0.0, "cross_reference": 0.0}

    scores["correlation_present"] = 1.0

    # Check causal chain
    chain = correlation.get("causal_chain", [])
    if isinstance(chain, list) and len(chain) >= 5:
        scores["causal_chain"] = 1.0
    elif isinstance(chain, list) and len(chain) >= 3:
        scores["causal_chain"] = 0.6
    elif isinstance(chain, list) and len(chain) >= 1:
        scores["causal_chain"] = 0.3
    else:
        scores["causal_chain"] = 0.0

    # Check cross-references (claims backed by multiple sources)
    cross_refs = correlation.get("data_source_cross_references", [])
    if isinstance(cross_refs, list) and len(cross_refs) >= 3:
        scores["cross_reference"] = 1.0
    elif isinstance(cross_refs, list) and len(cross_refs) >= 1:
        scores["cross_reference"] = 0.5
    else:
        # Check if root_cause field has evidence
        if correlation.get("root_cause"):
            scores["cross_reference"] = 0.3
        else:
            scores["cross_reference"] = 0.0

    return scores


def _score_korean_summary(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the Korean executive summary."""
    scores = {}
    summary = data.get("summary_ko_md", "")

    if not summary:
        return {"ko_present": 0.0, "ko_length": 0.0, "ko_content": 0.0}

    scores["ko_present"] = 1.0

    # Check length (should be <= 80 chars, but some flexibility for Korean)
    # Count actual Korean/content characters (excluding whitespace)
    content_len = len(summary.strip())
    if content_len <= 100:
        scores["ko_length"] = 1.0
    elif content_len <= 150:
        scores["ko_length"] = 0.7
    elif content_len <= 200:
        scores["ko_length"] = 0.5
    else:
        scores["ko_length"] = 0.3  # Still has content, just too long

    # Check for Korean characters
    korean_chars = len(re.findall(r'[가-힯ᄀ-ᇿ]', summary))
    if korean_chars >= 10:
        scores["ko_content"] = 1.0
    elif korean_chars >= 5:
        scores["ko_content"] = 0.7
    elif korean_chars >= 1:
        scores["ko_content"] = 0.5
    else:
        scores["ko_content"] = 0.0

    # Check consistency with RCA (should mention Redis/payment)
    summary_lower = summary.lower()
    if "redis" in summary_lower or "결제" in summary or "지불" in summary:
        scores["ko_consistency"] = 1.0
    elif any(term in summary_lower for term in ["payment", "서비스", "장애"]):
        scores["ko_consistency"] = 0.7
    else:
        scores["ko_consistency"] = 0.3

    return scores


def _score_action_items(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the action items quality."""
    scores = {}
    actions = data.get("action_items", [])

    if not actions:
        return {"actions_present": 0.0, "actions_structured": 0.0, "actions_quality": 0.0}

    scores["actions_present"] = 1.0

    # Count and structure
    if isinstance(actions, list) and len(actions) >= 5:
        scores["actions_count"] = 1.0
    elif isinstance(actions, list) and len(actions) >= 3:
        scores["actions_count"] = 0.7
    elif isinstance(actions, list) and len(actions) >= 1:
        scores["actions_count"] = 0.4
    else:
        scores["actions_count"] = 0.0

    # Check structure (should have id, description, owner, priority, due_date)
    structured_count = 0
    for action in (actions if isinstance(actions, list) else []):
        if isinstance(action, dict):
            fields = {"id", "description", "owner", "priority", "due_date",
                      "description_en"}
            found = sum(1 for f in fields if f in action or any(f in k for k in action.keys()))
            if found >= 3:
                structured_count += 1
    scores["actions_structured"] = structured_count / max(len(actions), 1) if actions else 0.0

    # Check priority values
    priorities = [a.get("priority", "") for a in (actions if isinstance(actions, list) else []) if isinstance(a, dict)]
    valid_priorities = sum(1 for p in priorities if p in ("P0", "P1", "P2"))
    scores["actions_priority"] = valid_priorities / max(len(priorities), 1) if priorities else 0.0

    return scores


def _score_runbook(data: Dict[str, Any]) -> Dict[str, float]:
    """Score the runbook update."""
    scores = {}
    runbook = _safe_read(_find_file("runbook_update.md"))

    if not runbook:
        return {"runbook_present": 0.0}

    scores["runbook_present"] = 1.0

    runbook_lower = runbook.lower()
    quality = 0.0
    if "alert" in runbook_lower:
        quality += 0.25
    if "diagnostic" in runbook_lower or "command" in runbook_lower:
        quality += 0.25
    if "escalat" in runbook_lower:
        quality += 0.25
    if "rollback" in runbook_lower or "hotfix" in runbook_lower:
        quality += 0.25
    scores["runbook_quality"] = quality

    return scores


def grade() -> Dict[str, Any]:
    """
    Multi-dimensional grading for HQ-03.
    Returns dict with dimension scores and weighted overall_score.
    """
    data = _load_answer()

    if not data:
        return {
            "overall_score": 0.0,
            "dimensions": {},
            "error": "No answer found."
        }

    dimensions = {}

    # Dimension 1: Timeline & Timezone (weight: 0.20)
    tz_scores = _score_timeline_and_timezone(data)
    dimensions["timeline_timezone"] = {
        "score": sum(tz_scores.values()) / max(len(tz_scores), 1),
        "weight": 0.20,
        "details": tz_scores
    }

    # Dimension 2: RCA Structure & Content (weight: 0.25)
    rca_scores = _score_rca_structure(data)
    dimensions["rca_quality"] = {
        "score": sum(rca_scores.values()) / max(len(rca_scores), 1),
        "weight": 0.25,
        "details": rca_scores
    }

    # Dimension 3: Impact Metrics (weight: 0.15)
    impact_scores = _score_impact_metrics(data)
    dimensions["impact_metrics"] = {
        "score": sum(impact_scores.values()) / max(len(impact_scores), 1),
        "weight": 0.15,
        "details": impact_scores
    }

    # Dimension 4: Correlation Analysis (weight: 0.15)
    corr_scores = _score_correlation_analysis(data)
    dimensions["correlation"] = {
        "score": sum(corr_scores.values()) / max(len(corr_scores), 1),
        "weight": 0.15,
        "details": corr_scores
    }

    # Dimension 5: Korean Summary (weight: 0.10)
    ko_scores = _score_korean_summary(data)
    dimensions["korean_summary"] = {
        "score": sum(ko_scores.values()) / max(len(ko_scores), 1),
        "weight": 0.10,
        "details": ko_scores
    }

    # Dimension 6: Action Items & Runbook (weight: 0.15)
    action_scores = _score_action_items(data)
    runbook_scores = _score_runbook(data)
    combined = {**{f"act_{k}": v for k, v in action_scores.items()},
                **{f"rb_{k}": v for k, v in runbook_scores.items()}}
    dimensions["actions_runbook"] = {
        "score": sum(combined.values()) / max(len(combined), 1),
        "weight": 0.15,
        "details": combined
    }

    # Calculate weighted overall score
    overall_score = sum(
        dim["score"] * dim["weight"]
        for dim in dimensions.values()
    )

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": dimensions
    }


# === Pytest-compatible tests ===

def test_grade_overall():
    """Main grading test — reports overall score."""
    result = grade()
    print(f"\n{'='*60}")
    print(f"HQ-03 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for dim_name, dim_data in result.get("dimensions", {}).items():
        print(f"  {dim_name}: {dim_data['score']:.2%} (weight: {dim_data['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.0, "No valid output produced"


def test_rca_core_content():
    """RCA must contain key incident facts."""
    data = _load_answer()
    rca = data.get("rca_md", "")
    assert rca, "No RCA document produced"
    rca_lower = rca.lower()
    # Must mention Redis as root cause
    assert "redis" in rca_lower, "RCA must identify Redis as root cause"
    # Must have timeline section or timeline content
    assert "timeline" in rca_lower or "23:00" in rca, "RCA must have Timeline section"


def test_timezone_normalization():
    """Events should be normalized to KST timezone."""
    result = grade()
    tz = result["dimensions"].get("timeline_timezone", {})
    details = tz.get("details", {})
    # Timezone correctness should be at least partially correct
    tz_correct = details.get("timezone_correct", 0.0)
    if tz_correct == 0.0:
        # Check if RCA timeline uses KST
        data = _load_answer()
        rca = data.get("rca_md", "")
        assert "23:00" in rca or "KST" in rca, (
            "Timeline should use KST timezone (23:xx hour range)"
        )


def test_korean_summary_exists():
    """Korean summary must exist and contain Korean text."""
    data = _load_answer()
    summary = data.get("summary_ko_md", "")
    assert summary, "Korean executive summary not produced"
    korean_chars = len(re.findall(r'[가-힯]', summary))
    assert korean_chars >= 5, f"Korean summary has only {korean_chars} Korean characters"
