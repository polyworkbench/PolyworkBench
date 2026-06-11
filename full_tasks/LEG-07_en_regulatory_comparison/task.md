# Cross-Jurisdiction Asian Data Protection Regulatory Comparison

## Overview
Tests the ability to read and compare data protection regulations in four Asian languages (Chinese, Korean, Vietnamese, Japanese) and produce a comprehensive English comparative analysis with compliance roadmap.

## Scenario
A company is expanding into four Asian markets (China, South Korea, Vietnam, Japan) and needs a unified compliance strategy. The agent must read key excerpts from PIPL (Chinese), PIPA (Korean), PDPD (Vietnamese), and APPI (Japanese) in their original languages, then produce a comprehensive English comparative analysis covering scope, data subject rights, cross-border transfers, consent, breach notification, penalties, and DPO requirements.

## Language Configuration
- **Instruction Language**: English
- **Source Material Languages**: Chinese, Korean, Vietnamese, Japanese
- **Target Output Language(s)**: English
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `comparative_analysis.md` | Comprehensive English comparative analysis document |
| `regulation_matrix.json` | Structured matrix mapping requirements across 4 jurisdictions |
| `gap_summary.json` | Key differences and potential conflicts between jurisdictions |
| `compliance_roadmap.json` | Prioritized action items with timelines and effort estimates |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Coverage Breadth | 25% | All four regulations analyzed across all comparison dimensions |
| Analytical Accuracy | 25% | Correct interpretation of each regulation's requirements |
| Comparative Insight | 20% | Meaningful identification of conflicts and gaps |
| Roadmap Practicality | 15% | Actionable and prioritized compliance recommendations |
| Structural Quality | 15% | Well-organized matrix and JSON structures |

## Key Challenges
- Reading regulations in four different Asian languages simultaneously
- Accurately comparing legal concepts that may not have direct equivalents across jurisdictions
- Identifying conflicts between regulations (e.g., data localization vs. cross-border transfer)
- Producing actionable compliance roadmap that addresses all four jurisdictions
