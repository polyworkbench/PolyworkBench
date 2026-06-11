# Multi-Market Product Launch Planning with 5-Language Synthesis

## Overview
Tests the agent's ability to synthesize market research data from five languages, detect contradictions between sources, and produce a Chinese strategic launch plan and English executive brief for a simultaneous multi-market product launch.

## Scenario
A Chinese headquarters is planning the simultaneous launch of a smart health wristband across four international markets (Japan, Korea, Russia, Vietnam). Market research reports are available in each country's language, alongside English competitive landscape data and Chinese budget constraints. The agent must synthesize insights from all five languages, identify contradictions between data sources (e.g., conflicting market size estimates or growth rates), develop a Chinese-language strategic launch plan with localization strategies per market, write a concise English executive brief, create a multi-market launch timeline considering optimal timing per market, and allocate resources within budget constraints while accounting for cultural differences and local consumer habits.

## Language Configuration
- **Instruction Language**: Chinese
- **Source Material Languages**: Japanese (JP market), Korean (KR market), Russian (RU market), Vietnamese (VN market), English (competitive landscape), Chinese (budget)
- **Target Output Language(s)**: Chinese (strategy plan), English (executive brief)
- **Complexity Level**: L6

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: markets, contradictions, launch order, budget, revenue forecast, go/no-go |
| `launch_plan_zh.md` | Chinese strategic launch plan (3000+ characters) |
| `executive_brief_en.md` | English executive brief (800-1500 words) |
| `market_synthesis.json` | Consolidated market data analysis results |
| `contradiction_report.json` | Detected contradictions between data sources |
| `timeline.json` | Multi-market launch timeline with phases and milestones |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Synthesis Quality | 0.20 | Quality of multi-language market data synthesis |
| Contradiction Detection | 0.20 | Detection of contradictions across data sources |
| Chinese Plan | 0.20 | Quality of Chinese strategic launch plan |
| English Brief | 0.15 | Quality of English executive brief |
| Timeline Feasibility | 0.15 | Feasibility and completeness of launch timeline |
| Data Accuracy | 0.10 | Accuracy of numerical data and budget alignment |

## Key Challenges
- Synthesizing market intelligence from five different languages into coherent insights
- Detecting when sources provide contradictory information (market sizes, growth projections)
- Balancing budget constraints across four markets with different cost structures
- Writing a 3000+ character Chinese strategic plan with proper business language
- Producing a concise English executive brief suitable for C-level audience
- Considering cultural nuances and optimal launch timing for each market
