from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.update import UpdateRecord

router = APIRouter()

@router.get("/")
async def list_updates(
    status: str | None = Query(None),
    update_type: str | None = Query(None),
    is_security: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(UpdateRecord)
    if status:
        query = query.where(UpdateRecord.status == status)
    if update_type:
        query = query.where(UpdateRecord.update_type == update_type)
    if is_security is not None:
        query = query.where(UpdateRecord.is_security == is_security)
    result = await db.execute(query.order_by(UpdateRecord.detected_at.desc()))
    return result.scalars().all()

@router.patch("/{update_id}/status")
async def set_update_status(update_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    result = await db.execute(select(UpdateRecord).where(UpdateRecord.id == update_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404)
    record.status = data["status"]
    await db.commit()
    return {"ok": True}
