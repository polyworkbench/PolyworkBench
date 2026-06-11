# Russian Legal Memo from English-Chinese Contract Review

## Overview
Tests the ability to perform cross-lingual contract analysis between English and Chinese documents and produce a structured legal memorandum in Russian identifying conflicts and risks.

## Scenario
A supply agreement exists in two forms: a master agreement in English and a supplementary side letter in Chinese. The agent must compare both documents to identify contradictions, determine document priority under applicable law, assess risk severity, and produce a formal legal opinion in Russian with recommendations for resolving the conflicts.

## Language Configuration
- **Instruction Language**: Russian
- **Source Material Languages**: English, Chinese
- **Target Output Language(s)**: Russian
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total_conflicts, high_risk_count, primary_jurisdiction_conflict |
| `legal_memo_ru.md` | Formal legal memorandum in Russian identifying all conflicts |
| `risk_register.json` | Risk register with severity ratings (high/medium/low) |
| `conflict_analysis.json` | Structured analysis mapping specific clauses in both documents |
| `recommendations_ru.md` | Recommendations for resolving contradictions under applicable law |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Conflict Identification | 30% | Completeness and accuracy of detected contradictions |
| Legal Analysis Quality | 25% | Depth of legal reasoning and jurisdiction analysis |
| Russian Language Quality | 20% | Professional legal Russian writing style |
| Risk Assessment | 15% | Appropriateness of severity ratings and prioritization |
| Structural Completeness | 10% | Proper formatting and all required sections present |

## Key Challenges
- Reading and comparing legal documents across English and Chinese
- Applying correct legal terminology in Russian output
- Determining document hierarchy and priority under governing law
- Producing structured JSON risk assessments alongside narrative legal writing
