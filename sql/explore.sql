-- VietSky · Exploratory queries on staging and mart
-- Timestamps are stored in UTC. Convert to Vietnam time with AT TIME ZONE 'Asia/Ho_Chi_Minh'.

-- =========================================================
-- Basics: SELECT / WHERE / ORDER BY
-- =========================================================

-- Q1: Central provinces, north to south
SELECT LOCATION_ID, NAME, LAT
FROM DIM_LOCATION
WHERE REGION = 'central'
ORDER BY LAT DESC;

-- Q2: 10 hottest hours nationwide
SELECT LOCATION_ID,
       TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS TS_VN,
       TEMPERATURE
FROM STG_WEATHER_HOURLY
ORDER BY TEMPERATURE DESC NULLS LAST
LIMIT 10;

-- Q3: Hours with more than 5 mm of rain
SELECT LOCATION_ID,
       TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS TS_VN,
       PRECIPITATION
FROM STG_WEATHER_HOURLY
WHERE PRECIPITATION > 5
ORDER BY PRECIPITATION DESC;

-- Q4: Lowest temperature and where it was recorded
SELECT LOCATION_ID,
       TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS TS_VN,
       TEMPERATURE
FROM STG_WEATHER_HOURLY
WHERE TEMPERATURE = (SELECT MIN(TEMPERATURE) FROM STG_WEATHER_HOURLY);

-- =========================================================
-- JOIN
-- =========================================================

-- Q5: Weather with province names
SELECT W.LOCATION_ID,
       L.NAME,
       W.TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh' AS TS_VN,
       W.TEMPERATURE,
       W.HUMIDITY,
       W.PRECIPITATION,
       W.WIND_SPEED
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
ORDER BY W.LOCATION_ID, W.TS_UTC
LIMIT 20;

-- Q6: Top 5 hottest provinces on the latest day (Vietnam time)
SELECT L.NAME,
       MAX(W.TEMPERATURE) AS MAX_TEMP
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
WHERE (W.TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE = (SELECT MAX((TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE)
                                                          FROM STG_WEATHER_HOURLY)
GROUP BY L.NAME
ORDER BY MAX_TEMP DESC NULLS LAST
LIMIT 5;

-- =========================================================
-- GROUP BY / HAVING
-- =========================================================

-- Q7: Average temperature by region
SELECT L.REGION,
       ROUND(AVG(W.TEMPERATURE)::NUMERIC, 1) AS AVG_TEMP
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.REGION
ORDER BY AVG_TEMP DESC;

-- Q8: Total rainfall by province
SELECT L.NAME,
       ROUND(SUM(W.PRECIPITATION)::NUMERIC, 1) AS TOTAL_RAIN
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.NAME
ORDER BY TOTAL_RAIN DESC NULLS LAST;

-- Q9: Provinces with total rainfall above 20 mm
SELECT L.NAME,
       ROUND(SUM(W.PRECIPITATION)::NUMERIC, 1) AS TOTAL_RAIN
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.NAME
HAVING SUM(W.PRECIPITATION) > 20
ORDER BY TOTAL_RAIN DESC;

-- Q10: Daily average temperature in Ho Chi Minh City (Vietnam time)
SELECT (TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE AS DAY_VN,
       ROUND(AVG(TEMPERATURE)::NUMERIC, 1)            AS AVG_TEMP
FROM STG_WEATHER_HOURLY
WHERE LOCATION_ID = '79'
GROUP BY DAY_VN
ORDER BY DAY_VN;

-- Q11: Average humidity by region
SELECT L.REGION,
       ROUND(AVG(W.HUMIDITY)::NUMERIC, 1) AS AVG_HUMIDITY
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.REGION
ORDER BY AVG_HUMIDITY DESC;

-- =========================================================
-- Data quality
-- =========================================================

-- Q12: Provinces with missing hours (LEFT JOIN also catches provinces with 0 rows)
SELECT L.LOCATION_ID,
       L.NAME,
       COUNT(W.TS_UTC) AS ROW_COUNT
FROM DIM_LOCATION AS L
         LEFT JOIN STG_WEATHER_HOURLY AS W ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.LOCATION_ID, L.NAME
HAVING COUNT(W.TS_UTC) <> (SELECT EXTRACT(EPOCH FROM MAX(TS_UTC) - MIN(TS_UTC)) / 3600 + 1
                           FROM STG_WEATHER_HOURLY);

-- Q13: NULL count per measure column
SELECT COUNT(*) FILTER (WHERE TEMPERATURE IS NULL)   AS NULL_TEMP,
       COUNT(*) FILTER (WHERE HUMIDITY IS NULL)      AS NULL_HUMIDITY,
       COUNT(*) FILTER (WHERE PRECIPITATION IS NULL) AS NULL_RAIN,
       COUNT(*) FILTER (WHERE WIND_SPEED IS NULL)    AS NULL_WIND
FROM STG_WEATHER_HOURLY;

-- Q14: Data time range (Vietnam time)
SELECT MIN(TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh') AS FIRST_TS_VN,
       MAX(TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh') AS LAST_TS_VN
FROM STG_WEATHER_HOURLY;

-- Q15: 5 provinces with the largest temperature range
SELECT L.NAME,
       ROUND((MAX(W.TEMPERATURE) - MIN(W.TEMPERATURE))::NUMERIC, 1) AS TEMP_RANGE
FROM STG_WEATHER_HOURLY AS W
         JOIN DIM_LOCATION AS L ON W.LOCATION_ID = L.LOCATION_ID
GROUP BY L.NAME
ORDER BY TEMP_RANGE DESC NULLS LAST
LIMIT 5;

-- =========================================================
-- Mart layer (star schema)
-- =========================================================

-- Q16: In which month and hour is Hanoi most polluted? (12 months × 24 hours heatmap)
SELECT D.MONTH,
       F.HOUR_VN,
       ROUND(AVG(F.PM2_5)::NUMERIC, 1) AS AVG_PM25
FROM MART.FACT_AIR_QUALITY_HOURLY AS F
         JOIN MART.DIM_LOCATION AS L ON F.LOCATION_KEY = L.LOCATION_KEY
         JOIN MART.DIM_DATE AS D ON F.DATE_KEY = D.DATE_KEY
WHERE L.NAME = 'Hà Nội'
GROUP BY D.MONTH, F.HOUR_VN
ORDER BY D.MONTH, F.HOUR_VN;
