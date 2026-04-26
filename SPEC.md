# HomeLab Orchestrator — Vollständige Implementierungsspezifikation

## Projektziel

Entwickle eine vollständige WebApp zur Verwaltung eines Home Labs. Die App soll:
- Verfügbare Updates (Sicherheitsupdates, Docker-Images, OS-Pakete) automatisch erkennen
- Den Status aller Services und Hosts in Echtzeit überwachen
- Ein zentrales Dashboard mit Ressourcenauslastung bieten
- Updates und Monitoring-Tasks automatisiert ausführen
- Bei Ausfällen oder neuen Security-Updates per E-Mail benachrichtigen

Die App läuft als **LXC Container auf einem einzelnen Proxmox-Node** und verwaltet:
- Docker/Compose Hosts (remote via TCP oder SSH)
- Proxmox VE selbst (via Proxmox REST API)
- Debian/Ubuntu VMs und LXCs (via SSH + apt)
- Home Assistant (via Supervisor/States API)

---

## Tech Stack (nicht verhandelbar)

| Schicht | Technologie | Version |
|---|---|---|
| Backend | Python + FastAPI | 3.12 / 0.115+ |
| Frontend | SvelteKit + Svelte 5 | 2.x / 5.x |
| CSS | Tailwind CSS | v4 (CSS-first, kein JS-Config) |
| Datenbank | SQLite (async) | via aiosqlite + SQLAlchemy 2.0 |
| Migrations | Alembic | 1.14+ |
| Scheduler | APScheduler | 4.x (async-native) |
| SSH | asyncssh | 2.19+ |
| HTTP Client | httpx | 0.28+ (async) |
| Secrets | Fernet (cryptography) | 44+ |
| Konfiguration | pydantic-settings | 2.6+ |
| E-Mail | aiosmtplib | 3.0+ |
| Package Mgr | uv (Python), npm (Node) | latest |
| Deploy | systemd + Nginx | im LXC |
| Frontend SPA | @sveltejs/adapter-node | SSR=false |

---

## Vollständige Projektstruktur

Erstelle EXAKT diese Verzeichnisstruktur (alle Dateien, alle Verzeichnisse):

```
homelab-orchestrator/
├── Makefile
├── CLAUDE.md
├── SPEC.md                           ← Diese Datei
│
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial.py
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── dependencies.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── host.py
│       │   ├── service.py
│       │   ├── update.py
│       │   ├── alert.py
│       │   ├── snapshot.py
│       │   └── job.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── host.py
│       │   ├── service.py
│       │   ├── update.py
│       │   ├── alert.py
│       │   ├── dashboard.py
│       │   └── job.py
│       │
│       ├── api/
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py
│       │       ├── hosts.py
│       │       ├── services.py
│       │       ├── updates.py
│       │       ├── dashboard.py
│       │       ├── alerts.py
│       │       ├── jobs.py
│       │       └── websocket.py
│       │
│       ├── connectors/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── proxmox.py
│       │   ├── docker_tcp.py
│       │   ├── docker_ssh.py
│       │   ├── ssh.py
│       │   ├── apt.py
│       │   ├── homeassistant.py
│       │   └── registry.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── monitor_service.py
│       │   ├── update_service.py
│       │   ├── alert_service.py
│       │   ├── notification.py
│       │   └── credential_service.py
│       │
│       ├── tasks/
│       │   ├── __init__.py
│       │   ├── scheduler.py
│       │   ├── health_check.py
│       │   ├── update_scan.py
│       │   ├── metric_collector.py
│       │   └── cleanup.py
│       │
│       └── core/
│           ├── __init__.py
│           ├── security.py
│           ├── logging.py
│           └── events.py
│
├── frontend/
│   ├── package.json
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── postcss.config.js
│   └── src/
│       ├── app.html
│       ├── app.css
│       ├── lib/
│       │   ├── api/
│       │   │   ├── client.ts
│       │   │   ├── hosts.ts
│       │   │   ├── services.ts
│       │   │   ├── updates.ts
│       │   │   ├── dashboard.ts
│       │   │   └── jobs.ts
│       │   ├── stores/
│       │   │   ├── hosts.svelte.ts
│       │   │   ├── services.svelte.ts
│       │   │   ├── updates.svelte.ts
│       │   │   ├── alerts.svelte.ts
│       │   │   └── websocket.svelte.ts
│       │   └── components/
│       │       ├── layout/
│       │       │   ├── Sidebar.svelte
│       │       │   ├── Topbar.svelte
│       │       │   └── PageWrapper.svelte
│       │       ├── ui/
│       │       │   ├── Badge.svelte
│       │       │   ├── Card.svelte
│       │       │   ├── DataTable.svelte
│       │       │   ├── Modal.svelte
│       │       │   ├── Toast.svelte
│       │       │   ├── Spinner.svelte
│       │       │   └── StatusDot.svelte
│       │       ├── dashboard/
│       │       │   ├── SummaryBar.svelte
│       │       │   ├── HostCard.svelte
│       │       │   ├── ServiceCard.svelte
│       │       │   └── ResourceGauge.svelte
│       │       ├── updates/
│       │       │   ├── UpdateTable.svelte
│       │       │   ├── ApplyUpdateModal.svelte
│       │       │   └── SecurityBadge.svelte
│       │       ├── hosts/
│       │       │   ├── HostForm.svelte
│       │       │   └── CredentialForm.svelte
│       │       └── alerts/
│       │           ├── AlertList.svelte
│       │           └── AlertRuleForm.svelte
│       └── routes/
│           ├── +layout.svelte
│           ├── +layout.ts
│           ├── +page.svelte
│           ├── dashboard/
│           │   └── +page.svelte
│           ├── hosts/
│           │   ├── +page.svelte
│           │   └── [id]/
│           │       └── +page.svelte
│           ├── updates/
│           │   └── +page.svelte
│           ├── services/
│           │   └── +page.svelte
│           ├── alerts/
│           │   └── +page.svelte
│           └── settings/
│               └── +page.svelte
│
├── deployment/
│   ├── install.sh
│   ├── homelab-orchestrator.service
│   ├── nginx.conf
│   └── lxc-config.conf
│
└── dev/
    ├── docker-compose.yml
    └── seed.py
```

