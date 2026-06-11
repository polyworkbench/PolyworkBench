# Cross-Language Fact Verification from 6 Sources

## Overview
Tests the ability to verify 20 factual claims against source documents in 6 different languages, detecting deliberate contradictions and assessing source reliability.

## Scenario
A fact-checking team needs to verify 20 claims against multilingual source documents: Chinese government statistics, Japanese industry report, Korean market data, Russian trade statistics, Vietnamese economic report, and French research institute data. Some claims are deliberately contradicted across sources. The agent must determine verification status (VERIFIED/CONTRADICTED/PARTIALLY_VERIFIED/UNVERIFIABLE), identify cross-source contradictions, rate source reliability, and provide confidence scores.

## Language Configuration
- **Instruction Language**: English
- **Source Material Languages**: Chinese, Japanese, Korean, Russian, Vietnamese, French
- **Target Output Language(s)**: English
- **Complexity Level**: L6

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `verification_report.md` | Detailed verification analysis for each claim |
| `claims_matrix.json` | Claims mapped to supporting/contradicting evidence per source |
| `contradictions.json` | Min. 5 pairs of contradictory data points between sources |
| `confidence_scores.json` | Confidence levels (0.0-1.0) for each verification decision |
| `source_reliability.json` | Source reliability ratings (1-5) with justification |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Verification Accuracy | 30% | Correct determination of claim status |
| Contradiction Detection | 25% | Identification of deliberate cross-source inconsistencies |
| Source Triangulation | 20% | Effective cross-referencing across multiple sources |
| Confidence Calibration | 15% | Appropriate confidence scoring with reasoning |
| Reliability Assessment | 10% | Logical source reliability evaluation |

## Key Challenges
- Processing factual claims against documents in 6 different languages
- Detecting deliberately embedded contradictions between sources
- Distinguishing genuine contradictions from methodology/timeframe differences
- Triangulating truth when sources disagree
- Rating source reliability while acknowledging different methodologies
