# Vietnamese Labor Contract Compliance Audit Against ILO Standards

## Overview
Tests the ability to audit Vietnamese labor contracts against both international ILO standards (in English) and Vietnamese domestic labor law, producing a comprehensive compliance report in Vietnamese.

## Scenario
An organization has three sample employment contracts in Vietnamese that need to be audited for compliance. The agent must compare these contracts against ILO convention requirements (in English), the Vietnamese Labor Code 2019 (in Vietnamese), and company HR policies (in English) to identify violations related to overtime limits, minimum rest periods, and probation durations, then produce a remediation plan.

## Language Configuration
- **Instruction Language**: Vietnamese
- **Source Material Languages**: Vietnamese, English
- **Target Output Language(s)**: Vietnamese
- **Complexity Level**: L3

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total_violations, high_risk_count, ilo_conventions_violated |
| `compliance_checklist_vi.md` | Compliance checklist evaluating each contract clause |
| `gap_analysis_vi.json` | Gap analysis between actual practice and legal requirements |
| `risk_items_vi.json` | Risk items with severity levels (high/medium/low) |
| `remediation_plan_vi.md` | Remediation plan with specific steps and deadlines |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Violation Detection | 30% | Accuracy in identifying non-compliant clauses |
| Legal Accuracy | 25% | Correct application of Vietnamese labor law and ILO standards |
| Vietnamese Quality | 20% | Professional Vietnamese legal writing |
| Remediation Quality | 15% | Practicality and specificity of remediation recommendations |
| Structural Completeness | 10% | All required outputs with proper formatting |

## Key Challenges
- Cross-referencing Vietnamese labor contracts with English ILO standards
- Identifying specific violations for overtime limits, rest periods, and probation
- Producing actionable remediation steps with realistic timelines
- Maintaining legal precision in Vietnamese output
