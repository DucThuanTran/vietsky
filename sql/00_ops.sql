CREATE SCHEMA IF NOT EXISTS OPS;

CREATE TABLE IF NOT EXISTS OPS.PIPELINE_RUNS
(
    RUN_ID        UUID        NOT NULL,
    RUN_DATE      DATE        NOT NULL,
    STAGE         TEXT        NOT NULL
        CHECK (STAGE IN ('extract', 'load')),
    SOURCE        TEXT        NOT NULL
        CHECK (SOURCE IN ('weather','air_quality')),
    STATUS        TEXT        NOT NULL
        CHECK (STATUS IN ('RUNNING', 'SUCCESS', 'FAILED')),
    STARTED_AT    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FINISHED_AT   TIMESTAMPTZ,
    ROWS_IN       INTEGER,
    ROWS_OUT      INTEGER,
    ERROR_MESSAGE TEXT,
    PRIMARY KEY (RUN_ID, STAGE, SOURCE)
);

-- Widen the stage CHECK for new stages (table already exists, so ALTER inside a transaction)
BEGIN;
ALTER TABLE OPS.PIPELINE_RUNS DROP CONSTRAINT IF EXISTS PIPELINE_RUNS_STAGE_CHECK;
ALTER TABLE OPS.PIPELINE_RUNS ADD CONSTRAINT PIPELINE_RUNS_STAGE_CHECK
    CHECK (STAGE IN ('extract', 'load', 'build_mart', 'quality_check', 'reconcile'));
COMMIT;

create table if not exists ops.dq_results
(
    run_id uuid not null,
    run_date date not null,
    source text not null,
    check_name text not null,
    severity text not null check (severity in ('CRITICAL', 'WARNING')),
    status text not null check (status in ('PASS', 'FAIL')),
    failed_rows integer not null,
    threshold integer not null,
    checked_at timestamptz not null default now(),
    primary key (run_id, source, check_name)
);
