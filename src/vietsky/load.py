import os
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from psycopg import sql

import psycopg
from dotenv import load_dotenv

from validate import load_provinces

load_dotenv()
RAW_DIR = Path("data/raw/")
PROVINCES_CSV = Path("config/provinces.csv")
SOURCES = {
    "weather":  {
        "table": "stg_weather_hourly",
        "columns": {
            "temperature_2m": "temperature",
            "relative_humidity_2m": "humidity",
            "precipitation": "precipitation",
            "wind_speed_10m": "wind_speed"
        },
    },
    "air_quality": {
        "table": "stg_air_quality_hourly",
        "columns": {
            "pm2_5":"pm2_5",
            "pm10":"pm10",
            "us_aqi":"us_aqi",
            "nitrogen_dioxide":"nitrogen_dioxide",
            "ozone":"ozone"
        },
    }
}

def get_conn():
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    dbname = os.environ["POSTGRES_DB"]
    return psycopg.connect(
        host='localhost',
        port='5433',
        dbname=dbname,
        user=user,
        password=password
    )

def to_rows(data: dict, location_id: str, json_cols:list) -> list:
    hourly = data['hourly']
    tz = timezone(timedelta(seconds=data['utc_offset_seconds']))
    times = hourly['time']

    for c in json_cols:
        if len(hourly[c]) != len(times):
            raise ValueError(f"{c}: {len(hourly[c])} values, expected {len(times)}")

    rows = []
    for i, t in enumerate(times):
        ts = datetime.fromisoformat(t).replace(tzinfo=tz)
        values = [hourly[c][i] for c in json_cols]
        rows.append((location_id, ts, *values))

    return rows

def load_rows(conn, table, db_cols: list, rows: list) -> None:
    query = sql.SQL(
        "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (location_id, ts_utc) DO NOTHING"
    ).format(
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, db_cols)),
        sql.SQL(", ").join([sql.Placeholder()] * len(db_cols)),
    )
    with conn.cursor() as cur:
        cur.executemany(query, rows)

def load_locations(conn, rows: list) -> None:
    query = """
          INSERT INTO dim_location (location_id, name, region, lat, lon)
          VALUES (%s, %s, %s, %s, %s)
          ON CONFLICT (location_id) DO UPDATE SET
              name = EXCLUDED.name,
              region = EXCLUDED.region,
              lat = EXCLUDED.lat,
              lon = EXCLUDED.lon
          """
    params = []
    for row in rows:
        params.append((
            row["province_code"],
            row["name"],
            row["region"],
            float(row["lat"]),
            float(row["lon"]),
        ))

    with conn.cursor() as cur:
        cur.executemany(query, params)

def main():
    with get_conn() as conn:
        load_locations(conn, load_provinces(PROVINCES_CSV))

        for source, cfg in SOURCES.items():
            day_dir = sorted((RAW_DIR / source).glob("date=*"))[-1]
            files = sorted(day_dir.glob("*.json"))
            json_cols = list(cfg["columns"].keys())
            db_cols = ["location_id", "ts_utc"] + list(cfg["columns"].values())

            loaded = 0
            for path in files:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                rows = to_rows(data, path.stem, json_cols)
                load_rows(conn, cfg["table"], db_cols, rows)
                loaded += len(rows)
            print(f"[{source}] read {loaded} rows from {len(files)} files in {day_dir}")

            count_query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(cfg["table"]))
            total = conn.execute(count_query).fetchone()[0]
            print(f"[{source}] total rows in {cfg['table']}: {total}")

if __name__ == "__main__":
    main()