---

## Backend: Detaillierte Implementierung

### `backend/pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "homelab-orchestrator"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "sqlalchemy[asyncio]>=2.0",
    "aiosqlite>=0.20",
    "alembic>=1.14",
    "pydantic-settings>=2.6",
    "httpx>=0.28",
    "asyncssh>=2.19",
    "apscheduler>=4.0",
    "cryptography>=44",
    "aiosmtplib>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.24",
    "ruff>=0.8",
    "mypy>=1.13",
]
```

### `backend/app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/homelab.db"

    # Encryption
    secret_key: str  # 32-byte Fernet key, generated on first run

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    alert_from_email: str = ""
    alert_to_emails: list[str] = []

    # App
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"

    # Scheduler intervals
    health_check_interval_seconds: int = 60
    update_scan_interval_seconds: int = 3600
    metric_collect_interval_seconds: int = 60

settings = Settings()
```

### `backend/app/main.py` — FastAPI App mit lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.tasks.scheduler import scheduler, register_tasks
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + start scheduler
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    register_tasks()
    await scheduler.start()
    yield
    # Shutdown
    await scheduler.shutdown()

app = FastAPI(title="HomeLab Orchestrator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # dev; prod: LXC IP only
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
```

### `backend/app/database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)

from sqlalchemy import event

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-32000")
    cursor.close()

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### `backend/app/core/security.py` — Fernet Encryption

```python
from cryptography.fernet import Fernet

def get_fernet(secret_key: str) -> Fernet:
    key = secret_key.encode() if isinstance(secret_key, str) else secret_key
    return Fernet(key)

def encrypt(value: str, secret_key: str) -> str:
    f = get_fernet(secret_key)
    return f.encrypt(value.encode()).decode()

def decrypt(encrypted: str, secret_key: str) -> str:
    f = get_fernet(secret_key)
    return f.decrypt(encrypted.encode()).decode()
```

---

## Datenbank-Models (SQLAlchemy 2.0 Mapped-Style)

### `backend/app/models/host.py`

```python
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Host(Base):
    __tablename__ = "hosts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    host_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # host_type: 'proxmox' | 'docker' | 'ssh' | 'homeassistant'
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    credentials: Mapped[list["HostCredential"]] = relationship(back_populates="host", cascade="all, delete-orphan")
    services: Mapped[list["Service"]] = relationship(back_populates="host", cascade="all, delete-orphan")

class HostCredential(Base):
    __tablename__ = "host_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"))
    cred_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # cred_type: 'api_token' | 'ssh_key' | 'ssh_password' | 'bearer_token'
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    encrypted_value: Mapped[str] = mapped_column(String(4096), nullable=False)
    key_fingerprint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    host: Mapped["Host"] = relationship(back_populates="credentials")
```

### `backend/app/models/service.py`

```python
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # service_type: 'container' | 'lxc' | 'vm' | 'compose_service' | 'ha_addon'
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    # status: 'running' | 'stopped' | 'paused' | 'error' | 'unknown'
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_checked: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    labels: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    host: Mapped["Host"] = relationship(back_populates="services")
    checks: Mapped[list["ServiceCheck"]] = relationship(back_populates="service", cascade="all, delete-orphan")

class ServiceCheck(Base):
    __tablename__ = "service_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"))
    checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    service: Mapped["Service"] = relationship(back_populates="checks")
```

### `backend/app/models/update.py`

```python
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class UpdateRecord(Base):
    __tablename__ = "update_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"))
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    update_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # update_type: 'apt' | 'docker_image' | 'pve' | 'homeassistant'
    package_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    current_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    available_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_security: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    # status: 'pending' | 'applied' | 'ignored' | 'failed'
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
```

### `backend/app/models/snapshot.py`

```python
from datetime import datetime
from sqlalchemy import DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    cpu_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    ram_used_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ram_total_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_used_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    disk_total_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    load_1m: Mapped[float | None] = mapped_column(Float, nullable=True)
```

