# 장비 예방정비 일정 수립 — 다국어 자료 기반 한국어 보전 계획

## 작업 설명

당신은 제조 공장의 설비 보전 엔지니어입니다. 일본어 장비 매뉴얼, 영문 부품 카탈로그, 중국어 정비 이력 데이터를 분석하여, 한국어로 된 예방정비(PM) 일정 및 보전 가이드를 작성하세요.

## 입력 데이터

- `/workspace/inputs/equipment_manual_ja.md` — 일본어 장비 운전/보전 매뉴얼
- `/workspace/inputs/spare_parts_en.csv` — 영문 부품 카탈로그 (부품번호, 가격, 리드타임)
- `/workspace/inputs/maintenance_log_zh.csv` — 중국어 정비 이력 기록
- `/workspace/inputs/equipment_specs_ja.json` — 일본어 장비 사양서

## 요구 사항

- 예방정비 일정 (`pm_schedule_ko.json`) 작성: 일일/주간/월간/분기/연간 점검 항목, 담당자, 소요 시간, 필요 부품을 포함할 것
- 한국어 보전 가이드 (`maintenance_guide_ko.md`) 작성: 일본어 매뉴얼 내용을 번역하고 실제 정비 이력을 반영한 실무 가이드
- 부품 매핑 테이블 (`parts_mapping.json`) 생성: 일본어 부품명 ↔ 영문 부품번호 ↔ 한국어 설명 연결
- 정비 이력 분석 (`maintenance_history_analysis.json`): 고장 패턴, MTBF(평균고장간격), MTTR(평균수리시간) 계산
- PM 일정은 장비 사양서의 권장 주기와 실제 고장 이력을 모두 반영할 것
- 부품 재고 관리를 위한 권장 안전재고 수량 산출 (리드타임 기반)
- 비용 분석 포함: 연간 예방정비 예상 비용 산출
- 우선순위 기반 정비 항목 분류 (Critical/High/Medium/Low)
- `answer.json` 생성: `{"total_pm_items": int, "annual_cost_estimate_usd": float, "critical_items": int, "avg_mtbf_hours": float, "avg_mttr_hours": float, "total_spare_parts": int}`

## 출력

모든 파일을 `/workspace/output/`에 저장:
- `pm_schedule_ko.json`
- `maintenance_guide_ko.md`
- `parts_mapping.json`
- `maintenance_history_analysis.json`

그리고 `/workspace/answer.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
