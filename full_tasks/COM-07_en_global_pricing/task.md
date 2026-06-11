# Cross-Market Pricing Validation and English Strategy Memo

## Overview
Tests the agent's ability to cross-validate product pricing across 4 international markets (China, Russia, South Korea, Vietnam) in their respective languages, detect pricing inconsistencies, identify arbitrage risks, and produce an English pricing strategy memo with a reusable validation script.

## Scenario
A global pricing team needs to validate product pricing consistency across four markets, each reporting prices in their local language and currency. The agent must convert all prices to USD using provided exchange rates, identify products priced more than 15% differently across markets, flag global margin policy violations, detect potential gray market arbitrage opportunities (price gaps >25%), perform statistical analysis of price gaps, create a reusable Python validation script, and write a strategic pricing memo with market-specific recommendations.

## Language Configuration
- **Instruction Language**: English
- **Source Material Languages**: Chinese (CN pricing), Russian (RU pricing), Korean (KR pricing), Vietnamese (VN pricing), English (FX rates, margin policy)
- **Target Output Language(s)**: English
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: product count, inconsistencies, violations, arbitrage opportunities |
| `pricing_analysis.json` | Full cross-market analysis with USD-normalized prices |
| `inconsistency_report.md` | Detailed report of all pricing inconsistencies |
| `pricing_strategy.md` | Strategic memo with market-specific recommendations |
| `market_comparison.json` | Product x Market x Price comparison matrix |
| `validation_script.py` | Reusable Python validation script |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Pricing Validation | 0.25 | Cross-market price validation with FX conversion |
| Inconsistency Detection | 0.25 | Detection of pricing inconsistencies and arbitrage risks |
| Strategy Memo | 0.20 | Quality of English pricing strategy memo |
| Script Quality | 0.15 | Validation script quality and reusability |
| Data Accuracy | 0.15 | Accuracy of numerical analysis and data handling |

## Key Challenges
- Parsing pricing data from four different languages with different currency formats
- Correct FX conversion and normalization to a common currency (USD)
- Statistical analysis: mean, median, standard deviation of price gaps per product
- Understanding margin policy rules and applying them correctly per product category
- Identifying economically meaningful arbitrage opportunities vs. acceptable variation
- Writing a reusable script that can handle future price updates
