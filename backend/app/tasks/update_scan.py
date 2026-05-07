import logging
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.update import UpdateRecord
from datetime import datetime

logger = logging.getLogger(__name__)


async def run_update_scan():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()
        for host in hosts:
            await _scan_host(db, host)
        await db.commit()


async def _scan_host(db, host: Host):
    from app.services.credential_service import get_credentials

    try:
        creds = await get_credentials(db, host.id)
        live = await _fetch_live(host, creds)
    except Exception as exc:
        logger.error("Update Scan fehlgeschlagen für Host %s (%s): %s", host.name, host.host_type, exc)
        return

    await _sync_records(db, host.id, live)


async def _fetch_live(host: Host, creds: dict) -> dict[str, dict]:
    """Return {package_name: pkg_data} for all currently available updates on this host."""
    live: dict[str, dict] = {}

    if host.host_type == "ssh":
        from app.connectors.ssh import SSHConnector
        from app.connectors.apt import AptConnector
        apt = AptConnector(SSHConnector(host.address, creds, host.port or 22))
        for pkg in await apt.get_upgradable_packages():
            live[pkg["name"]] = {
                "update_type": "apt",
                "current_version": pkg["current_version"],
                "available_version": pkg["available_version"],
                "is_security": pkg["is_security"],
                "notes": None,
            }

    elif host.host_type == "proxmox":
        from app.connectors.proxmox import ProxmoxConnector
        pve = ProxmoxConnector(host.address, creds, host.port or 8006, host.node_name or "pve")
        for pkg in await pve.get_pve_updates():
            name = pkg.get("Package")
            if not name:
                continue
            is_security = "security" in pkg.get("Origin", "").lower() or name.startswith("pve-")
            live[name] = {
                "update_type": "pve",
                "current_version": pkg.get("OldVersion"),
                "available_version": pkg.get("Version"),
                "is_security": is_security,
                "notes": None,
            }

    elif host.host_type == "homeassistant":
        from app.connectors.homeassistant import HomeAssistantConnector
        ha = HomeAssistantConnector(host.address, creds, host.port or 8123)
        for upd in await ha.get_pending_updates():
            live[upd["entity_id"]] = {
                "update_type": "homeassistant",
                "current_version": upd["installed_version"],
                "available_version": upd["latest_version"],
                "is_security": upd["is_security"],
                "notes": upd["name"],
            }

    return live


async def _sync_records(db, host_id: int, live: dict[str, dict]):
    """
    Reconcile DB records against the live update list:
    - Delete pending/ignored records that are no longer on the system
    - Deduplicate (keep newest) for the same package
    - Add new pending records for packages not yet in DB
    - Update version info for existing records; re-open applied records if a new version appears
    """
    result = await db.execute(select(UpdateRecord).where(UpdateRecord.host_id == host_id))
    all_records = result.scalars().all()

    # Deduplicate: for the same package_name keep only the most recent record
    by_name: dict[str, UpdateRecord] = {}
    for rec in all_records:
        key = rec.package_name or ""
        if key not in by_name:
            by_name[key] = rec
        else:
            # Delete the older duplicate
            older = rec if rec.detected_at <= by_name[key].detected_at else by_name[key]
            newer = by_name[key] if older is rec else rec
            await db.delete(older)
            by_name[key] = newer

    # Remove stale pending/ignored records that are no longer reported by the system
    for name, rec in list(by_name.items()):
        if name not in live and rec.status in ("pending", "ignored"):
            await db.delete(rec)
            del by_name[name]

    # Upsert live packages into DB
    for name, data in live.items():
        if name in by_name:
            rec = by_name[name]
            rec.current_version = data["current_version"]
            rec.available_version = data["available_version"]
            rec.is_security = data["is_security"]
            if data["notes"] is not None:
                rec.notes = data["notes"]
            # Re-open if the system still shows it as available after being marked applied
            if rec.status == "applied":
                rec.status = "pending"
                rec.detected_at = datetime.utcnow()
                rec.applied_at = None
        else:
            db.add(UpdateRecord(
                host_id=host_id,
                update_type=data["update_type"],
                package_name=name,
                current_version=data["current_version"],
                available_version=data["available_version"],
                is_security=data["is_security"],
                status="pending",
                detected_at=datetime.utcnow(),
                notes=data["notes"],
            ))
