# Multi-Plant Performance Benchmarking & Inconsistency Detection

In `/workspace/inputs/` you will find operations data from five manufacturing plants across five countries, each reporting in their local language:

- `plant_china_zh.csv` — Shenzhen plant monthly metrics (Chinese)
- `plant_vietnam_vi.csv` — Haiphong plant monthly metrics (Vietnamese)
- `plant_korea_ko.csv` — Busan plant monthly metrics (Korean)
- `plant_japan_ja.csv` — Osaka plant monthly metrics (Japanese)
- `plant_russia_ru.csv` — Kaluga plant monthly metrics (Russian)
- `benchmark_methodology_en.json` — Standardized benchmarking methodology and normalization rules

## Requirements

- Parse all five CSV files, handling Chinese, Vietnamese (diacritics), Korean, Japanese (kanji/katakana), and Russian (Cyrillic) column headers
- Normalize all data to a common English schema using the methodology in `benchmark_methodology_en.json`
- Compute standardized KPIs for each plant: OEE, yield, throughput per capita, energy efficiency, safety incident rate, on-time delivery
- Create a Python analysis script (`analysis_script.py`) that:
  - Reads all 5 CSVs
  - Normalizes column names and units
  - Calculates comparable metrics
  - Detects statistical anomalies and reporting inconsistencies
- Detect reporting inconsistencies — patterns that suggest data quality issues:
  - Suspiciously constant values (zero variance)
  - Metrics that don't cross-validate (e.g., OEE components don't multiply to reported OEE)
  - Outliers that are physically implausible
  - Missing data patterns that suggest selective reporting
- Generate `inconsistency_findings.json` documenting each finding with plant, metric, evidence, and confidence level
- Create `plant_comparison.json` with normalized comparable data across all plants
- Write an executive summary (`benchmark_report.md`) in English including:
  - Overall rankings
  - Strengths and weaknesses per plant
  - Data quality assessment
  - Strategic recommendations
- Create `recommendations.json` with prioritized improvement recommendations per plant

## Output

Save all files to `/workspace/output/`:
- `benchmark_report.md`
- `plant_comparison.json`
- `inconsistency_findings.json`
- `recommendations.json`
- `analysis_script.py`

Also save the final summary to `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
