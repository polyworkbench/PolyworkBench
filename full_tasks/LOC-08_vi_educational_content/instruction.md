# Nhiệm vụ: Chuyển đổi nội dung giáo dục sang tiếng Việt

## Mô tả
Bạn cần chuyển đổi chương trình giảng dạy Toán học (Đại số cơ bản) từ tiếng Anh sang tiếng Việt, kết hợp tham khảo tài liệu bổ sung từ tiếng Hàn và tiếng Trung. Nội dung phải phù hợp với chuẩn giáo dục Việt Nam và phong cách sư phạm địa phương.

## Tệp đầu vào
Tất cả tệp đầu vào nằm trong thư mục `/workspace/inputs/`:

- `curriculum_en.md` — Chương trình Toán học tiếng Anh: Đại số cơ bản, 10 bài học
- `supplementary_ko.md` — Ghi chú phương pháp giảng dạy Toán từ Hàn Quốc
- `practice_problems_zh.json` — Bài tập thực hành Toán từ tiếng Trung (có lời giải)
- `learning_standards_vi.json` — Chuẩn giáo dục Việt Nam để đối chiếu

## Yêu cầu

### Chương trình giảng dạy (`curriculum_vi.md`)
- Tệp Markdown với đầy đủ 10 bài học
- Mỗi bài học gồm: tiêu đề, mục tiêu học tập, nội dung chính, ví dụ minh họa, tóm tắt
- Sử dụng thuật ngữ Toán học chuẩn tiếng Việt (ví dụ: "phương trình", "biến số", "hệ số")
- Phù hợp với học sinh lớp 7-8 tại Việt Nam
- Tích hợp phương pháp giảng dạy tham khảo từ tài liệu Hàn Quốc

### Bài tập (`exercises_vi.json`)
- Tệp JSON chứa bài tập cho mỗi bài học (tối thiểu 5 bài/bài học = 50 bài tập)
- Mỗi bài tập gồm: `lesson_id`, `exercise_id`, `type` (trắc nghiệm/tự luận/điền khuyết), `question_vi`, `answer`, `difficulty` (1-3), `explanation_vi`
- Tham khảo và chuyển đổi bài tập từ tệp tiếng Trung
- Đảm bảo dấu tiếng Việt chính xác trong toàn bộ nội dung

### Hướng dẫn giáo viên (`teacher_guide_vi.md`)
- Tệp Markdown hướng dẫn giáo viên
- Bao gồm: phương pháp giảng dạy, gợi ý hoạt động lớp, cách xử lý lỗi sai phổ biến
- Tích hợp phương pháp sư phạm Hàn Quốc đã được Việt hóa
- Phân bổ thời gian cho mỗi bài học (45 phút/tiết)

### Đánh giá (`assessment_vi.json`)
- Tệp JSON chứa bài kiểm tra đánh giá
- Gồm: 2 bài kiểm tra giữa kỳ (sau bài 5) và cuối kỳ (sau bài 10)
- Mỗi bài kiểm tra: 10-15 câu hỏi, đa dạng mức độ
- Đối chiếu với chuẩn đánh giá trong `learning_standards_vi.json`

## Đường dẫn xuất
Tất cả tệp xuất được ghi vào thư mục gốc `/workspace/`.

---

**Quan trọng: Tất cả kết quả phải được ghi vào tệp trên ổ đĩa, không chỉ trả lời bằng văn bản. Sử dụng lệnh bash để tạo thư mục, ghi tệp và thực thi script.**
