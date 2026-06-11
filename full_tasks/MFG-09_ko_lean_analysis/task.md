# Korean Lean Manufacturing Improvement Plan from Multilingual Sources

## Overview
Tests the agent's ability to apply Toyota Production System (TPS) principles from Japanese documentation, analyze English lean metrics and Chinese shop floor data, identify the 7 wastes, and produce a Korean-language lean analysis report with value stream mapping and phased improvement plan.

## Scenario
A Korean manufacturing engineering team wants to implement lean manufacturing improvements based on TPS (Toyota Production System) principles. The agent must analyze Japanese-language TPS principles documentation to understand core concepts (Jidoka, Just-in-Time, Kaizen, Muda elimination), evaluate current production line performance using English lean metrics (takt time, cycle time, OEE), identify the 7 wastes (overproduction, waiting, transport, over-processing, inventory, motion, defects) from Chinese shop floor observation data, create a value stream map (VSM) in JSON format with per-process cycle times, wait times, WIP quantities, and value-add ratios, produce a comprehensive Korean lean analysis report, and develop a phased improvement plan (short/medium/long-term) with expected benefits and investment requirements.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: Japanese (TPS principles), English (lean metrics/KPIs), Chinese (shop floor observation data)
- **Target Output Language(s)**: Korean
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary of lean analysis findings |
| `lean_analysis_ko.md` | Korean lean analysis report: current state, TPS evaluation, 7 wastes, OEE |
| `value_stream_map.json` | VSM data: per-process cycle time, wait time, WIP, value-add ratio, lead time |
| `improvement_plan_ko.json` | Phased Korean improvement plan: short/medium/long-term with costs and priorities |
| `metrics_comparison.json` | Current values vs. targets vs. industry benchmarks |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| TPS Application | 0.25 | Correct application of Toyota Production System principles |
| Metrics Analysis | 0.25 | Accuracy of lean metrics calculation and waste identification |
| Korean Quality | 0.20 | Natural Korean manufacturing engineering terminology |
| Improvement Feasibility | 0.15 | Realistic improvement plan with proper phasing and cost estimates |
| VSM Accuracy | 0.15 | Correctness of value stream map data and lead time calculations |

## Key Challenges
- Understanding Japanese TPS concepts (jidoka, JIT, kaizen, muda) and their practical application
- Correctly identifying the 7 wastes from Chinese-language shop floor observations
- Calculating value-add ratios and overall lead time from process-level data
- Developing realistic phased improvement plans with appropriate cost/benefit analysis
- Writing in Korean with proper lean manufacturing and industrial engineering terminology
