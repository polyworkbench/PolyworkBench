# 任务：生成中文字幕（基于多语言源材料）

## 背景
你需要基于英文原始字幕文件，并参考日文和韩文的参考字幕，生成高质量的中文字幕文件。该视频是一部关于人工智能与机器学习的技术纪录片。

## 输入文件
所有输入文件位于 `/workspace/inputs/` 目录：

- `transcript_en.srt` — 英文原始字幕（SRT格式，50条字幕条目，含时间码）
- `reference_ja.srt` — 日文参考字幕（同一视频）
- `reference_ko.srt` — 韩文参考字幕（同一视频）
- `terminology_guide_en.json` — 领域术语翻译指南（英中日韩对照）
- `video_context.md` — 视频主题与场景描述

## 要求

### 字幕文件 (`subtitles_zh.srt`)
- 严格遵循 SRT 格式：序号、时间码（`HH:MM:SS,mmm --> HH:MM:SS,mmm`）、字幕文本、空行
- 必须包含 **50 条** 字幕条目，序号从 1 到 50 连续编号
- 每条字幕最多 **2 行**，每行不超过 **18 个中文字符**
- 时间码与英文原始字幕保持同步（允许 ±200ms 微调以适配中文表达节奏）
- 中文表达要自然流畅，符合字幕风格（简洁有力，避免书面语过重）
- 专业术语必须与 `terminology_guide_en.json` 保持一致

### 字幕数据文件 (`subtitle_data.json`)
- JSON 格式，包含所有 50 条字幕的结构化数据
- 每条记录包含：`id`, `start_time`, `end_time`, `text_zh`, `text_en_source`, `confidence_score`
- `confidence_score` 范围 0.0-1.0，表示翻译质量自评

### 时间同步报告 (`timing_report.json`)
- 记录所有时间调整信息
- 包含：`total_entries`, `adjusted_entries`, `max_adjustment_ms`, `average_adjustment_ms`
- 列出所有做了时间调整的条目及调整原因

### 术语表 (`terminology_glossary.json`)
- 从字幕中提取的所有专业术语中英对照
- 包含：`term_en`, `term_zh`, `occurrences`, `source`（标注术语来源：terminology_guide/ja_reference/ko_reference/context）

## 输出路径
所有输出文件写入 `/workspace/` 根目录。

---

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
