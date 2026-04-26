from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.host import Host, HostCredential
from app.core.security import encrypt
from app.config import settings

router = APIRouter()

@router.get("/")
async def list_hosts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host))
    return result.scalars().all()

@router.get("/{host_id}")
async def get_host(host_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host

@router.post("/")
async def create_host(data: dict, db: AsyncSession = Depends(get_db)):
    host = Host(
        name=data["name"],
        host_type=data["host_type"],
        address=data["address"],
        port=data.get("port"),
    )
    db.add(host)
    await db.flush()
    if cred_value := data.get("credential_value"):
        cred = HostCredential(
            host_id=host.id,
            cred_type=data.get("cred_type", "api_token"),
            username=data.get("username"),
            encrypted_value=encrypt(cred_value, settings.secret_key),
        )
        db.add(cred)
    await db.commit()
    await db.refresh(host)
    return host

@router.patch("/{host_id}")
async def update_host(host_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    for key, value in data.items():
        if hasattr(host, key):
            setattr(host, key, value)
    await db.commit()
    await db.refresh(host)
    return host

@router.delete("/{host_id}")
async def delete_host(host_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    await db.delete(host)
    await db.commit()
    return {"ok": True}
