from datetime import datetime, timedelta
from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models.snapshot import MetricSnapshot
from app.models.service import ServiceCheck

async def run_cleanup():
    cutoff = datetime.utcnow() - timedelta(days=30)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MetricSnapshot).where(MetricSnapshot.captured_at < cutoff))
        await db.execute(delete(ServiceCheck).where(ServiceCheck.checked_at < cutoff))
        await db.commit()
