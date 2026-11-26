import datetime
import json
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

from vietsky.config import DAYS_BACK, RAW_DIR

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
WINDOW = "ts_utc >= %(start)s AND ts_utc < %(end)s"

RULES = [
    {   # Có dòng nào mất khoá không? Mất khoá thì không JOIN được sang dim, dòng sẽ rơi khỏi mart.
        "name": "not_null_key",
        "severity": "CRITICAL",
        "threshold": 0,
        "sql": f"SELECT COUNT(*) FROM {{table}} WHERE {WINDOW} AND (location_id IS NULL OR ts_utc IS NULL)",
    },
    {   # Có tỉnh-giờ nào bị ghi 2 lần không? Trùng dòng thì AVG lệch, SUM gấp đôi.
        "name": "unique_key",
        "severity": "CRITICAL",
        "threshold": 0,
        "sql": f"SELECT COUNT(*) - COUNT(DISTINCT (location_id, ts_utc)) FROM {{table}} WHERE {WINDOW}",
    },
    {   # Có đủ 34 tỉnh trong khung này không?
        "name": "all_provinces",
        "severity": "CRITICAL",
        "threshold": 0,
        "sql": f"SELECT 34 - COUNT(DISTINCT location_id) FROM {{table}} WHERE {WINDOW}",
    },
    {   # Lần nạp gần nhất có quá 24 giờ trước không? (1 = quá hạn, 0 = còn mới)
        "name": "freshness_24h",
        "severity": "CRITICAL",
        "threshold": 0,
        "sql": "SELECT (NOW() - MAX(loaded_at) > INTERVAL '24 hours')::INT FROM {table}",
    },
    {   # PM2.5 có giá trị vô lý (âm hoặc trên 1000 µg/m³) không?
        "name": "pm25_range",
        "severity": "WARNING",
        "threshold": 0,
        "source": "air_quality",
        "sql": f"SELECT COUNT(*) FROM {{table}} WHERE {WINDOW} AND (pm2_5 < 0 OR pm2_5 > 1000)",
    },
]


def check_window(run_date: datetime.date) -> dict:
    start_day = run_date - datetime.timedelta(days=DAYS_BACK)
    end_day = run_date + datetime.timedelta(days=1)
    start = datetime.datetime.combine(start_day, datetime.time(), tzinfo=VN_TZ)
    end = datetime.datetime.combine(end_day, datetime.time(), tzinfo=VN_TZ)
    return {"start": start, "end": end}


def rules_for(source_name: str) -> list[dict]:
    return [r for r in RULES if r.get("source") in (source_name, None)]


def run_rule(conn, rule: dict, table: str, params: dict) -> dict:
    sql = rule["sql"].format(table=table)
    failed = conn.execute(sql, params).fetchone()[0]
    status = "PASS" if failed <= rule["threshold"] else "FAIL"
    return {
        "check_name": rule["name"],
        "severity": rule["severity"],
        "status": status,
        "failed_rows": failed,
        "threshold": rule["threshold"],
    }


def save_results(conn, run_id, run_date, source_name: str, results: list[dict]) -> None:
    for r in results:
        conn.execute(
            "INSERT INTO ops.dq_results"
            " (run_id, run_date, source, check_name, severity, status, failed_rows, threshold)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (run_id, run_date, source_name, r["check_name"], r["severity"], r["status"], r["failed_rows"], r["threshold"]),
        )


def make_result(check_name: str, severity: str, failed: int, threshold: int) -> dict:
    return {
        "check_name": check_name,
        "severity": severity,
        "status": "PASS" if failed <= threshold else "FAIL",
        "failed_rows": failed,
        "threshold": threshold,
    }


def raw_files(source, run_date) -> list[Path]:
    return sorted((RAW_DIR / source.name / f"date={run_date}").glob("*.json"))


def read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_raw_schema(source, run_date) -> dict:
    expected = {"time", *source.columns.keys()}
    bad_files = 0
    for path in raw_files(source, run_date):
        hourly = read_json(path).get("hourly", {})
        missing = expected - set(hourly.keys())
        if missing:
            print(f"[raw_schema] {source.name}/{path.name}: thiếu {sorted(missing)}")
            bad_files += 1
    return make_result("raw_schema", "CRITICAL", bad_files, 0)


STAGING_DAILY_SQL = f"""
SELECT ((ts_utc AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE)::TEXT AS day, COUNT(*)
FROM {{table}}
WHERE {WINDOW}
GROUP BY 1
"""

MART_DAILY_SQL = f"""
SELECT d.full_date::TEXT AS day, COUNT(*)
FROM mart.fact_{{name}}_hourly f
JOIN mart.dim_date d ON f.date_key = d.date_key
WHERE {WINDOW}
GROUP BY 1
"""


def raw_daily_counts(source, run_date) -> Counter:
    counts = Counter()
    for path in raw_files(source, run_date):
        for t in read_json(path)["hourly"]["time"]:
            counts[t[:10]] += 1
    return counts


def db_daily_counts(conn, sql: str, params: dict) -> dict:
    return dict(conn.execute(sql, params).fetchall())


def reconcile_daily(conn, source, run_date) -> dict:
    params = check_window(run_date)
    raw = raw_daily_counts(source, run_date)
    stg = db_daily_counts(conn, STAGING_DAILY_SQL.format(table=source.table), params)
    mart = db_daily_counts(conn, MART_DAILY_SQL.format(name=source.name), params)
    bad_days = 0
    for day in sorted(raw):
        r, s, m = raw[day], stg.get(day, 0), mart.get(day, 0)
        if not (r == s == m):
            print(f"[reconcile] {source.name} {day}: raw={r} staging={s} mart={m}")
            bad_days += 1
    return make_result("reconcile_daily", "CRITICAL", bad_days, 0)


def run_quality(conn, source, run_date, run_id) -> tuple[int, int]:
    params = check_window(run_date)
    results = [run_rule(conn, r, source.table, params) for r in rules_for(source.name)]
    results += [check_raw_schema(source, run_date), reconcile_daily(conn, source, run_date)]
    save_results(conn, run_id, run_date, source.name, results)
    conn.commit()
    critical = [r["check_name"] for r in results
                if r["status"] == "FAIL" and r["severity"] == "CRITICAL"]
    if critical:
        raise ValueError(f"DQ failed: {critical}")
    passed = sum(1 for r in results if r["status"] == "PASS")
    return len(results), passed

