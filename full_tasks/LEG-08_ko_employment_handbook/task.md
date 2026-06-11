# Korean Employee Handbook Localization from English Source

## Overview
Tests the ability to localize a global employee handbook from English to Korean, adapting content to comply with Korean labor law rather than merely translating it.

## Scenario
A multinational company's English employee handbook (~20 policies) needs to be localized for the Korean subsidiary. The adaptation must comply with the Korean Labor Standards Act, incorporate existing Korean subsidiary rules, and reflect recent HR policy updates. Key localization points include annual leave (Korean statutory minimums), the 52-hour work week cap, 30-day written termination notice, mandatory severance pay, and maternity leave requirements.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: English, Korean
- **Target Output Language(s)**: Korean
- **Complexity Level**: L3

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `handbook_ko.md` | Fully localized Korean employee handbook |
| `change_log_ko.json` | All changes/additions/deletions with reasons |
| `compliance_notes_ko.json` | Per-policy Korean law compliance notes and risks |
| `legal_references_ko.json` | Structured list of all referenced Korean legal provisions |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Legal Compliance | 30% | Correct adaptation to Korean labor law requirements |
| Localization Quality | 25% | Natural Korean business writing (not literal translation) |
| Change Documentation | 20% | Completeness of change log with proper justification |
| Consistency | 15% | Alignment with existing Korean subsidiary rules |
| Reference Accuracy | 10% | Correct citation of Korean legal provisions |

## Key Challenges
- Adapting (not just translating) policies to Korean labor law requirements
- Correctly applying Korean statutory minimums (annual leave, work hours, severance)
- Maintaining consistency with existing company rules in Korean
- Documenting all changes with proper legal justification
