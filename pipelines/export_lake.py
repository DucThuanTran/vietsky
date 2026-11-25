import shutil
from pathlib import Path

import pandas as pd

from vietsky.load import get_conn

LAKE_DIR = Path("data/lake")

EXPORT_SQL = """
SELECT l.location_id, l.name, f.ts_utc, f.hour_vn,
       d.year, d.month,
       f.pm2_5, f.pm10, f.us_aqi, f.nitrogen_dioxide, f.ozone
FROM mart.fact_air_quality_hourly f
JOIN mart.dim_location l ON f.location_key = l.location_key
JOIN mart.dim_date d     ON f.date_key = d.date_key
"""


def read_from_db() -> pd.DataFrame:
    with get_conn() as conn:
        cur = conn.execute(EXPORT_SQL)
        cols = [c.name for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)

def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    df.to_parquet(path, index=False)



def write_parquet_partitioned(df: pd.DataFrame, path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    df.to_parquet(path, index=False, partition_cols=["year", "month"])


def main():
    LAKE_DIR.mkdir(parents=True, exist_ok=True)
    df = read_from_db()
    print(f"{len(df)} rows")
    write_csv(df, LAKE_DIR / "air_quality.csv")
    write_parquet(df, LAKE_DIR / "air_quality.parquet")
    write_parquet_partitioned(df, LAKE_DIR / "air_quality")

if __name__ == "__main__":
    main()
