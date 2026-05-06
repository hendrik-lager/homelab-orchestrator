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
                    updates.append({
                        "entity_id": state["entity_id"],
                        "name": attrs.get("friendly_name", state["entity_id"]),
                        "installed_version": attrs.get("installed_version"),
                        "latest_version": attrs.get("latest_version"),
                        "is_security": "security" in release_notes.lower(),
                    })
            return updates

    async def get_addons(self) -> list[dict]:
        """Fetch add-ons via Supervisor API. Raises on non-supervised or unauthorized installs."""
        async with self._client() as client:
            r = await client.get("/api/hassio/addons")
            if r.status_code == 401:
                raise PermissionError(
                    "Supervisor API: Zugriff verweigert (401). "
                    "Bitte einen Long-Lived Access Token mit Supervisor-Berechtigung verwenden."
                )
            if r.status_code == 404:
                raise RuntimeError(
                    "Supervisor API nicht gefunden (404). "
                    "Diese HA-Installation unterstützt keine Add-on-Discovery "
                    "(nur HAOS / HA Supervised)."
                )
            r.raise_for_status()

            payload = r.json()
            logger.debug("Supervisor /api/hassio/addons response: %s", payload)

            # The proxy wraps the response: {"result": "ok", "data": {"addons": [...]}}
            addons_raw = payload.get("data", {}).get("addons")
            if addons_raw is None:
                # Some versions return the list directly
                addons_raw = payload if isinstance(payload, list) else []

            return [
                {
                    "slug": addon["slug"],
                    "name": addon.get("name", addon["slug"]),
                    "state": addon.get("state", "unknown"),
                    "version": addon.get("version"),
                }
                for addon in addons_raw
                if "slug" in addon
            ]
