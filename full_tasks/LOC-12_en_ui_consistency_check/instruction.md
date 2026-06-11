# Cross-Platform UI Localization Consistency Check

## Objective

You are a localization QA engineer for a mobile/web application that supports Japanese, Korean, and Chinese. The app has localizations across three platforms (iOS, Android, Web) maintained by different teams. Your task is to find all inconsistencies.

## Input Files

- `/workspace/inputs/ios_localizable_ja.strings` - iOS Localizable.strings (Japanese, 60 keys)
- `/workspace/inputs/android_strings_ko.xml` - Android strings.xml (Korean, 60 keys)
- `/workspace/inputs/web_i18n_zh.json` - Web i18n JSON (Chinese Simplified, 60 keys)

## Task

1. Parse all 3 localization files (different formats)
2. Align keys across platforms
3. Identify ALL semantic inconsistencies (8 total)
4. Produce a detailed consistency report

## Required Outputs (in /workspace/output/)

- consistency_report.md
- inconsistencies.json (total_inconsistencies, list with id/key/type/severity/values)
- key_alignment.json
- /workspace/answer.json

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
