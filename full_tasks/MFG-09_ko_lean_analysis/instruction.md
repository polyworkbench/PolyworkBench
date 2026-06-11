# 도요타 생산방식 기반 린 제조 분석 및 개선계획

`/workspace/inputs/` 디렉토리에 다음 파일들이 있습니다:

- `tps_principles_ja.md` — 도요타 생산방식(トヨタ生産方式)의 핵심 원칙 (일본어)
- `lean_metrics_en.csv` — 린 제조 KPI: 택트타임, 사이클타임, OEE 등 (영어)
- `floor_data_zh.csv` — 중국 공장 현장 관찰 데이터: 이동시간, 대기시간, 재공품 (중국어)
- `current_layout_description.txt` — 현재 생산라인 레이아웃 설명

## 요구사항

- 일본어 TPS 원칙 문서를 분석하여 핵심 개념(자동화/ジドーカ, 적시생산/ジャスト・イン・タイム, 카이젠/改善, 무다 제거/ムダ排除)을 파악
- 영어 린 메트릭스 데이터를 분석하여 현재 생산라인의 성과를 평가
- 중국어 현장 데이터에서 7대 낭비(과잉생산, 대기, 운반, 과잉가공, 재고, 동작, 불량)를 식별
- 가치흐름맵(VSM) 데이터를 JSON 형식으로 작성 (`value_stream_map.json`):
  - 각 공정 단계별: 사이클타임, 대기시간, 재공품 수량, 가치부가 비율
  - 리드타임 계산, 가치부가시간 비율
- 종합적인 린 분석 보고서를 한국어로 작성 (`lean_analysis_ko.md`):
  - 현상 분석 (현재 상태 설명)
  - TPS 원칙 적용 관점에서의 문제점
  - 7대 낭비 분석 결과
  - OEE 분석
- 개선계획을 JSON 형식으로 작성 (`improvement_plan_ko.json`):
  - 단기 개선(1-3개월), 중기 개선(3-6개월), 장기 개선(6-12개월)
  - 각 항목: 개선내용, 예상효과, 투자비용, 우선순위, 담당부서
- 개선 전후 메트릭스 비교 (`metrics_comparison.json`):
  - 현재 값 vs 목표 값 vs 업계 벤치마크

## 출력

모든 파일을 `/workspace/output/`에 저장:
- `lean_analysis_ko.md`
- `value_stream_map.json`
- `improvement_plan_ko.json`
- `metrics_comparison.json`

최종 요약을 `/workspace/answer.json`에 저장.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
