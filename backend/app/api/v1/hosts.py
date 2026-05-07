from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.host import Host, HostCredential
from app.core.security import encrypt, decrypt
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

    cred_result = await db.execute(
        select(HostCredential).where(HostCredential.host_id == host_id)
    )
    creds = cred_result.scalars().all()

    cred_meta: dict = {"has_secret": False}
    for cred in creds:
        if cred.cred_type == "token_id":
            cred_meta["token_id"] = decrypt(cred.encrypted_value, settings.secret_key)
        elif cred.cred_type == "token_secret":
            cred_meta["has_secret"] = True
        else:
            cred_meta["cred_type"] = cred.cred_type
            if cred.username:
                cred_meta["username"] = cred.username
            cred_meta["has_secret"] = True

    return {
        "id": host.id,
        "name": host.name,
        "host_type": host.host_type,
        "address": host.address,
        "port": host.port,
        "node_name": host.node_name,
        "enabled": host.enabled,
        "last_seen": host.last_seen,
        "last_error": host.last_error,
        "created_at": host.created_at,
        "updated_at": host.updated_at,
        **cred_meta,
    }

@router.post("/")
async def create_host(data: dict, db: AsyncSession = Depends(get_db)):
    host = Host(
        name=data["name"],
        host_type=data["host_type"],
        address=data["address"],
        port=data.get("port"),
        node_name=data.get("node_name"),
    )
    db.add(host)
    await db.flush()
    if data.get("host_type") == "proxmox":
        if token_id := data.get("token_id"):
            db.add(HostCredential(
                host_id=host.id,
                cred_type="token_id",
                encrypted_value=encrypt(token_id, settings.secret_key),
            ))
        if token_secret := data.get("token_secret"):
            db.add(HostCredential(
                host_id=host.id,
                cred_type="token_secret",
                encrypted_value=encrypt(token_secret, settings.secret_key),
            ))
    elif cred_value := data.get("credential_value"):
        db.add(HostCredential(
            host_id=host.id,
            cred_type=data.get("cred_type", "api_token"),
            username=data.get("username"),
            encrypted_value=encrypt(cred_value, settings.secret_key),
        ))
    await db.commit()
    await db.refresh(host)
    return host

@router.patch("/{host_id}")
async def update_host(host_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")

    host_fields = {"name", "host_type", "address", "port", "node_name", "enabled"}
    for key, value in data.items():
        if key in host_fields:
            setattr(host, key, value)

    if data.get("host_type") == "proxmox" or host.host_type == "proxmox":
        if token_id := data.get("token_id"):
            cred_result = await db.execute(
                select(HostCredential).where(
                    HostCredential.host_id == host_id,
                    HostCredential.cred_type == "token_id",
                )
            )
            existing = cred_result.scalar_one_or_none()
            if existing:
                existing.encrypted_value = encrypt(token_id, settings.secret_key)
            else:
                db.add(HostCredential(host_id=host_id, cred_type="token_id", encrypted_value=encrypt(token_id, settings.secret_key)))

        if token_secret := data.get("token_secret"):
            cred_result = await db.execute(
                select(HostCredential).where(
                    HostCredential.host_id == host_id,
                    HostCredential.cred_type == "token_secret",
                )
            )
            existing = cred_result.scalar_one_or_none()
            if existing:
                existing.encrypted_value = encrypt(token_secret, settings.secret_key)
            else:
                db.add(HostCredential(host_id=host_id, cred_type="token_secret", encrypted_value=encrypt(token_secret, settings.secret_key)))
    else:
        if cred_value := data.get("credential_value"):
            cred_type = data.get("cred_type", "api_token")
            username = data.get("username") or None
            cred_result = await db.execute(
                select(HostCredential).where(HostCredential.host_id == host_id)
            )
            existing = cred_result.scalar_one_or_none()
            if existing:
                existing.cred_type = cred_type
                existing.username = username
                existing.encrypted_value = encrypt(cred_value, settings.secret_key)
            else:
                db.add(HostCredential(host_id=host_id, cred_type=cred_type, username=username, encrypted_value=encrypt(cred_value, settings.secret_key)))

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
