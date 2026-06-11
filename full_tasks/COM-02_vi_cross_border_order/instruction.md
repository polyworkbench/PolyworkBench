# Xử lý đơn hàng xuyên biên giới Trung Quốc - Việt Nam

Trong `/workspace/inputs/` có các file dữ liệu đơn hàng xuyên biên giới từ nhà cung cấp Trung Quốc sang Việt Nam. Cần xử lý 10 đơn hàng: đối soát hóa đơn nhà cung cấp Trung Quốc với tờ khai hải quan Việt Nam, tạo nhãn vận chuyển bằng tiếng Việt.

Yêu cầu:
- Đối soát dữ liệu từ file hóa đơn nhà cung cấp (`supplier_invoices_zh.csv`) với thông tin tờ khai hải quan (`customs_forms_vi.txt`): kiểm tra số lượng, giá trị, mã HS
- Tạo file đối soát đơn hàng (`orders_reconciled.json`) gồm thông tin đầy đủ của 10 đơn hàng: mã đơn, sản phẩm, số lượng, giá CNY, giá VND quy đổi, mã HS, trạng thái đối soát
- Tạo nhãn vận chuyển tiếng Việt (`shipping_labels_vi.json`) cho 10 đơn hàng với đầy đủ thông tin: tên người nhận, địa chỉ, số điện thoại, mã bưu chính, trọng lượng, kích thước
- Tạo tờ khai hải quan tiếng Việt (`customs_declarations_vi.json`) bao gồm: mô tả hàng hóa, xuất xứ, giá trị khai báo (VND), mã HS 8 số, thuế suất áp dụng
- Phát hiện và báo cáo các sai lệch (`discrepancy_report.md`) giữa hóa đơn và tờ khai: chênh lệch giá, sai mã HS, sai số lượng
- Sử dụng file `hs_codes_reference.json` để tra cứu mã HS chính xác và thuế suất nhập khẩu
- Quy đổi tiền tệ CNY → VND theo tỷ giá trong dữ liệu đầu vào (1 CNY = 3,450 VND)
- Tổng hợp kết quả vào `/workspace/answer.json`

Kết quả lưu vào `/workspace/output/`, file tổng hợp tại `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
