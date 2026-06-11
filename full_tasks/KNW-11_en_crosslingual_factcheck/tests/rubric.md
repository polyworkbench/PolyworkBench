# Rubric: KNW-11 Cross-lingual Fact Verification Chain

## Dimensions (weights sum to 1.0)

### 1. Completeness (0.25)
- All 5 contradictions identified: 0.25
- 4 contradictions identified: 0.20
- 3 contradictions identified: 0.15
- 2 or fewer: 0.05

### 2. Accuracy (0.25)
- Correct determination of ground truth for all contradictions:
  - Date: March 15, 2024 (ES + ZH corroborate)
  - Member count: 12 countries (ES + ZH corroborate)
  - Trade volume: ~$2.4B USD (ES + EN agree; ZH slightly lower due to conversion; FR uses euros)
  - Signing location: Lima, Peru (3 sources agree vs. FR alone says Bogotá)
  - Lead negotiator: María González (ES + ZH agree; not mentioned in EN/FR)
- Full marks: all 5 correct
- Partial: 3-4 correct = 0.15-0.20

### 3. Structure (0.15)
- All three output files present and valid JSON where applicable: 0.15
- Missing one file or invalid JSON: 0.08
- Missing multiple files: 0.03

### 4. Reasoning (0.20)
- Clear explanation of why certain sources are more reliable
- Uses corroboration principle (multiple sources agreeing)
- Identifies source types and their expected reliability
- Full marks: detailed reasoning for each contradiction

### 5. Cross-lingual Coverage (0.15)
- Evidence of reading all 4 languages
- Correct extraction of facts from non-English sources
- Proper handling of currency/unit conversions
- Full marks: demonstrates comprehension of all 4 source languages
