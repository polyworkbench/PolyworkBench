# Korean IP Filing from English Patent with Japanese and Chinese Prior Art

## Overview
Tests the ability to prepare Korean patent filing documents by translating claims from English, analyzing prior art in Japanese and Chinese, and assessing novelty/inventive step in Korean.

## Scenario
A US patent application (in English with 15 claims) needs to be filed with the Korean Intellectual Property Office (KIPO). The agent must translate all claims into Korean using proper patent claim language conventions, analyze Japanese prior art literature and a Chinese utility model for technical differences, assess novelty and inventive step, and prepare a KIPO filing checklist — all output in Korean.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: English, Japanese, Chinese
- **Target Output Language(s)**: Korean
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total_claims, independent_claims, novelty_confirmed, key_differentiator |
| `patent_claims_ko.md` | All 15 claims translated to Korean in proper patent format |
| `prior_art_analysis_ko.json` | Structured prior art analysis with technical differences |
| `novelty_assessment_ko.md` | Novelty and inventive step assessment vs. prior art |
| `filing_checklist_ko.json` | KIPO filing requirements checklist |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Claims Translation | 30% | Accuracy and proper Korean patent claim conventions |
| Prior Art Analysis | 25% | Thoroughness of technical comparison across languages |
| Novelty Assessment | 20% | Quality of novelty/inventive step legal reasoning |
| Korean IP Terminology | 15% | Correct usage of Korean patent law terminology |
| Filing Completeness | 10% | All KIPO requirements properly addressed |

## Key Challenges
- Translating patent claims using Korean patent conventions (e.g., ~을 포함하는, ~로 구성되는)
- Analyzing prior art across three languages (EN, JA, ZH) simultaneously
- Distinguishing independent and dependent claims correctly
- Identifying specific technical differentiators with quantitative measures
