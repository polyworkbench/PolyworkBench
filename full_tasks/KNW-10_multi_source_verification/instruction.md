# Multi-Source Fact Verification Across 6 Languages

In `/workspace/inputs/` you will find claims to verify along with source documents in 6 languages:

- `claims_to_verify_en.json` — 20 factual claims to verify
- `source_china_zh.md` — Chinese government statistics
- `source_japan_ja.md` — Japanese industry report
- `source_korea_ko.md` — Korean market data
- `source_russia_ru.md` — Russian trade statistics
- `source_vietnam_vi.md` — Vietnamese economic report
- `source_france_fr.md` — French research institute data

## Requirements

- Verify each of the 20 claims against the multilingual sources
- For each claim, determine: VERIFIED, CONTRADICTED, PARTIALLY_VERIFIED, or UNVERIFIABLE
- Create `verification_report.md` with detailed analysis for each claim, including which sources support or contradict it
- Generate `claims_matrix.json` mapping each claim to supporting/contradicting evidence from each source document
- Produce `contradictions.json` identifying specific contradictions between sources (at least 5 pairs of contradictory data points)
- Create `confidence_scores.json` with confidence level (0.0-1.0) for each verification decision
- Generate `source_reliability.json` rating each source's reliability (1-5) with justification

## Key Notes
- Some claims are deliberately contradicted across sources (e.g., different sources may report different figures for the same metric)
- Cross-reference data points across multiple sources to triangulate truth
- Note when sources use different methodologies or timeframes that explain discrepancies
- All output must be in English

## Output

Save all files to `/workspace/output/`:
- `verification_report.md`
- `claims_matrix.json`
- `contradictions.json`
- `confidence_scores.json`
- `source_reliability.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
