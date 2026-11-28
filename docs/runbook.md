# Runbook · Pipeline VietSky lỗi thì kiểm tra theo thứ tự nào

Nguyên tắc: đi theo dòng chảy dữ liệu, từ nguồn đến đích. Dừng ở tầng đầu tiên có bất thường; đó là nơi khoanh vùng.

## 0. Pipeline có chạy không?
```sql
SELECT run_id, MIN(started_at) AS started, source, stage, status, error_message
FROM ops.pipeline_runs
WHERE started_at > NOW() - INTERVAL '2 days'
GROUP BY run_id, source, stage, status, error_message
ORDER BY started DESC;
```
- Không có dòng nào trong 24 giờ: scheduler (Airflow) chết hoặc DAG bị pause → `docker compose --profile airflow ps`, giao diện Airflow `localhost:8080`.
- Có dòng `RUNNING` quá 30 phút: task treo hoặc tiến trình bị kill giữa chừng.
- Lỗi xảy ra **trước** mọi chặng (ví dụ `provinces.csv không hợp lệ`) thì không có dòng trong `pipeline_runs`; xem log task `sync_locations` trên Airflow hoặc stderr.

## 1. Dữ liệu có đến không? (extract)
- `stage = 'extract'` FAILED, lỗi `failed after 4 attempts: HTTP 5xx` → API nguồn lỗi; đã retry 4 lần với backoff. Kiểm tra trang trạng thái Open-Meteo, chạy lại sau.
- Lỗi `HTTP 400 ... out of allowed range` → khoảng ngày vượt cửa sổ của `/forecast` (xem Data profiling trong README).
- Raw nằm ở `data/raw/<source>/date=<run_date>/`; đếm file phải là 34.

## 2. Đến đủ không? Đúng cấu trúc không? (raw)
```sql
SELECT source, check_name, status, failed_rows
FROM ops.dq_results
WHERE run_id = '<run_id>' ORDER BY status, check_name;
```
- `raw_schema` FAIL → nguồn đổi tên/xoá cột (schema drift). Mở 1 file JSON, so `hourly` với `source.columns` trong `config.py`.
- Lỗi `KeyError: 'pm2_5'` ở chặng load cũng là dấu hiệu schema drift.

## 3. Xử lý đúng không? (load + quality_check trên staging)
- `all_provinces` FAIL → thiếu tỉnh; tìm tỉnh thiếu bằng Q12 trong `sql/explore.sql`.
- `pm25_not_null` / `temperature_not_null` FAIL → nguồn trả toàn NULL cho 1 tỉnh; kiểm tra raw của tỉnh đó.
- `unique_key` FAIL → upsert/PK bị gỡ; kiểm tra `\d stg_<source>_hourly`.
- `freshness_24h` FAIL → load không ghi được gì; so `rows_out` của load với extract.
- `quality_check` FAILED thì `build_mart` **không chạy**: mart vẫn giữ bản cũ, đúng (không công bố dữ liệu lỗi).

## 4. Ghi vào đích đủ không? (build_mart + reconcile)
- `build_mart` FAILED với `Reconcile failed: staging=X mart=Y` → JOIN với dim làm rơi dòng; tìm `location_id` không có trong `mart.dim_location`.
- `reconcile_daily` FAIL, log in `day: raw=816 staging=816 mart=0` → mart thiếu ngày đó (build_mart hỏng, mart giữ bản cũ).
- `raw ≠ staging` → lỗi ở transform/load.

## 5. Đúng giờ không?
- `freshness_24h` và trang "Phòng điều hành" của dashboard (`streamlit run dashboard/app.py`).
- Lệch múi giờ (lỗi tz_shift) **không** bị check tự động nào bắt: heatmap giờ × tháng bị dịch 7 cột, đỉnh PM2.5 rơi vào 2–6h sáng thay vì 19–23h.

## Sửa xong thì làm gì
1. Chạy lại cho đúng ngày: `PYTHONPATH=src .venv/bin/python pipelines/run_pipeline.py --date <ngày>` hoặc Clear task trên Airflow. Pipeline idempotent nên chạy lại an toàn.
2. Kiểm tra lại `ops.dq_results` của run mới: tất cả PASS.
3. Viết postmortem vào `docs/incidents/` nếu sự cố ảnh hưởng người dùng dashboard.
