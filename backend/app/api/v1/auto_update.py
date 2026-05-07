from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.database import get_db
from app.models.auto_update_settings import AutoUpdateSettings

router = APIRouter()


_VALID_SEVERITIES = ("critical", "high", "medium", "low", "none")


class AutoUpdateSettingsIn(BaseModel):
    enabled: bool
    security_only: bool
    min_severity: str = "high"
    cron_expression: str


@router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AutoUpdateSettings).where(AutoUpdateSettings.id == 1))
    cfg = result.scalar_one_or_none()
    if not cfg:
        return {"enabled": False, "security_only": True, "min_severity": "high", "cron_expression": "0 3 * * *"}
    return cfg


@router.put("/settings")
async def save_settings(data: AutoUpdateSettingsIn, db: AsyncSession = Depends(get_db)):
    parts = data.cron_expression.strip().split()
    if len(parts) != 5:
        raise HTTPException(status_code=422, detail="Cron-Ausdruck muss 5 Felder haben (z.B. '0 3 * * *')")
    if data.min_severity not in _VALID_SEVERITIES:
        raise HTTPException(status_code=422, detail=f"min_severity muss eines von {_VALID_SEVERITIES} sein")

    result = await db.execute(select(AutoUpdateSettings).where(AutoUpdateSettings.id == 1))
    cfg = result.scalar_one_or_none()
    if cfg:
        cfg.enabled = data.enabled
        cfg.security_only = data.security_only
        cfg.min_severity = data.min_severity
        cfg.cron_expression = data.cron_expression
        cfg.updated_at = datetime.utcnow()
    else:
        cfg = AutoUpdateSettings(
            id=1,
            enabled=data.enabled,
            security_only=data.security_only,
            min_severity=data.min_severity,
            cron_expression=data.cron_expression,
        )
        db.add(cfg)
    await db.commit()

    from app.tasks.scheduler import refresh_auto_install_job
    await refresh_auto_install_job()

    return {"ok": True}


@router.post("/apply")
async def apply_all_now(
    security_only: bool = False,
    min_severity: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    from app.services.update_service import apply_all_pending
    results = await apply_all_pending(db, security_only=security_only, min_severity=min_severity)
    return {"results": results}
