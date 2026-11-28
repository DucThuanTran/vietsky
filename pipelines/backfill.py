import argparse
import datetime
import sys
import time

from vietsky.config    import SOURCES
from vietsky.extract   import fetch_hourly, save_raw
from vietsky.transform import to_rows
from vietsky.load      import get_conn, load_rows
from vietsky.stages    import read_provinces, sync_locations
from vietsky.run_log   import new_run_id, run_stage


def split_by_year(start: datetime.date, end: datetime.date) -> list[tuple[datetime.date, datetime.date]]:
    chunks, cur = [], start
    while cur <= end:
        chunk_end = min(datetime.date(cur.year, 12, 31), end)
        chunks.append((cur, chunk_end))
        cur = chunk_end + datetime.timedelta(days=1)
    return chunks

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=datetime.date.fromisoformat, required=True)
    parser.add_argument("--end", type=datetime.date.fromisoformat, default=datetime.date.today())
    parser.add_argument("--source", choices=[s.name for s in SOURCES])
    return parser.parse_args()


def backfill_source(conn, source, provinces, start, end) -> tuple[int, int]:
    start = max(start, source.history_start)
    db_cols = ["location_id", "ts_utc"] + list(source.columns.values())
    rows_in = rows_out = 0
    for chunk_start, chunk_end in split_by_year(start, end):
        for p in provinces:
            code = p["province_code"]
            data = fetch_hourly(float(p["lat"]), float(p["lon"]), source.api_variables,
                                chunk_start.isoformat(), chunk_end.isoformat(), source.history_url)
            save_raw(data, code, f"{chunk_start}_{chunk_end}", source=f"{source.name}/backfill")
            rows = to_rows(data, code, list(source.columns.keys()))
            rows_in += len(rows)
            rows_out += load_rows(conn, source.table, db_cols, rows)
            conn.commit()
            print(f"{source.name} {chunk_start.year} {code}: {len(rows)} rows", flush=True)
            time.sleep(1)
    return rows_in, rows_out


def main():
    args = parse_args()
    run_id = new_run_id()
    provinces = read_provinces()
    sources = [s for s in SOURCES if args.source in (None, s.name)]
    print(f"run_id={run_id} backfill {args.start} -> {args.end}", flush=True)
    ok = True
    with get_conn() as conn:
        sync_locations(conn, provinces)
        for source in sources:
            started = time.time()
            ok &= run_stage(conn, run_id, datetime.date.today(), "load", source,
                            backfill_source, conn, source, provinces, args.start, args.end)
            print(f"{source.name} done in {time.time() - started:.0f}s", flush=True)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
