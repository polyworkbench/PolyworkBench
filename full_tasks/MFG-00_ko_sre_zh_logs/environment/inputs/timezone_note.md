# 时区换算指引

- 中国生产集群日志（payment-service.log）：CST = UTC+8
- 韩国 SRE 值班 / 指令 / 产出报告：KST = UTC+9
- Prometheus / Redis 监控指标：UTC（默认）
- 换算公式：
  - CST → KST：+1 小时
  - UTC → KST：+9 小时
  - UTC → CST：+8 小时

## 事件窗口（KST 基准）

- 开始：2024-11-19 23:00 KST（即 2024-11-19 22:00 CST / 14:00 UTC）
- 结束：2024-11-19 23:45 KST（即 2024-11-19 22:45 CST / 14:45 UTC）
