# HQ-03 评分锚点（满分 100）

## Q1 模态保真度（20 分）

- [+5] 中文日志关键 ERROR 行（"下单失败-库存锁未释放"）至少 3 条被识别并归类
- [+5] Grafana 截图中的 4 个 Panel 信息均被引用（成功率/Redis/Kafka/锁等待）
- [+5] 语音备忘 [unclear] 处的 Kafka 数字（一万八千 ≈ 18,900）能与 Prometheus 数据交叉验证
- [+5] 不把粤语字面字（"喺"、"嘢"、"咁"）当作错误词或乱码

## Q2 语言准确性（20 分）

- [+8] 韩文摘要在 80 字以内，包含 4 要素：时间(23:00 KST) / 触发(Redis failover 18s) / 影响(45%) / 措施(TTL/Redlock)
- [+5] 英文 RCA 用专业 SRE 术语：failover / quorum / TTL / consumer lag / hot-patch
- [+4] "库存锁未释放" 不直译为 "inventory lock not released", 准确表达为 "stuck inventory lock" / "orphaned lock"
- [+3] 三语术语对齐（分布式锁 = distributed lock = 분산락）

## Q3 任务完成度（30 分）

| 检查项 | 分值 |
|---|---|
| RCA 含全部 9 个章节（Summary/Impact/Timeline/RootCause/Contributing/Detection/Resolution/Lessons/ActionItems） | 9 |
| Action Items ≥ 3 条且每条含 owner + due + priority | 6 |
| 时间线条目 ≥ 8 条 | 4 |
| 所有引用使用 `[source: filename, line N]` 格式 | 5 |
| 韩文摘要单独输出且确实在 80 字以内 | 3 |
| 提出 Redlock / TTL 调整等具体改进 | 3 |

## Q4 长程一致性（30 分；本任务关键权重）

- [+8] **时区对齐正确**：日志 22:00 CST = 23:00 KST = 14:00 UTC；时间线全部用 KST
- [+5] Action Items 在 RCA 与韩文摘要中的核心结论一致（不能英文报 Redlock 韩文报别的）
- [+5] 数字一致：成功率 45.0%、Kafka lag 18,900、TTL 30→60→90s 在多处文档中相同
- [+4] zhang.wei 的人工干预（TTL 30→60s）在 timeline、resolution、action items 三处都被提及
- [+4] 因果链清晰：Redis flap → Sentinel failover 18s → lock 无法续期 → SKU 锁卡死 → 订单失败
- [+4] 至少一处显示"语音备忘 [unclear] 与 Prometheus 数据交叉验证后确定 Kafka lag = 18,900"

## 常见错误归因

- `E-TZ-OFFSET`：时区算错（最常见，扣 8）
- `E-CITATION-MISS`：结论无 [source: ...] 引用
- `E-CONSIST-DRIFT`：英韩双语数字/结论不一致
- `E-LANG-LITERAL`：粤语字面被当作错误处理
- `E-SCOPE-MISS`：忽略 Kafka 部分，只看 Redis
- `E-AI-OWNER-MISS`：Action Item 缺 owner / due
