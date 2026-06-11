# 竞争情报分析：AI芯片市场竞品动态

`/workspace/inputs/` 目录下包含以下多语言竞争情报源：

- `competitor_a_en.md` — 竞争对手A（美国公司NovaTech）的英文新闻稿和产品发布公告
- `competitor_b_ko.md` — 竞争对手B（韩国公司SiliconWave）的韩文新闻稿
- `competitor_c_ja.md` — 竞争对手C（日本公司QuantumCore）的日文产品公告
- `our_product_roadmap_zh.json` — 我方产品路线图（用于对比分析）
- `market_context_en.json` — 市场规模和份额数据

## 任务要求

- 撰写中文**竞争情报简报** (`competitive_digest_zh.md`)，全面分析三家竞争对手的最新动态，字数1000-2000字
- 生成 `competitor_profiles.json`，为每个竞争对手建立档案：公司名称、总部所在地、核心产品、技术优势、市场份额、最新动态摘要、威胁等级(1-5)
- 创建 `threat_analysis_zh.json`，包含：各竞争对手对我方各产品线的威胁评估（高/中/低）、具体威胁描述、建议应对措施、时间紧迫程度
- 撰写 `strategic_implications_zh.md`，从战略层面分析竞争格局变化对我方的影响，提出至少5条战略建议
- 所有分析输出须使用中文（competitor_profiles.json中公司名可保留原文）
- 必须引用具体数据（市场份额、产品参数、发布时间等）

## 输出文件

保存至 `/workspace/output/`：
- `competitive_digest_zh.md`
- `competitor_profiles.json`
- `threat_analysis_zh.json`
- `strategic_implications_zh.md`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
