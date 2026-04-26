from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.alert import Alert, AlertRule

router = APIRouter()

@router.get("/")
async def list_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).order_by(Alert.fired_at.desc()))
    return result.scalars().all()

@router.post("/rules")
async def create_alert_rule(data: dict, db: AsyncSession = Depends(get_db)):
    rule = AlertRule(
        name=data["name"],
        rule_type=data["rule_type"],
        host_id=data.get("host_id"),
        threshold_value=data.get("threshold_value"),
        enabled=data.get("enabled", True),
        notify_email=data.get("notify_email", True),
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

@router.get("/rules")
async def list_alert_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertRule))
    return result.scalars().all()

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404)
    alert.status = "resolved"
    await db.commit()
    return {"ok": True}
