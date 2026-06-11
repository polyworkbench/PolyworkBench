# Patent Prior Art Analysis: JP2024-123456

## Objective

You are a patent examiner tasked with evaluating the novelty of a Japanese patent application (JP2024-123456) for a "Multi-Layer Thermal Interface Material with Self-Healing Properties" by comparing its claims against available prior art documents in English and German.

## Input Documents

1. `patent_jp2024_123456.md` — Japanese patent application with 8 claims (Japanese)
2. `prior_art_paper_1.md` — "Thermal Interface Materials: Recent Advances" (English, 2021)
3. `prior_art_paper_2.md` — "Self-Healing Polymers for Electronic Applications" (English, 2022)
4. `prior_art_paper_3.md` — "Bio-inspired Thermal Management Systems" (English, 2023)
5. `din_12345_standard.md` — German technical standard DIN 12345 "Thermal Interface Materials — Test Methods" (German)

## Task

For each of the 8 claims in the Japanese patent:

1. **Translate/understand the claim** from Japanese
2. **Search all prior art documents** for relevant disclosures
3. **Determine novelty**: Is the claim novel (no prior art found) or anticipated (prior art exists)?
4. **Map to specific prior art**: For non-novel claims, identify the exact section/figure in the prior art that anticipates the claim

## Required Output Files

### `prior_art_report.md`
An English-language report containing:
- Summary of the patent application
- Claim-by-claim analysis with prior art citations
- Overall novelty assessment
- Recommendations for the patent examiner

### `claim_mapping.json`
```json
{
  "patent_id": "JP2024-123456",
  "total_claims": 8,
  "novel_claims": [<list of novel claim numbers>],
  "anticipated_claims": [<list of anticipated claim numbers>],
  "mappings": [
    {
      "claim_number": <int>,
      "claim_summary": "<brief English translation/summary>",
      "status": "<novel|anticipated|partially_anticipated>",
      "prior_art_references": [
        {
          "document": "<document name>",
          "section": "<section/figure reference>",
          "relevance": "<identical|similar|combination>",
          "description": "<how it anticipates the claim>"
        }
      ]
    }
  ]
}
```

### `novelty_assessment.json`
```json
{
  "patent_id": "JP2024-123456",
  "overall_novelty": "<high|medium|low>",
  "novel_claim_count": <int>,
  "anticipated_claim_count": <int>,
  "novel_claims": [<claim numbers>],
  "key_findings": ["<finding1>", "<finding2>"],
  "recommendation": "<grant|reject|amend>"
}
```

## Ground Truth Claim Mapping
- Claim 1: Anticipated by Prior Art Paper 1, Section 3.2
- Claim 2: **NOVEL** (no prior art)
- Claim 3: Anticipated by DIN 12345 §4.1
- Claim 4: Anticipated by Prior Art Paper 2, Figure 4
- Claim 5: **NOVEL** (no prior art)
- Claim 6: Anticipated by combination of Paper 1 §5.1 + Paper 3 Abstract
- Claim 7: Anticipated by DIN 12345 §6.2
- Claim 8: Anticipated by Prior Art Paper 3, Section 2

## Evaluation Criteria
- Correct novelty determination for all 8 claims
- Accurate prior art mapping with specific section references
- Claims 2 and 5 correctly identified as novel
- Professional patent examination report quality

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
