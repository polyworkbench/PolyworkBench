# Bản địa hóa chiến dịch marketing sang tiếng Việt

## Nhiệm vụ

Bạn cần chuyển đổi nội dung marketing từ tiếng Anh và hướng dẫn thương hiệu từ tiếng Trung sang tài liệu chiến dịch tiếng Việt phù hợp với văn hóa và thị trường Việt Nam.

## Tệp nguồn

Tất cả tệp nằm trong `/workspace/inputs/`:

- `marketing_copy_en.md` — Nội dung chiến dịch tiếng Anh (5 bài đăng mạng xã hội, 3 biến thể quảng cáo, 2 tiêu đề email)
- `brand_guidelines_zh.md` — Hướng dẫn thương hiệu bằng tiếng Trung (giọng điệu, màu sắc, từ ngữ cấm)
- `target_audience_en.json` — Nhân khẩu học và sở thích đối tượng mục tiêu
- `cultural_calendar_vi.json` — Sự kiện văn hóa và ngày lễ Việt Nam

## Yêu cầu

- Chuyển đổi tất cả nội dung marketing sang tiếng Việt tự nhiên, hấp dẫn
- Tuân thủ hướng dẫn thương hiệu (giọng điệu, từ ngữ cấm)
- Điều chỉnh nội dung phù hợp với văn hóa Việt Nam
- Tích hợp các sự kiện văn hóa/ngày lễ Việt Nam vào thời điểm đăng bài
- Sử dụng ngôn ngữ marketing hấp dẫn (ví dụ: "Khám phá ngay", "Ưu đãi đặc biệt", "Mua sắm thông minh")
- Đảm bảo dấu tiếng Việt chính xác
- Mỗi bài đăng mạng xã hội có hashtag tiếng Việt phù hợp
- Giữ nguyên CTA (Call-to-Action) nhưng bản địa hóa phù hợp

## Tệp đầu ra

Lưu kết quả vào `/workspace/outputs/`:

- `campaign_materials_vi.md` — Tổng quan chiến dịch bằng tiếng Việt
- `social_posts_vi.json` — Bài đăng mạng xã hội (mảng JSON với nội dung, hashtag, thời điểm đề xuất)
- `ad_copy_vi.json` — Nội dung quảng cáo (tiêu đề, mô tả, CTA)
- `brand_compliance_report.json` — Báo cáo tuân thủ thương hiệu

## Định dạng social_posts_vi.json

```json
[
  {
    "id": "post_01",
    "platform": "facebook|instagram|tiktok",
    "content": "Nội dung bài đăng...",
    "hashtags": ["#hashtag1", "#hashtag2"],
    "suggested_timing": "Thời điểm đề xuất",
    "cultural_note": "Ghi chú văn hóa"
  }
]
```

## Định dạng ad_copy_vi.json

```json
[
  {
    "id": "ad_01",
    "headline": "Tiêu đề quảng cáo",
    "description": "Mô tả",
    "cta": "Hành động",
    "target_segment": "Phân khúc mục tiêu"
  }
]
```

**Quan trọng: Tất cả sản phẩm phải được ghi vào tệp trên đĩa, không chỉ trả lời bằng văn bản. Sử dụng lệnh bash để tạo thư mục, ghi tệp và thực thi script.**
