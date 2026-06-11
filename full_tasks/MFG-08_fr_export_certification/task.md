# French CE Marking Documentation from Chinese Test Data

## Overview
Tests the agent's ability to map Chinese laboratory test results to European EN harmonized standards and produce French-language CE marking documentation including an EU Declaration of Conformity and technical report.

## Scenario
A manufacturer needs to prepare CE marking documentation for exporting a product to the European market. Test reports are available from a Chinese laboratory (in Chinese), along with English references to applicable EN harmonized standards and notified body information. The agent must analyze the Chinese test results and map them to corresponding EN standard requirements, write a formal French EU Declaration of Conformity following the regulatory format (referencing LVD 2014/35/EU, EMC 2014/30/EU, RoHS 2011/65/EU directives), write a French technical report summarizing product characteristics, test results with standard-to-result mapping, risk assessment, and conformity conclusions, create a structured test summary mapping each Chinese test to its EN standard equivalent, and produce a CE checklist indicating compliance status for each requirement.

## Language Configuration
- **Instruction Language**: French
- **Source Material Languages**: Chinese (test reports, product description), English (EN standards reference, notified body info)
- **Target Output Language(s)**: French
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary of conformity assessment results |
| `declaration_conformite_fr.md` | French EU Declaration of Conformity in regulatory format |
| `rapport_technique_fr.md` | French technical report with test results and risk assessment |
| `test_summary.json` | Structured mapping of Chinese tests to EN standards |
| `checklist_ce.json` | CE checklist with compliance status per requirement |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Declaration Compliance | 0.30 | Conformity of declaration to EU regulatory format requirements |
| French Quality | 0.25 | Professional French technical writing with regulatory terminology |
| Technical Accuracy | 0.20 | Correct mapping of test results to EN standard requirements |
| Standards Mapping | 0.15 | Accuracy of Chinese test to EN standard correspondence |
| Completeness | 0.10 | Coverage of all required elements in declaration and report |

## Key Challenges
- Understanding Chinese laboratory test report formats and extracting measured values
- Mapping Chinese test procedures to their equivalent EN harmonized standards
- Writing a legally compliant EU Declaration of Conformity in formal French
- Knowledge of EU directives (LVD, EMC, RoHS) and their documentary requirements
- Correctly referencing notified body involvement and applicable standard editions
