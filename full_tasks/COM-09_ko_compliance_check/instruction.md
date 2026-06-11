# 다중 규제 프레임워크 제품 적합성 검사

## 작업 개요

3개 규제 프레임워크(미국 FDA, 중국 GB 국가표준, 일본 JIS 규격)에 대한 제품 적합성을 교차 검사하고, 한국어로 적합성 매트릭스와 갭 분석 보고서를 작성하세요.

## 입력 파일

- `/workspace/inputs/fda_requirements_en.json` — 미국 FDA 요구사항 (영어, 제품 카테고리별)
- `/workspace/inputs/gb_standards_zh.txt` — 중국 GB 국가표준 발췌 (중국어)
- `/workspace/inputs/jis_standards_ja.txt` — 일본 JIS 규격 (일본어)
- `/workspace/inputs/product_specs_en.json` — 검사 대상 제품 기술 사양 (영어)

## 요구사항

- 3개 규제 프레임워크의 요구사항을 체계적으로 분석하고 정리할 것
- 각 제품에 대해 FDA/GB/JIS 적합 여부를 매트릭스 형태로 정리할 것
- 적합하지 않은 항목에 대해 구체적인 갭(차이)을 식별할 것
- 각 갭에 대한 시정 조치 항목을 우선순위와 함께 제시할 것
- 규제 간 상충되는 요구사항이 있으면 명확히 표시할 것
- 모든 출력은 한국어로 작성할 것 (규격 번호/코드는 원어 유지)
- 적합성 판정 기준을 명시할 것 (적합/부분적합/부적합/해당없음)
- 시정 조치의 예상 비용 및 소요 기간도 포함할 것

## 출력

다음 파일을 `/workspace/output/`에 저장하세요:

1. `compliance_matrix_ko.json` — 제품별 규제별 적합성 매트릭스 (한국어)
2. `gap_analysis_ko.md` — 갭 분석 보고서 (한국어 Markdown)
3. `action_items_ko.json` — 시정 조치 항목 (한국어, 우선순위 포함)
4. `regulatory_summary.json` — 규제 요약 (구조화된 JSON)

또한 `/workspace/answer.json`에 요약 정보를 출력하세요:
```json
{
  "total_products": <int>,
  "total_requirements_checked": <int>,
  "compliant_count": <int>,
  "partial_compliant_count": <int>,
  "non_compliant_count": <int>,
  "not_applicable_count": <int>,
  "critical_gaps": <int>,
  "total_action_items": <int>,
  "conflicting_requirements": <int>
}
```

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
