# HQ-05 · 跨境 M&A 多模态尽调包 → 法文 DD memo

- **集合**：stress（极限难度）
- **难度**：★★★★★（5/5）
- **指令语 / 源语 / 产出语**：fr / en+zh+ja+ko / fr
- **模态**：scanned_pdf + table + audio + screenshot（4 模态 × 4 语言）
- **预计步骤数**：12+
- **预计人工耗时**：8–16 h（团队协作）

## 业务背景

法国奢侈品集团 LVMH 系子公司拟收购一家亚太区电商科技公司"AsiaCommerce Holdings"，该公司在中国（运营总部）、日本（技术中心）、韩国（市场分公司）均有实体。法语 M&A 团队需在 72 小时内完成一份初步尽职调查备忘录，依据：

- 英文主合同（Share Purchase Agreement 草案）
- 中文目标公司近三年财报（Excel）
- 日文董事会决议录音（30 min）
- 韩文工商登记/股权结构截图

输出**法文** DD memo 给巴黎仲裁律师与集团 CFO。

## Agent Prompt（fr，原样喂给 Agent）

```
Vous êtes un assistant de M&A spécialisé en transactions transfrontalières Asie-Europe. Préparez un mémorandum de due diligence préliminaire (en français) sur l'acquisition envisagée d'AsiaCommerce Holdings (cible) par notre groupe.

Sources fournies :
- inputs/spa_draft.md — Share Purchase Agreement (anglais)
- inputs/financials_zh.csv — Données financières 2021-2023 (chinois)
- inputs/board_minutes_ja.txt — Transcription du procès-verbal du conseil d'administration (japonais, audio transcrit avec balises [unclear])
- inputs/corporate_registry_ko.txt — Capture d'écran OCR du registre coréen (coréen)

Livrables attendus (tous en français) :

1. Mémorandum DD (memo_dd_fr.md) avec sections :
   1.1 Synthèse exécutive (½ page)
   1.2 Structure capitalistique de la cible (issue de la Corée)
   1.3 Performance financière 2021-2023 (issue de la Chine, conversion en EUR au taux moyen annuel)
   1.4 Gouvernance et résolutions récentes (issue du Japon)
   1.5 Termes clés du SPA (issue de l'anglais) — focus sur :
       - Conditions précédentes (CP / CPs)
       - Déclarations et garanties (R&W)
       - Indemnités et plafonds (caps and baskets)
       - Droit applicable et arbitrage
   1.6 Drapeaux rouges (red flags) — synthèse des risques détectés
   1.7 Recommandations de prochaines étapes

2. Tableau de risques (risk_register.json) — JSON structuré avec sévérité, probabilité, source.

3. Glossaire quadrilingue (glossaire_fr_en_zh_ja_ko.json) des 15 termes M&A et corporatifs critiques.

4. Annexe de traçabilité (traceability_fr.md) : chaque conclusion du mémo doit être traçable à au moins une source via [Source: fichier, ligne/section].

Contraintes critiques :
- Aucune conclusion sans citation traçable.
- Tous les chiffres financiers en EUR, avec le taux et la date de conversion explicites.
- Mentionner explicitement les zones d'incertitude (e.g., [unclear] dans la transcription audio, OCR douteux).
- Le français doit être conforme au registre juridique français (vouvoiement, formulations notariales).
- Aux endroits où les sources se contredisent (e.g., financiers chinois vs. déclarations japonaises), signaler la divergence sans la résoudre arbitrairement.
```

## 输入资料清单

- `inputs/spa_draft.md` — 英文 SPA 草案（含 CP, R&W, indemnity caps, governing law）
- `inputs/financials_zh.csv` — 中文财务数据（营收/净利/资产负债，2021-2023）
- `inputs/board_minutes_ja.txt` — 日文董事会会议录音转写（含敬语 + [unclear]）
- `inputs/corporate_registry_ko.txt` — 韩文公司登记截图 OCR（股东结构）
- `inputs/fx_rates.json` — 三年人民币 / 日元 / 韩元对欧元的年均汇率

## 工具需求

- 多语言 OCR / ASR（实际部署时）
- 跨语言 RAG（术语对齐）
- 表格解析 / 货币换算
- 法律术语规范库（法语司法术语）

## 关键考察点（极限难度专属）

1. **四语 × 四模态对齐**：每个结论必须能追溯到至少一个非法语源
2. **跨源矛盾识别**：故意在中文财报与日文董事会会议中埋下一处净利润数字不一致，看 Agent 是否能识别并标红
3. **货币换算链路**：CNY → EUR、JPY → EUR、KRW → EUR 三套年均汇率的正确使用
4. **法律语域**：法语必须是司法/notaire 文体（"il convient de noter que…"、"sous réserve de…"、"aux fins du présent mémorandum…"）
5. **不确定性显式化**：[unclear] / OCR 错误必须显式承认，而非掩盖
6. **长程链路 12+ 步**：解析→换算→对账→风险识别→引用回溯→法语生成→交叉校验
