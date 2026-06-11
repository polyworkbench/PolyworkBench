# 跨境仲裁争议诉讼策略简报

## 任务背景

在 `/workspace/inputs/` 目录中有一宗涉及中国企业与俄罗斯对手方的国际商事仲裁案件的相关文件。仲裁机构为国际商会仲裁院（ICC），需要为中方当事人编写中文诉讼策略简报。

## 输入文件

- `arbitration_clause_en.md` — 英文仲裁协议条款（ICC规则）
- `counterparty_filing_ru.md` — 俄罗斯对手方的仲裁申请书（俄文）
- `contract_history_en.json` — 交易记录和付款历史（英文）
- `correspondence_en.txt` — 当事人之间的电子邮件往来（英文）

## 具体要求

- 分析仲裁条款，确定仲裁地、适用法律、仲裁语言等关键程序要素
- 翻译并分析俄方仲裁申请书的主要主张和法律依据
- 编写完整的中文诉讼策略简报（`litigation_brief_zh.md`），包含：
  - 案件概述与争议焦点
  - 程序性分析（仲裁地、适用法律、时效等）
  - 实体性分析（合同解释、违约责任、不可抗力抗辩）
  - 我方答辩策略和建议
  - 风险评估
- 生成策略分析JSON（`strategy_analysis.json`），结构化记录：
  - 仲裁地（arbitration_seat）
  - 适用法律（applicable_law）
  - 争议金额（dispute_amount）
  - 对方主要主张（counterparty_claims）
  - 我方抗辩要点（defense_points）
  - 胜率评估（win_probability）
- 整理证据清单（`evidence_list_zh.json`），列出所有可用证据及其证明目的
- 制作时间线（`timeline_zh.json`），按时间顺序梳理案件关键事件

## 输出路径

所有结果文件保存至 `/workspace/output/`，总结保存至 `/workspace/answer.json`。

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
