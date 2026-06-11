# HQ-05 评分锚点（满分 100）

> 本任务为 stress 集，权重侧重「跨源矛盾识别」「不确定性显式化」「长程一致性」。

## Q1 模态保真度（20 分）

| 检查项 | 分值 |
|---|---|
| 中文 CSV 财务数据被准确解析（2023 年净利润 = 15200 万元） | 4 |
| 日文董事会录音的 [unclear] 处不被掩盖，被显式承认 | 4 |
| 日文敬语层级未被错误降级（"でございます" 不译为粗俗法语） | 3 |
| 韩文等记表的股东持股比例被准确提取（80/10/5/5） | 4 |
| 英文 SPA 的 cap (25% / 70M) 被正确读取 | 3 |
| OCR 不明处（韩文 [OCR_불명]）被显式标注 | 2 |

## Q2 语言准确性（20 分）

- [+5] 法文 memo 使用司法/notaire 文体（"il convient de noter"、"sous réserve de"、"aux fins du présent mémorandum"）
- [+5] 五语术语表 ≥ 15 项，且 controller/responsable/责任人/責任者/책임자 五语对齐准确
- [+4] "条件先决"译为 "conditions précédentes"（CP），不直译为 "conditions préalables"
- [+3] "陈述与保证"译为 "déclarations et garanties"（R&W），不译为 "représentations et garanties"（错误英化）
- [+3] 引用日文 board minutes 时，敬语原文片段以斜体保留

## Q3 任务完成度（25 分）

| 检查项 | 分值 |
|---|---|
| Memo 含全部 7 个章节（Synthèse/Capital/Financier/Gouvernance/SPA/RedFlags/Recommandations） | 7 |
| 风险登记 ≥ 5 条且每条含严重度+概率+来源+缓解 | 5 |
| 五语术语表 ≥ 15 项 | 4 |
| 货币换算明确使用年均汇率（CSV 2023 数据 × 0.1305） | 4 |
| Recommandations ≥ 5 条且含执行方建议 | 3 |
| 含免责声明（法律文体规范） | 2 |

## Q4 长程一致性（35 分；本任务核心权重）

| 检查项 | 分值 |
|---|---|
| **跨源矛盾被识别**：中文 CSV 净利 152M vs 日文董事会 142M 的差异被显式标红 | 10 |
| 矛盾的来源被双向引用（CSV + board minutes 同时给出） | 5 |
| 韩文契约诉讼金额（12 Mrd KRW）在 memo §1, §6, §7 三处出现且换算后 EUR 数值一致 | 5 |
| Cap 25% × 280M EUR = 70M EUR 在 §5、§7 两处一致 | 3 |
| 风险登记的 P0 项与 Recommandations §1-§3 对应 | 5 |
| Glossaire 中的 fr 翻译在 memo 全文使用一致（不能 §3 用 résultat net 而 §5 用 bénéfice net） | 4 |
| 所有结论可通过 traceability_fr.md 反向追溯到至少一个非法语源 | 3 |

## 常见错误归因（stress 级专属）

- `E-CONTRADICTION-MISS`：未发现 152M vs 142M 矛盾（最严重，扣 10 分）
- `E-FX-WRONG`：用 spot 汇率换算 2021-2023 年度数据
- `E-CITATION-MISS`：法文文段无 [Source: ...]
- `E-LEGAL-DIALECT`：用魁北克法文（"juste valeur marchande"）而非法国法文（"juste valeur de marché"）
- `E-OCR-MASK`：把 [OCR_불명] / [unclear] 当作真实数据处理
- `E-CONSIST-DRIFT`：金额/数字在不同章节之间漂移
- `E-CULTURE-HONORIFIC`：日文敬语被翻译为不当的法文非正式语
- `E-SCOPE-OMIT`：忽略 Woori Bank 担保（5% 持股有担保权）
- `E-AI-ENFORCE`：行动项缺少负责人 / due date

## 评分尺度（5 分制 → 转 100 分）

- ★1 (0–20)：仅完成单一语言/模态，未产出 memo
- ★2 (21–40)：产出 memo 但忽略多个模态/矛盾
- ★3 (41–60)：基本完成但有 ≥3 处一致性漂移
- ★4 (61–80)：识别核心矛盾，法语规范，少量瑕疵
- ★5 (81–100)：识别全部 ≥5 处风险，跨源引用完整，法律文体规范，矛盾显式化
