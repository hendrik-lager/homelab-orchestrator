#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import AsyncSessionLocal, engine, Base
from app.models import Host, HostCredential, Service, ScheduledJob
from app.core.security import encrypt
from cryptography.fernet import Fernet


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    secret_key = "test-secret-key-for-development-only"
    fernet = Fernet(secret_key.encode())

    async with AsyncSessionLocal() as db:
        proxmox_host = Host(
            name="Proxmox",
            host_type="proxmox",
            address="192.168.1.1",
            port=8006,
            enabled=True,
        )
        db.add(proxmox_host)
        await db.flush()

        pve_cred = HostCredential(
            host_id=proxmox_host.id,
            cred_type="api_token",
            username="admin@pam!homelab",
            encrypted_value=encrypt("dummy-token-secret", secret_key),
        )
        db.add(pve_cred)

        ssh_host = Host(
            name="Ubuntu Server",
            host_type="ssh",
            address="192.168.1.10",
            port=22,
            enabled=True,
        )
        db.add(ssh_host)
        await db.flush()

        ssh_cred = HostCredential(
            host_id=ssh_host.id,
            cred_type="ssh_key",
            username="root",
            encrypted_value=encrypt("-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----", secret_key),
        )
        db.add(ssh_cred)

        docker_host = Host(
            name="Docker Host",
            host_type="docker",
            address="192.168.1.20",
            port=2375,
            enabled=True,
        )
        db.add(docker_host)
        await db.flush()

        docker_cred = HostCredential(
            host_id=docker_host.id,
            cred_type="tcp_url",
            encrypted_value=encrypt("tcp://192.168.1.20:2375", secret_key),
        )
        db.add(docker_cred)

        ha_host = Host(
            name="Home Assistant",
            host_type="homeassistant",
            address="192.168.1.30",
            port=8123,
            enabled=True,
        )
        db.add(ha_host)
        await db.flush()

        ha_cred = HostCredential(
            host_id=ha_host.id,
            cred_type="bearer_token",
            encrypted_value=encrypt(" Bearer_Long_Lived_Token_Here", secret_key),
        )
        db.add(ha_cred)

        for i, host in enumerate([proxmox_host, docker_host, ha_host], 1):
            svc = Service(
                host_id=host.id,
                name=f"Service {i}",
                service_type="container",
                external_id=f"container-{i}",
                status="running" if i != 3 else "stopped",
            )
            db.add(svc)

        job = ScheduledJob(
            name="Daily Update Scan",
            job_type="update_scan",
            enabled=True,
        )
        db.add(job)

        await db.commit()
        print("Seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
