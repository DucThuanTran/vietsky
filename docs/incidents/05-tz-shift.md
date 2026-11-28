# Sự cố 05 · Giờ địa phương bị gắn nhãn UTC (lệch 7 tiếng)

**Hình thức:** diễn tập trên giấy (tabletop) + unit test `tests/test_chaos.py::test_tz_shift_moves_time_7_hours_later`.
Không chạy trên database thật, vì lỗi này **ghi đè dữ liệu đúng** bằng dữ liệu lệch giờ và không có check nào dừng pipeline lại (xem phân tích bên dưới).
**Mức độ:** rất cao (dữ liệu sai âm thầm) · **MTTD dự kiến:** chỉ khi có người nhìn heatmap

## Kịch bản
`VIETSKY_CHAOS=tz_shift`: `transform` gắn `tzinfo=UTC` cho chuỗi giờ VN `2026-11-28T08:00`, đúng ra phải là `+07:00`. Mỗi dòng bị dời **muộn hơn 7 tiếng**.

## Điều gì xảy ra với dữ liệu
- Khung đúng: 21/11 00:00 → 28/11 23:00 giờ VN. Khung bị lệch: 21/11 07:00 → 29/11 06:00.
- Upsert theo `(location_id, ts_utc)`: các giờ trùng khoá bị **ghi đè bằng giá trị của 7 tiếng trước**; thêm 7 giờ "tương lai" ngày 29/11 cho mỗi tỉnh.

## Check nào bắt được?
| Check | Kết quả | Vì sao |
|---|---|---|
| `not_null_key`, `unique_key`, `all_provinces` | PASS | Khoá vẫn đủ, không trùng, đủ 34 tỉnh |
| `freshness_24h` | PASS | `loaded_at` vẫn mới |
| `pm25_range`, `*_not_null` | PASS | Giá trị vẫn hợp lệ, chỉ sai giờ |
| `reconcile_daily` | PASS | Trong khung 8 ngày, mỗi ngày vẫn 816 dòng (giờ cũ bị ghi đè, không mất) |

→ **Không check nào bắt được.** Đây là lỗi khó phát hiện nhất trong 6 kịch bản.

## Phát hiện bằng gì
- Heatmap giờ × tháng trên dashboard: đỉnh PM2.5 buổi tối (19–23h) dời sang 2–6h sáng; nhiệt độ cao nhất rơi vào 19–21h thay vì 13–15h.
- Query: giờ nóng nhất trong ngày trung bình của TP.HCM ≠ 13–15h.

## Nguyên nhân gốc (5 Whys)
1. Vì sao heatmap lệch? `ts_utc` muộn hơn thật 7 giờ.
2. Vì sao? Transform gắn sai múi giờ.
3. Vì sao không bị chặn? Check hiện tại kiểm tra *có đủ không*, *có hợp lệ không*, không kiểm tra *có hợp lý theo vật lý không*.
4. Vì sao dữ liệu đúng bị mất? Upsert ghi đè; nhưng raw vẫn còn nguyên nên dựng lại được.
5. Vì sao unit test cũ không bắt? `test_transform.py` có test múi giờ; lỗi chỉ xuất hiện khi ai đó sửa code transform, nên test là lớp bảo vệ chính.

## Cách sửa
Sửa transform, rồi load lại từ raw cho các ngày bị ảnh hưởng (`backfill.py` hoặc chạy lại từng ngày), xoá các dòng tương lai thừa:
`DELETE FROM stg_<source>_hourly WHERE ts_utc >= '<cuối khung đúng>' AND loaded_at >= '<giờ chạy lỗi>'`.

## Phòng tránh
- Unit test cho transform (đã có) phải chạy trong CI trước khi deploy.
- Thêm check "hợp lý": giờ có nhiệt độ cao nhất trung bình trong ngày phải nằm trong 11–16h giờ VN (anomaly check theo lịch sử).
- Check "không có dòng ngoài khung extract" (`ts_utc >= end` được ghi ở run này) dạng WARNING.