### `backend/app/models/alert.py`

```python
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    host_id: Mapped[int | None] = mapped_column(ForeignKey("hosts.id", ondelete="SET NULL"), nullable=True)
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # alert_type: 'service_down' | 'security_update' | 'resource_high' | 'host_unreachable'
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    # severity: 'critical' | 'high' | 'medium' | 'low'
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="firing")
    # status: 'firing' | 'resolved' | 'silenced'
    fired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)

class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # rule_type: 'service_down' | 'security_update' | 'resource_threshold'
    host_id: Mapped[int | None] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), nullable=True)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

### `backend/app/models/job.py`

```python
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # job_type: 'update_scan' | 'health_check' | 'apply_updates' | 'custom'
    host_id: Mapped[int | None] = mapped_column(ForeignKey("hosts.id", ondelete="CASCADE"), nullable=True)
    cron_expression: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    next_run: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
```

---

## Connectors: Detaillierte Implementierung

### `backend/app/connectors/base.py`

```python
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
```

### `backend/app/connectors/proxmox.py`

```python
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
            verify=False,  # Proxmox nutzt self-signed certs
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
```

### `backend/app/connectors/ssh.py`

```python
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
            "known_hosts": None,  # TODO: known_host_key aus DB erzwingen
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
```

### `backend/app/connectors/apt.py`

```python
from .ssh import SSHConnector

class AptConnector:
    """
    apt-Update-Erkennung via SSH.
    Security-Updates erkennbar am 'security' im Quell-Repository.
    """

    def __init__(self, ssh_connector: SSHConnector):
        self.ssh = ssh_connector

    async def get_upgradable_packages(self) -> list[dict]:
        await self.ssh.run("sudo apt-get update -qq 2>/dev/null || true")
        stdout, _, _ = await self.ssh.run(
            "apt list --upgradable 2>/dev/null | grep -v '^Listing'"
        )
        packages = []
        for line in stdout.strip().splitlines():
            if "/" not in line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            name = parts[0].split("/")[0]
            available_version = parts[1] if len(parts) > 1 else None
            current_version = parts[-1].rstrip("]") if "upgradable from:" in line else None
            is_security = "security" in line.lower()
            packages.append({
                "name": name,
                "current_version": current_version,
                "available_version": available_version,
                "is_security": is_security,
            })
        return packages
```

### `backend/app/connectors/docker_tcp.py`

```python
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
        return ResourceMetrics()  # Host-Metriken via SSH/SSHConnector holen

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
```

### `backend/app/connectors/docker_ssh.py`

```python
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
```

### `backend/app/connectors/registry.py`

```python
import httpx

async def check_image_update(image_ref: str) -> dict | None:
    """
    Prüft ob ein neues Docker Image verfügbar ist via Docker Hub / OCI Registry.
    Vergleich über Manifest-Digest.
    image_ref: z.B. "nginx:latest", "ghcr.io/user/repo:main"
    Returns: {remote_digest: str} oder None bei Fehler.
    """
    if "." in image_ref.split("/")[0] and "/" in image_ref:
        # Private registry (ghcr.io, etc.) — vereinfachte Implementierung
        return None

    repo = image_ref.split(":")[0]
    tag = image_ref.split(":")[-1] if ":" in image_ref else "latest"
    if "/" not in repo:
        repo = f"library/{repo}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_r = await client.get(
                f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull"
            )
            token = token_r.json().get("token", "")
            manifest_r = await client.get(
                f"https://registry.hub.docker.com/v2/{repo}/manifests/{tag}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.docker.distribution.manifest.v2+json",
                },
            )
            remote_digest = manifest_r.headers.get("Docker-Content-Digest", "")
            return {"remote_digest": remote_digest}
    except Exception:
        return None
```

### `backend/app/connectors/homeassistant.py`

```python
import httpx
from .base import BaseConnector, HostStatus, ResourceMetrics

class HomeAssistantConnector(BaseConnector):
    """
    Home Assistant REST API.
    credentials: {bearer_token: "Long-Lived Access Token"}
    Updates via update.* Entities: state='on' = Update verfügbar.
    """

    def __init__(self, host_address: str, credentials: dict, port: int = 8123):
        super().__init__(host_address, credentials)
        self.base_url = f"http://{host_address}:{port}"
        self.headers = {"Authorization": f"Bearer {credentials['bearer_token']}"}

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
```

---

## Services: Business Logic

### `backend/app/services/credential_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.host import HostCredential
from app.core.security import decrypt
from app.config import settings

async def get_credentials(db: AsyncSession, host_id: int) -> dict:
    result = await db.execute(
        select(HostCredential).where(HostCredential.host_id == host_id)
    )
    creds = result.scalars().all()
    resolved = {}
    for cred in creds:
        value = decrypt(cred.encrypted_value, settings.secret_key)
        resolved[cred.cred_type] = value
        if cred.username:
            resolved["username"] = cred.username
    return resolved
```

### `backend/app/services/notification.py`

```python
import aiosmtplib
from email.message import EmailMessage
from app.config import settings

