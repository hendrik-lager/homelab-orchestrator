import asyncio
from datetime import datetime
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.host import Host

async def run_health_checks():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()
        await asyncio.gather(*[_check_host(db, host) for host in hosts])
        await db.commit()

async def _check_host(db, host: Host):
    from app.services.credential_service import get_credentials

    try:
        creds = await get_credentials(db, host.id)
        connector = _make_connector(host, creds)
        status = await connector.check_reachability()
        if status.reachable:
            host.last_seen = datetime.utcnow()
        host.last_error = status.error
    except Exception as e:
        host.last_error = str(e)

def _make_connector(host, creds):
    from app.connectors.proxmox import ProxmoxConnector
    from app.connectors.docker_tcp import DockerTCPConnector
    from app.connectors.ssh import SSHConnector
    from app.connectors.homeassistant import HomeAssistantConnector

    match host.host_type:
        case "proxmox":
            return ProxmoxConnector(host.address, creds, host.port or 8006)
        case "docker":
            return DockerTCPConnector(host.address, creds, host.port or 2375)
        case "ssh":
            return SSHConnector(host.address, creds, host.port or 22)
        case "homeassistant":
            return HomeAssistantConnector(host.address, creds, host.port or 8123)
        case _:
            raise ValueError(f"Unknown host_type: {host.host_type}")
