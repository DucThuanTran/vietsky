# Sự cố 04 · Đảo lat/lon của 3 tỉnh trong dữ liệu tham chiếu

**Diễn tập ngày:** 28/11/2026 · `VIETSKY_CHAOS=swap_latlon run_pipeline.py --date 2026-11-28 --source weather`
**Mức độ:** cao nếu lọt (lấy nhầm dữ liệu của nơi khác, bản đồ sai) · **MTTD:** < 1 giây

## Triệu chứng
Pipeline dừng ngay khi khởi động:
```
ValueError: provinces.csv không hợp lệ: Hà Nội nằm ngoài Việt Nam: (105.84117, 21.0245);
Cao Bằng nằm ngoài Việt Nam: (106.25786, 22.66568); Tuyên Quang nằm ngoài Việt Nam: (105.21424, 21.82356)
```

## Phát hiện lúc nào, bằng gì
Bằng kiểm tra toạ độ (`validate.check_coordinates`: lat 8–24, lon 102–110) trong `sync_locations`, chạy **trước** mọi chặng.

## Khoanh vùng
Dữ liệu tham chiếu (`config/provinces.csv` → `dim_location`). Không có gì được ghi: không raw, không staging, `dim_location` giữ toạ độ đúng.

## Nguyên nhân gốc (5 Whys)
1. Vì sao pipeline dừng? Toạ độ 3 tỉnh nằm ngoài Việt Nam.
2. Vì sao toạ độ sai? Cột lat và lon bị đổi chỗ (giả lập `chaos.swap_latlon`; ngoài đời: người sửa CSV dán nhầm cột).
3. Vì sao lại nguy hiểm? Nếu lọt: lat 105 không tồn tại nên API trả 400; nếu cả 2 toạ độ vẫn hợp lệ (ví dụ đảo nhầm giữa 2 tỉnh) thì API **trả dữ liệu của nơi khác** mà không báo lỗi gì.
4. Vì sao trước đây có thể lọt? Hàm kiểm tra có từ Ngày 2 nhưng pipeline **không gọi** nó; chỉ chạy tay bằng `python validate.py`.
5. Vì sao giờ chặn được? Ngày 13 gắn `validate_provinces` vào `sync_locations` (cả `run_pipeline.py` và DAG).

## Cách sửa
Sửa lại `config/provinces.csv`, chạy lại pipeline.

## Phòng tránh
- Dữ liệu tham chiếu cũng phải qua kiểm tra như dữ liệu chính (data contract cho file cấu hình).
- Điểm yếu còn lại: lỗi xảy ra **trước** `run_stage` nên không có dòng nào trong `ops.pipeline_runs`; phải xem log task `sync_locations` trên Airflow. Hướng sửa: ghi log cho cả bước chuẩn bị.
- Kiểm tra trực quan: bản đồ trên dashboard (tỉnh lệch sẽ rơi ra biển hoặc ra khỏi khung).
