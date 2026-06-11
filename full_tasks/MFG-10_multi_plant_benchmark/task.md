# Five-Country Plant Benchmarking with Inconsistency Detection

## Overview
Tests the agent's ability to normalize manufacturing performance data from five plants reporting in five different languages, compute standardized KPIs, detect data reporting inconsistencies, and produce a comprehensive English benchmarking report with a reusable Python analysis script.

## Scenario
A corporate manufacturing excellence team oversees five plants across China (Shenzhen), Vietnam (Haiphong), South Korea (Busan), Japan (Osaka), and Russia (Kaluga), each reporting monthly metrics in their local language. The agent must parse CSV files with headers in Chinese, Vietnamese (with diacritics), Korean, Japanese (kanji/katakana), and Russian (Cyrillic), normalize all data to a common English schema using a provided benchmarking methodology, compute standardized KPIs (OEE, yield, throughput per capita, energy efficiency, safety incident rate, on-time delivery), detect reporting inconsistencies suggesting data quality issues (suspiciously constant values, cross-validation failures, physically implausible outliers, selective reporting patterns), create a Python analysis script that performs all normalization and detection, and write an English executive benchmarking report with rankings, per-plant assessment, and strategic recommendations.

## Language Configuration
- **Instruction Language**: English
- **Source Material Languages**: Chinese (Shenzhen), Vietnamese (Haiphong), Korean (Busan), Japanese (Osaka), Russian (Kaluga), English (methodology)
- **Target Output Language(s)**: English
- **Complexity Level**: L6

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary metrics and findings |
| `benchmark_report.md` | English executive benchmarking report with rankings and recommendations |
| `plant_comparison.json` | Normalized comparable data across all five plants |
| `inconsistency_findings.json` | Documented inconsistencies with plant, metric, evidence, confidence |
| `recommendations.json` | Prioritized improvement recommendations per plant |
| `analysis_script.py` | Python script: reads CSVs, normalizes, calculates, detects anomalies |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Data Normalization | 0.20 | Correct parsing and normalization of five-language CSV data |
| Inconsistency Detection | 0.20 | Detection of data quality issues and reporting anomalies |
| Comparative Analysis | 0.20 | Quality of cross-plant benchmarking and ranking |
| Script Quality | 0.15 | Python analysis script quality and reproducibility |
| Report Quality | 0.15 | English executive report with actionable strategic insights |
| Recommendations | 0.10 | Prioritized, plant-specific improvement recommendations |

## Key Challenges
- Parsing CSV files with five different scripts/character sets and encoding handling
- Normalizing heterogeneous data formats to a single comparable schema
- Detecting subtle data quality issues (zero variance, cross-validation failures, implausible outliers)
- Distinguishing genuine performance differences from reporting artifacts
- Computing meaningful benchmarks when plants have different product mixes and scales
- Writing a robust Python script that handles all five languages and edge cases
