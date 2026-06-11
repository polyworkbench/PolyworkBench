# Mobile App Localization to Russian

## Overview
Tests the ability to localize mobile app UI strings from English to Russian, handling pluralization rules, length constraints, style guide compliance, and contextual understanding from a Chinese feature specification.

## Scenario
The mobile app "TaskFlow" needs its interface strings localized from English to Russian. The agent must use a Chinese feature specification to understand the context of each screen, follow a Russian style guide (terminology, formality level, button conventions), correctly handle Russian plural forms (one/few/many), respect maximum string length constraints (min. 80% compliance), and preserve placeholders. Output must include translated strings, a length compliance report, translator notes, and a QA checklist.

## Language Configuration
- **Instruction Language**: Russian
- **Source Material Languages**: English, Chinese
- **Target Output Language(s)**: Russian
- **Complexity Level**: L3

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `strings_ru.json` | Translated strings with plural form objects |
| `length_report.json` | String length compliance report |
| `context_notes_ru.md` | Translator context notes |
| `qa_checklist.json` | Quality assurance checklist |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Translation Accuracy | 25% | Correct and natural Russian translations |
| Pluralization | 25% | Proper handling of Russian one/few/many forms |
| Length Compliance | 20% | Min. 80% of strings within max_length limits |
| Style Guide Adherence | 15% | Terminology and conventions from style guide followed |
| Context Usage | 15% | Chinese feature spec used to inform contextual translations |

## Key Challenges
- Handling Russian three-form pluralization (1, 2-4, 5+) correctly
- Keeping translations within character length limits (Russian is typically longer than English)
- Using Chinese feature specification for contextual understanding
- Following style guide conventions (infinitive for buttons, lowercase for titles, вы-form)
- Preserving all placeholders ({count}, {name}) unchanged
