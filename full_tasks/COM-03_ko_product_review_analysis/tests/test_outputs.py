"""
BabelAgentBench grading for COM-03: Korean product review sentiment analysis.
Returns multi-dimensional scores (0.0-1.0) with weighted overall_score.
"""
import json, os, re
from pathlib import Path
from typing import Dict, Any, List

TASK_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))

EXPECTED_REVIEWS = 50

# Ground truth sentiment distribution (from the reviews)
# 5-star: 12 reviews (positive)
# 4-star: 11 reviews (positive)
# 3-star: 11 reviews (neutral)
# 2-star: 9 reviews (negative)
# 1-star: 7 reviews (negative)
POSITIVE_COUNT = 23
NEGATIVE_COUNT = 16
NEUTRAL_COUNT = 11


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


def _is_korean(text: str) -> bool:
    """Check if text contains Korean Hangul characters."""
    if not text:
        return False
    hangul_count = sum(1 for c in text if '가' <= c <= '힯' or 'ᄀ' <= c <= 'ᇿ' or '㄰' <= c <= '㆏')
    return hangul_count >= 5


def _score_sentiment_accuracy(data: Dict[str, Any]) -> Dict[str, float]:
    """Score sentiment analysis quality."""
    scores = {}
    sa_path = _find_file("sentiment_analysis.json")

    sa_data = None
    if sa_path.exists():
        try:
            sa_data = json.loads(sa_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not sa_data:
        return {"file_present": 0.0, "review_count": 0.0, "sentiment_labels": 0.0, "score_range": 0.0}

    scores["file_present"] = 1.0

    # Get reviews list
    reviews = sa_data if isinstance(sa_data, list) else sa_data.get("reviews", sa_data.get("analysis", list(sa_data.values()) if isinstance(sa_data, dict) else []))
    if isinstance(reviews, dict):
        reviews = list(reviews.values())

    scores["review_count"] = min(1.0, len(reviews) / EXPECTED_REVIEWS)

    # Check sentiment labels present
    labeled = 0
    valid_scores = 0
    for review in reviews:
        if isinstance(review, dict):
            # Check for sentiment label
            sentiment = review.get("sentiment", review.get("sentiment_label", review.get("label", "")))
            if sentiment and str(sentiment).lower() in ["positive", "negative", "neutral", "긍정", "부정", "중립", "pos", "neg", "neu"]:
                labeled += 1
            # Check for numeric score
            score_val = review.get("score", review.get("sentiment_score", review.get("polarity", None)))
            if isinstance(score_val, (int, float)) and -1.0 <= score_val <= 1.0:
                valid_scores += 1

    scores["sentiment_labels"] = labeled / max(len(reviews), 1)
    scores["score_range"] = valid_scores / max(len(reviews), 1)

    return scores


def _score_issue_extraction(data: Dict[str, Any]) -> Dict[str, float]:
    """Score issue extraction and categorization."""
    scores = {}
    sa_path = _find_file("sentiment_analysis.json")
    report_path = _find_file("issues_report_ko.md")

    # Check if issues are categorized
    sa_data = None
    if sa_path.exists():
        try:
            sa_data = json.loads(sa_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    report_text = ""
    if report_path.exists():
        report_text = report_path.read_text(encoding="utf-8-sig")

    if not sa_data and not report_text:
        return {"categorization": 0.0, "taxonomy_usage": 0.0, "issue_count": 0.0}

    # Check if taxonomy categories are referenced
    taxonomy_ids = ["QUAL-HW", "QUAL-SW", "PERF", "FIT", "TRUST", "SVC"]
    taxonomy_names = ["Hardware", "Software", "Performance", "Fit", "Trust", "Service",
                      "품질", "연결", "성능", "착용", "신뢰", "서비스"]

    blob = (json.dumps(sa_data, ensure_ascii=False) if sa_data else "") + report_text
    taxonomy_found = sum(1 for t in taxonomy_ids + taxonomy_names if t.lower() in blob.lower())
    scores["taxonomy_usage"] = min(1.0, taxonomy_found / 6)

    # Check if issues are identified with categories
    if sa_data:
        reviews = sa_data if isinstance(sa_data, list) else sa_data.get("reviews", sa_data.get("analysis", []))
        if isinstance(reviews, dict):
            reviews = list(reviews.values())
        categorized = 0
        for review in reviews:
            if isinstance(review, dict):
                issues = review.get("issues", review.get("categories", review.get("problems", [])))
                if issues:
                    categorized += 1
        scores["categorization"] = categorized / max(len(reviews), 1) if reviews else 0.0
    else:
        # Check from report if categories are mentioned
        scores["categorization"] = 0.5 if taxonomy_found >= 3 else 0.0

    # Check issue count is reasonable (there should be ~25-35 issues across negative/neutral reviews)
    issue_keywords = ["문제", "이슈", "불만", "개선", "issue", "problem"]
    issue_mentions = sum(blob.lower().count(kw) for kw in issue_keywords)
    scores["issue_count"] = min(1.0, issue_mentions / 10)

    return scores


def _score_korean_report(data: Dict[str, Any]) -> Dict[str, float]:
    """Score Korean executive report quality."""
    scores = {}
    report_path = _find_file("issues_report_ko.md")

    if not report_path.exists():
        return {"file_present": 0.0, "korean_quality": 0.0, "structure": 0.0, "recommendations": 0.0}

    report_text = report_path.read_text(encoding="utf-8-sig")

    scores["file_present"] = 1.0
    scores["korean_quality"] = 1.0 if _is_korean(report_text) and len(report_text) > 500 else 0.5 if _is_korean(report_text) else 0.0

    # Check report structure (headers, sections)
    headers = re.findall(r'^#{1,3}\s+.+', report_text, re.MULTILINE)
    scores["structure"] = min(1.0, len(headers) / 4)

    # Check for recommendations section
    rec_keywords = ["권고", "추천", "개선", "제안", "방안", "대책"]
    has_recommendations = any(kw in report_text for kw in rec_keywords)
    scores["recommendations"] = 1.0 if has_recommendations else 0.0

    return scores


def _score_english_appendix(data: Dict[str, Any]) -> Dict[str, float]:
    """Score English data appendix."""
    scores = {}
    appendix_path = _find_file("data_appendix_en.json")

    appendix = None
    if appendix_path.exists():
        try:
            appendix = json.loads(appendix_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not appendix:
        return {"file_present": 0.0, "english_content": 0.0, "data_completeness": 0.0}

    scores["file_present"] = 1.0

    # Check it's in English (not Korean)
    blob = json.dumps(appendix, ensure_ascii=False)
    scores["english_content"] = 1.0 if not _is_korean(blob) and len(blob) > 100 else 0.5

    # Check data completeness
    expected_keys = ["sentiment", "distribution", "categories", "issues", "trend", "statistics"]
    found_keys = sum(1 for k in expected_keys if k in blob.lower())
    scores["data_completeness"] = min(1.0, found_keys / 3)

    return scores


def _score_statistics(data: Dict[str, Any]) -> Dict[str, float]:
    """Score summary statistics."""
    scores = {}
    stats_path = _find_file("summary_stats.json")

    stats = None
    if stats_path.exists():
        try:
            stats = json.loads(stats_path.read_text(encoding="utf-8-sig"))
        except Exception:
            pass

    if not stats:
        return {"file_present": 0.0, "distribution_correct": 0.0, "metrics_present": 0.0}

    scores["file_present"] = 1.0

    # Check if sentiment distribution is reasonable
    blob = json.dumps(stats)
    has_distribution = any(k in blob.lower() for k in ["positive", "negative", "neutral", "distribution"])
    scores["distribution_correct"] = 1.0 if has_distribution else 0.0

    # Check for key metrics
    metrics = ["average", "mean", "count", "total", "ratio", "percentage"]
    found_metrics = sum(1 for m in metrics if m in blob.lower())
    scores["metrics_present"] = min(1.0, found_metrics / 3)

    return scores


def grade() -> Dict[str, Any]:
    """Multi-dimensional grading for COM-03."""
    data = _load_answer()

    dimensions = {}

    # Dimension 1: Sentiment Accuracy (weight: 0.25)
    sent_scores = _score_sentiment_accuracy(data)
    dimensions["sentiment_accuracy"] = {
        "score": sum(sent_scores.values()) / max(len(sent_scores), 1),
        "weight": 0.25,
        "details": sent_scores
    }

    # Dimension 2: Issue Extraction (weight: 0.25)
    issue_scores = _score_issue_extraction(data)
    dimensions["issue_extraction"] = {
        "score": sum(issue_scores.values()) / max(len(issue_scores), 1),
        "weight": 0.25,
        "details": issue_scores
    }

    # Dimension 3: Korean Report (weight: 0.20)
    report_scores = _score_korean_report(data)
    dimensions["korean_report"] = {
        "score": sum(report_scores.values()) / max(len(report_scores), 1),
        "weight": 0.20,
        "details": report_scores
    }

    # Dimension 4: English Appendix (weight: 0.15)
    appendix_scores = _score_english_appendix(data)
    dimensions["english_appendix"] = {
        "score": sum(appendix_scores.values()) / max(len(appendix_scores), 1),
        "weight": 0.15,
        "details": appendix_scores
    }

    # Dimension 5: Statistics (weight: 0.15)
    stats_scores = _score_statistics(data)
    dimensions["statistics"] = {
        "score": sum(stats_scores.values()) / max(len(stats_scores), 1),
        "weight": 0.15,
        "details": stats_scores
    }

    overall_score = sum(d["score"] * d["weight"] for d in dimensions.values())

    return {"overall_score": round(overall_score, 4), "dimensions": dimensions}


# === Pytest-compatible tests ===

def test_grade_overall():
    result = grade()
    print(f"\n{'='*60}")
    print(f"COM-03 Overall Score: {result['overall_score']:.2%}")
    print(f"{'='*60}")
    for name, dim in result.get("dimensions", {}).items():
        print(f"  {name}: {dim['score']:.2%} (weight: {dim['weight']})")
    print(f"{'='*60}\n")
    assert result["overall_score"] > 0.15, "Score too low — output likely incomplete or invalid"


def test_sentiment_analysis_present():
    result = grade()
    sent = result["dimensions"].get("sentiment_accuracy", {})
    details = sent.get("details", {})
    assert details.get("file_present", 0) == 1.0, "sentiment_analysis.json must be present"


def test_korean_report_quality():
    result = grade()
    report = result["dimensions"].get("korean_report", {})
    details = report.get("details", {})
    assert details.get("korean_quality", 0) >= 0.5, "Report must be written in Korean"


def test_english_appendix_present():
    result = grade()
    appendix = result["dimensions"].get("english_appendix", {})
    details = appendix.get("details", {})
    assert details.get("file_present", 0) == 1.0, "data_appendix_en.json must be present"


def test_all_reviews_analyzed():
    result = grade()
    sent = result["dimensions"].get("sentiment_accuracy", {})
    details = sent.get("details", {})
    assert details.get("review_count", 0) >= 0.8, "At least 40 of 50 reviews should be analyzed"


# === Strengthened standard pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    required_files = ["answer.json"]
    optional_important = ["sentiment_analysis.json", "issues_report_ko.md",
                          "data_appendix_en.json", "summary_stats.json"]
    for fname in required_files:
        path = _find_file(fname)
        assert path.exists(), f"Required output file missing: {fname}"
    found_optional = sum(1 for f in optional_important if _find_file(f).exists())
    assert found_optional >= 2, f"Only {found_optional}/4 key output files found"


def test_target_language():
    """Verify report is in Korean (Hangul), not English fallback."""
    report_path = _find_file("issues_report_ko.md")
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8-sig")
    hangul_chars = sum(1 for c in text if '가' <= c <= '힣')
    ratio = hangul_chars / max(len(text.replace(" ", "").replace("\n", "")), 1)
    assert ratio > 0.2, f"Korean report Hangul ratio too low ({ratio:.1%}), likely English fallback"


def test_minimum_content():
    """Verify output has sufficient content, not empty/trivial."""
    data = _load_answer()
    assert data, "answer.json is empty"
    blob = json.dumps(data, ensure_ascii=False)
    assert len(blob) > 200, f"Output too short ({len(blob)} chars), likely incomplete"


def test_no_english_fallback():
    """Verify Korean report isn't in English."""
    report_path = _find_file("issues_report_ko.md")
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8-sig")
    if not text:
        return
    ascii_words = len(re.findall(r'\b[a-zA-Z]{4,}\b', text))
    total_chars = len(text)
    english_ratio = ascii_words * 5 / max(total_chars, 1)
    assert english_ratio < 0.7, f"Korean report appears to be mostly English ({english_ratio:.0%})"


def test_review_count_50():
    """Verify 50 reviews analyzed in sentiment_analysis.json."""
    sa_path = _find_file("sentiment_analysis.json")
    if not sa_path.exists():
        return
    try:
        sa_data = json.loads(sa_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return
    reviews = sa_data if isinstance(sa_data, list) else sa_data.get("reviews", sa_data.get("analysis", []))
    if isinstance(reviews, dict):
        reviews = list(reviews.values())
    assert len(reviews) >= 40, f"Only {len(reviews)} reviews analyzed, expected ~50"
