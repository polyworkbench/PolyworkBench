# Convert English Slides and Chinese Docs into Vietnamese Training Manual

## Overview
Tests the ability to transform English training slides and Chinese technical documentation into a complete Vietnamese cloud computing training manual with exercises, glossary, and assessment questions.

## Scenario
A training department needs a Vietnamese cloud computing course. The agent must convert 12 English training slides on cloud fundamentals and Chinese technical documentation on AWS/Alibaba Cloud services into a comprehensive Vietnamese training manual (min. 3000 words), hands-on exercises, a trilingual glossary (Vietnamese-English-Chinese, min. 40 terms), and assessment questions (min. 20) — all using correct Vietnamese technical terminology.

## Language Configuration
- **Instruction Language**: Vietnamese
- **Source Material Languages**: English, Chinese
- **Target Output Language(s)**: Vietnamese
- **Complexity Level**: L3

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Summary: total_chapters, total_exercises, total_glossary_terms, total_questions, covered_objectives |
| `training_manual_vi.md` | Complete Vietnamese training manual (min. 3000 words) |
| `exercises_vi.json` | Hands-on exercises (min. 10) with step-by-step instructions |
| `glossary_vi_en_zh.json` | Trilingual glossary (min. 40 terms) |
| `assessment_questions_vi.json` | Assessment questions (min. 20) with answers and explanations |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Content Coverage | 25% | Full coverage of topics from source materials |
| Vietnamese Quality | 25% | Natural language with accurate technical terminology |
| Exercise Quality | 20% | Practical and pedagogically useful exercises |
| Terminology Accuracy | 15% | Complete and correct trilingual glossary |
| Pedagogical Structure | 15% | Logical progression from basic to advanced |

## Key Challenges
- Synthesizing content from English slides and Chinese docs into coherent Vietnamese
- Using correct Vietnamese cloud computing terminology
- Creating practical hands-on exercises from theoretical content
- Building a comprehensive trilingual glossary with Vietnamese definitions
- Designing assessment questions covering multiple Bloom's taxonomy levels
