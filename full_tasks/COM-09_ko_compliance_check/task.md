# Multi-Framework Regulatory Compliance Check with Korean Output

## Overview
Tests the agent's ability to cross-check product compliance against three international regulatory frameworks (US FDA, Chinese GB standards, Japanese JIS specifications) in their source languages, and produce a Korean-language compliance matrix, gap analysis, and corrective action plan.

## Scenario
A product compliance team needs to verify whether their products meet regulatory requirements across three major markets: the US (FDA), China (GB national standards), and Japan (JIS specifications). The agent must analyze requirements from English FDA documentation, Chinese GB standards text, and Japanese JIS specifications, create a compliance matrix showing conformity status for each product against each framework, identify specific gaps where products fail to meet requirements, detect conflicting requirements between frameworks, and produce all outputs in Korean with original regulation codes preserved.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: English (FDA requirements, product specs), Chinese (GB standards), Japanese (JIS specifications)
- **Target Output Language(s)**: Korean
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: products, requirements checked, compliance counts, critical gaps |
| `compliance_matrix_ko.json` | Product-by-regulation compliance matrix in Korean |
| `gap_analysis_ko.md` | Korean gap analysis report with identified non-conformities |
| `action_items_ko.json` | Corrective action items in Korean with priorities, costs, timelines |
| `regulatory_summary.json` | Structured regulatory requirement summary |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Compliance Accuracy | 0.30 | Accuracy of compliance matrix across three frameworks |
| Gap Detection | 0.25 | Quality of gap identification and conflict detection |
| Korean Output | 0.20 | Korean language quality and consistency |
| Action Items | 0.15 | Quality of corrective action items with priorities |
| Regulatory Mapping | 0.10 | Mapping between regulatory frameworks |

## Key Challenges
- Understanding technical regulatory requirements in three different languages (English, Chinese, Japanese)
- Identifying when requirements from different frameworks conflict with each other
- Applying consistent compliance judgments (compliant/partial/non-compliant/N/A)
- Estimating remediation costs and timelines for identified gaps
- Writing technical Korean with proper regulatory terminology while preserving original standard codes
