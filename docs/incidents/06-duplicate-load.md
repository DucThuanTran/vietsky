# Incident 06 · Double run with upsert disabled (duplicate rows)

**Format:** design analysis. No fault needs to be injected: the system blocks this **through its table structure**.

## Scenario
Someone replaces `ON CONFLICT ... DO UPDATE` with a plain `INSERT` and runs the pipeline twice for the same date.

## What happens
- Staging has `PRIMARY KEY (location_id, ts_utc)`, so the second run fails with `duplicate key value violates unique constraint`. The `load` stage FAILS, the transaction rolls back, and no duplicate is written.
- If the PK is removed too, `unique_key` (`COUNT(*) - COUNT(DISTINCT (location_id, ts_utc))`) returns 6,528. `quality_check` FAILS, `build_mart` does not run, and the dashboard never shows doubled `SUM`s.
- In the mart, the fact PK `(location_key, ts_utc)` and the staging = mart reconciliation form a third layer.

## Lesson
Defense in depth: database constraints → quality gate → reconciliation. Each layer catches what the previous one lets through.
