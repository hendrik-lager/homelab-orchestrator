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
    "auto_install": "Auto-Install",
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


async def refresh_auto_install_job():
    """Read AutoUpdateSettings from DB and add/update/remove the auto_install job."""
    from app.database import AsyncSessionLocal
    from app.models.auto_update_settings import AutoUpdateSettings
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AutoUpdateSettings).where(AutoUpdateSettings.id == 1))
        cfg = result.scalar_one_or_none()

    existing = scheduler.get_job("auto_install")

    if not cfg or not cfg.enabled:
        if existing:
            scheduler.remove_job("auto_install")
        return

    from app.tasks.auto_install import run_auto_install
    parts = cfg.cron_expression.split()
    if len(parts) != 5:
        return
    minute, hour, day, month, day_of_week = parts
    trigger = CronTrigger(
        minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week
    )

    if existing:
        scheduler.reschedule_job("auto_install", trigger=trigger)
    else:
        scheduler.add_job(
            _wrap("auto_install", run_auto_install),
            trigger,
            id="auto_install",
            max_instances=1,
            replace_existing=True,
        )
