# Multi-Factory Operations Dashboard

In `/workspace/inputs/` you will find production and quality data from three factories operating in different countries, each reporting in their local language:

- `factory_shenzhen_zh.csv` — Daily production and quality metrics from the Shenzhen, China factory (in Chinese)
- `factory_haiphong_vi.csv` — Daily production and quality metrics from the Haiphong, Vietnam factory (in Vietnamese)
- `factory_busan_ko.csv` — Daily production and quality metrics from the Busan, South Korea factory (in Korean)
- `kpi_definitions_en.json` — KPI calculation formulas, targets, and thresholds in English

## Requirements

- Parse all three CSV files, correctly handling Chinese, Vietnamese (with diacritics), and Korean column headers and data values
- Aggregate the data into a unified English-language dashboard JSON (`dashboard_data.json`) with daily and weekly roll-ups per factory
- Calculate all KPIs defined in `kpi_definitions_en.json` for each factory (OEE, yield rate, throughput, downtime percentage, defect rate)
- Write a Python aggregation script (`aggregation_script.py`) that can reproduce the dashboard from the raw CSVs
- Detect anomalies: any day where a KPI deviates more than 2 standard deviations from the factory's mean, or misses the target by more than 15%
- Produce an anomaly report (`anomaly_report.json`) listing each anomaly with factory, date, KPI name, actual value, expected range, and severity
- Generate a KPI summary in Markdown (`kpi_summary.md`) with a table comparing all three factories across all KPIs, including trend indicators

## Output

Save all files to `/workspace/output/`:
- `dashboard_data.json`
- `kpi_summary.md`
- `aggregation_script.py`
- `anomaly_report.json`

Also save the final summary to `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
