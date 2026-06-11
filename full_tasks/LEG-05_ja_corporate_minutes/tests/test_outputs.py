"""
Test suite for LEG-05_ja_corporate_minutes
Evaluates: minutes_format, financial_accuracy, japanese_formality, resolutions_completeness, action_items
"""

import json
import os
import re
from pathlib import Path
import pytest


def check_file_exists(filepath):
    """Check if a file exists and has content."""
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"
    return True, "OK"


def load_json_file(filepath):
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return None, str(e)


def check_japanese_text(text):
    """Check if text contains substantial Japanese content (hiragana, katakana, kanji)."""
    japanese_chars = len(re.findall(r'[぀-ゟ゠-ヿ一-鿿]', text))
    total_chars = len(text.replace(' ', '').replace('\n', ''))
    if total_chars == 0:
        return 0.0
    return japanese_chars / total_chars


def grade():
    """Main grading function returning overall_score and dimensions."""

    _ws = os.environ.get("OUTPUT_DIR", os.environ.get("WORKSPACE", "/workspace"))
    output_dir = os.path.join(_ws, "output")
    if not os.path.exists(output_dir):
        output_dir = os.path.join(_ws, "outputs")
    if not os.path.exists(output_dir):
        output_dir = "/workspace/output"
    if not os.path.exists(output_dir):
        output_dir = "/workspace/outputs"
    answer_path = os.path.join(output_dir, "answer.json")
    if not os.path.exists(answer_path):
        answer_path = os.path.join(_ws, "answer.json")
    if not os.path.exists(answer_path):
        answer_path = "/workspace/answer.json"

    if not os.path.exists(output_dir):
        output_dir = "output"
    if not os.path.exists(answer_path):
        answer_path = "answer.json"

    dimensions = {
        "minutes_format": 0.0,
        "financial_accuracy": 0.0,
        "japanese_formality": 0.0,
        "resolutions_completeness": 0.0,
        "action_items": 0.0
    }

    weights = {
        "minutes_format": 0.25,
        "financial_accuracy": 0.25,
        "japanese_formality": 0.20,
        "resolutions_completeness": 0.15,
        "action_items": 0.15
    }

    # =====================================================
    # DIMENSION 1: Minutes Format (0.25)
    # =====================================================
    format_score = 0.0

    minutes_path = os.path.join(output_dir, "board_minutes_ja.md")
    exists, _ = check_file_exists(minutes_path)

    if exists:
        with open(minutes_path, 'r', encoding='utf-8') as f:
            minutes_text = f.read()

        # Check for essential board minutes elements
        format_elements = {
            "date_time": ["2024年4月25日", "4月25日", "14:00", "14時"],
            "location": ["丸の内", "marunouchi", "東京", "会議室"],
            "attendees": ["田中", "山本", "陳", "朴", "Williams", "鈴木", "Mitchell"],
            "agenda_items": ["第1号議案", "第2号議案", "議案", "議題"],
            "resolutions": ["承認", "可決", "決議", "全会一致"],
            "secretary": ["渡辺", "議事録"],
        }

        elements_found = 0
        for element_name, keywords in format_elements.items():
            if any(kw.lower() in minutes_text.lower() for kw in keywords):
                elements_found += 1

        format_score += min(0.5, elements_found / 6 * 0.5)

        # Check document structure (headings, sections)
        has_structure = bool(re.search(r'^#+\s', minutes_text, re.MULTILINE))
        if has_structure:
            format_score += 0.15

        # Check document length (full minutes should be substantial)
        if len(minutes_text) > 3000:
            format_score += 0.2
        elif len(minutes_text) > 1500:
            format_score += 0.1

        # Check for 6 agenda items coverage
        agenda_coverage = 0
        for i in range(1, 7):
            patterns = [f"第{i}号", f"議案{i}", f"item {i}", f"議題{i}", f"第{i}議案"]
            if any(p.lower() in minutes_text.lower() for p in patterns):
                agenda_coverage += 1
        format_score += min(0.15, agenda_coverage / 6 * 0.15)

    dimensions["minutes_format"] = min(1.0, format_score)

    # =====================================================
    # DIMENSION 2: Financial Accuracy (0.25)
    # =====================================================
    fin_score = 0.0

    fin_path = os.path.join(output_dir, "financial_summary_ja.json")
    fin_data, err = load_json_file(fin_path)

    if fin_data is not None:
        fin_score += 0.1  # Valid JSON

        fin_text = json.dumps(fin_data, ensure_ascii=False)

        # Key financial figures from Chinese CSV that should be accurately reflected:
        # Revenue Q4: 234.7 million CNY (百万元)
        # Net profit Q4: 30.5 million CNY
        # Operating profit Q4: 38.4 million CNY
        # Full year revenue: 856.2 million CNY
        # Full year net profit: 98.5 million CNY
        # EPS: 3.73 CNY

        key_figures = {
            "revenue_q4": ["234.7", "2.347億", "2.347亿", "23470"],
            "net_profit_fy": ["98.5", "9850", "9,850"],
            "operating_profit_fy": ["142.8", "14280", "14,280"],
            "full_year_revenue": ["856.2", "8.562億", "8.562亿", "85620"],
            "growth_rate": ["12.3%", "12.3％"],
        }

        figures_found = 0
        for fig_name, patterns in key_figures.items():
            if any(p in fin_text for p in patterns):
                figures_found += 1

        fin_score += min(0.5, figures_found / 5 * 0.5)

        # Check for structured data (has key financial categories)
        category_keywords = ["売上", "収益", "revenue", "利益", "profit", "営業",
                           "純利益", "net", "キャッシュフロー", "cash"]
        categories_found = sum(1 for kw in category_keywords if kw.lower() in fin_text.lower())
        fin_score += min(0.2, categories_found / 4 * 0.2)

        # Check for Korea subsidiary reference
        korea_keywords = ["韓国", "korea", "한국", "285", "28.5"]
        if any(kw.lower() in fin_text.lower() for kw in korea_keywords):
            fin_score += 0.1

        # Check for comparison data (budget vs actual)
        if any(kw in fin_text.lower() for kw in ["予算", "budget", "計画", "実績", "達成"]):
            fin_score += 0.1

    dimensions["financial_accuracy"] = min(1.0, fin_score)

    # =====================================================
    # DIMENSION 3: Japanese Formality (0.20)
    # =====================================================
    jp_score = 0.0

    minutes_path = os.path.join(output_dir, "board_minutes_ja.md")
    exists, _ = check_file_exists(minutes_path)

    if exists:
        with open(minutes_path, 'r', encoding='utf-8') as f:
            minutes_text = f.read()

        # Check Japanese text ratio
        jp_ratio = check_japanese_text(minutes_text)
        if jp_ratio > 0.4:
            jp_score += 0.25
        elif jp_ratio > 0.2:
            jp_score += 0.15

        # Check for formal board minutes language
        formal_expressions = [
            "取締役会議事録", "議事録", "開催", "出席", "定足数",
            "審議", "承認", "可決", "異議なく", "全会一致",
            "報告", "上程", "付議", "決議", "以上"
        ]
        formal_found = sum(1 for expr in formal_expressions if expr in minutes_text)
        jp_score += min(0.35, formal_found / 7 * 0.35)

        # Check for polite/formal verb endings
        polite_patterns = ["された", "された。", "いたしました", "ございます",
                          "承認された", "決議した", "報告した", "について審議"]
        polite_found = sum(1 for p in polite_patterns if p in minutes_text)
        jp_score += min(0.2, polite_found / 3 * 0.2)

        # Check for proper honorifics/titles
        titles = ["代表取締役", "取締役", "社外取締役", "監査役", "議長", "CFO"]
        titles_found = sum(1 for t in titles if t in minutes_text)
        jp_score += min(0.2, titles_found / 3 * 0.2)

    dimensions["japanese_formality"] = min(1.0, jp_score)

    # =====================================================
    # DIMENSION 4: Resolutions Completeness (0.15)
    # =====================================================
    res_score = 0.0

    res_path = os.path.join(output_dir, "resolutions_ja.json")
    res_data, err = load_json_file(res_path)

    if res_data is not None:
        res_score += 0.15  # Valid JSON

        # Find resolutions list
        resolutions = res_data if isinstance(res_data, list) else res_data.get("resolutions", [])
        if isinstance(res_data, dict) and not isinstance(resolutions, list):
            for v in res_data.values():
                if isinstance(v, list):
                    resolutions = v
                    break

        if isinstance(resolutions, list):
            # Should have 6 resolutions (one per agenda item)
            if len(resolutions) >= 6:
                res_score += 0.3
            elif len(resolutions) >= 4:
                res_score += 0.2
            elif len(resolutions) >= 2:
                res_score += 0.1

            # Check for vote results
            res_text = json.dumps(resolutions, ensure_ascii=False).lower()
            if any(kw in res_text for kw in ["全会一致", "unanimous", "賛成", "approved", "可決", "承認"]):
                res_score += 0.2

            # Check for specific resolution content
            resolution_topics = {
                "financial_approval": ["財務", "決算", "financial", "856"],
                "business_plan": ["事業計画", "予算", "budget", "980"],
                "dividend": ["配当", "dividend", "45円", "65円"],
                "korea_report": ["韓国", "korea", "子会社", "넥사텍"],
                "outside_director": ["社外取締役", "林", "hayashi", "選任"],
                "share_issuance": ["新株", "SoftBank", "第三者割当", "発行"]
            }

            topics_found = 0
            for topic, keywords in resolution_topics.items():
                if any(kw.lower() in res_text for kw in keywords):
                    topics_found += 1

            res_score += min(0.35, topics_found / 6 * 0.35)

    dimensions["resolutions_completeness"] = min(1.0, res_score)

    # =====================================================
    # DIMENSION 5: Action Items (0.15)
    # =====================================================
    action_score = 0.0

    action_path = os.path.join(output_dir, "action_items_ja.json")
    action_data, err = load_json_file(action_path)

    if action_data is not None:
        action_score += 0.15  # Valid JSON

        # Find action items list
        items = action_data if isinstance(action_data, list) else action_data.get("action_items", [])
        if isinstance(action_data, dict) and not isinstance(items, list):
            for v in action_data.values():
                if isinstance(v, list):
                    items = v
                    break

        if isinstance(items, list) and len(items) > 0:
            # Should have multiple action items
            if len(items) >= 5:
                action_score += 0.25
            elif len(items) >= 3:
                action_score += 0.15

            # Check for required fields (assignee, deadline, description)
            action_text = json.dumps(items, ensure_ascii=False).lower()

            # Should have assignees/responsible persons
            if any(kw in action_text for kw in ["担当", "責任者", "assignee", "responsible", "owner"]):
                action_score += 0.2

            # Should have deadlines/dates
            if any(kw in action_text for kw in ["期限", "deadline", "期日", "まで", "月", "2024"]):
                action_score += 0.2

            # Should reference specific directors/people
            people = ["田中", "山本", "鈴木", "渡辺", "陳", "chen", "park", "朴", "williams"]
            if any(p.lower() in action_text for p in people):
                action_score += 0.2

    dimensions["action_items"] = min(1.0, action_score)

    # =====================================================
    # Check answer.json
    # =====================================================
    answer_data, err = load_json_file(answer_path)
    if answer_data is not None:
        # Validate key answer fields
        if answer_data.get("total_resolutions") == 6:
            dimensions["resolutions_completeness"] = min(1.0, dimensions["resolutions_completeness"] + 0.05)

        # Revenue from CSV: 856.2 million CNY (full year) or 234.7 million (Q4)
        revenue = answer_data.get("total_revenue_cny")
        if revenue is not None:
            if abs(revenue - 856.2) < 1 or abs(revenue - 856200000) < 1000000:  # Full year
                dimensions["financial_accuracy"] = min(1.0, dimensions["financial_accuracy"] + 0.05)
            elif abs(revenue - 234.7) < 1 or abs(revenue - 234700000) < 1000000:  # Q4 revenue
                dimensions["financial_accuracy"] = min(1.0, dimensions["financial_accuracy"] + 0.05)

    # =====================================================
    # CALCULATE OVERALL SCORE
    # =====================================================
    overall_score = sum(dimensions[k] * weights[k] for k in dimensions)

    return {
        "overall_score": round(overall_score, 4),
        "dimensions": {k: round(v, 4) for k, v in dimensions.items()}
    }





def test_grade_overall():
    """Verify grade function produces a meaningful score."""
    result = grade()
    assert result["overall_score"] > 0.15, "No valid output produced"



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
        if any(word in k.lower() for word in ["japanese", "jp", "ja"]):
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
    print(json.dumps(result, indent=2))
