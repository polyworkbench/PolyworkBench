# Compile Multilingual Market Research into Russian Market Brief

## Overview
Tests the ability to compile market research from English, Chinese, and Korean sources into a comprehensive Russian-language EV battery market analysis with SWOT analysis and competitor profiling.

## Scenario
An analyst needs a comprehensive EV battery market overview in Russian. Source materials include an English analyst report, Chinese production/capacity data (CSV), Korean competitor quarterly filings (Samsung SDI, LG Energy Solution), and English pricing trend data. The agent must produce a 2000+ word Russian market brief, structured competitor analysis, market sizing with forecasts, and a SWOT analysis — all in professional Russian business analytics style.

## Language Configuration
- **Instruction Language**: Russian
- **Source Material Languages**: English, Chinese, Korean
- **Target Output Language(s)**: Russian
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: market_size_2024_billion_usd, market_size_2030_forecast, cagr_pct, top_3_players, key_trend |
| `market_brief_ru.md` | Comprehensive Russian market overview (min. 2000 words) |
| `competitor_analysis_ru.json` | Structured competitor profiles (min. 5 companies) |
| `market_sizing.json` | Market size data 2022-2030 with segmentation and CAGR |
| `swot_analysis_ru.json` | SWOT analysis with min. 3 items per category in Russian |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Market Sizing | 25% | Accuracy and justification of market figures |
| Competitor Analysis | 25% | Depth and completeness of competitive landscape |
| Russian Language Quality | 20% | Professional business analytics writing style |
| Data Synthesis | 15% | Effective integration across three language sources |
| SWOT Coherence | 15% | Logical consistency of SWOT analysis |

## Key Challenges
- Extracting production data from Chinese CSV format
- Synthesizing Korean corporate filings into competitive intelligence
- Producing consistent market sizing with CAGR calculations
- Writing in professional Russian business analytics register
