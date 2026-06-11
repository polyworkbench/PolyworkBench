# Chinese Quality Alert from Vietnamese QC Logs and English Specifications

## Overview
Tests the agent's ability to analyze Vietnamese QC inspection logs and English product specifications, then generate a Chinese-language quality alert document with root cause analysis (5M1E method) and corrective action plan conforming to ISO 9001 standards.

## Scenario
A quality engineer needs to issue a formal quality alert based on defects detected by Vietnamese QC inspectors. The agent must parse Vietnamese-language inspection logs to extract defect descriptions, compare actual measurements against English specification tolerances, correlate production parameters (in Chinese) with defect occurrences, perform root cause analysis using the 5M1E (Man, Machine, Material, Method, Measurement, Environment) fishbone methodology, classify all defects by type and severity (Critical/Major/Minor), and produce a Chinese-language quality alert document following ISO 9001 format with both containment actions and long-term corrective measures.

## Language Configuration
- **Instruction Language**: Chinese
- **Source Material Languages**: Vietnamese (QC inspection logs), English (product specifications), Chinese (production parameters)
- **Target Output Language(s)**: Chinese
- **Complexity Level**: L3

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: alert level, total/critical defects, affected batches, top root cause |
| `quality_alert_zh.md` | Chinese quality alert: level, scope, description, emergency measures |
| `root_cause_analysis.json` | 5M1E fishbone analysis with categorized causes |
| `defect_classification.json` | Defect types, severity, frequency, affected batches |
| `corrective_actions_zh.json` | Short-term and long-term corrective actions with owners and deadlines |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Defect Detection | 0.30 | Accuracy of defect extraction from Vietnamese QC logs |
| Root Cause Analysis | 0.25 | Quality of 5M1E analysis with parameter correlation |
| Chinese Alert | 0.20 | Professional Chinese quality alert following ISO 9001 format |
| Classification | 0.15 | Correct severity classification and frequency analysis |
| Corrective Actions | 0.10 | Actionable short-term and long-term corrective measures |

## Key Challenges
- Extracting structured defect data from Vietnamese-language QC inspection comments
- Comparing measured values against English specification tolerances to identify out-of-spec items
- Correlating Chinese production parameters with defect patterns to identify root causes
- Applying the 5M1E (fishbone) root cause analysis methodology systematically
- Writing a formal Chinese quality alert that conforms to ISO 9001 documentation standards
