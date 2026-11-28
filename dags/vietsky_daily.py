import datetime
import uuid
from zoneinfo import ZoneInfo

from airflow.sdk import dag, task, get_current_context

from vietsky.config import SOURCES, TIMEZONE
from vietsky.load import get_conn
from vietsky.run_log import run_stage
from vietsky.stages import run_extract, run_load, read_provinces, sync_locations
from vietsky.mart import build_mart
from vietsky.quality import run_quality, run_reconcile

SOURCE_BY_NAME = {s.name: s for s in SOURCES}


def run_context() -> tuple[datetime.date, uuid.UUID]:
    ctx = get_current_context()
    dag_run = ctx["dag_run"]
    moment = ctx.get("logical_date") or dag_run.run_after
    run_date = moment.astimezone(ZoneInfo(TIMEZONE)).date()
    run_id = uuid.uuid5(uuid.NAMESPACE_URL, f"vietsky/{dag_run.run_id}")
    return run_date, run_id


def stage_call(stage: str, conn, source, run_date, run_id) -> tuple:
    if stage == "extract":
        return run_extract, source, read_provinces(), run_date
    if stage == "load":
        return run_load, conn, source, run_date
    if stage == "quality_check":
        return run_quality, conn, source, run_date, run_id
    if stage == "build_mart":
        return build_mart, conn, source
    return run_reconcile, conn, source, run_date, run_id


@task
def run_pipeline_stage(stage: str, source_name: str) -> None:
    source = SOURCE_BY_NAME[source_name]
    run_date, run_id = run_context()
    with get_conn() as conn:
        func, *args = stage_call(stage, conn, source, run_date, run_id)
        if not run_stage(conn, run_id, run_date, stage, source, func, *args):
            raise RuntimeError(f"{stage}/{source_name} FAILED, xem ops.pipeline_runs run_id={run_id}")


@task
def sync_locations_task() -> None:
    with get_conn() as conn:
        sync_locations(conn, read_provinces())


@dag(
    dag_id="vietsky_daily",
    schedule="0 7 * * *",
    start_date=datetime.datetime(2026, 11, 25, tzinfo=ZoneInfo(TIMEZONE)),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": datetime.timedelta(minutes=1)},
    tags=["vietsky"],
)
def vietsky_daily():
    locations = sync_locations_task.override(task_id="sync_locations")()
    for source in SOURCES:
        name = source.name
        extract = run_pipeline_stage.override(task_id=f"extract_{name}")("extract", name)
        load = run_pipeline_stage.override(task_id=f"load_{name}")("load", name)
        quality = run_pipeline_stage.override(task_id=f"quality_check_{name}", retries=0)(
            "quality_check", name)
        mart = run_pipeline_stage.override(task_id=f"build_mart_{name}")("build_mart", name)
        reconcile = run_pipeline_stage.override(
            task_id=f"reconcile_{name}", retries=0, trigger_rule="all_done")("reconcile", name)
        locations >> extract >> load >> quality >> mart >> reconcile


vietsky_daily()
