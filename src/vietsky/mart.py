from pathlib import Path

MART_SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "mart"


def run_sql_file(conn, name: str) -> None:
    sql_text = (MART_SQL_DIR / f"{name}.sql").read_text(encoding="utf-8")
    conn.execute(sql_text)


def count_rows(conn, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def build_mart(conn, source) -> tuple[int, int]:
    run_sql_file(conn, "dims")
    run_sql_file(conn, f"fact_{source.name}")
    rows_in = count_rows(conn, source.table)
    rows_out = count_rows(conn, f"mart.fact_{source.name}_hourly")
    if rows_in != rows_out:
        raise ValueError(f"Reconcile failed: staging={rows_in} mart={rows_out}")
    conn.commit()
    return rows_in, rows_out
