# Synthesize English Whitepaper and Japanese Notes into Korean Tech Assessment

## Overview
Tests the ability to combine an English technical whitepaper on edge AI inference and Japanese research notes on model compression into a comprehensive Korean technology assessment report.

## Scenario
A technology team needs an edge AI feasibility assessment in Korean. The agent must synthesize an English whitepaper (~1500 words) on edge AI inference, Japanese research notes on model compression techniques, English benchmark data (latency, accuracy, power consumption in CSV), and Japanese edge device market data into a comprehensive Korean technical assessment with comparison matrices, feasibility scoring, and strategic recommendations.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: English, Japanese
- **Target Output Language(s)**: Korean
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: top_recommendation, feasibility_score, key_technologies, market_size_estimate |
| `tech_assessment_ko.md` | Korean technology assessment report (min. 2000 characters) |
| `comparison_matrix.json` | Edge AI solution comparison matrix (min. 5 solutions) |
| `feasibility_ko.json` | Feasibility analysis with scored dimensions (1-5) |
| `recommendations_ko.md` | Technology adoption recommendations (min. 800 characters) |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Synthesis Quality | 25% | Effective integration of English and Japanese sources |
| Korean Technical Writing | 25% | Appropriate Korean technical terminology |
| Benchmark Analysis | 20% | Accurate reflection of benchmark data |
| Feasibility Analysis | 15% | Logical and systematic feasibility scoring |
| Recommendations | 15% | Actionable and specific strategic suggestions |

## Key Challenges
- Merging technical content from English and Japanese into coherent Korean
- Correctly translating technical terms with English annotations where needed
- Processing CSV benchmark data into meaningful comparison matrices
- Producing short/medium/long-term strategic recommendations with risk analysis
