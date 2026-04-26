from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.alert import Alert, AlertRule
from app.services.notification import send_alert_email
from datetime import datetime

async def create_alert(
    db: AsyncSession,
    alert_type: str,
    severity: str,
    title: str,
    body: str | None = None,
    host_id: int | None = None,
    service_id: int | None = None,
) -> Alert:
    alert = Alert(
        host_id=host_id,
        service_id=service_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        body=body,
        status="firing",
        fired_at=datetime.utcnow(),
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    rules_result = await db.execute(select(AlertRule).where(AlertRule.enabled == True))
    rules = rules_result.scalars().all()

    for rule in rules:
        if rule.rule_type == alert_type and rule.notify_email:
            await send_alert_email(title, body or "")

    return alert

async def resolve_alert(db: AsyncSession, alert_id: int) -> bool:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        return False

    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    await db.commit()
    return True
