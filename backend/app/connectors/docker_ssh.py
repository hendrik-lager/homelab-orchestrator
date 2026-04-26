import asyncssh
import json
from .base import BaseConnector, HostStatus, ResourceMetrics

class DockerSSHConnector(BaseConnector):
    """
    Docker Engine API via SSH-Tunnel (bevorzugte Methode — kein exponierter Docker Socket).
    credentials: {username: str, private_key: "PEM string"}
    """

    def __init__(self, host_address: str, credentials: dict, port: int = 22):
        super().__init__(host_address, credentials)
        self.port = port

    def _connect_args(self) -> dict:
        key = asyncssh.import_private_key(self.credentials["private_key"])
        return {
            "host": self.host_address,
            "port": self.port,
            "username": self.credentials["username"],
            "client_keys": [key],
            "known_hosts": None,
        }

    async def _docker_api(self, path: str) -> dict | list:
        async with asyncssh.connect(**self._connect_args()) as conn:
            result = await conn.run(
                f'curl -s --unix-socket /var/run/docker.sock http://localhost{path}',
                check=True
            )
            return json.loads(result.stdout)

    async def check_reachability(self) -> HostStatus:
        try:
            await self._docker_api("/info")
            return HostStatus(reachable=True)
        except Exception as e:
            return HostStatus(reachable=False, error=str(e))

    async def get_resources(self) -> ResourceMetrics:
        return ResourceMetrics()

    async def get_containers(self) -> list[dict]:
        return await self._docker_api("/containers/json?all=true")
