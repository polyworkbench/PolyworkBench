# Аудит безопасности v2 — Расчёт MTBF и анализ повторяющихся паттернов

## Цель

Вы — инженер по безопасности на производстве. Проведите аудит безопасности на основе отчётов об инцидентах и истории оборудования. В этой версии добавлено:
1. Расчёт MTBF (среднее время между отказами) для 5 типов оборудования
2. Идентификация повторяющихся паттернов из истории оборудования

## Входные файлы

- `/workspace/inputs/safety_reports_zh.txt` — Отчёты о безопасности (китайский)
- `/workspace/inputs/iso_checklist_en.json` — Чек-лист ISO 45001 (английский)
- `/workspace/inputs/equipment_history_en.csv` — **НОВОЕ** История отказов оборудования (английский, 50 записей)

## Задачи

1. Провести аудит по чек-листу ISO 45001
2. Проанализировать отчёты об инцидентах (китайский)
3. **НОВОЕ**: Рассчитать MTBF для каждого из 5 типов оборудования
4. **НОВОЕ**: Выявить повторяющиеся паттерны отказов
5. Составить план действий на русском языке

## Выходные файлы (/workspace/output/)

### safety_audit_ru.md — Полный отчёт аудита на русском
### mtbf_analysis.json
{"equipment_types": [{"type": str, "mtbf_hours": float, "failures": int, "total_hours": int}]}
### repeat_patterns.json
{"patterns": [{"equipment_type": str, "failure_mode": str, "occurrences": int, "avg_interval_days": float}]}
### action_plan_ru.json — План корректирующих действий

### /workspace/answer.json
{"total_findings": int, "critical_findings": int, "mtbf_calculated": 5, "repeat_patterns_found": int, "worst_mtbf_equipment": str, "iso_compliance_percent": float}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
