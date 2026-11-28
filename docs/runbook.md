# Runbook · VietSky pipeline troubleshooting

Principle: follow the data flow from source to destination. Stop at the first layer that looks wrong: that is where the problem is.

## 0. Did the pipeline run?
```sql
SELECT run_id, MIN(started_at) AS started, source, stage, status, error_message
FROM ops.pipeline_runs
WHERE started_at > NOW() - INTERVAL '2 days'
GROUP BY run_id, source, stage, status, error_message
ORDER BY started DESC;
```
- **No rows in the last 24h:** the scheduler (Airflow) is down or the DAG is paused. Check `docker compose --profile airflow ps` and the Airflow UI at `localhost:8080`.
- **A row stuck in `RUNNING` for more than 30 minutes:** the task is hung, or the process was killed mid-stage.
- **Errors raised before any stage** (e.g. `Invalid provinces.csv`) leave no row in `pipeline_runs`. Check the `sync_locations` task log in Airflow, or stderr.

## 1. Did the data arrive? (extract)
- **`stage = 'extract'` FAILED with `failed after 4 attempts: HTTP 5xx`:** the source API is down. The call was already retried 4 times with backoff. Check Open-Meteo's status, then re-run later.
- **`HTTP 400 ... out of allowed range`:** the date range is outside the `/forecast` window (see Data profiling in the README).
- **Raw files** live in `data/raw/<source>/date=<run_date>/`. There must be 34 files.

## 2. Is it complete and well-formed? (raw)
```sql
SELECT source, check_name, status, failed_rows
FROM ops.dq_results
WHERE run_id = '<run_id>' ORDER BY status, check_name;
```
- **`raw_schema` FAIL, or load fails with `Schema drift: ... missing [...]`:** the source renamed or removed a field. Compare `hourly` in one JSON file with `source.columns` in `config.py`.

## 3. Was it processed correctly? (load + quality_check on staging)
- **`all_provinces` FAIL:** a province is missing. Find it with Q12 in `sql/explore.sql`.
- **`pm25_not_null` / `temperature_not_null` FAIL:** the source returned all NULLs for a province. Inspect that province's raw file.
- **`unique_key` FAIL:** the upsert or the primary key was removed. Check `\d stg_<source>_hourly`.
- **`freshness_24h` FAIL:** load wrote nothing. Compare the load stage's `rows_out` with extract's.
- When `quality_check` FAILS, `build_mart` **does not run**. The mart keeps its last good version, which is the intended behavior: bad data is never published.

## 4. Did everything reach the destination? (build_mart + reconcile)
- **`build_mart` FAILED with `Reconcile failed: staging=X mart=Y`:** the join with a dimension dropped rows. Look for a `location_id` missing from `mart.dim_location`.
- **`reconcile_daily` FAIL with a log line like `day: raw=816 staging=816 mart=0`:** the mart is missing that day (build_mart failed and the previous mart was kept).
- **`raw ≠ staging`:** the bug is in transform/load.

## 5. Is it on time and correct in time?
- Check `freshness_24h` and the dashboard's Operations page (`streamlit run dashboard/app.py`).
- A timezone shift (incident 05) is **not** caught by any automated check. The hour × month heatmap shifts by 7 columns, and the PM2.5 peak moves from 19–23h to 2–6h.

## After the fix
1. Re-run for the affected date: `PYTHONPATH=src .venv/bin/python pipelines/run_pipeline.py --date <date>`, or Clear the task in Airflow. The pipeline is idempotent, so re-runs are safe.
2. Confirm every check in `ops.dq_results` for the new run is PASS.
3. Write a postmortem in `docs/incidents/` if dashboard users were affected.
