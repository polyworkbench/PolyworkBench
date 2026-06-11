# SCADA Alert Correlation and Root Cause Clustering

## Objective

You are a reliability engineer. Analyze 30 SCADA alerts from the past week and group them into root cause clusters. Cross-reference with maintenance tickets and shift reports to identify true positives vs false alarms.

## Input Files

- `/workspace/inputs/scada_alerts_ja.json` - Japanese SCADA alert data (30 alerts)
- `/workspace/inputs/maintenance_tickets_en.txt` - English maintenance tickets (10 tickets)
- `/workspace/inputs/shift_reports_vi.txt` - Vietnamese shift reports (3 shifts)

## Task

1. Parse SCADA alerts (Japanese) and extract alert IDs, timestamps, equipment, descriptions
2. Parse maintenance tickets (English) and correlate with alerts
3. Parse shift reports (Vietnamese) to identify operator-reported issues and false alarms
4. Group alerts into root cause clusters:
   - Cluster A (bearing wear): Alerts 1,5,8,12,19
   - Cluster B (power fluctuation): Alerts 3,7,14,22,27
   - Cluster C (sensor drift - FALSE ALARMS): Alerts 2,9,15,23
   - Cluster D (coolant leak): Alerts 4,11,18,25,30
   - Cluster E (operator error): Alerts 6,10,16,20,24,28
   - Unclassified: Alerts 13,17,21,26,29
5. Link clusters to maintenance tickets where applicable

## Required Outputs (/workspace/output/)

### alert_clusters.json
{"clusters": [{"id": "A", "name": "...", "alerts": [...], "ticket": "...", "is_false_alarm": false}]}

### correlation_report.md
Detailed English report with analysis

### false_alarm_analysis.json
{"false_alarms": [...], "total_false": 4, "total_true": 26}

### /workspace/answer.json
{"total_clusters": 5, "false_alarm_count": 4, "true_positive_count": 21, "unclassified_count": 5, "largest_cluster": "E", "ticket_linked_clusters": 3}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
