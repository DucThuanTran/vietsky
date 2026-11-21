import argparse
import datetime
import json
import sys
import time

from vietsky.config    import SOURCES, RAW_DIR, PROVINCES_PATH, DAYS_BACK
from vietsky.validate  import load_provinces
from vietsky.extract   import fetch_hourly, save_raw
from vietsky.transform import to_rows
from vietsky.load      import get_conn, load_rows, load_locations
from vietsky.run_log   import new_run_id, start_stage, finish_stage

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=datetime.date.fromisoformat,
                        default=datetime.date.today())
    return parser.parse_args()

def run_extract(source, provinces, run_date) -> tuple[int, int]:
    start = (run_date - datetime.timedelta(days=DAYS_BACK)).isoformat()
    end = run_date.isoformat()
    rows_out = 0
    for p in provinces:
        data = fetch_hourly(float(p["lat"]), float(p["lon"]), source.api_variables,
                            start, end, source.url)
        save_raw(data, p["province_code"], run_date.isoformat(), source=source.name)
        rows_out += len(data["hourly"]["time"])
        time.sleep(1)
    return len(provinces), rows_out

def run_load(conn, source, run_date) -> tuple[int, int]:
    day_dir = RAW_DIR / source.name / f"date={run_date}"
    db_cols = ["location_id", "ts_utc"] + list(source.columns.values())
    rows_in = rows_out = 0
    for path in sorted(day_dir.glob("*.json")):
        with open(path, mode="r", encoding='utf-8') as f:
            data = json.load(f)
        rows = to_rows(data, path.stem, list(source.columns.keys()))
        rows_in += len(rows)
        rows_out += load_rows(conn, source.table, db_cols, rows)
    conn.commit()
    return rows_in, rows_out

def run_stage(conn, run_id, run_date, stage, source, func, *args) -> bool:
    start_stage(conn, run_id, run_date, stage, source.name)
    try:
        rows_in, rows_out = func(*args)
        finish_stage(conn, run_id, stage, source.name, "SUCCESS", rows_in, rows_out)
        return True
    except Exception as e:
        conn.rollback()
        finish_stage(conn, run_id, stage, source.name, "FAILED", error_message=str(e))
        return False


def main():
    args = parse_args() ; run_id = new_run_id()
    provinces = load_provinces(PROVINCES_PATH)
    print(f"run_id={run_id} run_date={args.date}")
    ok = True
    with get_conn() as conn:
        load_locations(conn, provinces) ; conn.commit()
        for source in SOURCES:
            if not run_stage(conn, run_id, args.date, "extract", source,
                             run_extract, source, provinces, args.date):
                ok = False
                continue
            if not run_stage(conn, run_id, args.date, "load", source,
                             run_load, conn, source, args.date):
                ok = False
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
