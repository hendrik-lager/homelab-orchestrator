from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.update import UpdateRecord
from datetime import datetime

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

        if host.host_type == "ssh":
            from app.connectors.ssh import SSHConnector
            from app.connectors.apt import AptConnector
            ssh = SSHConnector(host.address, creds, host.port or 22)
            apt = AptConnector(ssh)
            packages = await apt.get_upgradable_packages()
            for pkg in packages:
                record = UpdateRecord(
                    host_id=host.id,
                    update_type="apt",
                    package_name=pkg["name"],
                    current_version=pkg["current_version"],
                    available_version=pkg["available_version"],
                    is_security=pkg["is_security"],
                    status="pending",
                    detected_at=datetime.utcnow(),
                )
                db.add(record)

        elif host.host_type == "proxmox":
            from app.connectors.proxmox import ProxmoxConnector
            pve = ProxmoxConnector(host.address, creds, host.port or 8006)
            updates = await pve.get_pve_updates()
            for pkg in updates:
                is_security = "security" in pkg.get("origin", "").lower() or pkg.get("package", "").startswith("pve-")
                record = UpdateRecord(
                    host_id=host.id,
                    update_type="pve",
                    package_name=pkg.get("package"),
                    current_version=pkg.get("OldVersion"),
                    available_version=pkg.get("Version"),
                    is_security=is_security,
                    status="pending",
                    detected_at=datetime.utcnow(),
                )
                db.add(record)

        elif host.host_type == "homeassistant":
            from app.connectors.homeassistant import HomeAssistantConnector
            ha = HomeAssistantConnector(host.address, creds, host.port or 8123)
            updates = await ha.get_pending_updates()
            for upd in updates:
                record = UpdateRecord(
                    host_id=host.id,
                    update_type="homeassistant",
                    package_name=upd["name"],
                    current_version=upd["installed_version"],
                    available_version=upd["latest_version"],
                    is_security=upd["is_security"],
                    status="pending",
                    detected_at=datetime.utcnow(),
                )
                db.add(record)

    except Exception:
        pass
