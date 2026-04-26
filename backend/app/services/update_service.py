from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.update import UpdateRecord
from datetime import datetime

async def apply_update(db: AsyncSession, update_id: int) -> bool:
    result = await db.execute(select(UpdateRecord).where(UpdateRecord.id == update_id))
    update = result.scalar_one_or_none()

    if not update:
        return False

    update.status = "applied"
    update.applied_at = datetime.utcnow()
    await db.commit()
    return True

async def ignore_update(db: AsyncSession, update_id: int) -> bool:
    result = await db.execute(select(UpdateRecord).where(UpdateRecord.id == update_id))
    update = result.scalar_one_or_none()

    if not update:
        return False

    update.status = "ignored"
    await db.commit()
    return True
