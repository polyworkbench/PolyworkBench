# Cross-Lingual QA from 5-Language Sources

## Overview
Tests the ability to extract specific factual answers from source documents in 5 different languages (Chinese, Japanese, Korean, Russian, Vietnamese) and report findings in English with verification methodology.

## Scenario
A researcher has 15 specific factual questions that must be answered by extracting information from source documents written in Chinese (government economic statistics), Japanese (technology industry report), Korean (semiconductor market data), Russian (energy sector analysis), and Vietnamese (manufacturing growth data). The agent must locate each fact, provide the original text snippet and English translation, and assess confidence levels.

## Language Configuration
- **Instruction Language**: English
- **Source Material Languages**: Chinese, Japanese, Korean, Russian, Vietnamese
- **Target Output Language(s)**: English
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `fact_sheet.json` | Answers to all 15 questions with source snippets and translations |
| `verification_report.md` | Methodology explanation and cross-referencing analysis |
| `source_citations.json` | Formal citations for each source document |
| `confidence_scores.json` | Confidence levels (0.0-1.0) for each answer with justification |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Answer Accuracy | 30% | Correct extraction of factual information |
| Source Attribution | 25% | Proper identification of which source provides each answer |
| Cross-referencing | 20% | Detection of discrepancies between sources |
| Confidence Calibration | 15% | Appropriate confidence scoring with reasoning |
| Verification Methodology | 10% | Clear explanation of fact-finding approach |

## Key Challenges
- Locating specific facts across 5 different languages
- Providing accurate original-language text snippets alongside English translations
- Cross-referencing when multiple sources address the same topic
- Calibrating confidence appropriately (directly stated vs. inferred)
- Noting discrepancies between sources on the same metrics
