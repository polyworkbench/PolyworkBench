# K8s 결제장애 RCA 분석

`/workspace/inputs/`에 결제 서비스 장애 관련 자료가 있어요 (중국어 로그, Redis 메트릭, Grafana 캡처, 음성 메모). 2024-11-19 KST 23:00~23:45 사이 결제 실패율 급증 사건을 분석해주세요.

해야 할 것:
- 시간대 정규화 스크립트 작성해서 CST/UTC/KST 통일 (Python으로)
- 타임라인 생성 (KST 기준, 각 이벤트에 source 출처 표시)
- 영향도 계산: 실패 건수, 영향받은 금액 추정, MTTD/MTTR
- 근본원인 분석 (RCA) 영문으로, Redis Redlock 관련 이슈 특정
- 한국어 경영진 요약 (80자 이내)
- 재발 방지 Action items (담당자, 기한, 우선순위)
- 비상 대응 Runbook

결과는 `/workspace/output/`에, 최종 요약은 `/workspace/answer.json`에.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash/shell 命令创建目录、写文件、执行脚本。**
