# 多市场产品发布战略规划

## 任务概述

综合5种语言的市场调研数据，规划新产品（智能健康手环）的多市场同步发布方案。需要识别各来源数据之间的矛盾，制定中文战略计划和英文高管简报。

## 输入文件

- `/workspace/inputs/market_japan_ja.md` — 日本市场研究报告（日语）
- `/workspace/inputs/market_korea_ko.md` — 韩国市场分析（韩语）
- `/workspace/inputs/market_russia_ru.md` — 俄罗斯市场概况（俄语）
- `/workspace/inputs/market_vietnam_vi.md` — 越南市场数据（越南语）
- `/workspace/inputs/competitive_landscape_en.json` — 竞争格局（英语）
- `/workspace/inputs/budget_constraints_zh.json` — 总部预算参数（中文）

## 要求

- 综合所有5种语言的市场数据，提取关键洞察
- 检测各数据来源之间的矛盾信息（如市场规模不一致、增长率冲突等）
- 制定中文产品发布战略计划，包含各市场的本地化策略
- 撰写英文高管简报，简明扼要地呈现核心决策要点
- 创建发布时间线，考虑各市场的最佳发布时机
- 在预算约束范围内合理分配资源
- 考虑各市场的文化差异和消费习惯
- 识别主要风险并提出缓解措施

## 输出

将以下文件保存到 `/workspace/output/`：

1. `launch_plan_zh.md` — 中文产品发布战略计划（3000字以上）
2. `executive_brief_en.md` — 英文高管简报（800-1500字）
3. `market_synthesis.json` — 市场数据综合分析结果
4. `contradiction_report.json` — 数据矛盾检测报告
5. `timeline.json` — 多市场发布时间线

同时输出 `/workspace/answer.json`：
```json
{
  "markets_covered": <int>,
  "total_contradictions_found": <int>,
  "recommended_launch_order": ["<market1>", "<market2>", ...],
  "total_budget_allocated_usd": <float>,
  "primary_risk": "<description>",
  "expected_year1_revenue_usd": <float>,
  "go_no_go_recommendation": "<go|no-go|conditional>"
}
```

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
