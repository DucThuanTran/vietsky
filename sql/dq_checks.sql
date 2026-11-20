-- VietSky · Ngày 4 · Kiểm tra chất lượng stg_air_quality_hourly
-- Quy ước: mỗi check trả 0 dòng = đạt; có dòng = lỗi.

-- DQ1 · Uniqueness: một tỉnh, một giờ bị ghi nhiều lần
WITH ranked AS (
    SELECT location_id, ts_utc,
           ROW_NUMBER() OVER (PARTITION BY location_id, ts_utc ORDER BY loaded_at DESC) AS rn
    FROM stg_air_quality_hourly
)
SELECT *
FROM ranked
WHERE rn > 1;

-- DQ2 · Completeness (cột): số ô NULL theo từng cột đo
SELECT COUNT(*) FILTER (WHERE pm2_5 IS NULL)            AS null_pm25,
       COUNT(*) FILTER (WHERE pm10 IS NULL)             AS null_pm10,
       COUNT(*) FILTER (WHERE us_aqi IS NULL)           AS null_aqi,
       COUNT(*) FILTER (WHERE nitrogen_dioxide IS NULL) AS null_no2,
       COUNT(*) FILTER (WHERE ozone IS NULL)            AS null_o3
FROM stg_air_quality_hourly
HAVING COUNT(*) FILTER (WHERE pm2_5 IS NULL
                           OR pm10 IS NULL
                           OR us_aqi IS NULL
                           OR nitrogen_dioxide IS NULL
                           OR ozone IS NULL) > 0;

-- DQ3 · Validity: PM2.5 ngoài khoảng 0–1000 µg/m³
SELECT location_id, ts_utc, pm2_5
FROM stg_air_quality_hourly
WHERE pm2_5 < 0
   OR pm2_5 > 1000;

-- DQ4 · Completeness (thời gian): chuỗi giờ của mỗi tỉnh bị đứt
WITH gaps AS (
    SELECT location_id, ts_utc,
           LAG(ts_utc) OVER (PARTITION BY location_id ORDER BY ts_utc) AS prev_ts
    FROM stg_air_quality_hourly
)
SELECT location_id, prev_ts, ts_utc, ts_utc - prev_ts AS khoang_cach
FROM gaps
WHERE ts_utc - prev_ts > INTERVAL '1 hour';

-- DQ5 · Completeness (thực thể): tỉnh thiếu dòng hoặc vắng mặt hoàn toàn
SELECT l.location_id, l.name, COUNT(a.ts_utc) AS so_dong
FROM dim_location AS l
LEFT JOIN stg_air_quality_hourly AS a ON a.location_id = l.location_id
GROUP BY l.location_id, l.name
HAVING COUNT(a.ts_utc) <> 192;
