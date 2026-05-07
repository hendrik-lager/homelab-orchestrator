import asyncio
import httpx
from .base import BaseConnector, HostStatus, ResourceMetrics

class ProxmoxConnector(BaseConnector):
    """
    Proxmox VE REST API v2.
    credentials: {token_id: "user@realm!token-name", token_secret: "uuid"}
    """

    def __init__(self, host_address: str, credentials: dict, port: int = 8006, node_name: str = "pve"):
        super().__init__(host_address, credentials)
        self.base_url = f"https://{host_address}:{port}/api2/json"
        self.node = node_name
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
            r = await client.get(f"/nodes/{self.node}/status")
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
            r = await client.get(f"/nodes/{self.node}/lxc")
            r.raise_for_status()
            return r.json()["data"]

    async def get_vm_list(self) -> list[dict]:
        async with self._client() as client:
            r = await client.get(f"/nodes/{self.node}/qemu")
            r.raise_for_status()
            return r.json()["data"]

    async def install_pve_updates(self, username: str, private_key: str, packages: list[str] | None = None) -> tuple[bool, str]:
        """Install PVE updates via SSH using pveupgrade or apt-get dist-upgrade."""
        import asyncssh
        key = asyncssh.import_private_key(private_key)
        connect_args = {
            "host": self.host_address,
            "port": 22,
            "username": username,
            "client_keys": [key],
            "known_hosts": None,
        }
        if packages:
            pkgs = " ".join(packages)
            cmd = f"DEBIAN_FRONTEND=noninteractive apt-get install --only-upgrade -y {pkgs} 2>&1"
        else:
            cmd = "DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y 2>&1"
        async with asyncssh.connect(**connect_args) as conn:
            result = await conn.run(cmd, check=False)
            output = (result.stdout or "") + (result.stderr or "")
            return result.exit_status == 0, output

    async def get_pve_updates(self) -> list[dict]:
        """
        Triggert apt-Update via API-Task, wartet, liest dann verfügbare Pakete.
        Security-Updates: packages mit Origin 'debian-security' oder 'pve-*' prefix.
        """
        async with self._client() as client:
            r = await client.post(f"/nodes/{self.node}/apt/update")
            r.raise_for_status()
            upid = r.json()["data"]
            for _ in range(30):
                status_r = await client.get(f"/nodes/{self.node}/tasks/{upid}/status")
                status_r.raise_for_status()
                task_data = status_r.json()["data"]
                if task_data.get("status") == "stopped":
                    if task_data.get("exitstatus") != "OK":
                        raise RuntimeError(f"apt update task failed: {task_data.get('exitstatus')}")
                    break
                await asyncio.sleep(2)
            updates_r = await client.get(f"/nodes/{self.node}/apt/update")
            updates_r.raise_for_status()
            return updates_r.json()["data"]
