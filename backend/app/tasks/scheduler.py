from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.config import settings

scheduler = AsyncIOScheduler()

def register_tasks():
    from app.tasks.health_check import run_health_checks
    from app.tasks.update_scan import run_update_scan
    from app.tasks.metric_collector import run_metric_collection
    from app.tasks.cleanup import run_cleanup

    scheduler.add_job(
        run_health_checks,
        IntervalTrigger(seconds=settings.health_check_interval_seconds),
        id="health_check",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        run_update_scan,
        IntervalTrigger(seconds=settings.update_scan_interval_seconds),
        id="update_scan",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        run_metric_collection,
        IntervalTrigger(seconds=settings.metric_collect_interval_seconds),
        id="metric_collector",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        run_cleanup,
        CronTrigger(hour=3, minute=0),
        id="cleanup",
        max_instances=1,
        replace_existing=True,
    )
