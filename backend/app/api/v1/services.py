from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.service import Service, ServiceCheck

router = APIRouter()

@router.get("/")
async def list_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service))
    return result.scalars().all()

@router.get("/{service_id}")
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/")
async def create_service(data: dict, db: AsyncSession = Depends(get_db)):
    service = Service(
        host_id=data["host_id"],
        name=data["name"],
        service_type=data["service_type"],
        external_id=data.get("external_id"),
        image=data.get("image"),
        status=data.get("status", "unknown"),
        labels=data.get("labels"),
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service

@router.patch("/{service_id}")
async def update_service(service_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    for key, value in data.items():
        if hasattr(service, key):
            setattr(service, key, value)
    await db.commit()
    await db.refresh(service)
    return service

@router.delete("/{service_id}")
async def delete_service(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.delete(service)
    await db.commit()
    return {"ok": True}
