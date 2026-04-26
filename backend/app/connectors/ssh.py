import asyncssh
from .base import BaseConnector, HostStatus, ResourceMetrics

class SSHConnector(BaseConnector):
    """
    SSH-Connector via asyncssh.
    credentials: {username: str, private_key: "PEM string"}
    SSH-Keys werden NIEMALS auf Disk geschrieben — nur im RAM via client_keys=[].
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

    async def run(self, command: str) -> tuple[str, str, int]:
        async with asyncssh.connect(**self._connect_args()) as conn:
            result = await conn.run(command, check=False)
            return result.stdout or "", result.stderr or "", result.exit_status

    async def check_reachability(self) -> HostStatus:
        try:
            _, _, code = await self.run("echo ok")
            return HostStatus(reachable=(code == 0))
        except Exception as e:
            return HostStatus(reachable=False, error=str(e))

    async def get_resources(self) -> ResourceMetrics:
        stdout, _, _ = await self.run(
            "cat /proc/loadavg; free -b; df -B1 --output=used,size / | tail -1"
        )
        lines = stdout.strip().splitlines()
        metrics = ResourceMetrics()
        try:
            if lines:
                metrics.load_1m = float(lines[0].split()[0])
            if len(lines) > 1:
                mem = lines[1].split()
                metrics.ram_total_bytes = int(mem[1])
                metrics.ram_used_bytes = int(mem[2])
            if len(lines) > 2:
                disk = lines[2].split()
                metrics.disk_used_bytes = int(disk[0])
                metrics.disk_total_bytes = int(disk[1])
        except (IndexError, ValueError):
            pass
        return metrics
