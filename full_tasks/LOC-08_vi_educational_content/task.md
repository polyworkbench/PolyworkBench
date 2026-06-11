# Vietnamese Educational Content Adaptation

## Overview
Tests the ability to adapt an English mathematics curriculum (Basic Algebra, 10 lessons) into Vietnamese, integrating Korean pedagogical methods and Chinese practice problems while aligning with Vietnamese educational standards.

## Scenario
A Vietnamese school needs a localized Basic Algebra curriculum for Grade 7-8 students. The agent must adapt 10 English lessons into Vietnamese using proper Vietnamese math terminology, integrate Korean teaching methodology notes, convert Chinese practice problems (with solutions), align with Vietnamese national learning standards, and produce a teacher's guide with 45-minute lesson plans. The output includes the full curriculum, 50+ exercises, teacher guide, and mid-term/final assessments.

## Language Configuration
- **Instruction Language**: Vietnamese
- **Source Material Languages**: English, Korean, Chinese
- **Target Output Language(s)**: Vietnamese
- **Complexity Level**: L4

## Required Outputs
| File | Description |
|------|-------------|
| `answer.json` | Consolidated results summary |
| `curriculum_vi.md` | Full 10-lesson Vietnamese math curriculum |
| `exercises_vi.json` | Min. 50 exercises (5 per lesson) with answers |
| `teacher_guide_vi.md` | Teacher guide with pedagogical methods |
| `assessment_vi.json` | Mid-term and final assessments (10-15 questions each) |

## Evaluation Dimensions
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Curriculum Completeness | 25% | All 10 lessons with required sections |
| Vietnamese Math Terminology | 25% | Correct use of standard terms (phuong trinh, bien so, etc.) |
| Pedagogical Integration | 20% | Korean methods adapted for Vietnamese context |
| Exercise Quality | 15% | Varied difficulty with correct answers and explanations |
| Standards Alignment | 15% | Alignment with Vietnamese national learning standards |

## Key Challenges
- Using correct Vietnamese mathematics terminology consistently
- Adapting Korean pedagogical methods for Vietnamese classroom context
- Converting Chinese practice problems with appropriate difficulty for Grade 7-8
- Aligning with Vietnamese national educational standards
- Producing time-allocated lesson plans (45 minutes per period)
