# Sự cố 02 · Nguồn đổi tên trường `pm2_5` → `pm25` (schema drift)

**Diễn tập ngày:** 28/11/2026 · `VIETSKY_CHAOS=rename_field run_pipeline.py --date 2026-11-28 --source air_quality` · run `2ebd1b4d`
**Mức độ:** cao (toàn bộ nguồn air_quality dừng) · **MTTD:** ~75 giây (hết extract + load)

## Triệu chứng
- `extract` SUCCESS (34 tỉnh, 6.528 giờ): API vẫn trả 200, JSON vẫn đủ dòng.
- `load` FAILED với `error_message = 'pm2_5'`: một `KeyError` không nói gì về nguyên nhân.

## Phát hiện lúc nào, bằng gì
- Lần diễn tập đầu: chỉ có thông báo `'pm2_5'` trong `ops.pipeline_runs`. Phải mở `data/raw/air_quality/date=2026-11-28/01.json` mới thấy `hourly` có `pm25` thay vì `pm2_5`.
- Check `raw_schema` (Ngày 10) **không kịp chạy**: nó nằm trong `quality_check`, đứng sau `load`, mà `load` đã crash trước.

## Khoanh vùng
extract đạt, load hỏng ngay ở `transform.to_rows` → lỗi nằm giữa raw và staging: cấu trúc raw không khớp hợp đồng (data contract) trong `config.py`.

## Nguyên nhân gốc (5 Whys)
1. Vì sao load hỏng? `to_rows` đọc `hourly['pm2_5']` không tồn tại.
2. Vì sao không tồn tại? Nguồn đổi tên trường (giả lập `chaos.break_payload`).
3. Vì sao thông báo khó hiểu? Không có kiểm tra cấu trúc **trước khi** dùng dữ liệu; lỗi lộ ra ở nơi sâu nhất.
4. Vì sao `raw_schema` có mà không giúp được? Đặt sai vị trí: kiểm tra chạy sau bước mà nó cần bảo vệ.
5. Vì sao mart không bị ảnh hưởng? Load dừng trước khi ghi; build_mart không chạy; dữ liệu cũ còn nguyên.

## Cách sửa
- Ngắn hạn: khi nguồn thật đổi tên, cập nhật `columns` trong `config.py` (tên API → tên DB) rồi chạy lại.
- Đã sửa trong code: `run_load` gọi `assert_raw_schema` đầu tiên. Thông báo giờ là:
  `Schema drift: 34 file raw thiếu cột, ví dụ 01.json thiếu ['pm2_5']`.

## Phòng tránh
- Validate cấu trúc ở **ranh giới** dữ liệu vào hệ thống (fail fast), không đợi đến bước dùng.
- Raw giữ nguyên bản lỗi → sau khi sửa mapping có thể load lại từ raw, không cần gọi lại API.
- Schema drift "mềm" (đổi đơn vị, đổi ý nghĩa) không bị check này bắt; cần so phân phối giá trị với lịch sử.
