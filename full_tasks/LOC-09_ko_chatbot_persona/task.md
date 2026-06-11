# Korean Chatbot Persona Design and Adaptation

## Overview
Tests the ability to design a Korean chatbot persona by adapting English dialogue flows, Japanese politeness systems, and Chinese brand voice into Korean speech-level-aware chatbot scripts with context-appropriate formality switching.

## Scenario
A company is launching a Korean chatbot that must handle 20 intents with culturally appropriate speech levels. The agent must adapt English dialogue flows (20 intents, 3-5 responses each), map Japanese keigo concepts to Korean politeness, apply Chinese brand personality traits, and produce Korean scripts that switch between 해요체 (standard polite), 합쇼체 (formal, for payments/contracts), and 해체 (casual, for events/celebrations) depending on context. A persona guide and tone analysis comparing source languages must also be produced.

## Language Configuration
- **Instruction Language**: Korean
- **Source Material Languages**: English, Japanese, Chinese
- **Target Output Language(s)**: Korean
- **Complexity Level**: L5

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `chatbot_scripts_ko.json` | 20 intents with min. 3 response variants each, annotated with speech level |
| `persona_guide_ko.md` | Character definition, speech level rules, tone guidelines |
| `dialogue_flows_ko.json` | Full Korean dialogue tree with user input examples |
| `tone_analysis.json` | Cross-language tone comparison per intent |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Speech Level Accuracy | 25% | Correct application of 해요체/합쇼체/해체 by context |
| Persona Consistency | 25% | Coherent chatbot character across all responses |
| Natural Korean | 20% | Colloquial and natural conversational Korean |
| Dialogue Coverage | 15% | All 20 intents with sufficient response variants |
| Tone Mapping | 15% | Logical mapping between source language tones and Korean output |

## Key Challenges
- Designing consistent Korean chatbot persona from trilingual inputs
- Correctly applying three Korean speech levels by conversational context
- Mapping Japanese keigo system concepts to Korean 존대법
- Creating natural colloquial Korean conversational responses
- Maintaining brand voice consistency across formal and casual registers
