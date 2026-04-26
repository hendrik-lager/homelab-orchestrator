import asyncio
from datetime import datetime
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.snapshot import MetricSnapshot

async def run_metric_collection():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()
        await asyncio.gather(*[_collect_host(db, host) for host in hosts])
        await db.commit()

async def _collect_host(db, host: Host):
    from app.services.credential_service import get_credentials
    try:
        creds = await get_credentials(db, host.id)
        from app.tasks.health_check import _make_connector
        connector = _make_connector(host, creds)
        metrics = await connector.get_resources()
        snapshot = MetricSnapshot(
            host_id=host.id,
            captured_at=datetime.utcnow(),
            cpu_percent=metrics.cpu_percent,
            ram_used_bytes=metrics.ram_used_bytes,
            ram_total_bytes=metrics.ram_total_bytes,
            disk_used_bytes=metrics.disk_used_bytes,
            disk_total_bytes=metrics.disk_total_bytes,
            load_1m=metrics.load_1m,
        )
        db.add(snapshot)
    except Exception:
        pass
