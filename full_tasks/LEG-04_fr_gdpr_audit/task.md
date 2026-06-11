# French GDPR Audit Report from English Privacy Policy and German Ruling

## Overview
Tests the ability to conduct a multi-jurisdictional GDPR compliance audit using source materials in English, French, and German, producing a comprehensive French-language audit report.

## Scenario
A SaaS company's privacy policy (in English) must be audited against GDPR requirements, using CNIL guidance (in French) and a German court ruling on consent requirements (in German) as reference materials. The agent must identify non-conformities, assess Schrems II implications, determine if a DPIA is required, and produce all deliverables using proper French legal terminology.

## Language Configuration
- **Instruction Language**: French
- **Source Material Languages**: English, French, German
- **Target Output Language(s)**: French
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total_nonconformities, critical_issues, schrems_ii_violation, dpia_required |
| `rapport_audit_fr.md` | Comprehensive GDPR audit report identifying all non-conformities |
| `conformite_matrix.json` | Compliance matrix mapping GDPR articles to compliance status |
| `plan_action_fr.json` | Action plan with corrective measures, priorities, and deadlines |
| `synthese_risques_fr.md` | Risk synthesis with impact analysis |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Non-conformity Detection | 30% | Completeness of GDPR violation identification |
| Legal Precision | 25% | Correct application of GDPR, CNIL guidance, and German case law |
| French Legal Terminology | 20% | Proper use of French data protection legal terms |
| Action Plan Quality | 15% | Practicality and prioritization of remediation measures |
| Cross-jurisdictional Analysis | 10% | Integration of French and German legal perspectives |

## Key Challenges
- Reading German legal text (court ruling) alongside English and French sources
- Applying correct French GDPR terminology (responsable de traitement, sous-traitant, etc.)
- Assessing Schrems II cross-border transfer implications
- Determining DPIA requirements for profiling activities
