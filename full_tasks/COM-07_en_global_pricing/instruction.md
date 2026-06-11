# Cross-Market Pricing Validation & Strategy

## Task Overview

Cross-validate product pricing across 4 international markets (China/CNY, Russia/RUB, South Korea/KRW, Vietnam/VND), identify pricing inconsistencies that violate global margin policy, and produce an English-language pricing strategy memo with recommendations.

## Input Files

- `/workspace/inputs/pricing_china_zh.csv` — Chinese domestic pricing in CNY (Simplified Chinese)
- `/workspace/inputs/pricing_russia_ru.csv` — Russian marketplace prices in RUB (Russian)
- `/workspace/inputs/pricing_korea_ko.csv` — Korean market prices in KRW (Korean)
- `/workspace/inputs/pricing_vietnam_vi.csv` — Vietnamese market prices in VND (Vietnamese)
- `/workspace/inputs/fx_rates.json` — Current exchange rates (all to USD)
- `/workspace/inputs/margin_policy_en.md` — Global margin policy guidelines

## Requirements

- Convert all prices to USD using provided exchange rates for cross-market comparison
- Identify pricing inconsistencies: products priced >15% differently across markets after FX conversion
- Flag any products violating the global margin policy (minimum margins by category)
- Detect potential gray market arbitrage opportunities (price gaps >25%)
- Create a validation script that can be rerun when prices change
- Produce a market comparison matrix showing normalized prices across all 4 markets
- Write a strategic pricing memo with specific recommendations for each market
- Include statistical analysis: mean, median, std deviation of price gaps per product

## Output

Save the following to `/workspace/output/`:

1. `pricing_analysis.json` — Full cross-market pricing analysis with USD-normalized prices
2. `inconsistency_report.md` — Detailed report of all pricing inconsistencies found
3. `pricing_strategy.md` — Strategic memo with market-specific recommendations
4. `market_comparison.json` — Comparison matrix (product × market × price)
5. `validation_script.py` — Reusable Python validation script

Also output `/workspace/answer.json`:
```json
{
  "total_products": <int>,
  "inconsistency_count": <int>,
  "margin_violations": <int>,
  "arbitrage_opportunities": <int>,
  "most_inconsistent_product": "<product_id>",
  "recommended_adjustments": <int>,
  "markets_analyzed": ["CN", "RU", "KR", "VN"]
}
```

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
