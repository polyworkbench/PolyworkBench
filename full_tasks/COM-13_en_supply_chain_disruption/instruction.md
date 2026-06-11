# Supply Chain Disruption Analysis & Decision Report

## Context

You are the VP of Supply Chain Operations for a global electronics manufacturer. Multiple disruptions have been reported across your supplier network in South Korea, China, and Southeast Asia. You must analyze multilingual intelligence sources, assess risk levels, and produce an actionable decision report.

## Source Data

The following files are in the `inputs/` directory:

1. **ko_supplier_alerts.md** — Supplier alert reports from Korean partners (in Korean)
2. **zh_logistics_delays.md** — Logistics delay reports from Chinese freight partners (in Chinese)
3. **en_demand_forecast.csv** — Q2 2024 demand forecast by product line (in English)
4. **en_inventory_status.csv** — Current inventory levels and reorder points (in English)

## Required Tasks

### 1. Supplier Risk Assessment
Analyze the Korean supplier alerts and identify critical suppliers:
- **SKR-7** (Seoul Semiconductor): Risk score 92/100 — chip shortage, 6-week delay
- **SZH-3** (Shenzhen HiTech): Risk score 87/100 — factory fire, partial capacity
- **SEN-2** (SE Asia Network): Risk score 78/100 — port congestion, 3-week delay

### 2. Logistics Impact Analysis
Process the Chinese logistics reports to understand:
- Current port congestion levels
- Estimated delay impacts on delivery schedules
- Alternative routing options

### 3. Financial Risk Quantification
- Total supply chain risk exposure: **$2.4M**
- Breakdown by supplier and product line
- Impact on Q2 revenue projections

### 4. Output Files

#### decision_report.md
Executive decision report including:
- Executive summary with key findings
- Risk assessment by supplier (with scores)
- Financial impact analysis ($2.4M total exposure)
- Recommended actions with timelines
- Contingency plans

#### action_plan.json
```json
{
  "immediate_actions": [
    {
      "priority": 1,
      "action": "Activate secondary chip supplier for SKR-7 shortage",
      "supplier": "SKR-7",
      "timeline_days": 7,
      "estimated_cost": 450000
    },
    {
      "priority": 2,
      "action": "Reroute shipments through alternate port for SZH-3",
      "supplier": "SZH-3",
      "timeline_days": 14,
      "estimated_cost": 280000
    },
    {
      "priority": 3,
      "action": "Increase safety stock for SE Asia components",
      "supplier": "SEN-2",
      "timeline_days": 21,
      "estimated_cost": 180000
    }
  ],
  "total_mitigation_cost": 910000,
  "risk_reduction_percentage": 65
}
```

#### risk_matrix.json
```json
{
  "critical_suppliers": [
    {
      "id": "SKR-7",
      "name": "Seoul Semiconductor",
      "risk_score": 92,
      "max_score": 100,
      "impact_category": "critical",
      "financial_exposure_usd": 1100000,
      "delay_weeks": 6
    },
    {
      "id": "SZH-3",
      "name": "Shenzhen HiTech",
      "risk_score": 87,
      "max_score": 100,
      "impact_category": "critical",
      "financial_exposure_usd": 850000,
      "delay_weeks": 4
    },
    {
      "id": "SEN-2",
      "name": "SE Asia Network",
      "risk_score": 78,
      "max_score": 100,
      "impact_category": "high",
      "financial_exposure_usd": 450000,
      "delay_weeks": 3
    }
  ],
  "total_financial_exposure_usd": 2400000,
  "assessment_date": "2024-03-15"
}
```

## Success Criteria

- All 3 critical suppliers identified with correct risk scores (SKR-7:92, SZH-3:87, SEN-2:78)
- Total risk quantified at $2.4M
- Action plan with prioritized mitigations
- All output files generated in specified format
- Analysis demonstrates understanding of Korean and Chinese source materials

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
