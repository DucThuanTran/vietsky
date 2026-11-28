-- VietSky · Ad-hoc data quality checks for stg_air_quality_hourly
-- The automated version runs in the pipeline: src/vietsky/quality.py
-- Convention: a check returning 0 rows passes. Any returned row is a failure.

-- DQ1 · Uniqueness: the same province-hour written more than once
WITH ranked AS (
    SELECT location_id, ts_utc,
           ROW_NUMBER() OVER (PARTITION BY location_id, ts_utc ORDER BY loaded_at DESC) AS rn
    FROM stg_air_quality_hourly
)
SELECT *
FROM ranked
WHERE rn > 1;

-- DQ2 · Completeness (columns): NULL count per measure column
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

-- DQ3 · Validity: PM2.5 outside 0–1000 µg/m³
SELECT location_id, ts_utc, pm2_5
FROM stg_air_quality_hourly
WHERE pm2_5 < 0
   OR pm2_5 > 1000;

-- DQ4 · Completeness (time): gaps in each province's hourly series
WITH gaps AS (
    SELECT location_id, ts_utc,
           LAG(ts_utc) OVER (PARTITION BY location_id ORDER BY ts_utc) AS prev_ts
    FROM stg_air_quality_hourly
)
SELECT location_id, prev_ts, ts_utc, ts_utc - prev_ts AS gap
FROM gaps
WHERE ts_utc - prev_ts > INTERVAL '1 hour';

-- DQ5 · Completeness (entities): provinces with missing rows or absent entirely
-- Expected rows per province = number of hours in the staging range (no hard-coded count)
WITH expected AS (
    SELECT EXTRACT(EPOCH FROM MAX(ts_utc) - MIN(ts_utc)) / 3600 + 1 AS hours
    FROM stg_air_quality_hourly
)
SELECT l.location_id, l.name, COUNT(a.ts_utc) AS row_count
FROM dim_location AS l
LEFT JOIN stg_air_quality_hourly AS a ON a.location_id = l.location_id
GROUP BY l.location_id, l.name
HAVING COUNT(a.ts_utc) <> (SELECT hours FROM expected);
