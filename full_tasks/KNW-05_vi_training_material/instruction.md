# Xây dựng tài liệu đào tạo Điện toán đám mây bằng tiếng Việt

## Mô tả nhiệm vụ

Chuyển đổi nội dung slide đào tạo tiếng Anh về cơ bản điện toán đám mây và tài liệu kỹ thuật tiếng Trung về dịch vụ AWS/Alibaba Cloud thành tài liệu đào tạo hoàn chỉnh bằng tiếng Việt kèm bài tập thực hành.

## Tệp đầu vào

Tất cả tệp đầu vào nằm trong thư mục `/workspace/inputs/`:

- `training_slides_en.md`: Nội dung slide tiếng Anh về điện toán đám mây cơ bản (12 slides)
- `technical_docs_zh.md`: Tài liệu kỹ thuật tiếng Trung về dịch vụ AWS/Alibaba Cloud
- `terminology_en_zh.json`: Bảng thuật ngữ kỹ thuật Anh-Trung
- `learning_objectives_en.json`: Mục tiêu học tập của khóa học

## Yêu cầu đầu ra

Tạo các tệp sau vào thư mục `/workspace/output/`:

### 1. `training_manual_vi.md`
- Tài liệu đào tạo hoàn chỉnh bằng tiếng Việt
- Bao gồm các phần:
  - Giới thiệu về điện toán đám mây
  - Các mô hình dịch vụ (IaaS, PaaS, SaaS)
  - Các mô hình triển khai (Public, Private, Hybrid)
  - Dịch vụ lưu trữ và cơ sở dữ liệu
  - Dịch vụ mạng và bảo mật
  - Điện toán serverless
  - So sánh nhà cung cấp (AWS vs Alibaba Cloud)
  - Thực hành tốt nhất (Best practices)
- Tối thiểu 3000 từ
- Sử dụng thuật ngữ kỹ thuật tiếng Việt phù hợp
- Mỗi chương có tóm tắt và từ khóa

### 2. `exercises_vi.json`
- Bài tập thực hành cho mỗi chương
- Tối thiểu 10 bài tập
- Mỗi bài tập bao gồm: tiêu đề, mô tả, mức độ khó (1-3), thời gian ước tính, hướng dẫn từng bước, kết quả mong đợi
- Tất cả bằng tiếng Việt

### 3. `glossary_vi_en_zh.json`
- Bảng thuật ngữ ba ngôn ngữ (Việt-Anh-Trung)
- Tối thiểu 40 thuật ngữ
- Mỗi mục bao gồm: thuật ngữ tiếng Việt, tiếng Anh, tiếng Trung, định nghĩa tiếng Việt
- Sắp xếp theo thứ tự bảng chữ cái tiếng Việt

### 4. `assessment_questions_vi.json`
- Câu hỏi đánh giá cuối khóa
- Tối thiểu 20 câu hỏi
- Bao gồm: trắc nghiệm (multiple choice), đúng/sai, câu hỏi mở
- Mỗi câu có: nội dung, loại, đáp án đúng, giải thích, mục tiêu học tập liên quan
- Tất cả bằng tiếng Việt

### 5. `/workspace/answer.json`
- Bao gồm:
  - `total_chapters`: Số chương trong tài liệu
  - `total_exercises`: Tổng số bài tập
  - `total_glossary_terms`: Số thuật ngữ trong bảng
  - `total_questions`: Số câu hỏi đánh giá
  - `covered_objectives`: Danh sách mục tiêu học tập đã đề cập

## Tiêu chí đánh giá

- **Phạm vi nội dung (25%)**: Bao phủ đầy đủ các chủ đề từ nguồn
- **Chất lượng tiếng Việt (25%)**: Ngôn ngữ tự nhiên, thuật ngữ chính xác
- **Chất lượng bài tập (20%)**: Bài tập thực tế và có ích cho người học
- **Độ chính xác thuật ngữ (15%)**: Bảng thuật ngữ đầy đủ và chính xác
- **Cấu trúc sư phạm (15%)**: Trình tự hợp lý, từ cơ bản đến nâng cao

**Quan trọng: Tất cả kết quả phải được ghi vào tệp trên đĩa, không chỉ trả lời dạng văn bản. Sử dụng lệnh bash để tạo thư mục, viết tệp và thực thi script.**
