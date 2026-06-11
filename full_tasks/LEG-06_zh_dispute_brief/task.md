# Chinese Litigation Brief from English-Russian Sources

## Overview
Tests the ability to analyze an international commercial arbitration case from English and Russian source materials and produce a comprehensive Chinese-language litigation strategy brief.

## Scenario
A Chinese company is involved in an ICC international commercial arbitration dispute with a Russian counterparty. The agent must analyze the English arbitration clause (ICC rules), translate and analyze the Russian counterparty's arbitration filing, review transaction history and correspondence (English), and produce a complete Chinese litigation strategy brief covering procedural analysis, substantive analysis, defense strategy, and risk assessment.

## Language Configuration
- **Instruction Language**: Chinese
- **Source Material Languages**: English, Russian
- **Target Output Language(s)**: Chinese
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `litigation_brief_zh.md` | Complete litigation strategy brief in Chinese |
| `strategy_analysis.json` | Structured strategy data: seat, applicable law, claims, defense points |
| `evidence_list_zh.json` | Evidence inventory with proof purposes |
| `timeline_zh.json` | Chronological timeline of key case events |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Strategy Quality | 30% | Depth and coherence of litigation strategy |
| Russian Source Analysis | 25% | Accurate translation and analysis of Russian filing |
| Legal Accuracy | 20% | Correct application of ICC arbitration rules and procedure |
| Chinese Legal Writing | 15% | Professional Chinese litigation document style |
| Evidence Organization | 10% | Logical organization of evidence and timeline |

## Key Challenges
- Translating and interpreting Russian arbitration filings into Chinese legal context
- Identifying the arbitration seat, applicable law, and procedural elements
- Analyzing force majeure defenses and breach of contract claims
- Producing win probability assessment with legal justification
