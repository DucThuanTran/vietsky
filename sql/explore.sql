-- VietSky · Ngày 3 · Khám phá dữ liệu staging
-- Giờ lưu ở UTC; quy về giờ VN bằng AT TIME ZONE 'Asia/Ho_Chi_Minh'.

-- =========================================================
-- Cơ bản: SELECT / WHERE / ORDER BY
-- =========================================================

-- Q1: Các tỉnh miền Trung, từ Bắc xuống Nam
SELECT LOCATION_ID, NAME, LAT
FROM DIM_LOCATION
WHERE REGION = 'central'
ORDER BY LAT DESC;

-- Q2: 10 giờ nóng nhất toàn quốc
SELECT LOCATION_ID,
       TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS GIO_VN,
       TEMPERATURE
FROM STG_WEATHER_HOURLY
ORDER BY TEMPERATURE DESC NULLS LAST
LIMIT 10;

-- Q3: Các giờ mưa trên 5 mm
SELECT LOCATION_ID,
       TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS GIO_VN,
       PRECIPITATION
FROM STG_WEATHER_HOURLY
WHERE PRECIPITATION > 5
ORDER BY PRECIPITATION DESC;

-- Q4: Nhiệt độ thấp nhất và nơi đo được
SELECT LOCATION_ID,
       TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS GIO_VN,
       TEMPERATURE
FROM STG_WEATHER_HOURLY
WHERE TEMPERATURE = (SELECT MIN(TEMPERATURE) FROM STG_WEATHER_HOURLY);

-- =========================================================
-- JOIN
-- =========================================================

-- Q5: Thời tiết kèm tên tỉnh
SELECT W.LOCATION_ID,
       L.NAME,
       W.TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS GIO_VN,
       W.TEMPERATURE,
       W.HUMIDITY,
       W.PRECIPITATION,
       W.WIND_SPEED
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
ORDER BY W.LOCATION_ID, W.TS_UTC
LIMIT 20;

-- Q6: 🏆 Top 5 tỉnh nóng nhất trong ngày mới nhất (giờ VN)
SELECT L.NAME,
       MAX(W.TEMPERATURE) AS NHIET_CAO_NHAT
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
WHERE (W.TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE = (SELECT MAX((TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE)
                                                          FROM STG_WEATHER_HOURLY)
GROUP BY L.NAME
ORDER BY NHIET_CAO_NHAT DESC NULLS LAST
LIMIT 5;

-- =========================================================
-- GROUP BY / HAVING
-- =========================================================

-- Q7: Nhiệt trung bình theo vùng
SELECT L.REGION,
       ROUND(AVG(W.TEMPERATURE)::NUMERIC, 1) AS NHIET_TB
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.REGION
ORDER BY NHIET_TB DESC;

-- Q8: Tổng mưa theo tỉnh
SELECT L.NAME,
       ROUND(SUM(W.PRECIPITATION)::NUMERIC, 1) AS TONG_MUA
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.NAME
ORDER BY TONG_MUA DESC NULLS LAST;

-- Q9: Tỉnh có tổng mưa trên 20 mm
SELECT L.NAME,
       ROUND(SUM(W.PRECIPITATION)::NUMERIC, 1) AS TONG_MUA
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.NAME
HAVING SUM(W.PRECIPITATION) > 20
ORDER BY TONG_MUA DESC;

-- Q10: Nhiệt trung bình theo ngày (giờ VN) của TP.HCM
SELECT (TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE AS NGAY,
       ROUND(AVG(TEMPERATURE)::NUMERIC, 1)            AS NHIET_TB
FROM STG_WEATHER_HOURLY
WHERE LOCATION_ID = '79'
GROUP BY NGAY
ORDER BY NGAY;

-- Q11: Độ ẩm trung bình theo vùng
SELECT L.REGION,
       ROUND(AVG(W.HUMIDITY)::NUMERIC, 1) AS DO_AM_TB
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.REGION
ORDER BY DO_AM_TB DESC;

-- =========================================================
-- Kiểm tra chất lượng
-- =========================================================

-- Q12: Tỉnh thiếu dòng (LEFT JOIN để bắt cả tỉnh có 0 dòng)
SELECT L.LOCATION_ID,
       L.NAME,
       COUNT(W.TS_UTC) AS SO_DONG
FROM DIM_LOCATION AS L
         LEFT JOIN STG_WEATHER_HOURLY AS W ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.LOCATION_ID, L.NAME
HAVING COUNT(W.TS_UTC) <> 192;

-- Q13: Số giá trị NULL ở từng cột đo
SELECT COUNT(*) FILTER (WHERE TEMPERATURE IS NULL)   AS NULL_NHIET,
       COUNT(*) FILTER (WHERE HUMIDITY IS NULL)      AS NULL_DO_AM,
       COUNT(*) FILTER (WHERE PRECIPITATION IS NULL) AS NULL_MUA,
       COUNT(*) FILTER (WHERE WIND_SPEED IS NULL)    AS NULL_GIO
FROM STG_WEATHER_HOURLY;

-- Q14: Khoảng thời gian dữ liệu (giờ VN)
SELECT MIN(TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh') AS BAT_DAU,
       MAX(TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh') AS KET_THUC
FROM STG_WEATHER_HOURLY;

-- Q15: 5 tỉnh có biên độ nhiệt lớn nhất
SELECT L.NAME,
       ROUND((MAX(W.TEMPERATURE) - MIN(W.TEMPERATURE))::NUMERIC, 1) AS BIEN_DO
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.NAME
ORDER BY BIEN_DO DESC NULLS LAST
LIMIT 5;

-- =========================================================
-- Ngày 8 · Query trên tầng mart (star schema)
-- =========================================================

-- Q16: 🏆 Hà Nội ô nhiễm nhất vào tháng nào, giờ nào? (heatmap 12 tháng × 24 giờ)
SELECT D.MONTH                         AS THANG,
       F.HOUR_VN                       AS GIO_VN,
       ROUND(AVG(F.PM2_5)::NUMERIC, 1) AS PM25_TB
FROM MART.FACT_AIR_QUALITY_HOURLY AS F
         JOIN MART.DIM_LOCATION AS L ON F.LOCATION_KEY = L.LOCATION_KEY
         JOIN MART.DIM_DATE AS D ON F.DATE_KEY = D.DATE_KEY
WHERE L.NAME = 'Hà Nội'
GROUP BY D.MONTH, F.HOUR_VN
ORDER BY THANG, GIO_VN;
