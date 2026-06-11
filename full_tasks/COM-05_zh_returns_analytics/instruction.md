# 跨境退货数据分析与中文报告生成

`/workspace/inputs/` 目录下包含来自俄罗斯和越南市场的退货数据（含多语言客户评论），以及英文产品主数据和退货政策。请分析退货原因，生成中文分析仪表板数据和改进建议报告。

要求：
- 解析俄罗斯退货数据 (`returns_russia_ru.csv`)：提取俄语客户评论中的退货原因、情感倾向、产品SKU
- 解析越南退货数据 (`returns_vietnam_vi.csv`)：提取越南语客户评论中的退货原因、情感倾向、产品SKU
- 关联产品主数据 (`product_master_en.json`)：将退货记录与产品信息（类别、价格、供应商）匹配
- 根据公司退货政策 (`return_policy_en.md`) 判断每笔退货的合规性（是否在政策范围内）
- 生成退货分析汇总 (`returns_analysis_zh.json`)：包含各市场退货率、退货原因分布、产品维度分析
- 生成仪表板数据 (`dashboard_data.json`)：适用于可视化的结构化数据，含时间趋势、地区对比、TOP问题产品
- 生成品类分析 (`category_breakdown.json`)：按产品品类统计退货率、主要退货原因、同比变化
- 撰写中文改进建议报告 (`recommendations_zh.md`)：管理层摘要、根因分析、改进优先级、预期收益
- 最终汇总结果写入 `/workspace/answer.json`

结果保存到 `/workspace/output/`，最终汇总写入 `/workspace/answer.json`。

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
