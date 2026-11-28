# Incident 02 · Source renames field `pm2_5` → `pm25` (schema drift)

**Drill date:** 2026-11-28 · `VIETSKY_CHAOS=rename_field run_pipeline.py --date 2026-11-28 --source air_quality` · run `2ebd1b4d`
**Severity:** high (the whole air_quality source stops) · **Time to detect:** ~75 seconds (end of extract + load)

## Symptoms
- `extract` SUCCESS (34 provinces, 6,528 hours): the API still returns 200 and the JSON has every row.
- `load` FAILED with `error_message = 'pm2_5'`: a bare `KeyError` that says nothing about the cause.

## Detection
- **First drill:** the only signal was `'pm2_5'` in `ops.pipeline_runs`. Opening `data/raw/air_quality/date=2026-11-28/01.json` showed `hourly` contained `pm25` instead of `pm2_5`.
- **Why `raw_schema` did not help:** the existing check **never got to run**. It lives in `quality_check`, after `load`, and `load` had already crashed.

## Scope
Extract passed and load broke inside `transform.to_rows`, so the problem sits between raw and staging: the raw structure no longer matches the data contract in `config.py`.

## Root cause (5 Whys)
1. Why did load fail? `to_rows` read `hourly['pm2_5']`, which does not exist.
2. Why does it not exist? The source renamed the field (simulated by `chaos.break_payload`).
3. Why was the error message unhelpful? Nothing validated the structure **before** using it, so the error surfaced at the deepest point.
4. Why didn't the existing `raw_schema` check help? It was in the wrong place: it ran after the step it was meant to protect.
5. Why was the mart unaffected? Load stopped before writing, `build_mart` never ran, and the previous data stayed intact.

## Fix
- **Short term:** when the real source renames a field, update `columns` in `config.py` (API name → DB name) and re-run.
- **Done in code:** `run_load` now calls `assert_raw_schema` first. The error now reads:
  `Schema drift: 34 raw files missing columns, e.g. 01.json missing ['pm2_5']`.

## Prevention
- Validate structure at the **boundary** where data enters the system (fail fast), not where it is used.
- Raw keeps the broken payload, so after fixing the mapping the data can be reloaded from raw without calling the API again.
- "Soft" schema drift (changed units or meaning) is not caught by this check. That needs comparing value distributions against history.
