TRUNCATE MART.FACT_WEATHER_HOURLY;

INSERT INTO MART.FACT_WEATHER_HOURLY
(LOCATION_KEY, DATE_KEY, HOUR_VN, TS_UTC, temperature, humidity, precipitation, wind_speed)
SELECT L.LOCATION_KEY,
       TO_CHAR(S.TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh', 'YYYYMMDD')::INT,
       EXTRACT(HOUR FROM S.TS_UTC AT TIME ZONE 'Asia/Ho_Chi_Minh'),
       S.TS_UTC,
       S.temperature,
       S.humidity,
       S.precipitation,
       S.wind_speed
FROM STG_weather_HOURLY S
         JOIN MART.DIM_LOCATION L ON S.LOCATION_ID = L.LOCATION_ID;
