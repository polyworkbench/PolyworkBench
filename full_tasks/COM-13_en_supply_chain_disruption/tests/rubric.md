# Rubric: COM-13 Supply Chain Disruption Analysis

## Overview
This task evaluates the ability to process multilingual intelligence sources (Korean, Chinese, English), assess supply chain risks, and produce actionable decision documents.

## Scoring Criteria (7 points total)

### 1. Decision Report Exists (1 point)
- File `decision_report.md` exists
- References all 3 critical suppliers (SKR-7, SZH-3, SEN-2)
- Comprehensive content (>800 characters)

### 2. Financial Risk in Report (1 point)
- Report mentions total risk exposure of $2.4M
- Breakdown by supplier included

### 3. Action Plan (1 point)
- File `action_plan.json` exists with valid JSON
- Contains at least 3 prioritized immediate actions
- References all 3 suppliers

### 4. Risk Matrix Exists (1 point)
- File `risk_matrix.json` exists with valid JSON
- Contains at least 3 critical suppliers

### 5. Risk Scores (1 point)
- SKR-7: 92/100
- SZH-3: 87/100
- SEN-2: 78/100

### 6. Total Financial Exposure (1 point)
- Total exposure = $2,400,000 ($2.4M)

### 7. Supplier Financial Breakdown (1 point)
- SKR-7: $1,100,000
- SZH-3: $850,000
- SEN-2: $450,000
- Sum = $2,400,000

## Ground Truth Values
- **Critical Suppliers**: SKR-7 (Seoul Semiconductor), SZH-3 (Shenzhen HiTech), SEN-2 (SE Asia Network)
- **Risk Scores**: 92, 87, 78 (out of 100)
- **Total Financial Exposure**: $2,400,000
- **Breakdown**: SKR-7=$1.1M, SZH-3=$850K, SEN-2=$450K
- **Delay Periods**: SKR-7=6 weeks, SZH-3=4 weeks, SEN-2=3 weeks
- **Root Causes**: Chip shortage (SKR-7), Factory fire (SZH-3), Port congestion (SEN-2)
