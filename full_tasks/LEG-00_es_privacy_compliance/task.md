# HQ-04 · 西文指令对比 EN/DE 隐私政策 → 西文 LFPDPPP 合规报告

- **集合**：baseline
- **难度**：★★★★（4/5）
- **指令语 / 源语 / 产出语**：es / en+de / es
- **模态**：text + scanned_pdf（德文政策为扫描件）
- **预计步骤数**：8
- **预计人工耗时**：4–6 h（律师协助）

## 业务背景

某 SaaS 公司美国总部沿用 CCPA 框架（英文政策），德国分公司沿用 DSGVO/BDSG 框架（德文政策）。墨西哥城拉美区 DPO（数据保护官）需评估两份政策与墨西哥《联邦个人数据保护法》（LFPDPPP，含 ARCO 权利）的差距，输出西班牙文合规差异报告。

## Agent Prompt（es，原样喂给 Agent）

```
Eres un asistente legal especializado en protección de datos personales. Compara las dos políticas de privacidad adjuntas (Estados Unidos en inglés bajo CCPA, y Alemania en alemán bajo DSGVO/BDSG) y genera un informe de cumplimiento conforme a la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP) de México.

Requisitos:
1. Extrae las cláusulas clave de cada política y mapea su correspondencia trilateral:
   - Base legal de tratamiento (CCPA business purpose vs. DSGVO Art. 6 vs. LFPDPPP Art. 8/9)
   - Derechos del titular (CCPA right-to-know/delete/opt-out vs. DSGVO Auskunft/Löschung vs. LFPDPPP ARCO)
   - Periodo de retención
   - Transferencias internacionales (CCPA Service Provider, DSGVO SCC/Adequacy, LFPDPPP arts. 36-37)
   - Edad de consentimiento de menores (13 EE.UU. / 16 UE / variable LFPDPPP)
   - Notificación de violaciones de seguridad
2. Para cada categoría, indica:
   - ✅ Cumple con LFPDPPP
   - ⚠️ Cumple parcialmente, requiere ajuste
   - ❌ No cumple
3. Cita textualmente las cláusulas relevantes con su idioma original entre paréntesis para trazabilidad. Formato: [Fuente: archivo, línea/sección].
4. Incluye una tabla de equivalencia terminológica trilingüe (ES/EN/DE) para los 10 términos más críticos (data subject, controller, processor, etc.).
5. Termina con una lista priorizada de 5-8 acciones recomendadas para que la empresa pueda operar legalmente en México.
6. El informe debe ser apto para presentación al INAI (Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales).
```

## 输入资料清单

- `inputs/policy_us_ccpa.md`：美国总部隐私政策（英文，简化版，9 个核心条款）
- `inputs/policy_de_dsgvo.md`：德国分公司隐私政策（德文，简化版，9 个核心条款）
- `inputs/lfpdppp_extracts.md`：墨西哥 LFPDPPP 关键条款摘录（西文，参考）
- `inputs/COMPANY_CONTEXT.md`：公司业务背景（B2B SaaS，处理拉美区 ~50 万用户数据）

## 工具需求

- 长文档检索 / 跨文档引用
- 多语术语对齐（建议 RAG 或 IATE 术语库注入）
- 结构化报告生成

## 关键考察点

1. **三法对齐**：CCPA / DSGVO / LFPDPPP 的等价、半等价、无对应关系正确判别
2. **ARCO 权利映射**：墨西哥特有的 Acceso/Rectificación/Cancelación/Oposición 是否被准确映射到英德两边
3. **跨境传输**：英文政策可能未覆盖墨西哥→美国传输（仅覆盖加州内）；德文政策的 SCC 是否能复用
4. **未成年人门槛**：墨西哥 LFPDPPP 第 8 条对未成年人有特殊规定
5. **西文输出文体**：LATAM 法律西文 vs 西班牙半岛西文（用法美西文为佳，墨西哥读者）
