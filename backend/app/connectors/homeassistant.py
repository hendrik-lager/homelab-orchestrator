import logging
import httpx
from .base import BaseConnector, HostStatus, ResourceMetrics

logger = logging.getLogger(__name__)

class HomeAssistantConnector(BaseConnector):
    """
    Home Assistant REST API.
    credentials: {bearer_token: "Long-Lived Access Token"}
    Updates via update.* Entities: state='on' = Update verfügbar.
    """

    def __init__(self, host_address: str, credentials: dict, port: int = 8123):
        super().__init__(host_address, credentials)
        self.base_url = f"http://{host_address}:{port}"
        token = credentials.get("bearer_token")
        if not token:
            raise ValueError("Kein Bearer Token konfiguriert. Bitte Credential vom Typ 'bearer_token' hinzufügen.")
        self.headers = {"Authorization": f"Bearer {token}"}

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=10.0)

    async def check_reachability(self) -> HostStatus:
        try:
            async with self._client() as client:
                r = await client.get("/api/")
                r.raise_for_status()
                return HostStatus(reachable=True)
        except Exception as e:
            return HostStatus(reachable=False, error=str(e))

    async def get_resources(self) -> ResourceMetrics:
        return ResourceMetrics()

    async def apply_update(self, entity_id: str) -> tuple[bool, str]:
        """Trigger update installation via HA service call.

        Accepts both a proper entity_id ("update.xxx") and old records that
        stored the friendly name — the latter are resolved via /api/states.
        """
        actual = entity_id if entity_id.startswith("update.") else await self._resolve_entity_by_name(entity_id)
        if actual is None:
            return False, (
                f"Keine HA-Entity für '{entity_id}' gefunden. "
                "Bitte den Update-Scan erneut ausführen, damit entity_ids aktualisiert werden."
            )

        async with self._client() as client:
            r = await client.post(
                "/api/services/update/install",
                json={"entity_id": actual},
            )
            if r.status_code in (200, 201):
                return True, f"Update für {actual} gestartet"
            return False, f"HTTP {r.status_code}: {r.text}"

    async def _resolve_entity_by_name(self, friendly_name: str) -> str | None:
        """Look up entity_id by friendly_name from /api/states."""
        async with self._client() as client:
            r = await client.get("/api/states")
            if r.status_code != 200:
                return None
            for state in r.json():
                if not state["entity_id"].startswith("update."):
                    continue
                if state.get("attributes", {}).get("friendly_name") == friendly_name:
                    return state["entity_id"]
        return None

    async def get_pending_updates(self) -> list[dict]:
        async with self._client() as client:
            r = await client.get("/api/states")
            r.raise_for_status()
            states = r.json()
            updates = []
            for state in states:
                if state["entity_id"].startswith("update.") and state["state"] == "on":
                    attrs = state.get("attributes", {})
                    release_notes = attrs.get("release_notes") or ""
                    # HA 2023.6+ sets release_summary with a direct security flag;
                    # older versions only expose release_notes free text.
                    is_security = (
                        attrs.get("skipped_version") is None  # not user-skipped
                        and (
                            bool(attrs.get("release_summary", {}).get("security"))
                            or "security" in release_notes.lower()
                        )
                    )
                    updates.append({
                        "entity_id": state["entity_id"],
                        "name": attrs.get("friendly_name", state["entity_id"]),
                        "installed_version": attrs.get("installed_version"),
                        "latest_version": attrs.get("latest_version"),
                        "is_security": is_security,
                    })
            return updates

    async def get_addons(self) -> list[dict]:
        """Discover installed add-ons via update.* entities from /api/states.

        The Supervisor REST API requires an internal token that long-lived access
        tokens from the UI cannot provide. Instead, every installed add-on in modern
        HA (2022+) exposes an update.* entity whose entity_picture URL contains the
        add-on slug: /api/hassio/addons/{slug}/icon.
        """
        async with self._client() as client:
            r = await client.get("/api/states")
            r.raise_for_status()
            states = r.json()

        addons: list[dict] = []
        for state in states:
            if not state["entity_id"].startswith("update."):
                continue
            attrs = state.get("attributes", {})

            # Extract slug from entity_picture, e.g. /api/hassio/addons/core_mosquitto/icon
            picture = attrs.get("entity_picture", "")
            slug = _slug_from_picture(picture)
            if slug is None:
                continue  # not a Supervisor add-on (e.g. HACS, HA Core, OS updates)

            addons.append({
                "slug": slug,
                "name": attrs.get("title") or attrs.get("friendly_name") or state["entity_id"],
                "state": "started",
                "version": attrs.get("installed_version"),
            })

        return addons


def _slug_from_picture(url: str) -> str | None:
    """Return the add-on slug from a Supervisor icon URL, or None if not a Supervisor URL."""
    marker = "/api/hassio/addons/"
    idx = url.find(marker)
    if idx == -1:
        return None
    after = url[idx + len(marker):]
    slug = after.split("/")[0]
    return slug or None
