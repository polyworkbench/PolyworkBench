# Kiểm tra tuân thủ pháp luật lao động

## Nhiệm vụ

Bạn được cung cấp các hợp đồng lao động mẫu bằng tiếng Việt, tiêu chuẩn ILO bằng tiếng Anh, trích dẫn Bộ luật Lao động Việt Nam 2019, và chính sách nhân sự của công ty. Hãy thực hiện kiểm tra tuân thủ toàn diện và tạo báo cáo bằng tiếng Việt.

## Tệp đầu vào

- `/workspace/inputs/labor_contracts_vi.txt` — 3 hợp đồng lao động mẫu (tiếng Việt)
- `/workspace/inputs/ilo_standards_en.json` — Yêu cầu từ các công ước ILO liên quan
- `/workspace/inputs/vietnam_labor_code_vi.txt` — Trích dẫn Bộ luật Lao động 2019
- `/workspace/inputs/company_policies_en.md` — Chính sách nhân sự của công ty (tiếng Anh)

## Yêu cầu

- So sánh các hợp đồng lao động với tiêu chuẩn ILO và Bộ luật Lao động Việt Nam 2019
- Tạo danh sách kiểm tra tuân thủ (compliance_checklist_vi.md) với đánh giá từng điều khoản
- Phân tích khoảng cách (gap_analysis_vi.json) giữa thực tế và yêu cầu pháp luật
- Liệt kê các hạng mục rủi ro (risk_items_vi.json) với mức độ nghiêm trọng (cao/trung bình/thấp)
- Đề xuất kế hoạch khắc phục (remediation_plan_vi.md) với các bước cụ thể và thời hạn
- Xác định các vi phạm cụ thể liên quan đến: giới hạn làm thêm giờ, thời gian nghỉ ngơi tối thiểu, thời gian thử việc
- Trong answer.json ghi: `{"total_violations": int, "high_risk_count": int, "ilo_conventions_violated": [str]}`

## Tệp đầu ra

Kết quả lưu vào `/workspace/output/`:
- `/workspace/output/compliance_checklist_vi.md`
- `/workspace/output/gap_analysis_vi.json`
- `/workspace/output/risk_items_vi.json`
- `/workspace/output/remediation_plan_vi.md`

Tóm tắt cuối cùng lưu vào `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
