# Multi-Jurisdiction M&A Review with French Synthesis Memo

## Overview
Tests the ability to analyze a complex cross-border M&A transaction involving five jurisdictions (China, Japan, Korea, Russia, English-law structure) from sources in six languages and produce a comprehensive French legal analysis.

## Scenario
A multinational acquisition involves a Japanese parent company acquiring a Chinese target, with regulatory requirements in Korea, sanctions concerns regarding Russia, and an English-law deal structure. The agent must detect key conflicts: a valuation discrepancy ($50M approved vs. $38M net assets), Korean antitrust threshold exceedance, and a sanctioned board member. All analysis must be synthesized into a formal French legal memorandum with regulatory conflict register and risk assessment.

## Language Configuration
- **Instruction Language**: French
- **Source Material Languages**: English, Chinese, Japanese, Korean, Russian
- **Target Output Language(s)**: French
- **Complexity Level**: L6

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `memo_synthese_fr.md` | Comprehensive French legal memorandum |
| `regulatory_conflicts.json` | Detected regulatory conflicts with severity and mitigation |
| `jurisdiction_matrix.json` | Cross-jurisdiction regulatory requirements comparison |
| `risk_register_fr.json` | Full risk register with probability/impact scoring |
| `glossaire_multilingue.json` | Multilingual legal glossary (FR, EN, ZH, JA, KO, RU) |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Conflict Detection | 25% | Identification of deliberate contradictions across documents |
| Multi-jurisdiction Analysis | 25% | Accurate understanding of each jurisdiction's requirements |
| French Legal Quality | 20% | Professional French M&A legal writing style |
| Risk Assessment | 15% | Logical risk scoring with appropriate mitigation measures |
| Language Breadth | 15% | Effective processing of all 5 source languages |

## Key Challenges
- Processing source documents in 5 different languages (EN, ZH, JA, KO, RU)
- Detecting the deliberate valuation discrepancy between Japanese resolution and Chinese financials
- Identifying Korean antitrust notification threshold breach
- Recognizing sanctions compliance issue with a board member
- Producing a 6-language legal glossary
