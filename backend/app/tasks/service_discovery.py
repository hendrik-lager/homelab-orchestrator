from datetime import datetime
from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.service import Service


async def run_service_discovery():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()
        for host in hosts:
            await _discover_host(db, host)
        await db.commit()


async def _discover_host(db, host: Host):
    from app.services.credential_service import get_credentials

    try:
        creds = await get_credentials(db, host.id)

        if host.host_type == "homeassistant":
            from app.connectors.homeassistant import HomeAssistantConnector
            ha = HomeAssistantConnector(host.address, creds, host.port or 8123)
            addons = await ha.get_addons()
            await _upsert_services(db, host.id, "addon", addons, slug_key="slug")

        elif host.host_type == "docker":
            from app.connectors.docker_tcp import DockerTCPConnector
            docker = DockerTCPConnector(host.address, creds, host.port or 2375)
            containers = await docker.get_containers()
            normalized = [
                {
                    "slug": c["Id"][:12],
                    "name": (c.get("Names") or [c["Id"][:12]])[0].lstrip("/"),
                    "state": c.get("State", "unknown"),
                    "version": c.get("Image"),
                }
                for c in containers
            ]
            await _upsert_services(db, host.id, "container", normalized, slug_key="slug")

    except Exception:
        pass


async def _upsert_services(db, host_id: int, service_type: str, items: list[dict], slug_key: str):
    seen_ids: set[str] = set()

    for item in items:
        external_id = item[slug_key]
        seen_ids.add(external_id)

        result = await db.execute(
            select(Service).where(
                and_(Service.host_id == host_id, Service.external_id == external_id)
            )
        )
        service = result.scalar_one_or_none()

        ha_state = item.get("state", "unknown")
        status = "running" if ha_state == "started" else ("stopped" if ha_state == "stopped" else ha_state)

        if service is None:
            db.add(Service(
                host_id=host_id,
                name=item["name"],
                service_type=service_type,
                external_id=external_id,
                image=item.get("version"),
                status=status,
                last_checked=datetime.utcnow(),
            ))
        else:
            service.status = status
            service.image = item.get("version")
            service.last_checked = datetime.utcnow()

    # Mark services no longer returned by the API as "removed"
    result = await db.execute(
        select(Service).where(
            and_(Service.host_id == host_id, Service.service_type == service_type)
        )
    )
    for service in result.scalars().all():
        if service.external_id not in seen_ids:
            service.status = "removed"
            service.last_checked = datetime.utcnow()
