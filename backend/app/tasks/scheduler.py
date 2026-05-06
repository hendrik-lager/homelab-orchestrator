from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.config import settings

scheduler = AsyncIOScheduler()

_task_runs: dict[str, dict] = {}

JOB_LABELS: dict[str, str] = {
    "health_check": "Health Check",
    "update_scan": "Update Scan",
    "metric_collector": "Metrik Erfassung",
    "service_discovery": "Service Discovery",
    "cleanup": "Datenbereinigung",
}


def _wrap(job_id: str, fn):
    async def wrapper():
        started = datetime.now(timezone.utc)
        try:
            await fn()
            _task_runs[job_id] = {
                "last_run": started.isoformat(),
                "last_result": "ok",
                "last_error": None,
            }
        except Exception as exc:
            _task_runs[job_id] = {
                "last_run": started.isoformat(),
                "last_result": "error",
                "last_error": str(exc),
            }

    wrapper.__name__ = fn.__name__
    return wrapper


def register_tasks():
    from app.tasks.health_check import run_health_checks
    from app.tasks.update_scan import run_update_scan
    from app.tasks.metric_collector import run_metric_collection
    from app.tasks.service_discovery import run_service_discovery
    from app.tasks.cleanup import run_cleanup

    scheduler.add_job(
        _wrap("health_check", run_health_checks),
        IntervalTrigger(seconds=settings.health_check_interval_seconds),
        id="health_check",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        _wrap("update_scan", run_update_scan),
        IntervalTrigger(seconds=settings.update_scan_interval_seconds),
        id="update_scan",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        _wrap("metric_collector", run_metric_collection),
        IntervalTrigger(seconds=settings.metric_collect_interval_seconds),
        id="metric_collector",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        _wrap("service_discovery", run_service_discovery),
        IntervalTrigger(seconds=settings.service_discovery_interval_seconds),
        id="service_discovery",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        _wrap("cleanup", run_cleanup),
        CronTrigger(hour=3, minute=0),
        id="cleanup",
        max_instances=1,
        replace_existing=True,
    )
