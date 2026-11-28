import datetime
import json
import time

from vietsky import chaos
from vietsky.config import RAW_DIR, DAYS_BACK, PROVINCES_PATH
from vietsky.extract import fetch_hourly, save_raw
from vietsky.transform import to_rows
from vietsky.load import load_rows, load_locations
from vietsky.quality import assert_raw_schema
from vietsky.validate import load_provinces, validate_provinces


def run_extract(source, provinces, run_date) -> tuple[int, int]:
    start = (run_date - datetime.timedelta(days=DAYS_BACK)).isoformat()
    end = run_date.isoformat()
    rows_out = 0
    for p in provinces:
        data = fetch_hourly(float(p["lat"]), float(p["lon"]), source.api_variables,
                            start, end, source.url)
        data = chaos.break_payload(data, p["province_code"])
        save_raw(data, p["province_code"], run_date.isoformat(), source=source.name)
        rows_out += len(data["hourly"]["time"])
        time.sleep(1)
    return len(provinces), rows_out


def run_load(conn, source, run_date) -> tuple[int, int]:
    assert_raw_schema(source, run_date)
    day_dir = RAW_DIR / source.name / f"date={run_date}"
    db_cols = ["location_id", "ts_utc"] + list(source.columns.values())
    rows_in = rows_out = 0
    for path in sorted(day_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        rows = chaos.shift_tz(to_rows(data, path.stem, list(source.columns.keys())))
        rows_in += len(rows)
        rows_out += load_rows(conn, source.table, db_cols, rows)
    conn.commit()
    return rows_in, rows_out


def read_provinces() -> list[dict]:
    return chaos.swap_latlon(load_provinces(PROVINCES_PATH))


def sync_locations(conn, provinces: list[dict]) -> None:
    errors = validate_provinces(provinces)
    if errors:
        raise ValueError("Invalid provinces.csv: " + "; ".join(errors))
    load_locations(conn, provinces)
    conn.commit()
