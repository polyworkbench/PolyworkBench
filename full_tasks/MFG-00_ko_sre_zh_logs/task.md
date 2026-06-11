# HQ-03 · 韩文指令分析中文 K8s 日志 → 英文 RCA + 韩文摘要

- **集合**：baseline
- **难度**：★★★★（4/5）
- **指令语 / 源语 / 产出语**：ko / zh+en / en+ko
- **模态**：text(logs) + screenshot(grafana) + audio(中文语音备忘)
- **预计步骤数**：8
- **预计人工耗时**：3–4 h

## 业务背景

韩国 NAVER 收购的中国子公司运行支付微服务集群（Spring Boot + Redis + Kafka），生产 K8s 集群在 KST 23:00（CST 22:00）出现支付失败率飙升。韩国总部 SRE 值班用韩文发起调查，需要：

- 跨语言读取中文运维日志（部分含粤语口音的语音备忘）
- 跨时区对齐时间线（KST = CST + 1h）
- 输出符合 Google SRE post-mortem 模板的英文 RCA
- 同时给高管 Slack 一条韩文一段式摘要

## Agent Prompt（ko，原样喂给 Agent）

```
당신은 다국어 SRE 어시스턴트입니다. 어제(2024-11-19) KST 23:00 ~ 23:45 사이 결제 실패율 급증 사건의 원인을 분석해 주세요. 결제 모듈(payment-service) 위주로 봐주세요.

업무 요구사항:
1. inputs/ 디렉토리의 모든 자료를 읽어 시간대(KST)를 기준으로 통합 타임라인을 작성합니다.
   - 중국 측 로그는 CST 타임존이므로 KST로 +1시간 변환 필요
   - 음성 메모(audio_memo_zh.txt)는 사고 당시 중국 SRE의 구두 보고이며, 광둥어 발음 일부 포함됨
2. 로그 클러스터링: 중복 메시지를 묶고, 빈도순으로 상위 5개 패턴을 식별합니다.
3. Grafana 스크린샷(grafana_screenshot.txt)에서 보이는 Redis 및 Kafka 메트릭 이상을 추출합니다.
4. 근본 원인 가설을 제시하고, 각 가설에 대한 증거를 inputs 자료의 정확한 라인/타임스탬프로 인용합니다.
5. 영어 Google-style post-mortem(rca.md)를 작성합니다. 다음 섹션 필수:
   - Summary / Impact / Timeline (KST) / Root Cause / Contributing Factors / Detection / Resolution / Lessons Learned / Action Items (with owners and due dates)
6. 한국어 임원 요약(summary_ko.md)을 1단락(80자 이내)으로 별도 작성합니다.
7. 액션 아이템은 영어 RCA와 한국어 요약 양쪽에 동일한 내용이 일관되게 반영되어야 합니다.
8. 모든 인용은 [source: filename, line N] 형식으로 추적 가능해야 합니다.
```

## 输入资料清单

- `inputs/payment_service.log`：中文 Spring Boot 日志（CST 时区，含 ERROR/WARN）
- `inputs/redis_metrics.txt`：Prometheus 抓取的 Redis 指标（英文，UTC 时区）
- `inputs/grafana_screenshot.txt`：Grafana 面板截图的 OCR 文本（中文标题 + 英文指标）
- `inputs/audio_memo_zh.txt`：中文语音备忘的转写（含 ASR 错误标注 [unclear]）
- `inputs/timezone_note.md`：时区换算指引

## 工具需求

- 文本检索 / 日志解析
- 时区换算（KST/CST/UTC）
- 文本聚类（可用 LLM 直接做）
- 多语言生成（韩英中三语）

## 关键考察点

1. **三时区对齐**：KST(指令) / CST(日志) / UTC(Prometheus) 三套时间戳归一到 KST 时间线
2. **方言鲁棒性**：粤语口音的中文 ASR 含 [unclear]，需上下文推断
3. **多源因果链**：从 Redis 主从切换 → 分布式锁失效 → 库存锁未释放 → 支付幂等失败
4. **双语一致性**：韩文摘要的核心结论必须与英文 RCA 一致（数字、责任人不能漂移）
5. **可追溯性**：所有结论必须 `[source: file, line N]` 引用
