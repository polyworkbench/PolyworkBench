# Multi-Factory Operations Dashboard from Trilingual Data

## Overview
Tests the agent's ability to parse production and quality data from three factories reporting in Chinese, Vietnamese, and Korean, aggregate it into a unified English-language operations dashboard, calculate standardized KPIs, and detect statistical anomalies.

## Scenario
An operations management team oversees three factories in Shenzhen (China), Haiphong (Vietnam), and Busan (South Korea), each reporting daily production and quality metrics in their local language. The agent must correctly parse CSV files with Chinese, Vietnamese (with diacritics), and Korean column headers, aggregate data into a unified English dashboard with daily and weekly roll-ups, calculate all defined KPIs (OEE, yield rate, throughput, downtime percentage, defect rate) per factory, write a Python aggregation script that can reproduce the dashboard from raw CSVs, detect anomalies where KPIs deviate more than 2 standard deviations from the mean or miss targets by more than 15%, and generate a comparative KPI summary report.

## Language Configuration
- **Instruction Language**: English
- **Source Material Languages**: Chinese (Shenzhen factory), Vietnamese (Haiphong factory), Korean (Busan factory), English (KPI definitions)
- **Target Output Language(s)**: English
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary metrics across all factories |
| `dashboard_data.json` | Unified dashboard JSON with daily/weekly roll-ups per factory |
| `kpi_summary.md` | Markdown comparison table of all three factories across all KPIs |
| `aggregation_script.py` | Python script to reproduce dashboard from raw CSVs |
| `anomaly_report.json` | List of anomalies with factory, date, KPI, actual value, expected range, severity |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Data Aggregation | 0.30 | Correct parsing of trilingual CSVs and unified data structure |
| KPI Accuracy | 0.25 | Correctness of OEE, yield, throughput, downtime, defect rate calculations |
| Script Quality | 0.20 | Python aggregation script quality and reproducibility |
| Anomaly Detection | 0.15 | Statistical anomaly detection with proper thresholds |
| Report Quality | 0.10 | Clarity and completeness of KPI comparison report |

## Key Challenges
- Correctly parsing CSV files with Chinese, Vietnamese (diacritical marks), and Korean headers
- Mapping different column naming conventions to a unified English schema
- Calculating OEE (Overall Equipment Effectiveness) and its components correctly
- Implementing proper statistical anomaly detection (2-sigma rule)
- Building a reusable Python script that handles encoding and language-specific data formats
