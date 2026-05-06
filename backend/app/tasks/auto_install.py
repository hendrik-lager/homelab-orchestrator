import logging
from app.database import AsyncSessionLocal
from app.models.auto_update_settings import AutoUpdateSettings
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def run_auto_install():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AutoUpdateSettings).where(AutoUpdateSettings.id == 1))
        cfg = result.scalar_one_or_none()
        if not cfg or not cfg.enabled:
            return

        from app.services.update_service import apply_all_pending
        results = await apply_all_pending(db, security_only=cfg.security_only)

    ok_count = sum(1 for r in results if r["ok"])
    fail_count = len(results) - ok_count
    logger.info("Auto-Install: %d erfolgreich, %d fehlgeschlagen", ok_count, fail_count)
