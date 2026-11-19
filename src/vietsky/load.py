import os
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

import psycopg
from dotenv import load_dotenv

from validate import load_provinces

load_dotenv()
RAW_DIR = Path("data/raw/weather")
PROVINCES_CSV = Path("config/provinces.csv")

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

def to_rows(data: dict, location_id: str) -> list:
    hourly = data['hourly']
    tz = timezone(timedelta(seconds=data['utc_offset_seconds']))

    rows = []
    for time, temp, hump, prec, wind in zip (
        hourly['time'],
        hourly['temperature_2m'],
        hourly['relative_humidity_2m'],
        hourly['precipitation'],
        hourly['wind_speed_10m'],
        strict = True
    ):
        ts = datetime.fromisoformat(time).replace(tzinfo=tz)
        rows.append((location_id, ts, temp, hump, prec, wind))

    return rows

def load_locations(conn, rows: list) -> None:
    sql = """
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
        cur.executemany(sql, params)


def load_weather(conn, rows: list) -> None:
    sql = """
        INSERT INTO stg_weather_hourly
            (location_id, ts_utc,temperature_2m,humidity,precipitation,wind_speed)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (location_id,ts_utc) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.executemany(sql, rows)

def main():
    day_dir = sorted(RAW_DIR.glob("date=*"))[-1]
    files = sorted(day_dir.glob("*.json"))
    print(f"Load {len(files)} files from {day_dir}")

    with get_conn() as conn:
        load_locations(conn, load_provinces(PROVINCES_CSV))

        for path in files:
            location_id = path.stem
            with open(path, mode="r", encoding='utf-8') as f:
                data = json.load(f)
            rows = to_rows(data, location_id)
            load_weather(conn, rows)
            print(f"Loaded {len(rows)} rows from {path}")

        total = conn.execute("SELECT COUNT(*) FROM stg_weather_hourly").fetchone()[0]
        print(f"Total rows in stg_weather_hourly: {total}")


if __name__ == "__main__":
    main()

