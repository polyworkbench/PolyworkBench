# Rubric: MFG-06

## Dimension 1: Data Aggregation (Weight: 30%)
- **Excellent (9-10)**: Dashboard covering all 3 factories (Shenzhen, Haiphong, Busan), daily data, weekly rollups, and English field mapping from trilingual sources
- **Good (7-8)**: 2+ factories with daily data and field mapping
- **Adequate (5-6)**: Some factory data with partial structure
- **Poor (1-4)**: Minimal aggregation
- **Zero (0)**: No dashboard data

## Dimension 2: KPI Accuracy (Weight: 25%)
- **Excellent (9-10)**: 5+ KPIs calculated (OEE, yield, throughput, downtime, defect rate, energy efficiency), reasonable values (20+ numeric entries), targets referenced
- **Good (7-8)**: 4+ KPIs with reasonable values
- **Adequate (5-6)**: 2-3 KPIs calculated
- **Poor (1-4)**: Minimal KPI data
- **Zero (0)**: No KPI calculations

## Dimension 3: Script Quality (Weight: 20%)
- **Excellent (9-10)**: Python script that reads CSVs, handles encoding, calculates KPIs, and produces JSON output
- **Good (7-8)**: Script with 3-4 of required capabilities
- **Adequate (5-6)**: Script exists with basic functionality
- **Poor (1-4)**: Script with major gaps
- **Zero (0)**: No script

## Dimension 4: Anomaly Detection (Weight: 15%)
- **Excellent (9-10)**: Anomaly report with findings (power outages on Nov 6, Nov 10), severity levels, and complete fields (factory, date, KPI, value)
- **Good (7-8)**: Anomalies found with severity classification
- **Adequate (5-6)**: Some anomalies detected
- **Poor (1-4)**: Minimal detection
- **Zero (0)**: No anomaly report

## Dimension 5: Report Quality (Weight: 10%)
- **Excellent (9-10)**: KPI summary with markdown tables, all 3 factories compared, trend indicators (↑↓→)
- **Good (7-8)**: Report with tables and factory comparison
- **Adequate (5-6)**: Basic report without tables
- **Poor (1-4)**: Minimal report
- **Zero (0)**: No report

## Language Quality Assessment
- Target language output must be professional quality English
- Field names must be properly translated from Chinese/Vietnamese/Korean sources
- Technical terminology must be domain-appropriate for manufacturing operations
