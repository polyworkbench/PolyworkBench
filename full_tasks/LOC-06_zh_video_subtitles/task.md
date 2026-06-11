# Chinese Subtitle Generation from Multilingual Sources

## Overview
Tests the ability to generate high-quality Chinese subtitles from an English SRT file, using Japanese and Korean reference subtitles and a terminology guide, while respecting strict SRT formatting and character-per-line limits.

## Scenario
A technical documentary on AI and machine learning needs Chinese subtitles. The agent must translate 50 English subtitle entries into Chinese SRT format, referencing Japanese and Korean subtitle versions of the same video for context. Strict constraints apply: max 2 lines per entry, max 18 Chinese characters per line, time codes synchronized with English (±200ms adjustment allowed), and terminology must match a provided guide. Output includes the SRT file, structured subtitle data with confidence scores, timing adjustment report, and extracted terminology glossary.

## Language Configuration
- **Instruction Language**: Chinese
- **Source Material Languages**: English, Japanese, Korean
- **Target Output Language(s)**: Chinese
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `subtitles_zh.srt` | Chinese subtitles in SRT format (50 entries) |
| `subtitle_data.json` | Structured subtitle data with confidence scores |
| `timing_report.json` | Time code adjustment report |
| `terminology_glossary.json` | Extracted bilingual terminology list |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| SRT Format Compliance | 25% | Strict adherence to SRT format and character limits |
| Translation Quality | 25% | Natural, concise Chinese subtitle style |
| Timing Accuracy | 20% | Proper synchronization with English time codes |
| Terminology Consistency | 15% | Alignment with terminology guide |
| Reference Utilization | 15% | Meaningful use of JA/KO reference subtitles |

## Key Challenges
- Fitting Chinese translations within 18-character-per-line limit (subtitle brevity)
- Maintaining proper SRT format with sequential numbering and time codes
- Balancing natural Chinese expression with subtitle constraints
- Referencing Japanese and Korean versions for context and terminology
- Adjusting timing for Chinese reading rhythm while staying within ±200ms
