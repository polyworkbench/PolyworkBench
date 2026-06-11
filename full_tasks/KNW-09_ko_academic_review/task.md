# Korean Academic Peer Review from EN/ZH/JA Sources

## Overview
Tests the ability to simulate academic peer review of an English paper draft by comparing it against Chinese and Japanese reference papers, producing detailed Korean-language review comments and revision suggestions.

## Scenario
A Korean academic conference needs a peer review of a paper on "Multimodal Learning for Cross-lingual Transfer" (English, ~1500 words). The agent must evaluate the paper against review criteria (novelty, methodology, clarity, significance), compare it with related Chinese and Japanese reference papers, check compliance with Korean conference submission guidelines, and produce detailed review comments, evaluation scores, revision suggestions, and reference comparison — all in Korean.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: English, Chinese, Japanese, Korean
- **Target Output Language(s)**: Korean
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `review_comments_ko.md` | Detailed Korean peer review comments |
| `evaluation_matrix.json` | Scores (1-10) for novelty, methodology, clarity, significance |
| `revision_suggestions_ko.json` | Min. 8 prioritized revision suggestions |
| `reference_comparison.json` | Comparison with Chinese and Japanese reference papers |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Review Depth | 30% | Thoroughness of strengths/weaknesses analysis |
| Cross-paper Comparison | 25% | Meaningful comparison with reference papers |
| Korean Academic Style | 20% | Proper Korean academic writing conventions |
| Revision Quality | 15% | Actionable and specific improvement suggestions |
| Scoring Calibration | 10% | Justified and consistent evaluation scores |

## Key Challenges
- Evaluating an English paper's novelty against Chinese and Japanese prior work
- Producing constructive Korean-language review comments in academic style
- Comparing methodologies, experimental scale, and contributions across languages
- Checking compliance with Korean conference formatting guidelines
- Prioritizing revision suggestions by importance