async def send_alert_email(subject: str, body: str) -> bool:
    if not settings.smtp_host or not settings.alert_to_emails:
        return False
    msg = EmailMessage()
    msg["From"] = settings.alert_from_email
    msg["To"] = ", ".join(settings.alert_to_emails)
    msg["Subject"] = f"[HomeLab] {subject}"
    msg.set_content(body)
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_pass or None,
            start_tls=True,
        )
        return True
    except Exception:
        return False
```

---

## Tasks und Scheduler

### `backend/app/tasks/scheduler.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.config import settings

scheduler = AsyncIOScheduler()

def register_tasks():
    from app.tasks.health_check import run_health_checks
    from app.tasks.update_scan import run_update_scan
    from app.tasks.metric_collector import run_metric_collection
    from app.tasks.cleanup import run_cleanup

    scheduler.add_job(
        run_health_checks,
        IntervalTrigger(seconds=settings.health_check_interval_seconds),
        id="health_check",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        run_update_scan,
        IntervalTrigger(seconds=settings.update_scan_interval_seconds),
        id="update_scan",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        run_metric_collection,
        IntervalTrigger(seconds=settings.metric_collect_interval_seconds),
        id="metric_collector",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        run_cleanup,
        CronTrigger(hour=3, minute=0),
        id="cleanup",
        max_instances=1,
        replace_existing=True,
    )
```

### `backend/app/tasks/health_check.py`

```python
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.host import Host

async def run_health_checks():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()
        await asyncio.gather(*[_check_host(db, host) for host in hosts])
        await db.commit()

async def _check_host(db, host: Host):
    from app.services.credential_service import get_credentials

    try:
        creds = await get_credentials(db, host.id)
        connector = _make_connector(host, creds)
        status = await connector.check_reachability()
        if status.reachable:
            host.last_seen = datetime.utcnow()
        host.last_error = status.error
    except Exception as e:
        host.last_error = str(e)

def _make_connector(host, creds):
    from app.connectors.proxmox import ProxmoxConnector
    from app.connectors.docker_tcp import DockerTCPConnector
    from app.connectors.ssh import SSHConnector
    from app.connectors.homeassistant import HomeAssistantConnector

    match host.host_type:
        case "proxmox":
            return ProxmoxConnector(host.address, creds, host.port or 8006)
        case "docker":
            return DockerTCPConnector(host.address, creds, host.port or 2375)
        case "ssh":
            return SSHConnector(host.address, creds, host.port or 22)
        case "homeassistant":
            return HomeAssistantConnector(host.address, creds, host.port or 8123)
        case _:
            raise ValueError(f"Unknown host_type: {host.host_type}")
```

### `backend/app/tasks/update_scan.py`

```python
from sqlalchemy import select, and_
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.update import UpdateRecord
from datetime import datetime

async def run_update_scan():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()
        for host in hosts:
            await _scan_host(db, host)
        await db.commit()

async def _scan_host(db, host: Host):
    from app.services.credential_service import get_credentials

    try:
        creds = await get_credentials(db, host.id)

        if host.host_type == "ssh":
            from app.connectors.ssh import SSHConnector
            from app.connectors.apt import AptConnector
            ssh = SSHConnector(host.address, creds, host.port or 22)
            apt = AptConnector(ssh)
            packages = await apt.get_upgradable_packages()
            for pkg in packages:
                record = UpdateRecord(
                    host_id=host.id,
                    update_type="apt",
                    package_name=pkg["name"],
                    current_version=pkg["current_version"],
                    available_version=pkg["available_version"],
                    is_security=pkg["is_security"],
                    status="pending",
                    detected_at=datetime.utcnow(),
                )
                db.add(record)

        elif host.host_type == "proxmox":
            from app.connectors.proxmox import ProxmoxConnector
            pve = ProxmoxConnector(host.address, creds, host.port or 8006)
            updates = await pve.get_pve_updates()
            for pkg in updates:
                is_security = "security" in pkg.get("origin", "").lower() or pkg.get("package", "").startswith("pve-")
                record = UpdateRecord(
                    host_id=host.id,
                    update_type="pve",
                    package_name=pkg.get("package"),
                    current_version=pkg.get("OldVersion"),
                    available_version=pkg.get("Version"),
                    is_security=is_security,
                    status="pending",
                    detected_at=datetime.utcnow(),
                )
                db.add(record)

        elif host.host_type == "homeassistant":
            from app.connectors.homeassistant import HomeAssistantConnector
            ha = HomeAssistantConnector(host.address, creds, host.port or 8123)
            updates = await ha.get_pending_updates()
            for upd in updates:
                record = UpdateRecord(
                    host_id=host.id,
                    update_type="homeassistant",
                    package_name=upd["name"],
                    current_version=upd["installed_version"],
                    available_version=upd["latest_version"],
                    is_security=upd["is_security"],
                    status="pending",
                    detected_at=datetime.utcnow(),
                )
                db.add(record)

    except Exception:
        pass  # Einzelne Host-Fehler nicht den ganzen Scan abbrechen
```

### `backend/app/tasks/metric_collector.py`

```python
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.host import Host
from app.models.snapshot import MetricSnapshot

