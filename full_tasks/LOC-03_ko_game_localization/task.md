# Game Dialogue Localization to Korean

## Overview
Tests the ability to localize Japanese game dialogue into Korean, correctly converting Japanese honorific system (keigo) to Korean speech levels (존댓말/반말/해요체), with character voice consistency and cultural adaptation notes.

## Scenario
A Japanese RPG game with 40 lines of dialogue needs Korean localization. The agent must translate all dialogue while maintaining character-specific speech patterns, convert Japanese keigo (honorifics) to appropriate Korean speech levels, transliterate character names from katakana to hangul, use Korean-native gaming terminology, document cultural adaptations, and flag items needing QA attention. A game design document (English) provides character backstories and world-building context.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: Japanese, English
- **Target Output Language(s)**: Korean
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `game_dialogue_ko.json` | 40 translated dialogue lines with speech level annotations |
| `adaptation_notes_ko.md` | Cultural adaptation notes in Korean |
| `character_voice_guide_ko.md` | Per-character voice guide (speech patterns, endings) |
| `qa_flags.json` | QA flags for items needing review |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Translation Accuracy | 25% | Faithful meaning transfer from Japanese |
| Speech Level Mapping | 25% | Correct keigo→Korean speech level conversion |
| Character Consistency | 20% | Consistent voice per character across all lines |
| Gaming Terminology | 15% | Use of Korean-native gaming expressions |
| Cultural Adaptation | 15% | Appropriate handling of cultural differences |

## Key Challenges
- Converting Japanese keigo system to Korean 존대법 system appropriately
- Maintaining consistent character voice (speech endings, formality) across 40 lines
- Transliterating katakana names naturally into hangul
- Using gaming terminology familiar to Korean gamers
- Identifying and flagging culturally sensitive or ambiguous translations
