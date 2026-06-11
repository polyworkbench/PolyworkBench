# HQ-02 · 日文发票扫描件 → 英文报销 Excel

- **集合**：baseline
- **难度**：★★★（3/5）
- **指令语 / 源语 / 产出语**：zh / ja / en
- **模态**：scanned_pdf + image（含手写体 + 印章）
- **预计步骤数**：6
- **预计人工耗时**：1–2 h

## 业务背景

跨国财务共享中心（中国上海）每月需要处理日本子公司员工提交的差旅发票（領収書 + 請求書）。发票为扫描件 PDF 与手机拍照 JPG 混合，含印章遮挡、手写补充金额、税额拆分。最终需录入 SAP Concur 的英文报销表，并用人民币换算（取当日中国人民银行中间价）。

## Agent Prompt（zh，原样喂给 Agent）

```
你是一个跨境财务自动化助手。请处理 inputs/ 目录下的日文票据图像（含 PDF 扫描件和 JPG 手机拍照），完成以下流程：

1. 对每张票据做 OCR，提取以下字段：
   - 発行日（日期，注意和历日号如「令和6年」需换算为公历）
   - 発行者 / 店舗名（开票方）
   - 宛名（抬头，可能为「上様」需特别标注）
   - 税抜金額 / 消費税 / 税込合計（注意 8% 与 10% 税率并存，便利店食品多为 8%）
   - 手写补充内容（如手写的项目说明）
   - 印章存在与否（仅记录，不影响录入）
2. 对印章遮挡或手写不清的字段，给出 confidence ∈ [0, 1]，并在 issues 字段记录。
3. 用 inputs/jpy_cny_rate.json 提供的当日汇率换算为 CNY，保留两位小数。
4. 按 SAP Concur 英文模板（Date / Vendor / Description / Amount JPY / Tax Rate / Amount CNY / Receipt ID）输出 CSV。
5. 输出一份英文异常清单（exceptions.md），列出需要财务复核的票据 ID 与原因。
6. 对于「上様」抬头的发票，根据日本国税厅规定，单笔金额 < 30,000 JPY 可入账，否则必须打回，请在 exceptions.md 中明确标注。

输出三件事：
A. concur_expense.csv（UTF-8，含 BOM 以兼容 Excel）
B. extraction.json（每张票据的完整字段，含 confidence）
C. exceptions.md（英文，按严重度排序）
```

## 输入资料清单

- `inputs/receipt_001.txt`：模拟 OCR 后的日文文本（替代真实图片，便于纯文本环境测试）
- `inputs/receipt_002.txt`、`inputs/receipt_003.txt`：另两张
- `inputs/jpy_cny_rate.json`：当日汇率与日期
- `inputs/IMAGE_DESCRIPTIONS.md`：原始图像的人工描述（用于多模态 Agent 模拟视觉输入）

> 真实评测时，把 `IMAGE_DESCRIPTIONS.md` 替换为真实 JPG/PDF 即可。

## 工具需求

- OCR（PaddleOCR / Azure DI / Textract，支持日文 + 手写）
- 文件读写、JSON/CSV 处理
- 日期与货币换算（含和历→公历）

## 关键考察点

- 和历转换（令和 6 年 = 2024 年）
- 「上様」抬头的合规边界（30,000 JPY 阈值）
- 8%/10% 税率混合
- OCR 噪声 + 手写体的 confidence 标注
- 输出 CSV 的编码兼容性（Excel 在 Windows 下需 UTF-8 BOM）
