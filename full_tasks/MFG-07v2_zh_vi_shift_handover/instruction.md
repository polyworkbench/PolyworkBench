# 双语交班协议 v2 — 格式验证与质量指标整合

## 目标

你是一家中越合资工厂的生产主管。需要创建标准化的双语（中文/越南语）交班文件。v2新增：
1. **新增**：运行 validate_handover.py 验证交班文件格式
2. **新增**：整合质量指标CSV到交班记录中

## 输入文件

- `/workspace/inputs/shift_notes_zh.txt` — 中文班组笔记
- `/workspace/inputs/shift_notes_vi.txt` — 越南语班组笔记
- `/workspace/inputs/quality_metrics.csv` — **新增** 质量指标数据（英文）
- `/workspace/inputs/validate_handover.py` — **新增** 格式验证脚本

## 任务要求

1. 综合中越两方班组笔记，创建标准化交班文件
2. 中文版(handover_zh.md)和越南语版(handover_vi.md)内容对应
3. **新增**：将quality_metrics.csv中的数据整合到交班文件中
4. **新增**：运行validate_handover.py验证格式，修正直到通过
5. 生成quality_summary.json汇总质量数据

## 输出文件 (/workspace/output/)

### handover_zh.md — 中文交班记录
### handover_vi.md — 越南语交班记录
### quality_summary.json
{"shift_yield": float, "defect_count": int, "top_defect": str, "lines_below_target": []}
### validation_output.json
{"validation_passed": bool, "checks": [{"name": str, "passed": bool}]}

### /workspace/answer.json
{"zh_sections": int, "vi_sections": int, "quality_integrated": bool, "validation_passed": bool, "shift_yield": float, "defect_count": int}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
