from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.host import Host
from app.models.service import Service
from app.models.update import UpdateRecord
from app.models.alert import Alert

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    hosts_total = (await db.execute(select(func.count()).select_from(Host))).scalar()
    services_running = (await db.execute(
        select(func.count()).select_from(Service).where(Service.status == "running")
    )).scalar()
    services_down = (await db.execute(
        select(func.count()).select_from(Service).where(Service.status.in_(["stopped", "error"]))
    )).scalar()
    pending_updates = (await db.execute(
        select(func.count()).select_from(UpdateRecord).where(UpdateRecord.status == "pending")
    )).scalar()
    security_updates = (await db.execute(
        select(func.count()).select_from(UpdateRecord).where(
            UpdateRecord.status == "pending", UpdateRecord.is_security == True
        )
    )).scalar()
    active_alerts = (await db.execute(
        select(func.count()).select_from(Alert).where(Alert.status == "firing")
    )).scalar()

    return {
        "hosts_total": hosts_total,
        "services_running": services_running,
        "services_down": services_down,
        "pending_updates": pending_updates,
        "security_updates": security_updates,
        "active_alerts": active_alerts,
    }
