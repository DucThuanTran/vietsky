# Incident 04 · Lat/lon swapped for 3 provinces in reference data

**Drill date:** 2026-11-28 · `VIETSKY_CHAOS=swap_latlon run_pipeline.py --date 2026-11-28 --source weather`
**Severity:** high if it slips through (data fetched for the wrong place, wrong map) · **Time to detect:** < 1 second

## Symptoms
The pipeline stops immediately on startup:
```
ValueError: Invalid provinces.csv: Hà Nội is outside Vietnam: (105.84117, 21.0245);
Cao Bằng is outside Vietnam: (106.25786, 22.66568); Tuyên Quang is outside Vietnam: (105.21424, 21.82356)
```

## Detection
The coordinate check (`validate.check_coordinates`: lat 8–24, lon 102–110) inside `sync_locations` caught it. That step runs **before** every stage.

## Scope
The failure is in the reference data (`config/provinces.csv` → `dim_location`). Nothing was written: no raw files, no staging rows, and `dim_location` kept the correct coordinates.

## Root cause (5 Whys)
1. Why did the pipeline stop? Three provinces had coordinates outside Vietnam.
2. Why were the coordinates wrong? The lat and lon columns were swapped (simulated by `chaos.swap_latlon`; in real life, someone pasting columns in the wrong order while editing the CSV).
3. Why is this dangerous? If it slips through, lat 105 does not exist and the API returns 400. Worse, if both swapped values are still valid coordinates (e.g. two provinces mixed up), the API **returns data for another place** with no error at all.
4. Why could it slip through before? The validator existed from the start, but the pipeline **never called it**. It only ran manually via `python validate.py`.
5. Why is it blocked now? After this drill, `validate_provinces` was wired into `sync_locations`, in both `run_pipeline.py` and the DAG.

## Fix
Correct `config/provinces.csv`, then re-run the pipeline.

## Prevention
- Reference data needs the same checks as the main data (a data contract for config files).
- **Remaining gap:** the error is raised **before** `run_stage`, so no row is written to `ops.pipeline_runs`. You have to read the `sync_locations` task log in Airflow. A follow-up would log the setup step as well.
- **Visual check:** the dashboard map. A misplaced province lands in the sea or off the map.
