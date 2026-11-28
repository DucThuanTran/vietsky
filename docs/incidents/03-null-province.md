# Incident 03 · One province returns all NULLs

**Drill date:** 2026-11-28 · `VIETSKY_CHAOS=null_province run_pipeline.py --date 2026-11-28 --source weather`
Drill 1: run `1c1beffa` (before the fix) · Drill 2: run `0771d653` (after adding the rule)
**Severity:** high (Hanoi shows empty on the dashboard and the national average is skewed) · **Time to detect:** drill 1, not detected; drill 2, ~1 second after load

## Symptoms
The API returned 200 with all 192 hours for Hanoi (`01`), but every measure was `null`.

## Detection
- **Drill 1: no check caught it.** All 5 stages succeeded and 6/6 checks passed. Result: 192 rows with `temperature IS NULL` for Hanoi in both staging and the mart.
  - `all_provinces` PASS: `location_id = '01'` is still present.
  - `reconcile_daily` PASS: row counts match across all three layers (a NULL row is still a row).
  - An ad-hoc NULL check (`dq_checks.sql`) exists, but only runs manually.
- **Drill 2, after adding `temperature_not_null` / `pm25_not_null` (CRITICAL):** `quality_check` FAILED with `DQ failed: ['temperature_not_null']`, `failed_rows = 192`, and `build_mart` **did not run**.

## Scope
The source (extract) delivered empty values, while the pipeline itself moved data correctly. This is a **content** failure, not a **volume** failure.

## Root cause (5 Whys)
1. Why is Hanoi empty on the dashboard? The mart has 192 NULL hours.
2. Why did NULLs reach the mart? No rule checked the NULL rate of measure columns.
3. Why was the rule missing? The original rules focused on keys, volume and freshness, treating "all rows present" as "all data present".
4. Why did the source return NULLs? It is simulated here. In the real world, a station or model stops reporting for one point, like the 238 NULL hours at the start of 2022-08-04.
5. Why did the mart still hold NULLs during drill 2? The gate keeps the mart at its **previous** version, and that version was already polluted by drill 1. A gate stops new bad data, it does not clean up old bad data.

## Fix
Once the source returns real values, re-run the pipeline: the upsert overwrites the 192 NULL rows and the mart is rebuilt. Done in run `f04107cd`: Hanoi's NULL count in staging and the mart is back to 0.

## Prevention
- Added `*_not_null` rules on each source's main measure (threshold 0 within the 8-day window).
- "All rows present" ≠ "all data present": completeness must be checked at both the **row** and the **value** level.
- If a source has legitimate NULLs (e.g. the first hours of a series), use a ratio threshold (e.g. ≤ 1%) instead of 0.
