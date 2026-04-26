from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.host import Host
from app.models.service import Service, ServiceCheck
from datetime import datetime

async def check_service(db: AsyncSession, service: Service) -> ServiceCheck:
    from app.services.credential_service import get_credentials
    from app.tasks.health_check import _make_connector

    host_result = await db.execute(select(Host).where(Host.id == service.host_id))
    host = host_result.scalar_one_or_none()

    if not host:
        check = ServiceCheck(
            service_id=service.id,
            checked_at=datetime.utcnow(),
            status="unknown",
            error_message="Host not found",
        )
        db.add(check)
        return check

    creds = await get_credentials(db, host.id)
    connector = _make_connector(host, creds)

    status = await connector.check_reachability()
    check = ServiceCheck(
        service_id=service.id,
        checked_at=datetime.utcnow(),
        status="running" if status.reachable else "stopped",
        error_message=status.error,
    )
    db.add(check)
    service.last_checked = datetime.utcnow()
    service.status = check.status

    return check
