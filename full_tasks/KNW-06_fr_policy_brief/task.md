# French Policy Brief from Trilingual Sources

## Overview
Tests the ability to synthesize policy research from English, Chinese, and Russian sources into a formal French policy brief on AI regulation, following French institutional writing conventions.

## Scenario
A policy advisor needs a French-language policy note on AI governance. Source materials include an English policy paper on AI governance, Chinese government AI development plan excerpts, a Russian think-tank analysis on AI governance, a French EU AI Act summary (context), and global AI market statistics (English JSON). The agent must synthesize these perspectives into a 1500-2500 word French policy brief with structured recommendations, source analysis, and bibliography.

## Language Configuration
- **Instruction Language**: French
- **Source Material Languages**: English, Chinese, Russian, French
- **Target Output Language(s)**: French
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `note_politique_fr.md` | French policy brief (1500-2500 words) |
| `synthese_sources.json` | Source analysis with key points and EU relevance ratings |
| `recommandations_fr.json` | Min. 6 structured recommendations with priority/timeline |
| `bibliographie.json` | Structured bibliography of all sources |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Policy Analysis Quality | 30% | Depth of comparative analysis across three perspectives |
| French Institutional Style | 25% | Proper French policy document conventions and vocabulary |
| Source Synthesis | 20% | Effective integration of trilingual sources |
| Recommendations Quality | 15% | Actionable, prioritized, and well-sourced recommendations |
| Statistical Integration | 10% | Meaningful use of market statistics in the analysis |

## Key Challenges
- Reading and synthesizing policy positions from English, Chinese, and Russian
- Writing in French institutional/policy style (impersonal, rigorous argumentation)
- Comparing US, Chinese, and Russian approaches to AI regulation
- Integrating quantitative market data into qualitative policy analysis
- Producing time-horizon-differentiated recommendations
