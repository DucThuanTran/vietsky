from psycopg import sql
import psycopg
from vietsky.config import db_conninfo

def get_conn():
    return psycopg.connect(**db_conninfo())

def load_rows(conn, table, db_cols: list, rows: list) -> int:
    query = sql.SQL(
        "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (location_id, ts_utc) DO NOTHING"
    ).format(
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, db_cols)),
        sql.SQL(", ").join([sql.Placeholder()] * len(db_cols)),
    )
    with conn.cursor() as cur:
        cur.executemany(query, rows)
        return cur.rowcount

def load_locations(conn, rows: list) -> int:
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
        return cur.rowcount
