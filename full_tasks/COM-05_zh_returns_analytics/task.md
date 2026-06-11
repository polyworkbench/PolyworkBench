# Multilingual Returns Analytics with Chinese Dashboard Reporting

## Overview
Tests the agent's ability to analyze product return data from Russian and Vietnamese markets (with multilingual customer comments), correlate with English product master data and return policies, and produce Chinese-language analytics dashboards and improvement recommendations.

## Scenario
A Chinese e-commerce headquarters needs to analyze cross-border return data from its Russian and Vietnamese market operations. The agent must parse Russian-language customer return comments to extract return reasons and sentiment, parse Vietnamese-language return comments similarly, correlate returns with English product master data (categories, prices, suppliers), evaluate each return against the English return policy for compliance, and produce Chinese-language analytics outputs including return rate analysis, dashboard visualization data, category breakdowns, and a management recommendations report.

## Language Configuration
- **Instruction Language**: Chinese
- **Source Material Languages**: Russian (return comments), Vietnamese (return comments), English (product master, return policy)
- **Target Output Language(s)**: Chinese
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated analytics summary |
| `returns_analysis_zh.json` | Return rate analysis by market, reason distribution, product dimensions |
| `dashboard_data.json` | Structured visualization data with time trends, regional comparison, top issues |
| `category_breakdown.json` | Per-category return rates, primary reasons, year-over-year changes |
| `recommendations_zh.md` | Chinese management report with root cause analysis and improvement priorities |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Data Extraction | 0.25 | Accuracy of extracting return reasons from Russian and Vietnamese comments |
| Analytics Accuracy | 0.25 | Correctness of computed metrics, rates, and distributions |
| Chinese Report | 0.20 | Quality of Chinese-language recommendations with business terminology |
| Dashboard Completeness | 0.15 | Structured data suitable for visualization with all required dimensions |
| Recommendations | 0.15 | Actionable improvement suggestions with prioritization and policy references |

## Key Challenges
- Extracting structured return reasons from unstructured Russian customer comments
- Extracting structured return reasons from unstructured Vietnamese customer comments
- Correlating multilingual data sources into a unified analytical framework
- Evaluating policy compliance based on English policy documents
- Producing professional Chinese business analytics language with proper terminology
