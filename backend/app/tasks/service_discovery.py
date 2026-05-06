import logging
from datetime import datetime
from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.service import Service

logger = logging.getLogger(__name__)


async def run_service_discovery():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()

        errors: list[str] = []
        for host in hosts:
            error = await _discover_host(db, host)
            if error:
                errors.append(f"{host.name}: {error}")

        await db.commit()

        if errors:
            raise RuntimeError("; ".join(errors))


async def _discover_host(db, host: Host) -> str | None:
    """Returns an error message on failure, None on success."""
    from app.services.credential_service import get_credentials

    try:
        creds = await get_credentials(db, host.id)

        if host.host_type == "homeassistant":
            from app.connectors.homeassistant import HomeAssistantConnector
            ha = HomeAssistantConnector(host.address, creds, host.port or 8123)
            addons = await ha.get_addons()
            logger.info("Host %s: %d Add-on(s) gefunden", host.name, len(addons))
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
            logger.info("Host %s: %d Container gefunden", host.name, len(normalized))
            await _upsert_services(db, host.id, "container", normalized, slug_key="slug")

        return None

    except Exception as exc:
        logger.error("Service Discovery fehlgeschlagen für Host %s: %s", host.name, exc)
        return str(exc)


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

    result = await db.execute(
        select(Service).where(
            and_(Service.host_id == host_id, Service.service_type == service_type)
        )
    )
    for service in result.scalars().all():
        if service.external_id not in seen_ids:
            service.status = "removed"
            service.last_checked = datetime.utcnow()
