# Báo Cáo Sản Xuất Tuần v2 — Xác Minh Tính Toán và Tương Quan Bảo Trì

## Mô tả nhiệm vụ

Bạn là kỹ sư sản xuất tại nhà máy điện tử. Phiên bản nâng cấp này yêu cầu:
1. Phân tích dữ liệu MES và tạo báo cáo (như v1)
2. **MỚI**: Chạy calculation_script.py và xác minh kết quả
3. **MỚI**: Tương quan dữ liệu bảo trì với thời gian dừng máy

## Dữ liệu đầu vào

- `/workspace/inputs/mes_data_zh.csv` — Dữ liệu MES (tiếng Trung)
- `/workspace/inputs/shift_notes_vi.txt` — Ghi chú giao ca (tiếng Việt)
- `/workspace/inputs/target_plan_zh.json` — Mục tiêu sản xuất (tiếng Trung)
- `/workspace/inputs/maintenance_log_vi.txt` — **MỚI** Nhật ký bảo trì (tiếng Việt)
- `/workspace/inputs/calculation_script.py` — **MỚI** Script xác minh tính toán

## Yêu cầu

1. Tạo báo cáo sản xuất tuần bằng tiếng Việt (production_report_vi.md)
2. Tính toán yield cho từng dây chuyền (yield_analysis.json)
3. **MỚI** Chạy calculation_script.py và so sánh kết quả với phân tích của bạn
4. **MỚI** Tương quan nhật ký bảo trì với dữ liệu dừng máy từ MES
5. Xuất verification_results.json với kết quả xác minh
6. Xuất maintenance_correlation.json

## Đầu ra (/workspace/output/)

- production_report_vi.md
- yield_analysis.json: {"by_line": {...}, "by_day": {...}, "overall": float}
- maintenance_correlation.json: {"correlations": [{"maintenance_event": str, "downtime_minutes": int, "line": str, "date": str}]}
- verification_results.json: {"script_output": {...}, "manual_calculation": {...}, "match": bool, "discrepancies": []}

### /workspace/answer.json
{"total_output": int, "overall_yield": float, "total_downtime_minutes": int, "maintenance_events": int, "verification_passed": bool, "correlation_found": int}

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
