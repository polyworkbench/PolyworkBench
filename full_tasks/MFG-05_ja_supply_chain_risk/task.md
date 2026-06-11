# Japanese Supply Chain Risk Assessment from Multilingual Supplier Data

## Overview
Tests the agent's ability to evaluate supply chain risks by analyzing supplier data from China, Korea, and Vietnam (each in their local language), applying an English ISO 31000 risk framework, and producing a Japanese-language risk register, assessment report, and mitigation plan.

## Scenario
A supply chain manager needs to assess risks across suppliers in three countries. Supplier performance data is available in Chinese (China suppliers), Korean (Korea suppliers), and Vietnamese (Vietnam suppliers), alongside an English ISO 31000-based risk framework and geopolitical risk factors document. The agent must score each supplier on quality, delivery, cost, flexibility, and financial stability, assign risk categories with probability and impact ratings, identify single-source concentration risks, incorporate geopolitical risk factors per country, produce a Japanese-language risk register and assessment report, and develop a mitigation plan with alternative supplier strategies and safety stock recommendations.

## Language Configuration
- **Instruction Language**: Japanese
- **Source Material Languages**: Chinese (China suppliers), Korean (Korea suppliers), Vietnamese (Vietnam suppliers), English (risk framework, geopolitical factors)
- **Target Output Language(s)**: Japanese
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total suppliers, high-risk count, critical risks, single-source items, avg risk score |
| `risk_register_ja.json` | Per-supplier risk register with categories, probability, impact, and scores |
| `assessment_report_ja.md` | Japanese risk assessment report: summary, country analysis, geopolitical evaluation |
| `supplier_scorecard.json` | 5-axis supplier scoring (quality, delivery, cost, flexibility, financial stability) |
| `mitigation_plan_ja.md` | Japanese mitigation plan with alternative strategies and safety stock plans |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Risk Identification | 0.25 | Completeness of risk identification with proper scoring |
| Supplier Scoring | 0.25 | Quality of multi-axis supplier evaluation |
| Japanese Report | 0.20 | Japanese language quality in assessment report and mitigation plan |
| Mitigation Quality | 0.15 | Actionability of mitigation strategies and alternative supplier plans |
| Framework Compliance | 0.15 | Adherence to ISO 31000 risk management methodology |

## Key Challenges
- Extracting comparable supplier metrics from three different languages and formats
- Applying ISO 31000 risk framework systematically to each supplier
- Evaluating geopolitical risks and incorporating them into supplier risk scores
- Identifying concentration risks (single-source dependencies) across the supply base
- Writing professional Japanese supply chain management reports with proper business terminology
