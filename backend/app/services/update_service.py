import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.update import UpdateRecord
from app.models.host import Host

logger = logging.getLogger(__name__)


async def apply_update(db: AsyncSession, update_id: int) -> tuple[bool, str]:
    result = await db.execute(select(UpdateRecord).where(UpdateRecord.id == update_id))
    update = result.scalar_one_or_none()
    if not update:
        return False, "Update nicht gefunden"

    host_result = await db.execute(select(Host).where(Host.id == update.host_id))
    host = host_result.scalar_one_or_none()
    if not host:
        return False, "Host nicht gefunden"

    from app.services.credential_service import get_credentials
    creds = await get_credentials(db, host.id)

    ok, output = await _execute_install(host, creds, update)
    if ok:
        update.status = "applied"
        update.applied_at = datetime.utcnow()
        await db.commit()
    return ok, output


async def _execute_install(host: Host, creds: dict, update: UpdateRecord) -> tuple[bool, str]:
    if host.host_type == "ssh":
        from app.connectors.ssh import SSHConnector
        from app.connectors.apt import AptConnector
        ssh = SSHConnector(host.address, creds, host.port or 22)
        apt = AptConnector(ssh)
        packages = [update.package_name] if update.package_name else None
        return await apt.install_packages(packages)

    if host.host_type == "proxmox":
        private_key = creds.get("private_key")
        username = creds.get("username")
        if not private_key or not username:
            return False, "SSH-Credentials (private_key + username) für Proxmox-Installation benötigt"
        from app.connectors.proxmox import ProxmoxConnector
        pve = ProxmoxConnector(host.address, creds, host.port or 8006, host.node_name or "pve")
        packages = [update.package_name] if update.package_name else None
        return await pve.install_pve_updates(username, private_key, packages)

    if host.host_type == "homeassistant":
        entity_id = update.package_name
        if not entity_id:
            return False, "Keine entity_id für dieses Update gespeichert"
        from app.connectors.homeassistant import HomeAssistantConnector
        ha = HomeAssistantConnector(host.address, creds, host.port or 8123)
        return await ha.apply_update(entity_id)

    return False, f"Unbekannter host_type: {host.host_type}"


_SEVERITY_ORDER = ["critical", "high", "medium", "low", "none"]


async def apply_all_pending(
    db: AsyncSession,
    security_only: bool = False,
    min_severity: str | None = None,
) -> list[dict]:
    query = select(UpdateRecord).where(UpdateRecord.status == "pending")
    if min_severity and min_severity in _SEVERITY_ORDER:
        allowed = _SEVERITY_ORDER[: _SEVERITY_ORDER.index(min_severity) + 1]
        query = query.where(UpdateRecord.severity.in_(allowed))
    elif security_only:
        query = query.where(UpdateRecord.is_security == True)
    result = await db.execute(query)
    updates = result.scalars().all()

    results = []
    for update in updates:
        try:
            ok, output = await apply_update(db, update.id)
            results.append({"id": update.id, "ok": ok, "output": output})
        except Exception as exc:
            logger.exception("Fehler bei Update %s", update.id)
            results.append({"id": update.id, "ok": False, "output": str(exc)})
    return results


async def ignore_update(db: AsyncSession, update_id: int) -> bool:
    result = await db.execute(select(UpdateRecord).where(UpdateRecord.id == update_id))
    update = result.scalar_one_or_none()
    if not update:
        return False
    update.status = "ignored"
    await db.commit()
    return True
