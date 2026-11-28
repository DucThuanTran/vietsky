# Incident 05 · Vietnam local time labelled as UTC (7-hour shift)

**Format:** tabletop exercise + unit test `tests/test_chaos.py::test_tz_shift_moves_time_7_hours_later`.
It was not run against the real database, because this fault **overwrites correct data** with time-shifted data and no check stops the pipeline (see the analysis below).
**Severity:** very high (silently wrong data) · **Expected time to detect:** only when someone looks at the heatmap

## Scenario
With `VIETSKY_CHAOS=tz_shift`, `transform` attaches `tzinfo=UTC` to the Vietnam-time string `2026-11-28T08:00`, when the correct offset is `+07:00`. Every row moves **7 hours later**.

## What happens to the data
- Correct window: 2026-11-21 00:00 → 2026-11-28 23:00 Vietnam time. Shifted window: 2026-11-21 07:00 → 2026-11-29 06:00.
- The upsert on `(location_id, ts_utc)` **overwrites** every overlapping hour with the value from 7 hours earlier, and adds 7 "future" hours on 2026-11-29 for each province.

## Which checks catch it?
| Check | Result | Why |
|---|---|---|
| `not_null_key`, `unique_key`, `all_provinces` | PASS | Keys are complete, unique, and all 34 provinces are present |
| `freshness_24h` | PASS | `loaded_at` is still recent |
| `pm25_range`, `*_not_null` | PASS | Values are valid, only the hours are wrong |
| `reconcile_daily` | PASS | Inside the 8-day window every day still has 816 rows (old hours are overwritten, not lost) |

→ **No check catches it.** This is the hardest of the 6 scenarios to detect.

## Detection
- **Dashboard hour × month heatmap:** the evening PM2.5 peak (19–23h) moves to 2–6h, and the daily temperature peak lands at 19–21h instead of 13–15h.
- **A query:** the average hottest hour of the day in Ho Chi Minh City is no longer 13–15h.

## Root cause (5 Whys)
1. Why is the heatmap shifted? `ts_utc` is 7 hours later than reality.
2. Why? Transform attached the wrong timezone.
3. Why wasn't it blocked? Current checks test *completeness* and *validity*, not *physical plausibility*.
4. Why was correct data lost? The upsert overwrote it. Raw is still intact, so it can be rebuilt.
5. Why would existing unit tests help? `test_transform.py` already tests the timezone handling. This bug only appears when someone changes the transform code, so tests are the main line of defense.

## Fix
Fix the transform, reload the affected days from raw (`backfill.py`, or re-run each day), and delete the extra future rows:
`DELETE FROM stg_<source>_hourly WHERE ts_utc >= '<end of the correct window>' AND loaded_at >= '<time of the bad run>'`.

## Prevention
- Run the transform unit tests in CI before every deploy.
- Add a plausibility check: the average hottest hour of the day must fall within 11–16h Vietnam time (anomaly check against history).
- Add a WARNING-level check for rows outside the extract window written by the current run (`ts_utc >= end`).
