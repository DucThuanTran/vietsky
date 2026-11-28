-- (A) Province dim: SCD1 upsert, location_key stays stable across runs
INSERT INTO MART.DIM_LOCATION (LOCATION_ID, NAME, REGION, LAT, LON)
SELECT LOCATION_ID, NAME, REGION, LAT, LON
FROM PUBLIC.DIM_LOCATION
ON CONFLICT (LOCATION_ID) DO UPDATE SET NAME   = EXCLUDED.NAME,
                                        REGION = EXCLUDED.REGION,
                                        LAT    = EXCLUDED.LAT,
                                        LON    = EXCLUDED.LON;

-- (B) Date dim: 1 row per day, covering the date range of BOTH staging tables (Vietnam time)
WITH all_ts AS (
    SELECT ts_utc FROM stg_weather_hourly
    UNION ALL
    SELECT ts_utc FROM stg_air_quality_hourly
)
INSERT INTO MART.DIM_DATE (DATE_KEY, FULL_DATE, YEAR, MONTH, DAY_OF_WEEK, IS_WEEKEND, SEASON)
SELECT TO_CHAR(D, 'YYYYMMDD')::INT,
       D::DATE,
       EXTRACT(YEAR FROM D),
       EXTRACT(MONTH FROM D),
       EXTRACT(ISODOW FROM D),
       EXTRACT(ISODOW FROM D) IN (6, 7),
       CASE WHEN EXTRACT(MONTH FROM D) IN (11, 12, 1, 2, 3, 4) THEN 'dry' ELSE 'wet' END
FROM GENERATE_SERIES(
             (SELECT MIN(TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE FROM all_ts),
             (SELECT MAX(TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE FROM all_ts),
             INTERVAL '1 day') AS D
ON CONFLICT (DATE_KEY) DO NOTHING;
