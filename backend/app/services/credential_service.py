from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.host import HostCredential
from app.core.security import decrypt
from app.config import settings

async def get_credentials(db: AsyncSession, host_id: int) -> dict:
    result = await db.execute(
        select(HostCredential).where(HostCredential.host_id == host_id)
    )
    creds = result.scalars().all()
    resolved = {}
    for cred in creds:
        value = decrypt(cred.encrypted_value, settings.secret_key)
        resolved[cred.cred_type] = value
        if cred.username:
            resolved["username"] = cred.username
    return resolved
