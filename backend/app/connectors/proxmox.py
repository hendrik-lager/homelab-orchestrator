import asyncio
import httpx
from .base import BaseConnector, HostStatus, ResourceMetrics

class ProxmoxConnector(BaseConnector):
    """
    Proxmox VE REST API v2.
    credentials: {token_id: "user@realm!token-name", token_secret: "uuid"}
    """

    def __init__(self, host_address: str, credentials: dict, port: int = 8006):
        super().__init__(host_address, credentials)
        self.base_url = f"https://{host_address}:{port}/api2/json"
        self.headers = {
            "Authorization": f"PVEAPIToken={credentials['token_id']}={credentials['token_secret']}"
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            verify=False,
            timeout=10.0,
        )

    async def check_reachability(self) -> HostStatus:
        try:
            async with self._client() as client:
                r = await client.get("/nodes")
                r.raise_for_status()
                return HostStatus(reachable=True)
        except Exception as e:
            return HostStatus(reachable=False, error=str(e))

    async def get_resources(self) -> ResourceMetrics:
        async with self._client() as client:
            r = await client.get("/nodes/pve/status")
            r.raise_for_status()
            d = r.json()["data"]
            return ResourceMetrics(
                cpu_percent=round(d.get("cpu", 0) * 100, 1),
                ram_used_bytes=d.get("memory", {}).get("used"),
                ram_total_bytes=d.get("memory", {}).get("total"),
                disk_used_bytes=d.get("rootfs", {}).get("used"),
                disk_total_bytes=d.get("rootfs", {}).get("total"),
                load_1m=d.get("loadavg", [None])[0],
            )

    async def get_lxc_list(self) -> list[dict]:
        async with self._client() as client:
            r = await client.get("/nodes/pve/lxc")
            r.raise_for_status()
            return r.json()["data"]

    async def get_vm_list(self) -> list[dict]:
        async with self._client() as client:
            r = await client.get("/nodes/pve/qemu")
            r.raise_for_status()
            return r.json()["data"]

    async def get_pve_updates(self) -> list[dict]:
        """
        Triggert apt-Update via API-Task, wartet, liest dann verfügbare Pakete.
        Security-Updates: packages mit Origin 'debian-security' oder 'pve-*' prefix.
        """
        async with self._client() as client:
            r = await client.post("/nodes/pve/apt/update")
            r.raise_for_status()
            upid = r.json()["data"]
            for _ in range(30):
                status_r = await client.get(f"/nodes/pve/tasks/{upid}/status")
                if status_r.json()["data"].get("status") == "stopped":
                    break
                await asyncio.sleep(2)
            updates_r = await client.get("/nodes/pve/apt/update")
            updates_r.raise_for_status()
            return updates_r.json()["data"]