async def run_metric_collection():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Host).where(Host.enabled == True))
        hosts = result.scalars().all()
        await asyncio.gather(*[_collect_host(db, host) for host in hosts])
        await db.commit()

async def _collect_host(db, host: Host):
    from app.services.credential_service import get_credentials
    try:
        creds = await get_credentials(db, host.id)
        from app.tasks.health_check import _make_connector
        connector = _make_connector(host, creds)
        metrics = await connector.get_resources()
        snapshot = MetricSnapshot(
            host_id=host.id,
            captured_at=datetime.utcnow(),
            cpu_percent=metrics.cpu_percent,
            ram_used_bytes=metrics.ram_used_bytes,
            ram_total_bytes=metrics.ram_total_bytes,
            disk_used_bytes=metrics.disk_used_bytes,
            disk_total_bytes=metrics.disk_total_bytes,
            load_1m=metrics.load_1m,
        )
        db.add(snapshot)
    except Exception:
        pass

```

### `backend/app/tasks/cleanup.py`

```python
from datetime import datetime, timedelta
from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models.snapshot import MetricSnapshot
from app.models.service import ServiceCheck

async def run_cleanup():
    cutoff = datetime.utcnow() - timedelta(days=30)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(MetricSnapshot).where(MetricSnapshot.captured_at < cutoff))
        await db.execute(delete(ServiceCheck).where(ServiceCheck.checked_at < cutoff))
        await db.commit()
```

---

## API Router

### `backend/app/api/v1/router.py`

```python
from fastapi import APIRouter
from .hosts import router as hosts_router
from .services import router as services_router
from .updates import router as updates_router
from .dashboard import router as dashboard_router
from .alerts import router as alerts_router
from .jobs import router as jobs_router
from .websocket import router as ws_router

api_router = APIRouter()
api_router.include_router(hosts_router, prefix="/hosts", tags=["hosts"])
api_router.include_router(services_router, prefix="/services", tags=["services"])
api_router.include_router(updates_router, prefix="/updates", tags=["updates"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(ws_router, tags=["websocket"])
```

### `backend/app/api/v1/hosts.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.host import Host, HostCredential
from app.core.security import encrypt
from app.config import settings

router = APIRouter()

@router.get("/")
async def list_hosts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host))
    return result.scalars().all()

@router.get("/{host_id}")
async def get_host(host_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host

@router.post("/")
async def create_host(data: dict, db: AsyncSession = Depends(get_db)):
    host = Host(
        name=data["name"],
        host_type=data["host_type"],
        address=data["address"],
        port=data.get("port"),
    )
    db.add(host)
    await db.flush()
    if cred_value := data.get("credential_value"):
        cred = HostCredential(
            host_id=host.id,
            cred_type=data.get("cred_type", "api_token"),
            username=data.get("username"),
            encrypted_value=encrypt(cred_value, settings.secret_key),
        )
        db.add(cred)
    await db.commit()
    await db.refresh(host)
    return host

@router.patch("/{host_id}")
async def update_host(host_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    for key, value in data.items():
        if hasattr(host, key):
            setattr(host, key, value)
    await db.commit()
    await db.refresh(host)
    return host

@router.delete("/{host_id}")
async def delete_host(host_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    await db.delete(host)
    await db.commit()
    return {"ok": True}
```

### `backend/app/api/v1/updates.py`

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.update import UpdateRecord

router = APIRouter()

@router.get("/")
async def list_updates(
    status: str | None = Query(None),
    update_type: str | None = Query(None),
    is_security: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(UpdateRecord)
    if status:
        query = query.where(UpdateRecord.status == status)
    if update_type:
        query = query.where(UpdateRecord.update_type == update_type)
    if is_security is not None:
        query = query.where(UpdateRecord.is_security == is_security)
    result = await db.execute(query.order_by(UpdateRecord.detected_at.desc()))
    return result.scalars().all()

@router.patch("/{update_id}/status")
async def set_update_status(update_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    result = await db.execute(select(UpdateRecord).where(UpdateRecord.id == update_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404)
    record.status = data["status"]
    await db.commit()
    return {"ok": True}
```

### `backend/app/api/v1/dashboard.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.host import Host
from app.models.service import Service
from app.models.update import UpdateRecord
from app.models.alert import Alert

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    hosts_total = (await db.execute(select(func.count()).select_from(Host))).scalar()
    services_running = (await db.execute(
        select(func.count()).select_from(Service).where(Service.status == "running")
    )).scalar()
    services_down = (await db.execute(
        select(func.count()).select_from(Service).where(Service.status.in_(["stopped", "error"]))
    )).scalar()
    pending_updates = (await db.execute(
        select(func.count()).select_from(UpdateRecord).where(UpdateRecord.status == "pending")
    )).scalar()
    security_updates = (await db.execute(
        select(func.count()).select_from(UpdateRecord).where(
            UpdateRecord.status == "pending", UpdateRecord.is_security == True
        )
    )).scalar()
    active_alerts = (await db.execute(
        select(func.count()).select_from(Alert).where(Alert.status == "firing")
    )).scalar()

    return {
        "hosts_total": hosts_total,
        "services_running": services_running,
        "services_down": services_down,
        "pending_updates": pending_updates,
        "security_updates": security_updates,
        "active_alerts": active_alerts,
    }
```

### `backend/app/api/v1/websocket.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()
_connections: list[WebSocket] = []

async def broadcast(message: dict):
    data = json.dumps(message)
    dead = []
    for ws in _connections:
        try:
            await ws.send_text(data)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.remove(ws)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        if websocket in _connections:
            _connections.remove(websocket)
```

---

## Frontend: SvelteKit

### `frontend/package.json`

```json
{
  "name": "homelab-orchestrator-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json"
  },
  "devDependencies": {
    "@sveltejs/adapter-node": "^5",
    "@sveltejs/kit": "^2",
    "svelte": "^5",
    "svelte-check": "^4",
    "typescript": "^5",
    "vite": "^6",
    "tailwindcss": "^4",
    "@tailwindcss/vite": "^4"
  }
}
```

### `frontend/svelte.config.js`

```javascript
import adapter from '@sveltejs/adapter-node';

export default {
  kit: {
    adapter: adapter({ out: 'build' }),
  },
};
```

### `frontend/vite.config.ts`

```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
```

### `frontend/src/app.css`

```css
@import "tailwindcss";

:root {
  --color-status-up: theme(colors.green.500);
  --color-status-down: theme(colors.red.500);
  --color-status-degraded: theme(colors.yellow.500);
  --color-status-unknown: theme(colors.gray.400);
}

body {
  @apply bg-gray-950 text-gray-100;
}
```

### `frontend/src/routes/+layout.ts`

```typescript
export const ssr = false;
export const prerender = false;
```

### `frontend/src/routes/+layout.svelte`

```svelte
<script lang="ts">
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import Topbar from '$lib/components/layout/Topbar.svelte';
  import { wsStore } from '$lib/stores/websocket.svelte';
  import { onMount } from 'svelte';

  onMount(() => wsStore.connect());
</script>

<div class="flex h-screen bg-gray-950">
  <Sidebar />
  <div class="flex flex-col flex-1 overflow-hidden">
    <Topbar />
    <main class="flex-1 overflow-auto p-6">
      <slot />
    </main>
  </div>
</div>
```

### `frontend/src/lib/api/client.ts`

```typescript
const BASE = '/api/v1';

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`API ${response.status}: ${await response.text()}`);
  }
  return response.json() as Promise<T>;
}
```

### `frontend/src/lib/stores/websocket.svelte.ts`

```typescript
let socket: WebSocket | null = null;
let connected = $state(false);

