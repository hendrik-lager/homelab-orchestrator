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
    from app.services.security_enrichment import enrich_packages_batch

    live: dict[str, dict] = {}

    if host.host_type == "ssh":
        from app.connectors.ssh import SSHConnector
        from app.connectors.apt import AptConnector
        apt = AptConnector(SSHConnector(host.address, creds, host.port or 22))
        raw = await apt.get_upgradable_packages()
        enriched = await enrich_packages_batch(raw, ecosystem="Debian")
        for pkg in enriched:
            live[pkg["name"]] = {
                "update_type": "apt",
                "current_version": pkg["current_version"],
                "available_version": pkg["available_version"],
                "is_security": pkg["is_security"],
                "severity": pkg.get("severity", "none"),
                "cve_ids": pkg.get("cve_ids"),
                "notes": None,
            }

    elif host.host_type == "proxmox":
        from app.connectors.proxmox import ProxmoxConnector
        pve = ProxmoxConnector(host.address, creds, host.port or 8006, host.node_name or "pve")
        raw_pkgs = await pve.get_pve_updates()
        packages = []
        for pkg in raw_pkgs:
            name = pkg.get("Package")
            if not name:
                continue
            # Only use Origin field — pve-* blanket heuristic removed
            hint_is_security = "security" in pkg.get("Origin", "").lower()
            packages.append({
                "name": name,
                "current_version": pkg.get("OldVersion"),
                "available_version": pkg.get("Version"),
                "is_security": hint_is_security,
            })
        enriched = await enrich_packages_batch(packages, ecosystem="Debian")
        for pkg in enriched:
            live[pkg["name"]] = {
                "update_type": "pve",
                "current_version": pkg["current_version"],
                "available_version": pkg.get("available_version"),
                "is_security": pkg["is_security"],
                "severity": pkg.get("severity", "none"),
                "cve_ids": pkg.get("cve_ids"),
                "notes": None,
            }

    elif host.host_type == "homeassistant":
        from app.connectors.homeassistant import HomeAssistantConnector
        ha = HomeAssistantConnector(host.address, creds, host.port or 8123)
        for upd in await ha.get_pending_updates():
            # HA updates are not Debian packages — skip external CVE lookup,
            # rely on the connector's own is_security flag and mark severity accordingly.
            severity = "low" if upd["is_security"] else "none"
            live[upd["entity_id"]] = {
                "update_type": "homeassistant",
                "current_version": upd["installed_version"],
                "available_version": upd["latest_version"],
                "is_security": upd["is_security"],
                "severity": severity,
                "cve_ids": None,
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
            rec.severity = data.get("severity", "none")
            rec.cve_ids = data.get("cve_ids")
            if data["notes"] is not None:
                rec.notes = data["notes"]
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
                severity=data.get("severity", "none"),
                cve_ids=data.get("cve_ids"),
                status="pending",
                detected_at=datetime.utcnow(),
                notes=data["notes"],
            ))
