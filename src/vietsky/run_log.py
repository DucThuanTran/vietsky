import uuid

def new_run_id() -> uuid.UUID:
    return uuid.uuid4()

def start_stage(conn, run_id, run_date, stage, source) -> None:
    conn.execute(
        "INSERT INTO ops.pipeline_runs (run_id, run_date, stage, source, status) "
        "VALUES (%s, %s, %s, %s, 'RUNNING') "
        "ON CONFLICT (run_id, stage, source) DO UPDATE SET status = 'RUNNING', "
        "started_at = now(), finished_at = NULL, error_message = NULL",
        (run_id, run_date, stage, source),
    )
    conn.commit()

def finish_stage(conn, run_id, stage, source, status,
                 rows_in=None, rows_out=None, error_message=None) -> None:
    conn.execute(
        "UPDATE ops.pipeline_runs"
        " SET status = %s, finished_at = NOW(), rows_in = %s, rows_out = %s, error_message = %s"
        " WHERE run_id = %s AND stage = %s AND source = %s",
        (status, rows_in, rows_out, error_message, run_id, stage, source),
    )
    conn.commit()

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
