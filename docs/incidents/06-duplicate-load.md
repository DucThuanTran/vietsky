# Sự cố 06 · Chạy pipeline 2 lần, tắt upsert (dòng trùng)

**Hình thức:** phân tích thiết kế, không cần gây lỗi: hệ thống **chặn được ngay từ cấu trúc bảng**.

## Kịch bản
Ai đó đổi `ON CONFLICT ... DO UPDATE` thành `INSERT` thường rồi chạy pipeline 2 lần cho cùng ngày.

## Điều gì xảy ra
- Staging có `PRIMARY KEY (location_id, ts_utc)` → lần chạy thứ 2 lỗi `duplicate key value violates unique constraint`, chặng `load` FAILED, transaction rollback, không dòng nào bị trùng.
- Nếu PK cũng bị gỡ: `unique_key` (`COUNT(*) - COUNT(DISTINCT (location_id, ts_utc))`) trả 6.528 → `quality_check` FAILED → `build_mart` không chạy → dashboard không bị `SUM` gấp đôi.
- Mart: fact có PK `(location_key, ts_utc)` và reconcile staging = mart là lớp thứ ba.

## Bài học
Phòng thủ nhiều lớp (defense in depth): ràng buộc DB → quality gate → reconcile. Mỗi lớp bắt được lỗi mà lớp trước để lọt.
