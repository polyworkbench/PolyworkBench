# Multi-Locale Simultaneous Release Coordination

## Overview
Tests the ability to perform QA verification across 6 locale translations simultaneously, detect deliberately embedded issues, produce locale-specific changelogs, and generate a comprehensive release coordination report.

## Scenario
A mobile app is preparing a simultaneous release across 6 locales (Chinese, Japanese, Korean, Russian, Vietnamese, French). The agent must verify 50 translated strings across all locales for completeness, placeholder consistency, string length, and terminology consistency. Translation files contain deliberately embedded issues that must be detected. Additionally, English release notes must be localized into 6 separate changelogs adapted to each locale's conventions (date format, versioning style).

## Language Configuration
- **Instruction Language**: English
- **Source Material Languages**: Chinese, Japanese, Korean, Russian, Vietnamese, French
- **Target Output Language(s)**: English (QA report), Chinese, Japanese, Korean, Russian, Vietnamese, French (changelogs)
- **Complexity Level**: L6

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `qa_report.md` | Comprehensive English QA report with severity levels |
| `consistency_matrix.json` | Cross-locale comparison matrix for all 50 strings |
| `changelogs/changelog_zh.md` | Chinese changelog |
| `changelogs/changelog_ja.md` | Japanese changelog |
| `changelogs/changelog_ko.md` | Korean changelog |
| `changelogs/changelog_ru.md` | Russian changelog |
| `changelogs/changelog_vi.md` | Vietnamese changelog |
| `changelogs/changelog_fr.md` | French changelog |
| `issues_found.json` | All detected issues with type and severity |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Issue Detection | 30% | Finding deliberately embedded translation issues |
| QA Thoroughness | 25% | Completeness, placeholders, length, terminology all checked |
| Changelog Quality | 20% | Natural localization in 6 languages with locale conventions |
| Consistency Analysis | 15% | Accurate cross-locale comparison matrix |
| Report Professionalism | 10% | Clear, actionable release management documentation |

## Key Challenges
- Detecting deliberately planted issues across 6 different language files
- Checking placeholder consistency ({variable} intact) across all locales
- Producing natural changelogs in 6 different languages from one English source
- Adapting date formats and versioning conventions per locale
- Creating actionable QA report with prioritized severity levels
