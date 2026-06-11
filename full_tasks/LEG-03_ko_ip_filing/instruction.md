# 한국 특허출원 준비: 다국어 선행기술 분석

## 과제

미국 특허출원서(영어), 일본 선행기술문헌(일본어), 중국 실용신안(중국어)을 기반으로 한국특허청(KIPO) 출원을 위한 서류를 준비하십시오. 모든 결과물은 한국어로 작성해야 합니다.

## 입력 파일

- `/workspace/inputs/us_patent_en.md` — 미국 특허출원서 (영어, 청구항 15개)
- `/workspace/inputs/prior_art_ja.md` — 일본 선행기술 문헌 (일본어)
- `/workspace/inputs/utility_model_zh.md` — 중국 실용신안 (중국어, 유사 발명)
- `/workspace/inputs/kipo_filing_guide_ko.txt` — KIPO 출원 가이드 발췌 (한국어)

## 요구사항

- 미국 특허출원서의 15개 청구항을 한국어로 번역 (`patent_claims_ko.md`): 특허 청구항 형식 준수, 독립항/종속항 구분 명확히 표시
- 일본 선행기술 및 중국 실용신안에 대한 선행기술 분석 (`prior_art_analysis_ko.json`): 각 선행기술 문헌과의 기술적 차이점을 구조화하여 JSON으로 정리
- 신규성 및 진보성 평가서 (`novelty_assessment_ko.md`): 출원 발명의 신규성(novelty)과 진보성(inventive step)을 선행기술 대비 분석
- 출원 체크리스트 (`filing_checklist_ko.json`): KIPO 출원 요건에 따른 준비 사항 점검표
- 선행기술과의 기술적 차이를 구체적 수치/구성으로 명시
- 청구항 번역 시 한국 특허법상 용어 관례를 따를 것 (예: ~을 포함하는, ~로 구성되는)
- answer.json에 기재: `{"total_claims": 15, "independent_claims": int, "novelty_confirmed": bool, "key_differentiator": str}`

## 출력 파일

결과물을 `/workspace/output/`에 저장:
- `/workspace/output/patent_claims_ko.md`
- `/workspace/output/prior_art_analysis_ko.json`
- `/workspace/output/novelty_assessment_ko.md`
- `/workspace/output/filing_checklist_ko.json`

요약 파일: `/workspace/answer.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
