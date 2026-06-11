# China-Russia vs China-Vietnam Logistics Route Comparison with Russian Report

## Overview
Tests the agent's ability to compare logistics routes from China to Russia and China to Vietnam using multilingual data sources, build a cost calculator, and produce a Russian-language analytical report with route recommendations.

## Scenario
A logistics optimization team needs a comparative analysis of shipping routes from China to Russia versus China to Vietnam. The agent must extract and systematize route data from Chinese logistics providers (in Chinese), Vietnamese logistics providers (in Vietnamese), and international carrier rates (in English), calculate total delivery costs for each route including transport, customs, and last-mile components, compare delivery timelines including customs clearance, build a Python cost calculator parameterized by weight, volume, product type, and route, and produce a comprehensive Russian-language analytical report with recommendations for optimal routes by product category.

## Language Configuration
- **Instruction Language**: Russian
- **Source Material Languages**: Chinese (logistics providers), Vietnamese (logistics providers), English (carrier rates, customs timelines)
- **Target Output Language(s)**: Russian
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: routes analyzed, cheapest/fastest per destination, cost/time differences |
| `logistics_comparison_ru.md` | Russian-language analytical report with full comparison |
| `route_analysis.json` | Structured analysis of all routes with costs and times |
| `cost_calculator.py` | Python cost calculator script with parameterized inputs |
| `recommendations_ru.json` | Russian-language recommendations by product category |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Route Comparison | 0.25 | Completeness of route comparison across destinations |
| Cost Calculations | 0.25 | Accuracy of cost and time calculations |
| Russian Report | 0.20 | Quality of Russian language report |
| Script Quality | 0.15 | Cost calculator script quality |
| Recommendations | 0.15 | Quality and actionability of recommendations |

## Key Challenges
- Extracting comparable logistics data from three languages with different measurement units
- Calculating total cost including multiple components (freight, customs, last mile)
- Comparing routes fairly when they have different intermediate stops and timelines
- Building a parameterized calculator that handles different product categories
- Writing analytical Russian with proper logistics and supply chain terminology
