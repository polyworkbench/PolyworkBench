# Multi-Warehouse Inventory Reconciliation and Japanese Demand Forecast

## Overview
Tests the agent's ability to reconcile inventory data across Chinese warehouses and Korean 3PL systems, create a demand forecasting Python script incorporating Japanese holiday calendars, and produce a Japanese-language forecast report.

## Scenario
A Japanese market supply chain team needs to reconcile inventory data from a Chinese warehouse (30 SKUs, in Chinese) and a Korean third-party logistics provider (in Korean) with English sales history, then forecast demand for the next 3 months. The forecast must account for Japanese holiday-driven demand spikes (Golden Week, Obon, year-end). The agent must identify inventory discrepancies between the two sources, build an executable Python forecasting script with Japanese comments, and produce a structured Japanese-language demand forecast report.

## Language Configuration
- **Instruction Language**: Japanese
- **Source Material Languages**: Chinese (warehouse inventory), Korean (3PL data), English (sales history)
- **Target Output Language(s)**: Japanese
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total SKUs, discrepancy count, forecast period, top demand SKUs, holiday impact |
| `inventory_reconciliation.json` | Per-SKU inventory levels, locations, and reconciliation status |
| `forecast_report_ja.md` | Japanese-language demand forecast report with chart-ready data |
| `forecast_script.py` | Executable Python forecasting script with Japanese comments |
| `discrepancies.json` | Detailed inventory discrepancies with estimated causes |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Reconciliation | 0.25 | Inventory reconciliation accuracy and completeness |
| Forecast Quality | 0.25 | Quality of demand forecast with holiday integration |
| Script Execution | 0.20 | Forecast script quality and executability |
| Japanese Report | 0.20 | Japanese language quality and report structure |
| Discrepancy Detection | 0.10 | Detection and explanation of inventory discrepancies |

## Key Challenges
- Reconciling inventory data across Chinese and Korean systems with different naming conventions
- Building a demand forecast that properly incorporates Japanese holiday patterns (GW, Obon, Nenmatsu-Nenshi)
- Writing an executable Python script with meaningful Japanese-language comments
- Producing a well-structured Japanese business report with appropriate formality
- Handling SKU matching across systems using different languages and ID formats
