CREATE SCHEMA IF NOT EXISTS mart;

-- Grain: 1 dòng = 1 tỉnh. SCD1: đổi tên thì ghi đè
CREATE TABLE IF NOT EXISTS mart.dim_location (
    location_key  serial       PRIMARY KEY,
    location_id   TEXT        NOT NULL UNIQUE,
    name          TEXT        NOT NULL,
    region        TEXT        NOT NULL,
    lat           NUMERIC(8,5),
    lon           NUMERIC(8,5)
);

-- Grain: 1 dòng = 1 ngày theo giờ VN
CREATE TABLE IF NOT EXISTS mart.dim_date (
    date_key     INTEGER  PRIMARY KEY,
    full_date    DATE     NOT NULL UNIQUE,
    year         SMALLINT NOT NULL,
    month          SMALLINT NOT NULL,
    day_of_week  SMALLINT NOT NULL,
    is_weekend   BOOLEAN  NOT NULL,
    season       TEXT     NOT NULL CHECK (season IN ('dry', 'wet'))
);

-- Grain: 1 dòng = 1 tỉnh × 1 giờ (location_key, ts_utc)
CREATE TABLE IF NOT EXISTS mart.fact_air_quality_hourly (
    location_key     INTEGER NOT NULL REFERENCES mart.dim_location(location_key),
    date_key         INTEGER NOT NULL REFERENCES mart.dim_date(date_key),
    hour_vn          SMALLINT NOT NULL CHECK (hour_vn BETWEEN 0 AND 23),
    ts_utc           TIMESTAMPTZ NOT NULL,
    pm2_5            DOUBLE PRECISION,
    pm10             DOUBLE PRECISION,
    us_aqi           INTEGER,
    nitrogen_dioxide DOUBLE PRECISION,
    ozone            DOUBLE PRECISION,
    PRIMARY KEY (location_key, ts_utc)
);

-- Grain: 1 dòng = 1 tỉnh × 1 giờ (location_key, ts_utc)
CREATE TABLE IF NOT EXISTS mart.fact_weather_hourly (
    location_key     INTEGER NOT NULL REFERENCES mart.dim_location(location_key),
    date_key         INTEGER NOT NULL REFERENCES mart.dim_date(date_key),
    hour_vn          SMALLINT NOT NULL CHECK (hour_vn BETWEEN 0 AND 23),
    ts_utc           TIMESTAMPTZ NOT NULL,
    temperature      DOUBLE PRECISION,
    humidity         DOUBLE PRECISION,
    precipitation    DOUBLE PRECISION,
    wind_speed       DOUBLE PRECISION,
    PRIMARY KEY (location_key, ts_utc)
);
