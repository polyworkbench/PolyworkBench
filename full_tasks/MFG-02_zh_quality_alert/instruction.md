# 质量警报生成 — 从越南语QC日志和英文规格书生成中文质量警报

## 任务描述

你是一名质量工程师，需要分析来自越南质检人员的检验日志（越南语）和英文产品规格书，生成一份完整的中文质量警报报告，包含根本原因分析和纠正措施。

## 输入数据

- `/workspace/inputs/qc_inspection_vi.csv` — 越南语QC检验员日志，包含缺陷描述
- `/workspace/inputs/spec_sheets_en.json` — 英文产品规格书，包含公差要求
- `/workspace/inputs/defect_photos_description.txt` — 缺陷照片的文字描述
- `/workspace/inputs/production_params_zh.csv` — 中文生产参数日志

## 要求

- 生成中文质量警报文档（`quality_alert_zh.md`），包含：警报级别、影响范围、缺陷描述、紧急处理措施
- 进行根本原因分析，输出到 `root_cause_analysis.json`，使用鱼骨图（5M1E）方法，包含：人(Man)、机(Machine)、料(Material)、法(Method)、测(Measurement)、环(Environment)
- 对所有缺陷进行分类，输出到 `defect_classification.json`，包含：缺陷类型、严重程度(Critical/Major/Minor)、发生频率、受影响批次
- 制定纠正措施计划，输出到 `corrective_actions_zh.json`，包含：短期措施、长期措施、责任人、完成期限
- 对比实际检测数据与英文规格书中的公差要求，找出超标项
- 分析生产参数，找出参数偏移与缺陷的相关性
- 质量警报必须符合ISO 9001标准格式
- 生成 `answer.json`：`{"alert_level": str, "total_defects": int, "critical_defects": int, "affected_batches": list, "top_root_cause": str, "containment_action": str}`

## 输出

将所有文件写入 `/workspace/output/`:
- `quality_alert_zh.md`
- `root_cause_analysis.json`
- `defect_classification.json`
- `corrective_actions_zh.json`

以及 `/workspace/answer.json`

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
