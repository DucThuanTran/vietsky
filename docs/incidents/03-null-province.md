# Sự cố 03 · Một tỉnh trả về toàn NULL

**Diễn tập ngày:** 28/11/2026 · `VIETSKY_CHAOS=null_province run_pipeline.py --date 2026-11-28 --source weather`
Lần 1: run `1c1beffa` (trước khi sửa) · Lần 2: run `0771d653` (sau khi thêm quy tắc)
**Mức độ:** cao (dashboard hiển thị Hà Nội trống, AVG toàn quốc lệch) · **MTTD:** lần 1 không phát hiện; lần 2 ~1 giây sau load

## Triệu chứng
API trả 200, đủ 192 giờ cho Hà Nội (`01`), nhưng mọi cột đo đều `null`.

## Phát hiện lúc nào, bằng gì
- **Lần 1: không check nào bắt được.** Cả 5 chặng SUCCESS, 6/6 check PASS. Kết quả: 192 dòng `temperature IS NULL` của Hà Nội nằm trong cả staging lẫn mart.
  - `all_provinces` PASS: `location_id = '01'` vẫn có mặt.
  - `reconcile_daily` PASS: số dòng khớp ở cả 3 tầng (dòng NULL vẫn là dòng).
  - Check NULL của Ngày 4 (`dq_checks.sql`) có, nhưng chỉ chạy tay.
- **Lần 2, sau khi thêm `temperature_not_null` / `pm25_not_null` (CRITICAL):** `quality_check` FAILED với `DQ failed: ['temperature_not_null']`, `failed_rows = 192`, `build_mart` **không chạy**.

## Khoanh vùng
Nguồn (extract) trả dữ liệu rỗng về giá trị; đường ống vận chuyển đúng. Đây là lỗi **nội dung**, không phải lỗi **số lượng**.

## Nguyên nhân gốc (5 Whys)
1. Vì sao Hà Nội trống trên dashboard? Mart có 192 giờ NULL.
2. Vì sao NULL vào được mart? Không có quy tắc nào về tỷ lệ NULL của cột đo.
3. Vì sao thiếu quy tắc? Bộ quy tắc Ngày 10 tập trung vào khoá, số lượng, độ mới; coi "đủ dòng" là "đủ dữ liệu".
4. Vì sao nguồn trả NULL? (Giả lập; ngoài đời: trạm/mô hình của nguồn ngừng cho 1 điểm, giống 238 giờ NULL đầu tiên ngày 04/08/2022.)
5. Vì sao lần 2 mart vẫn còn NULL từ lần 1? Cổng chất lượng giữ mart **ở bản trước**, mà bản trước đã bẩn từ lần 1. Cổng chỉ ngăn lỗi mới, không tự dọn lỗi cũ.

## Cách sửa
Khi nguồn trả lại số liệu, chạy lại pipeline: upsert ghi đè 192 dòng NULL, mart dựng lại. Đã làm: run `f04107cd`, NULL của Hà Nội trong staging và mart về 0.

## Phòng tránh
- Đã thêm quy tắc `*_not_null` cho cột đo chính của mỗi nguồn (ngưỡng 0 trong khung 8 ngày).
- "Đủ dòng" ≠ "đủ dữ liệu": completeness phải kiểm cả cấp **dòng** lẫn cấp **giá trị**.
- Nếu nguồn có NULL hợp lệ (ví dụ giờ đầu tiên của chuỗi), dùng ngưỡng tỷ lệ (ví dụ ≤ 1%) thay vì 0.
