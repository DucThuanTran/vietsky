from psycopg import sql
import psycopg
from vietsky.config import db_conninfo

def get_conn():
    return psycopg.connect(**db_conninfo())

def load_rows(conn, table, db_cols: list, rows: list) -> int:
    value_cols = db_cols[2:]
    query = sql.SQL(
        "INSERT INTO {table} ({cols}) VALUES ({vals}) "
        "ON CONFLICT (location_id, ts_utc) DO UPDATE SET {updates}, loaded_at = now()"
    ).format(
        table=sql.Identifier(table),
        cols=sql.SQL(", ").join(map(sql.Identifier, db_cols)),
        vals=sql.SQL(", ").join([sql.Placeholder()] * len(db_cols)),
        updates=sql.SQL(", ").join(
            sql.SQL("{c} = EXCLUDED.{c}").format(c=sql.Identifier(c)) for c in value_cols
        ),
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
