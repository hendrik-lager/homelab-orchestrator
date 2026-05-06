from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.job import ScheduledJob

router = APIRouter()


@router.get("/status")
async def get_scheduler_status():
    from app.tasks.scheduler import scheduler, _task_runs, JOB_LABELS

    jobs = []
    for job in scheduler.get_jobs():
        run = _task_runs.get(job.id, {})
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        jobs.append({
            "id": job.id,
            "label": JOB_LABELS.get(job.id, job.id),
            "next_run": next_run,
            "last_run": run.get("last_run"),
            "last_result": run.get("last_result"),
            "last_error": run.get("last_error"),
        })
    return jobs


@router.get("/")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScheduledJob))
    return result.scalars().all()

@router.post("/")
async def create_job(data: dict, db: AsyncSession = Depends(get_db)):
    job = ScheduledJob(
        name=data["name"],
        job_type=data["job_type"],
        host_id=data.get("host_id"),
        cron_expression=data.get("cron_expression"),
        enabled=data.get("enabled", True),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

@router.patch("/{job_id}")
async def update_job(job_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in data.items():
        if hasattr(job, key):
            setattr(job, key, value)
    await db.commit()
    await db.refresh(job)
    return job

@router.delete("/{job_id}")
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
    await db.commit()
    return {"ok": True}