export const wsStore = {
  get connected() { return connected; },

  connect() {
    const url = `ws://${window.location.host}/api/v1/ws`;
    socket = new WebSocket(url);
    socket.onopen = () => { connected = true; };
    socket.onclose = () => {
      connected = false;
      setTimeout(() => wsStore.connect(), 5000);
    };
    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type !== 'ping') console.log('WS:', msg);
    };
  },
};
```

### `frontend/src/routes/+page.svelte` (Redirect)

```svelte
<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  onMount(() => goto('/dashboard'));
</script>
```

### `frontend/src/routes/dashboard/+page.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { apiFetch } from '$lib/api/client';

  let summary = $state<any>(null);
  let hosts = $state<any[]>([]);

  onMount(async () => {
    [summary, hosts] = await Promise.all([
      apiFetch('/dashboard/summary'),
      apiFetch('/hosts'),
    ]);
  });
</script>

<h1 class="text-2xl font-bold mb-6">Dashboard</h1>

{#if summary}
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
    <div class="bg-gray-800 rounded-lg p-4">
      <div class="text-3xl font-bold text-white">{summary.hosts_total}</div>
      <div class="text-gray-400 text-sm">Hosts</div>
    </div>
    <div class="bg-gray-800 rounded-lg p-4">
      <div class="text-3xl font-bold text-green-400">{summary.services_running}</div>
      <div class="text-gray-400 text-sm">Services aktiv</div>
    </div>
    <div class="bg-gray-800 rounded-lg p-4">
      <div class="text-3xl font-bold text-red-400">{summary.services_down}</div>
      <div class="text-gray-400 text-sm">Services down</div>
    </div>
    <div class="bg-gray-800 rounded-lg p-4">
      <div class="text-3xl font-bold text-yellow-400">{summary.pending_updates}</div>
      <div class="text-gray-400 text-sm">Updates verfügbar</div>
    </div>
    <div class="bg-gray-800 rounded-lg p-4">
      <div class="text-3xl font-bold text-red-500">{summary.security_updates}</div>
      <div class="text-gray-400 text-sm">Security Updates</div>
    </div>
    <div class="bg-gray-800 rounded-lg p-4">
      <div class="text-3xl font-bold text-orange-400">{summary.active_alerts}</div>
      <div class="text-gray-400 text-sm">Aktive Alerts</div>
    </div>
  </div>
{/if}

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each hosts as host}
    <a href="/hosts/{host.id}" class="block bg-gray-800 rounded-lg p-5 hover:bg-gray-700 transition">
      <div class="flex items-center justify-between mb-2">
        <span class="font-semibold text-white">{host.name}</span>
        <span class="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">{host.host_type}</span>
      </div>
      <div class="text-sm text-gray-400">{host.address}</div>
      <div class="mt-2 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full {host.last_seen ? 'bg-green-500' : 'bg-gray-500'}"></span>
        <span class="text-xs text-gray-500">
          {host.last_seen ? 'Erreichbar' : 'Unbekannt'}
        </span>
      </div>
    </a>
  {/each}
