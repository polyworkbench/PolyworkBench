# Korean PM Schedule from Japanese Manuals and Multilingual Maintenance Logs

## Overview
Tests the agent's ability to synthesize Japanese equipment manuals, English spare parts catalogs, and Chinese maintenance history to produce a Korean-language preventive maintenance (PM) schedule, maintenance guide, parts mapping, and failure pattern analysis.

## Scenario
A maintenance engineer at a manufacturing plant needs to establish a preventive maintenance program. Source materials include Japanese equipment operation/maintenance manuals, an English spare parts catalog with part numbers, pricing, and lead times, and Chinese-language historical maintenance records. The agent must create a comprehensive Korean PM schedule (daily/weekly/monthly/quarterly/annual), translate and adapt the Japanese manual into a practical Korean maintenance guide reflecting actual failure history, map parts across Japanese names, English part numbers, and Korean descriptions, analyze maintenance history for MTBF/MTTR patterns, and calculate safety stock recommendations based on lead times and failure frequencies.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: Japanese (equipment manual, specifications), English (spare parts catalog), Chinese (maintenance history)
- **Target Output Language(s)**: Korean
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total PM items, annual cost, critical items, avg MTBF/MTTR, spare parts count |
| `pm_schedule_ko.json` | Korean PM schedule with inspection items, intervals, personnel, parts needed |
| `maintenance_guide_ko.md` | Korean practical maintenance guide adapted from Japanese manual |
| `parts_mapping.json` | Trilingual parts mapping: Japanese name / English part number / Korean description |
| `maintenance_history_analysis.json` | Failure pattern analysis with MTBF, MTTR calculations |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Schedule Accuracy | 0.25 | PM schedule reflects both manufacturer recommendations and actual failure patterns |
| Korean Translation | 0.25 | Quality of Korean maintenance guide adapted from Japanese source |
| Parts Mapping | 0.20 | Correct trilingual mapping of parts across all three languages |
| History Analysis | 0.15 | Accuracy of MTBF/MTTR calculations and pattern identification |
| Completeness | 0.15 | Coverage of all PM items, cost estimates, priority classification |

## Key Challenges
- Translating technical Japanese maintenance instructions into practical Korean procedures
- Mapping spare parts across three naming systems (Japanese, English catalog numbers, Korean)
- Calculating MTBF and MTTR from Chinese-language maintenance log entries
- Balancing manufacturer-recommended PM intervals with actual failure history data
- Estimating annual maintenance costs and safety stock quantities from lead time data
