DROP TABLE IF EXISTS stg_weather_hourly;
DROP TABLE IF EXISTS dim_location;

CREATE TABLE dim_location (
    location_id TEXT PRIMARY KEY
        CHECK (location_id ~ '^[0-9]{2}$'),
    name TEXT NOT NULL,
    region TEXT NOT NULL
        CHECK (region IN ('north', 'central', 'south')),
    lat NUMERIC(8,5) NOT NULL CHECK (lat BETWEEN -90  AND 90),
    lon NUMERIC(8,5) NOT NULL CHECK (lon BETWEEN -180 AND 180)
);

CREATE TABLE stg_weather_hourly (
    location_id    TEXT NOT NULL REFERENCES dim_location(location_id),
    ts_utc         TIMESTAMPTZ NOT NULL,
    temperature_2m DOUBLE PRECISION,
    humidity       DOUBLE PRECISION,
    precipitation  DOUBLE PRECISION,
    wind_speed     DOUBLE PRECISION,
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (location_id, ts_utc)
);