# Cross-Lingual Fact Extraction and Verification

In `/workspace/inputs/` you will find research documents in 5 languages along with a set of questions:

- `source_zh.md` — Chinese government economic statistics report (Mandarin)
- `source_ja.md` — Japanese technology industry report (Japanese)
- `source_ko.md` — Korean semiconductor market data (Korean)
- `source_ru.md` — Russian energy sector analysis (Russian)
- `source_vi.md` — Vietnamese manufacturing growth data (Vietnamese)
- `questions_en.json` — 15 specific factual questions to answer from these sources

## Requirements

- Answer all 15 questions in `fact_sheet.json` by extracting specific facts from the multilingual source documents
- Each answer must include: the answer value, the source document it was extracted from, the original text snippet (in source language), and an English translation of the relevant passage
- Create `verification_report.md` explaining your verification methodology: how you located each fact, any cross-referencing between sources, and any ambiguities encountered
- Produce `source_citations.json` with formal citations for each source document (title, author/organization, date, language, document type)
- Generate `confidence_scores.json` assigning a confidence level (0.0–1.0) to each answer with justification (e.g., "directly stated" vs "inferred from context")
- Where multiple sources address the same topic, note any discrepancies
- All output must be in English

## Output

Save all files to `/workspace/output/`:
- `fact_sheet.json`
- `verification_report.md`
- `source_citations.json`
- `confidence_scores.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
