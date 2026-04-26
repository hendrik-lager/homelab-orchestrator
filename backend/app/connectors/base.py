from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class HostStatus:
    reachable: bool
    error: str | None = None

@dataclass
class ResourceMetrics:
    cpu_percent: float | None = None
    ram_used_bytes: int | None = None
    ram_total_bytes: int | None = None
    disk_used_bytes: int | None = None
    disk_total_bytes: int | None = None
    load_1m: float | None = None

class BaseConnector(ABC):
    def __init__(self, host_address: str, credentials: dict):
        self.host_address = host_address
        self.credentials = credentials

    @abstractmethod
    async def check_reachability(self) -> HostStatus: ...

    @abstractmethod
    async def get_resources(self) -> ResourceMetrics: ...
