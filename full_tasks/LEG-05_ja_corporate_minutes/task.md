# Japanese Board Minutes from English Agenda, Chinese Financials, Korean Report

## Overview
Tests the ability to synthesize multilingual corporate governance materials (English, Chinese, Korean) into formal Japanese board meeting minutes compliant with Japanese Companies Act requirements.

## Scenario
A multinational corporation needs formal board minutes drafted in Japanese. The source materials include an English board agenda (6 resolutions), Chinese quarterly financial data in CSV format, a Korean subsidiary report, and English shareholder/voting information. The agent must produce minutes in formal Japanese (polite register), accurately convert financial figures, and ensure compliance with Japanese corporate law documentation requirements.

## Language Configuration
- **Instruction Language**: Japanese
- **Source Material Languages**: English, Chinese, Korean
- **Target Output Language(s)**: Japanese
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total_resolutions, approved_unanimously, total_revenue_cny, action_items_count |
| `board_minutes_ja.md` | Formal board minutes with all legally required elements |
| `resolutions_ja.json` | Resolution details: content, votes, responsible directors |
| `financial_summary_ja.json` | Financial data converted from Chinese CSV to structured Japanese |
| `action_items_ja.json` | Action items extracted with assignees and deadlines |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Legal Compliance | 25% | Adherence to Japanese Companies Act minute requirements |
| Financial Accuracy | 25% | Correct transcription of Chinese financial figures |
| Japanese Formality | 20% | Proper use of keigo/formal register in minutes |
| Content Integration | 15% | Accurate synthesis of Korean subsidiary report |
| Structural Completeness | 15% | All statutory elements present (date, venue, attendees, etc.) |

## Key Challenges
- Converting Chinese CSV financial data accurately into Japanese
- Summarizing Korean subsidiary report as a specific agenda item
- Using correct formal Japanese register (keigo, polite forms)
- Meeting Japanese Companies Act requirements for board minute documentation
