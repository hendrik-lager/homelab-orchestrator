import httpx
from .base import BaseConnector, HostStatus, ResourceMetrics

class DockerTCPConnector(BaseConnector):
    """
    Docker Engine HTTP API via TCP.
    credentials: {tcp_url: "tcp://host:2375"} oder {tcp_url: "tcp://host:2376"} mit TLS
    """

    def __init__(self, host_address: str, credentials: dict, port: int = 2375):
        super().__init__(host_address, credentials)
        tcp_url = credentials.get("tcp_url", f"http://{host_address}:{port}")
        self.base_url = tcp_url.replace("tcp://", "http://")

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def check_reachability(self) -> HostStatus:
        try:
            async with self._client() as client:
                r = await client.get("/info")
                r.raise_for_status()
                return HostStatus(reachable=True)
        except Exception as e:
            return HostStatus(reachable=False, error=str(e))

    async def get_resources(self) -> ResourceMetrics:
        return ResourceMetrics()

    async def get_containers(self) -> list[dict]:
        async with self._client() as client:
            r = await client.get("/containers/json?all=true")
            r.raise_for_status()
            return r.json()

    async def get_container_stats(self, container_id: str) -> dict:
        async with self._client() as client:
            r = await client.get(f"/containers/{container_id}/stats?stream=false")
            r.raise_for_status()
            return r.json()
