# HQ-02 评分锚点（满分 100）

## Q1 模态保真度（30 分；OCR 重权重）

| 检查项 | 分值 |
|---|---|
| R001 三个税率字段全部正确（8%/10% 拆分，¥69 / ¥20） | 6 |
| R002 全部金额字段正确（¥8,910 / ¥5,490 / ¥1,309 / ¥14,400） | 5 |
| R003 因印章遮挡，总金额能从行项重构（¥31,130） | 5 |
| 印章存在性正确标注（R001=true, R002=false, R003=true） | 3 |
| 手写内容正确捕获（R001 的「出張交通費」） | 3 |
| confidence 与遮挡情况单调相关（R002 > R001 > R003） | 4 |
| 日期 OCR 正确（含和历→公历换算） | 4 |

## Q2 语言准确性（20 分）

- [+5] 「上様」未被字面直译为 "Mr. Above" 等错误，正确解释为 generic addressee
- [+5] 「軽減税率」概念在 Description / issues 中被正确传达
- [+5] CSV 列名为标准 SAP Concur 英文（Date / Vendor / Description / Amount_JPY / Tax_Rate / Amount_CNY / Receipt_ID）
- [+5] exceptions.md 用专业财务英文（reimbursement / re-issued / GL / posting）

## Q3 任务完成度（30 分）

| 检查项 | 分值 | 关键扣分点 |
|---|---|---|
| 和历→公历换算（令和 6 年 = 2024） | 5 | 错误 = 全扣 |
| 8%/10% 税率分别记录 | 5 | 合并成单一税率扣 3 |
| 上様 + 金额 ≥ 30,000 触发拒付 | 8 | 漏掉此规则扣全部，本任务最关键合规点 |
| CNY 换算正确（取两位小数，使用 0.04632） | 4 | 用其他汇率扣全部 |
| CSV 含 UTF-8 BOM | 3 | 缺失扣 3 |
| 异常清单按严重度排序（Critical / Warning / Info） | 5 | 未分级扣 3 |

## Q4 长程一致性（20 分）

- [+8] CSV 中的金额 = extraction.total_jpy = 行项之和（三处一致）
- [+5] CSV 行数 = extraction 元素数 = 输入票据数
- [+4] R003 的 PENDING REVIEW 标记同时出现在 CSV、extraction.issues、exceptions.md
- [+3] confidence < 0.7 的票据均出现在 exceptions.md

## 常见错误归因

- `E-OCR-CRITICAL`：金额关键字段 OCR 错误
- `E-COMPLIANCE-MISS`：未识别上様 + 30k 阈值
- `E-CULTURE-DATE`：和历未换算
- `E-CONSIST-DRIFT`：CSV 与 extraction 金额不一致
- `E-LANG-LITERAL`：上様 / 軽減税率 字面直译
