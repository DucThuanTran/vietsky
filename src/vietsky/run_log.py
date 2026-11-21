import uuid

def new_run_id() -> uuid.UUID:
    return uuid.uuid4()

def start_stage(conn, run_id, run_date, stage, source) -> None:
    conn.execute(
        "INSERT INTO ops.pipeline_runs (run_id, run_date, stage, source, status) "
        "VALUES (%s, %s, %s, %s, 'RUNNING')",
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
