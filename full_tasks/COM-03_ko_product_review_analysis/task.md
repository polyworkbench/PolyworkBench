# Korean Product Review Sentiment Analysis with Bilingual Reporting

## Overview
Tests the agent's ability to perform sentiment analysis on 50 Korean-language product reviews, classify issues using an English taxonomy, cross-reference with Chinese product specs, and produce bilingual outputs (Korean executive report + English data appendix).

## Scenario
A product team needs to analyze 50 Korean customer reviews to understand product sentiment and identify key issues. The agent must perform sentiment scoring for each review, classify issues against an English-language category taxonomy, cross-reference review complaints with Chinese product specifications to identify spec mismatches or misleading advertising claims, then produce a Korean-language executive issues report with a Top-5 analysis and improvement recommendations, alongside an English data appendix with statistical distributions and trend data.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: Korean (reviews), Chinese (product specs), English (category taxonomy)
- **Target Output Language(s)**: Korean (executive report), English (data appendix)
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary statistics and key findings |
| `sentiment_analysis.json` | Per-review sentiment scores (-1.0 to 1.0), labels, and keywords |
| `issues_report_ko.md` | Korean executive issues report with Top 5, category analysis, recommendations |
| `data_appendix_en.json` | English data appendix with distributions, counts, and trends |
| `summary_stats.json` | Overall sentiment distribution, average rating, category counts |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Sentiment Accuracy | 0.25 | Correctness of sentiment scoring and label assignment per review |
| Issue Extraction | 0.25 | Quality of issue classification against the taxonomy |
| Korean Report | 0.20 | Natural business Korean, proper structure, actionable recommendations |
| English Appendix | 0.15 | Data completeness and proper analytical terminology in English |
| Statistics | 0.15 | Accuracy of computed statistics and distributions |

## Key Challenges
- Nuanced Korean sentiment analysis with proper positive/negative/neutral classification
- Mapping Korean review complaints to English-language issue categories
- Cross-referencing Korean feedback with Chinese product specifications
- Producing natural business Korean for the executive summary
- Maintaining consistency between Korean narrative and English statistical appendix
