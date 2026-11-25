import time
from pathlib import Path

import duckdb
import pandas as pd

LAKE_DIR = Path("data/lake")
CSV = LAKE_DIR / "air_quality.csv"
PARQUET = LAKE_DIR / "air_quality.parquet"
PARTITIONED = LAKE_DIR / "air_quality"


def size_mb(path: Path) -> float:
    if path.is_file():
        size_bytes = path.stat().st_size
    else:
        size_bytes = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return size_bytes / (1024 * 1024)

def timed(func) -> float:
    start = time.perf_counter()
    func()
    return time.perf_counter() - start


def query_one_month(source_sql: str) -> float:
    sql = f"""
    SELECT ROUND(AVG(pm2_5), 1)
    FROM {source_sql}
    WHERE location_id = '01' AND year = 2025 AND month = 1
    """
    return duckdb.sql(sql).fetchall()[0][0]


def main():
    sources = {
        "CSV": f"read_csv('{CSV}')",
        "Parquet":           f"read_parquet('{PARQUET}')",
        "Partitioned": f"read_parquet('{PARTITIONED}/**/*.parquet', hive_partitioning = true)"
    }
    print(f"{size_mb(CSV):.2f}, {size_mb(PARQUET):.2f}, {size_mb(PARTITIONED):.2f}")

    t_csv = timed(lambda: pd.read_csv(CSV))
    t_parquet = timed(lambda: pd.read_parquet(PARQUET))
    print(f"CSV: {t_csv:.2f}s, Parquet: {t_parquet:.2f}s")

    for name, src in sources.items():
        result = query_one_month(src)
        t = timed(lambda: query_one_month(src))
        print(f"{name:>12} | PM2.5 = {result} | {t:.3f}s")

if __name__ == "__main__":
    main()
