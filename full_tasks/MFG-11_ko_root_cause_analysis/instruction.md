# 생산라인 정지 근본 원인 분석

## 목표

당신은 제조 공장의 품질 엔지니어입니다. 생산라인 B에서 발생한 비상 정지의 근본 원인을 파악해야 합니다. 3개 언어로 된 데이터 소스를 상호 참조하여 타임라인을 구성하고 인과 관계를 추적하세요.

## 입력 파일

- `/workspace/inputs/incident_reports_ko.txt` — 한국어 운전원 사고 보고서
- `/workspace/inputs/mes_alerts_zh.log` — 중국어 MES 경보 로그 (타임스탬프 포함)
- `/workspace/inputs/sensor_data.csv` — 영어 센서 데이터 (80행, 온도/진동/압력)

## 작업 요구사항

1. 3개 소스의 타임스탬프를 정렬하여 사건 타임라인 구성
2. 센서 데이터에서 이상값 식별 (정상 범위: 온도 <75도C, 진동 <2.5mm/s)
3. MES 경보와 센서 이상값 간의 상관관계 파악
4. 운전원 보고서와 시스템 데이터 교차 검증
5. 근본 원인 체인 도출: 베어링 열화 -> 온도 상승 -> 진동 -> 비상 정지

## 출력 파일 (/workspace/output/)

### root_cause_report_ko.md
한국어 근본 원인 분석 보고서 (타임라인, 원인 분석, 재발 방지 대책 포함)

### timeline.json
{"events": [{"time": "14:23", "source": "sensor", "description": "..."}]}

### correlation_matrix.json
소스 간 상관관계 매트릭스

### /workspace/answer.json
{"root_cause": "bearing_degradation", "first_anomaly_time": "14:23", "sensor_id": "T-07", "peak_temperature": 82.3, "total_events": 6, "stoppage_time": "14:32"}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
