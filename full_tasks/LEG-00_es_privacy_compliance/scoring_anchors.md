# HQ-04 评分锚点（满分 100）

## Q1 模态保真度（10 分；本任务文本为主）

- [+5] 三份政策的关键章节号被准确引用（§4, §7, Art. 6, Art. 22-25 等）
- [+5] 引用格式统一 `[Fuente: archivo, §N]`

## Q2 语言准确性（30 分；三语术语对齐为核心）

| 检查项 | 分值 |
|---|---|
| 三语术语表 ≥ 10 项，且 titular/data subject/betroffene Person 三对一映射正确 | 8 |
| ARCO 四字母正确展开（Acceso/Rectificación/Cancelación/Oposición）并映射到对应 EN/DE 概念 | 8 |
| 用墨西哥西文（"aviso de privacidad" 而非 "política de privacidad"，"cancelación" 而非 "supresión"） | 5 |
| 不把 "Widerspruch" 误译为 "objeción" 或 "rechazo"（应为 "oposición"） | 4 |
| Schrems II / DPF / SCC 等技术术语保留英文缩写但加西文解释 | 5 |

## Q3 任务完成度（35 分）

| 检查项 | 分值 | 说明 |
|---|---|---|
| 矩阵覆盖 6 大类别（base legal/ARCO/plazo/transferencia/menores/brechas） | 10 | 漏一类扣 2 |
| 每行有 CCPA + DSGVO + LFPDPPP 三列引用 | 6 | |
| ❌/⚠️/✅ 状态判断合理且一致 | 6 | 美国政策 §7 必须为 ❌ |
| 推荐行动 ≥ 5 条，每条含责任人 + 时限 + 优先级 | 6 | |
| 报告以"INAI 提交可用"标准撰写（含免责声明、版本、范围） | 4 | |
| 识别出 LFPDPPP 特有要求（aviso de privacidad Art. 16） | 3 | |

## Q4 长程一致性（25 分）

- [+8] 矩阵中的 ❌ 项均出现在"推荐行动"中（关键 ❌ 不能漏）
- [+5] 术语在报告全文一致（不能上一页 ARCO 下一页 ARC0）
- [+5] 时限一致（20 días LFPDPPP / 1 mes DSGVO / 45 días CCPA 在多处出现时数字相同）
- [+4] 行动项 due date 早于 Q1 2025 上线时间
- [+3] 矩阵 + 章节分析 + 行动项三处对同一议题（如 transfer EE.UU.→MX）结论自洽

## 常见错误归因

- `E-LANG-LITERAL`：Widerspruch → "rechazo"
- `E-LANG-DIALECT`：用半岛西文 "fichero" 而非美西 "archivo"
- `E-LEGAL-MISMAP`：把 right-to-opt-out 等同于 Widerspruch（实际是 right-to-sale 限定）
- `E-CITATION-MISS`：仅写"según CCPA"不带条款号
- `E-COMPLIANCE-DRIFT`：矩阵说 ❌ 但行动项里漏掉相应整改
