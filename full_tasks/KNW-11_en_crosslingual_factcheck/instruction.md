# Cross-lingual Fact Verification: 2024 Pacifica Trade Agreement

## Objective

You are given four source documents about the "2024 Pacifica Trade Agreement" written in different languages:
1. `articulo_prensa.md` — Spanish news article from EFE agency
2. `wikipedia_excerpt.md` — English Wikipedia excerpt
3. `government_report_zh.md` — Chinese government policy report
4. `academic_paper_fr.md` — French academic paper from Sciences Po

## Task

Perform a comprehensive cross-lingual fact verification by:

1. **Read all four sources carefully** in their original languages.
2. **Identify all factual contradictions** between the sources — differences in dates, numbers, names, locations, or claims.
3. **Determine the most likely correct fact** for each contradiction, using source reliability, corroboration across sources, and internal consistency.
4. **Produce the following outputs:**

### Required Output Files

#### `verification_report.md`
A structured English-language report containing:
- Executive summary of findings
- For each contradiction found: the conflicting claims, which sources agree/disagree, and your determination of the correct fact with reasoning
- A reliability assessment of each source

#### `contradictions.json`
```json
{
  "total_contradictions": <int>,
  "contradictions": [
    {
      "id": 1,
      "category": "<date|number|location|name|other>",
      "description": "<brief description>",
      "claims": {
        "es": "<what Spanish source says>",
        "en": "<what English source says>",
        "zh": "<what Chinese source says>",
        "fr": "<what French source says>"
      },
      "correct_value": "<determined correct value>",
      "confidence": "<high|medium|low>",
      "reasoning": "<brief reasoning>"
    }
  ]
}
```

#### `source_comparison.json`
```json
{
  "sources": [
    {
      "id": "es",
      "language": "Spanish",
      "type": "<news|encyclopedia|government|academic>",
      "reliability_score": <0.0-1.0>,
      "unique_facts": ["<facts only found in this source>"],
      "errors_found": <int>
    }
  ],
  "cross_reference_matrix": {
    "<fact_category>": {
      "es": "<value>",
      "en": "<value>",
      "zh": "<value>",
      "fr": "<value>",
      "consensus": "<value>"
    }
  }
}
```

## Evaluation Criteria
- Completeness: All 5 contradictions must be found
- Accuracy: Correct determination of true facts
- Structure: JSON files must be valid and follow the schema
- Reasoning: Clear justification for each determination

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
