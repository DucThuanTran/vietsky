-- VietSky · Ngày 3 · Khám phá dữ liệu staging
-- Giờ lưu ở UTC; quy về giờ VN bằng AT TIME ZONE 'Asia/Ho_Chi_Minh'.

-- =========================================================
-- Cơ bản: SELECT / WHERE / ORDER BY
-- =========================================================

-- Q1: Các tỉnh miền Trung, từ Bắc xuống Nam
SELECT location_id, name, lat
FROM dim_location
WHERE region = 'central'
ORDER BY lat DESC;

-- Q2: 10 giờ nóng nhất toàn quốc
SELECT location_id,
       ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh' AS gio_vn,
       temperature
FROM stg_weather_hourly
ORDER BY temperature DESC NULLS LAST
LIMIT 10;

-- Q3: Các giờ mưa trên 5 mm
SELECT location_id,
       ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh' AS gio_vn,
       precipitation
FROM stg_weather_hourly
WHERE precipitation > 5
ORDER BY precipitation DESC;

-- Q4: Nhiệt độ thấp nhất và nơi đo được
SELECT location_id,
       ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh' AS gio_vn,
       temperature
FROM stg_weather_hourly
WHERE temperature = (SELECT MIN(temperature) FROM stg_weather_hourly);

-- =========================================================
-- JOIN
-- =========================================================

-- Q5: Thời tiết kèm tên tỉnh
SELECT w.location_id,
       l.name,
       w.ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh' AS gio_vn,
       w.temperature,
       w.humidity,
       w.precipitation,
       w.wind_speed
FROM stg_weather_hourly AS w
JOIN dim_location AS l ON w.location_id = l.location_id
ORDER BY w.location_id, w.ts_utc
LIMIT 20;

-- Q6: 🏆 Top 5 tỉnh nóng nhất trong ngày mới nhất (giờ VN)
SELECT l.name,
       MAX(w.temperature) AS nhiet_cao_nhat
FROM stg_weather_hourly AS w
JOIN dim_location AS l ON w.location_id = l.location_id
WHERE (w.ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh')::date = (
    SELECT MAX((ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh')::date)
    FROM stg_weather_hourly
)
GROUP BY l.name
ORDER BY nhiet_cao_nhat DESC NULLS LAST
LIMIT 5;

-- =========================================================
-- GROUP BY / HAVING
-- =========================================================

-- Q7: Nhiệt trung bình theo vùng
SELECT l.region,
       ROUND(AVG(w.temperature)::numeric, 1) AS nhiet_tb
FROM stg_weather_hourly AS w
JOIN dim_location AS l ON w.location_id = l.location_id
GROUP BY l.region
ORDER BY nhiet_tb DESC;

-- Q8: Tổng mưa theo tỉnh
SELECT l.name,
       ROUND(SUM(w.precipitation)::numeric, 1) AS tong_mua
FROM stg_weather_hourly AS w
JOIN dim_location AS l ON w.location_id = l.location_id
GROUP BY l.name
ORDER BY tong_mua DESC NULLS LAST;

-- Q9: Tỉnh có tổng mưa trên 20 mm
SELECT l.name,
       ROUND(SUM(w.precipitation)::numeric, 1) AS tong_mua
FROM stg_weather_hourly AS w
JOIN dim_location AS l ON w.location_id = l.location_id
GROUP BY l.name
HAVING SUM(w.precipitation) > 20
ORDER BY tong_mua DESC;

-- Q10: Nhiệt trung bình theo ngày (giờ VN) của TP.HCM
SELECT (ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh')::date AS ngay,
       ROUND(AVG(temperature)::numeric, 1) AS nhiet_tb
FROM stg_weather_hourly
WHERE location_id = '79'
GROUP BY ngay
ORDER BY ngay;

-- Q11: Độ ẩm trung bình theo vùng
SELECT l.region,
       ROUND(AVG(w.humidity)::numeric, 1) AS do_am_tb
FROM stg_weather_hourly AS w
JOIN dim_location AS l ON w.location_id = l.location_id
GROUP BY l.region
ORDER BY do_am_tb DESC;

-- =========================================================
-- Kiểm tra chất lượng
-- =========================================================

-- Q12: Tỉnh thiếu dòng (LEFT JOIN để bắt cả tỉnh có 0 dòng)
SELECT l.location_id,
       l.name,
       COUNT(w.ts_utc) AS so_dong
FROM dim_location AS l
LEFT JOIN stg_weather_hourly AS w ON w.location_id = l.location_id
GROUP BY l.location_id, l.name
HAVING COUNT(w.ts_utc) <> 192;

-- Q13: Số giá trị NULL ở từng cột đo
SELECT COUNT(*) FILTER (WHERE temperature IS NULL) AS null_nhiet,
       COUNT(*) FILTER (WHERE humidity IS NULL)       AS null_do_am,
       COUNT(*) FILTER (WHERE precipitation IS NULL)  AS null_mua,
       COUNT(*) FILTER (WHERE wind_speed IS NULL)     AS null_gio
FROM stg_weather_hourly;

-- Q14: Khoảng thời gian dữ liệu (giờ VN)
SELECT MIN(ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh') AS bat_dau,
       MAX(ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh') AS ket_thuc
FROM stg_weather_hourly;

-- Q15: 5 tỉnh có biên độ nhiệt lớn nhất
SELECT l.name,
       ROUND((MAX(w.temperature) - MIN(w.temperature))::numeric, 1) AS bien_do
FROM stg_weather_hourly AS w
JOIN dim_location AS l ON w.location_id = l.location_id
GROUP BY l.name
ORDER BY bien_do DESC NULLS LAST
LIMIT 5;
