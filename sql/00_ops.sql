CREATE SCHEMA IF NOT EXISTS OPS;

CREATE TABLE IF NOT EXISTS OPS.PIPELINE_RUNS
(
    RUN_ID        UUID        NOT NULL,           -- kiểu dữ liệu riêng của Postgres cho mã uuid
    RUN_DATE      DATE        NOT NULL,           -- chỉ có ngày, không có giờ
    STAGE         TEXT        NOT NULL
        CHECK (STAGE IN ('extract', 'load')),
    SOURCE        TEXT        NOT NULL
        CHECK (SOURCE IN ('weather','air_quality')), -- 2 nguồn hiện có
    STATUS        TEXT        NOT NULL
        CHECK (STATUS IN ('RUNNING', 'SUCCESS', 'FAILED')),
    STARTED_AT    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FINISHED_AT   TIMESTAMPTZ,                    -- NULL khi đang chạy
    ROWS_IN       INTEGER,
    ROWS_OUT      INTEGER,
    ERROR_MESSAGE TEXT,
    PRIMARY KEY (RUN_ID, STAGE, SOURCE)
);