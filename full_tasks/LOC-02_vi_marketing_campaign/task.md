# Marketing Campaign Adaptation to Vietnamese

## Overview
Tests the ability to adapt English marketing content and Chinese brand guidelines into culturally appropriate Vietnamese marketing campaign materials with proper cultural calendar integration.

## Scenario
A brand is launching a marketing campaign in Vietnam. The agent must adapt English marketing copy (5 social media posts, 3 ad variants, 2 email subjects) into natural Vietnamese, following Chinese-language brand voice guidelines (tone, colors, forbidden words), integrating Vietnamese cultural events/holidays for post timing, and producing platform-specific social media content with Vietnamese hashtags. All CTAs must be localized and brand-compliant.

## Language Configuration
- **Instruction Language**: Vietnamese
- **Source Material Languages**: English, Chinese
- **Target Output Language(s)**: Vietnamese
- **Complexity Level**: L3

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `campaign_materials_vi.md` | Campaign overview in Vietnamese |
| `social_posts_vi.json` | Social media posts with hashtags and timing |
| `ad_copy_vi.json` | Ad copy variants with headlines, descriptions, CTAs |
| `brand_compliance_report.json` | Brand guideline compliance verification |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Cultural Adaptation | 25% | Appropriate adaptation for Vietnamese market |
| Marketing Appeal | 25% | Engaging and compelling Vietnamese marketing copy |
| Brand Compliance | 20% | Adherence to brand voice guidelines |
| Vietnamese Quality | 15% | Natural language with correct diacritics |
| Calendar Integration | 15% | Meaningful integration of Vietnamese cultural events |

## Key Challenges
- Adapting (not literally translating) marketing copy for Vietnamese cultural context
- Following brand guidelines written in Chinese while producing Vietnamese output
- Creating engaging Vietnamese hashtags for social media
- Integrating Vietnamese holidays/events into campaign timing
- Ensuring correct Vietnamese diacritical marks throughout
