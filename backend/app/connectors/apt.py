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
