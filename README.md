# VietSky

Pipeline dữ liệu thời tiết và chất lượng không khí cho 34 tỉnh thành Việt Nam.

## Data profiling

Ngày kiểm tra: 20/11/2026 · Tọa độ thử: TP.HCM (10.82, 106.63)

### Air Quality API (`pm2_5`)

| Mốc | start_date = end_date | Status | Dữ liệu (số thật / toàn null) | Ghi chú (`reason` nếu lỗi) |
|---|---|--------|-------------------------------|---|
| 1 tháng trước | 2026-10-20 | 200    | số thật                       | |
| 6 tháng trước | 2026-05-20 | 200    | số thật                       | |
| 1 năm trước | 2025-11-20 | 200    | số thật                       | |
| 3 năm trước | 2023-11-20 | 200    | số thật                       | |
| 5 năm trước | 2021-11-20 | 200    | toàn null                     | ⚠️ 200 nhưng không có dữ liệu (lỗi im lặng) |

### Weather API `/v1/forecast` (`temperature_2m`)

| Mốc | start_date = end_date | Status | Dữ liệu (số thật / toàn null) | Ghi chú (`reason` nếu lỗi) |
|---|---|--------|------------------------|---|
| 1 tháng trước | 2026-10-20 | 200    | số thật                | |
| 6 tháng trước | 2026-05-20 | 400    |                        | Parameter 'start_date' is out of allowed range from 2026-08-19 to 2026-12-05 |
| 1 năm trước | 2025-11-20 |    400       |                        | Parameter 'start_date' is out of allowed range from 2026-08-19 to 2026-12-05|
| 3 năm trước | 2023-11-20 |     400      |                        | Parameter 'start_date' is out of allowed range from 2026-08-19 to 2026-12-05|
| 5 năm trước | 2021-11-20 |      400     |                        | Parameter 'start_date' is out of allowed range from 2026-08-19 to 2026-12-05|

### Kết luận

- **Air Quality**: API nhận ngày từ 2013-01-01 (đúng định dạng thì vẫn trả 200), nhưng **số thật chỉ có từ 2022-08-04**; trước đó `pm2_5` toàn `null`.
- **Weather `/v1/forecast`**: chỉ nhận khoảng **~3 tháng trước → ~2 tuần tới** (lúc kiểm tra: 2026-08-19 → 2026-12-05); ngoài khoảng → 400 kèm `reason`. Cửa sổ này **trượt theo ngày**.
- **Ảnh hưởng tới pipeline**:
  - Dữ liệu thời tiết cũ hơn ~3 tháng sẽ **không lấy lại được** từ `/forecast` → phải chạy hằng ngày và **giữ raw vĩnh viễn**; raw là nguồn lịch sử duy nhất.
  - Kiểm tra số dòng là chưa đủ: 200 + đủ 24 dòng vẫn có thể toàn `null` → cần thêm check tỉ lệ `NULL`.
  - Muốn lịch sử thời tiết dài hơn phải dùng API khác (Historical Weather / archive) — nguồn mới, profiling lại.
