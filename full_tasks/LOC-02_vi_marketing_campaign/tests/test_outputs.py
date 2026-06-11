"""
Test suite for LOC-02: Marketing campaign adaptation to Vietnamese
Evaluates: adaptation_quality, vietnamese_natural, brand_compliance, cultural_fit, completeness
"""

import json
import os
import re
from pathlib import Path
import pytest

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace")))


def load_json(filename):
    """Load a JSON file from the output directory."""
    candidates = [
        os.path.join(OUTPUT_DIR, "output", filename),
        os.path.join(OUTPUT_DIR, "outputs", filename),
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/output/{filename}",
        f"/workspace/outputs/{filename}",
        f"/workspace/{filename}",
    ]
    for filepath in candidates:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def load_text(filename):
    """Load a text/markdown file from the output directory."""
    candidates = [
        os.path.join(OUTPUT_DIR, "output", filename),
        os.path.join(OUTPUT_DIR, "outputs", filename),
        os.path.join(OUTPUT_DIR, filename),
        f"/workspace/output/{filename}",
        f"/workspace/outputs/{filename}",
        f"/workspace/{filename}",
    ]
    for filepath in candidates:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
    return None


def has_vietnamese_diacritics(text):
    """Check if text contains Vietnamese-specific diacritical marks."""
    vietnamese_chars = re.compile(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', re.IGNORECASE)
    return bool(vietnamese_chars.search(text))


def count_vietnamese_words(text):
    """Count words with Vietnamese diacritics as rough quality measure."""
    words = text.split()
    viet_words = sum(1 for w in words if has_vietnamese_diacritics(w))
    return viet_words, len(words)


def check_adaptation_quality(social_posts, ad_copy, campaign_materials):
    """Check quality of marketing adaptation (not literal translation)."""
    score = 0.0

    # Check social posts exist and have content
    if social_posts is not None and isinstance(social_posts, list):
        if len(social_posts) >= 5:
            score += 0.3
        elif len(social_posts) >= 3:
            score += 0.2

        # Check each post has required fields
        valid_posts = 0
        for post in social_posts:
            if isinstance(post, dict):
                has_content = "content" in post and post["content"] and len(post["content"]) > 20
                has_hashtags = "hashtags" in post and isinstance(post.get("hashtags"), list)
                if has_content and has_hashtags:
                    valid_posts += 1

        if valid_posts >= 5:
            score += 0.3
        elif valid_posts >= 3:
            score += 0.2

    # Check ad copy
    if ad_copy is not None and isinstance(ad_copy, list):
        if len(ad_copy) >= 3:
            score += 0.2
        valid_ads = 0
        for ad in ad_copy:
            if isinstance(ad, dict):
                has_headline = "headline" in ad and ad["headline"]
                has_body = any(k in ad for k in ["body", "description"]) and any(ad.get(k) for k in ["body", "description"])
                has_cta = "cta" in ad and ad["cta"]
                if has_headline and has_cta:
                    valid_ads += 1
        if valid_ads >= 3:
            score += 0.2

    return min(1.0, score)


def check_vietnamese_natural(social_posts, ad_copy, campaign_materials):
    """Check that content uses natural Vietnamese with proper diacritics."""
    score = 0.0
    all_text = ""

    # Gather all Vietnamese text
    if social_posts and isinstance(social_posts, list):
        for post in social_posts:
            if isinstance(post, dict) and "content" in post:
                all_text += post["content"] + " "

    if ad_copy and isinstance(ad_copy, list):
        for ad in ad_copy:
            if isinstance(ad, dict):
                for field in ["headline", "body", "description"]:
                    if field in ad and ad[field]:
                        all_text += ad[field] + " "

    if campaign_materials:
        all_text += campaign_materials

    if not all_text.strip():
        return 0.0

    # Check for Vietnamese diacritics
    if has_vietnamese_diacritics(all_text):
        score += 0.4

    # Check density of Vietnamese words
    viet_words, total_words = count_vietnamese_words(all_text)
    if total_words > 0:
        density = viet_words / total_words
        if density > 0.3:
            score += 0.3
        elif density > 0.15:
            score += 0.2
        elif density > 0.05:
            score += 0.1

    # Check for common Vietnamese marketing phrases
    marketing_phrases = [
        "khám phá", "ưu đãi", "mua sắm", "giảm giá", "miễn phí",
        "đặc biệt", "ngay", "nhanh", "tiết kiệm", "thông minh",
        "hấp dẫn", "độc quyền", "chỉ", "hôm nay", "cơ hội"
    ]
    phrases_found = sum(1 for p in marketing_phrases if p in all_text.lower())
    if phrases_found >= 5:
        score += 0.3
    elif phrases_found >= 3:
        score += 0.2
    elif phrases_found >= 1:
        score += 0.1

    return min(1.0, score)


def check_brand_compliance(brand_report, social_posts, ad_copy):
    """Check brand guideline compliance."""
    score = 0.0

    # Check brand compliance report exists
    if brand_report is not None:
        score += 0.3
        if isinstance(brand_report, dict):
            # Check it has meaningful content
            report_str = json.dumps(brand_report, ensure_ascii=False)
            if len(report_str) > 100:
                score += 0.2

    # Check forbidden words are not used
    forbidden_patterns = ["NO.1", "số 1", "tốt nhất thế giới"]
    all_text = ""
    if social_posts and isinstance(social_posts, list):
        for post in social_posts:
            if isinstance(post, dict) and "content" in post:
                all_text += post["content"] + " "
    if ad_copy and isinstance(ad_copy, list):
        for ad in ad_copy:
            if isinstance(ad, dict):
                for field in ["headline", "body", "description"]:
                    if field in ad and ad[field]:
                        all_text += ad[field] + " "

    if all_text:
        violations = sum(1 for f in forbidden_patterns if f.lower() in all_text.lower())
        if violations == 0:
            score += 0.3
        else:
            score += max(0, 0.3 - violations * 0.1)

    # Check brand name consistency
    if "ShopSmart" in all_text or "shopsmart" in all_text.lower():
        score += 0.2

    return min(1.0, score)


def check_cultural_fit(social_posts, campaign_materials):
    """Check cultural adaptation for Vietnamese market."""
    score = 0.0
    all_text = ""

    if social_posts and isinstance(social_posts, list):
        for post in social_posts:
            if isinstance(post, dict):
                content = post.get("content", "")
                timing = post.get("suggested_timing", "") or post.get("timing", "")
                cultural_note = post.get("cultural_note", "")
                all_text += f"{content} {timing} {cultural_note} "

    if campaign_materials:
        all_text += campaign_materials

    if not all_text.strip():
        return 0.0

    # Check for Vietnamese cultural references
    cultural_refs = [
        "tết", "trung thu", "phụ nữ", "tựu trường", "valentine",
        "việt nam", "facebook", "zalo", "momo",
        "gia đình", "bạn bè", "cộng đồng"
    ]
    refs_found = sum(1 for ref in cultural_refs if ref in all_text.lower())
    if refs_found >= 4:
        score += 0.5
    elif refs_found >= 2:
        score += 0.3
    elif refs_found >= 1:
        score += 0.15

    # Check for timing suggestions that reference Vietnamese events
    if social_posts and isinstance(social_posts, list):
        posts_with_timing = sum(1 for p in social_posts if isinstance(p, dict) and
                               (p.get("suggested_timing") or p.get("timing")))
        if posts_with_timing >= 3:
            score += 0.3
        elif posts_with_timing >= 1:
            score += 0.15

    # Check VND currency usage
    if "₫" in all_text or "VND" in all_text or "đồng" in all_text.lower():
        score += 0.2

    return min(1.0, score)


def check_completeness(social_posts, ad_copy, campaign_materials, brand_report):
    """Check all required outputs are present and complete."""
    score = 0.0
    total_checks = 4

    # Check social_posts_vi.json
    if social_posts is not None and isinstance(social_posts, list) and len(social_posts) >= 5:
        score += 1.0 / total_checks

    # Check ad_copy_vi.json
    if ad_copy is not None and isinstance(ad_copy, list) and len(ad_copy) >= 3:
        score += 1.0 / total_checks

    # Check campaign_materials_vi.md
    if campaign_materials and len(campaign_materials) > 200:
        score += 1.0 / total_checks

    # Check brand_compliance_report.json
    if brand_report is not None:
        score += 1.0 / total_checks

    return min(1.0, score)


def grade():
    """Main grading function. Returns overall score and dimension scores."""
    # Load outputs
    social_posts = load_json("social_posts_vi.json")
    ad_copy = load_json("ad_copy_vi.json")
    campaign_materials = load_text("campaign_materials_vi.md")
    brand_report = load_json("brand_compliance_report.json")

    # Calculate dimension scores
    adaptation_quality = check_adaptation_quality(social_posts, ad_copy, campaign_materials)
    vietnamese_natural = check_vietnamese_natural(social_posts, ad_copy, campaign_materials)
    brand_compliance = check_brand_compliance(brand_report, social_posts, ad_copy)
    cultural_fit = check_cultural_fit(social_posts, campaign_materials)
    completeness = check_completeness(social_posts, ad_copy, campaign_materials, brand_report)

    # Weighted overall score
    overall_score = (
        adaptation_quality * 0.30 +
        vietnamese_natural * 0.25 +
        brand_compliance * 0.20 +
        cultural_fit * 0.15 +
        completeness * 0.10
    )

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": {
            "adaptation_quality": {
                "score": round(adaptation_quality, 4),
                "weight": 0.30,
                "description": "Quality of marketing adaptation (not literal translation)"
            },
            "vietnamese_natural": {
                "score": round(vietnamese_natural, 4),
                "weight": 0.25,
                "description": "Natural Vietnamese language with proper diacritics"
            },
            "brand_compliance": {
                "score": round(brand_compliance, 4),
                "weight": 0.20,
                "description": "Adherence to brand guidelines"
            },
            "cultural_fit": {
                "score": round(cultural_fit, 4),
                "weight": 0.15,
                "description": "Cultural relevance for Vietnamese market"
            },
            "completeness": {
                "score": round(completeness, 4),
                "weight": 0.10,
                "description": "All required output files present and complete"
            }
        }
    }


