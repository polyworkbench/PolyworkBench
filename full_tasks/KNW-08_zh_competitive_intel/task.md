# Chinese Competitive Intelligence from EN/KO/JA Sources

## Overview
Tests the ability to gather competitive intelligence from English, Korean, and Japanese sources about AI chip competitors and produce a strategic Chinese-language competitive digest.

## Scenario
A Chinese AI chip company needs a competitive intelligence briefing on three competitors: NovaTech (US, English press releases), SiliconWave (Korea, Korean press releases), and QuantumCore (Japan, Japanese product announcements). The agent must analyze each competitor's latest moves, create threat profiles, assess threats to each product line, and provide strategic recommendations — all in Chinese with specific data citations (market share, product specs, release dates).

## Language Configuration
- **Instruction Language**: Chinese
- **Source Material Languages**: English, Korean, Japanese
- **Target Output Language(s)**: Chinese
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `competitive_digest_zh.md` | Chinese competitive intelligence digest (1000-2000 characters) |
| `competitor_profiles.json` | Structured profiles with threat levels (1-5) |
| `threat_analysis_zh.json` | Per-product-line threat assessment |
| `strategic_implications_zh.md` | Strategic analysis with min. 5 recommendations |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Intelligence Extraction | 25% | Thorough extraction of competitor information |
| Threat Assessment | 25% | Logical and calibrated threat level ratings |
| Strategic Insight | 20% | Quality of strategic recommendations |
| Data Citations | 15% | Specific quantitative data referenced throughout |
| Chinese Business Writing | 15% | Professional Chinese competitive intelligence style |

## Key Challenges
- Extracting actionable intelligence from press releases in three languages
- Calibrating threat levels across different product lines
- Referencing specific quantitative metrics (market share, product parameters)
- Providing time-urgency assessments for competitive responses
- Writing in professional Chinese competitive intelligence format
