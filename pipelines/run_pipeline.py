import argparse
import datetime
import sys

from vietsky.config    import SOURCES
from vietsky.load      import get_conn
from vietsky.run_log   import new_run_id, run_stage
from vietsky.stages    import run_extract, run_load, read_provinces, sync_locations
from vietsky.mart      import build_mart
from vietsky.quality   import run_quality, run_reconcile

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=datetime.date.fromisoformat,
                        default=datetime.date.today())
    parser.add_argument("--source", choices=[s.name for s in SOURCES])
    return parser.parse_args()

def main():
    args = parse_args() ; run_id = new_run_id()
    provinces = read_provinces()
    sources = [s for s in SOURCES if args.source in (None, s.name)]
    print(f"run_id={run_id} run_date={args.date}")
    ok = True
    with get_conn() as conn:
        sync_locations(conn, provinces)
        for source in sources:
            if not run_stage(conn, run_id, args.date, "extract", source,
                             run_extract, source, provinces, args.date):
                ok = False
                continue
            if not run_stage(conn, run_id, args.date, "load", source,
                             run_load, conn, source, args.date):
                ok = False
                continue
            if not run_stage(conn, run_id, args.date, "quality_check", source,
                             run_quality, conn, source, args.date, run_id):
                ok = False
                continue
            if not run_stage(conn, run_id, args.date, "build_mart", source,
                             build_mart, conn, source):
                ok = False
            if not run_stage(conn, run_id, args.date, "reconcile", source,
                             run_reconcile, conn, source, args.date, run_id):
                ok = False
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