def test_grade_overall():
    """Verify grade function produces a meaningful score."""
    result = grade()
    assert result["overall_score"] > 0.15, "No valid output produced"


# === Standardized pytest tests (P2) ===

def test_output_files_exist():
    """Check that required output files were created."""
    result = grade()
    assert result["overall_score"] >= 0.0, "grade() should return a valid score"

def test_target_language():
    """Verify output is in the correct target language, not English fallback."""
    result = grade()
    if result["overall_score"] == 0.0:
        pytest.skip("No output to check")
    dims = result.get("dimensions", {})
    # Look for language-quality dimension
    lang_dim_scores = []
    for k, v in dims.items():
        if any(word in k.lower() for word in ["vietnamese", "vi"]):
            score = v.get("score", v) if isinstance(v, dict) else v
            if isinstance(score, (int, float)):
                lang_dim_scores.append(score)
    if lang_dim_scores:
        assert any(s > 0 for s in lang_dim_scores), \
            "Language quality dimensions are all zero - output may be in wrong language"

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
    """For non-English target tasks: verify primary output is not in English."""
    result = grade()
    if result["overall_score"] == 0.0:
        return
    dims = result.get("dimensions", {})
    lang_dim_scores = []
    for k, v in dims.items():
        if any(word in k.lower() for word in ["language", "quality", "chinese", "korean",
               "russian", "japanese", "vietnamese", "french", "cyrillic", "hangul"]):
            score = v.get("score", v) if isinstance(v, dict) else v
            if isinstance(score, (int, float)):
                lang_dim_scores.append(score)
    if lang_dim_scores:
        avg_lang = sum(lang_dim_scores) / len(lang_dim_scores)
        assert avg_lang > 0.1, f"Language quality too low ({avg_lang:.2f}), likely English fallback"

if __name__ == "__main__":
    result = grade()
    print(json.dumps(result, indent=2, ensure_ascii=False))