</div>
```

### `frontend/src/routes/updates/+page.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { apiFetch } from '$lib/api/client';

  let updates = $state<any[]>([]);
  let filter = $state({ status: 'pending', is_security: null as boolean | null });

  async function load() {
    const params = new URLSearchParams({ status: filter.status });
    if (filter.is_security !== null) params.set('is_security', String(filter.is_security));
    updates = await apiFetch(`/updates?${params}`);
  }

  async function setStatus(id: number, status: string) {
    await apiFetch(`/updates/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
    await load();
  }

  onMount(load);
</script>

<div class="flex items-center justify-between mb-6">
  <h1 class="text-2xl font-bold">Updates</h1>
  <div class="flex gap-2">
    <button
      class="px-3 py-1 rounded text-sm {filter.is_security === true ? 'bg-red-600 text-white' : 'bg-gray-700 text-gray-300'}"
      onclick={() => { filter.is_security = filter.is_security === true ? null : true; load(); }}
    >
      Nur Security
    </button>
  </div>
</div>

<div class="bg-gray-800 rounded-lg overflow-hidden">
  <table class="w-full text-sm">
    <thead class="bg-gray-700">
      <tr>
        <th class="text-left p-3 text-gray-300">Host</th>
        <th class="text-left p-3 text-gray-300">Paket</th>
        <th class="text-left p-3 text-gray-300">Typ</th>
        <th class="text-left p-3 text-gray-300">Version</th>
        <th class="text-left p-3 text-gray-300">Security</th>
        <th class="text-left p-3 text-gray-300">Aktion</th>
      </tr>
    </thead>
    <tbody>
      {#each updates as upd}
        <tr class="border-t border-gray-700 hover:bg-gray-750">
          <td class="p-3 text-gray-300">{upd.host_id}</td>
          <td class="p-3 text-white font-mono">{upd.package_name ?? '-'}</td>
          <td class="p-3">
            <span class="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">{upd.update_type}</span>
          </td>
          <td class="p-3 text-gray-400 font-mono text-xs">
            {upd.current_version ?? '?'} → {upd.available_version ?? '?'}
          </td>
          <td class="p-3">
            {#if upd.is_security}
              <span class="px-2 py-0.5 rounded text-xs bg-red-900 text-red-300 font-semibold">SECURITY</span>
            {/if}
          </td>
          <td class="p-3">
            <button
              class="text-xs px-2 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-300 mr-1"
              onclick={() => setStatus(upd.id, 'ignored')}
            >
              Ignorieren
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
  {#if updates.length === 0}
    <div class="p-8 text-center text-gray-500">Keine Updates gefunden</div>
  {/if}
</div>
```

### `frontend/src/lib/components/layout/Sidebar.svelte`

```svelte
<nav class="w-56 bg-gray-900 border-r border-gray-800 flex flex-col">
  <div class="p-4 border-b border-gray-800">
    <span class="font-bold text-white text-lg">HomeLab</span>
  </div>
  <ul class="flex-1 p-2 space-y-1">
    {#each [
      { href: '/dashboard', label: 'Dashboard' },
      { href: '/hosts', label: 'Hosts' },
      { href: '/services', label: 'Services' },
      { href: '/updates', label: 'Updates' },
      { href: '/alerts', label: 'Alerts' },
      { href: '/settings', label: 'Einstellungen' },
    ] as item}
      <li>
        <a
          href={item.href}
          class="block px-3 py-2 rounded text-gray-300 hover:bg-gray-800 hover:text-white transition text-sm"
        >
          {item.label}
        </a>
      </li>
    {/each}
  </ul>
</nav>
```

---

## Deployment

### `deployment/install.sh`

```bash
#!/bin/bash
set -euo pipefail

APP_DIR="/opt/homelab-orchestrator"
APP_USER="homelab"

echo "=== HomeLab Orchestrator Install ==="

apt-get update
apt-get install -y python3.12 python3.12-venv python3-pip nodejs npm nginx sqlite3 curl git

useradd -r -s /sbin/nologin -d "$APP_DIR" "$APP_USER" 2>/dev/null || true

mkdir -p "$APP_DIR"/{data,logs,frontend}
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

python3.12 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -e backend/

cd backend && "$APP_DIR/.venv/bin/alembic" upgrade head && cd ..

cd frontend && npm ci && npm run build && cp -r build/* "$APP_DIR/frontend/" && cd ..

if [ ! -f "$APP_DIR/.env" ]; then
    python3.12 -c "from cryptography.fernet import Fernet; print(f'SECRET_KEY={Fernet.generate_key().decode()}')" > "$APP_DIR/.env"
    cat >> "$APP_DIR/.env" <<'EOF'
DATABASE_URL=sqlite+aiosqlite:///./data/homelab.db
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
ALERT_FROM_EMAIL=
ALERT_TO_EMAILS=[]
APP_HOST=127.0.0.1
APP_PORT=8000
LOG_LEVEL=INFO
HEALTH_CHECK_INTERVAL_SECONDS=60
UPDATE_SCAN_INTERVAL_SECONDS=3600
METRIC_COLLECT_INTERVAL_SECONDS=60
EOF
    chmod 600 "$APP_DIR/.env"
    chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
fi

cp deployment/homelab-orchestrator.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable homelab-orchestrator

cp deployment/nginx.conf /etc/nginx/sites-available/homelab-orchestrator
ln -sf /etc/nginx/sites-available/homelab-orchestrator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl enable nginx

echo ""
echo "=== Installation abgeschlossen ==="
echo "1. Bearbeite: $APP_DIR/.env  (SMTP-Daten eintragen)"
echo "2. Starte:    systemctl start homelab-orchestrator nginx"
echo "3. Öffne:     http://$(hostname -I | awk '{print $1}')"
```

### `deployment/homelab-orchestrator.service`

```ini
[Unit]
Description=HomeLab Orchestrator
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=homelab
Group=homelab
WorkingDirectory=/opt/homelab-orchestrator/backend
EnvironmentFile=/opt/homelab-orchestrator/.env
ExecStart=/opt/homelab-orchestrator/.venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 1
Restart=on-failure
RestartSec=10s
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=/opt/homelab-orchestrator/data /opt/homelab-orchestrator/logs
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### `deployment/nginx.conf`

```nginx
server {
    listen 80;
    server_name _;

    root /opt/homelab-orchestrator/frontend;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## Makefile

```makefile
.PHONY: dev-backend dev-frontend test lint migrate seed build

dev-backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/pytest tests/ -v

lint:
	cd backend && .venv/bin/ruff check . && cd ../frontend && npm run check

migrate:
	cd backend && .venv/bin/alembic upgrade head

seed:
	cd backend && .venv/bin/python ../dev/seed.py

build:
	cd frontend && npm run build
```

---

## Implementierungs-Reihenfolge

Implementiere in dieser Reihenfolge (jeder Schritt baut auf dem vorherigen auf):

1. **Projektstruktur anlegen** — alle Verzeichnisse, leere `__init__.py` Dateien
2. **`backend/pyproject.toml`** und **`backend/app/config.py`**
3. **`backend/app/database.py`** und alle **`backend/app/models/*.py`** Dateien
4. **`backend/alembic/`** Setup + `0001_initial.py` Migration (alle Tabellen in einer Migration)
5. **`backend/app/core/security.py`** — Fernet Encryption
6. **`backend/app/services/credential_service.py`** und **`notification.py`**
7. **`backend/app/connectors/`** — in Reihenfolge: `base` → `ssh` → `apt` → `proxmox` → `docker_tcp` → `docker_ssh` → `registry` → `homeassistant`
8. **`backend/app/tasks/`** — `scheduler` → `health_check` → `update_scan` → `metric_collector` → `cleanup`
9. **`backend/app/api/v1/`** — alle Router + `main.py`
10. **`frontend/`** — SvelteKit + Tailwind Setup
11. **Frontend**: `lib/api/client.ts` → Stores → Komponenten → Routes

---

## Wichtige Implementierungsregeln

- **Async-first**: Alle I/O-Operationen müssen `async/await` verwenden. Kein blocking Code im async context.
- **SSH-Keys NIEMALS auf Disk**: Nur im RAM, direkt als `client_keys=[key_bytes]` an asyncssh übergeben.
- **Alle Secrets Fernet-verschlüsselt** in der Datenbank. `SECRET_KEY` nur in `.env` (chmod 600).
- **Tailwind v4 CSS-first**: Kein `tailwind.config.ts`. Stattdessen `@import "tailwindcss"` in `app.css` und `@tailwindcss/vite` Plugin.
- **Svelte 5 Runes**: `$state`, `$derived`, `$effect` verwenden. Keine alten `writable`/`readable` Stores.
- **SQLAlchemy 2.0 Style**: `Mapped[type]` annotations mit `mapped_column()`. Keine alten `Column()` Definitionen.
- **APScheduler 4.x**: `AsyncIOScheduler` mit `await scheduler.start()`. Nicht `BackgroundScheduler`.
- **FastAPI lifespan**: Kein deprecated `@app.on_event("startup")`. Nur `@asynccontextmanager async def lifespan()`.
- **Keine Auth in v1**: Single-User Home Lab. Nginx `auth_basic` als optionale Absicherung falls nötig.
- **SQLite WAL-Mode**: `PRAGMA journal_mode=WAL` und `PRAGMA foreign_keys=ON` beim ersten Connect setzen.
- **models `__init__.py`**: Alle Models in `backend/app/models/__init__.py` importieren, damit Alembic sie findet.
