#!/bin/bash
set -euo pipefail

echo "=== HomeLab Orchestrator - Proxmox LXC Helper ==="
echo ""

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "FEHLER: '$1' nicht gefunden. Bitte auf einem Proxmox VE Server ausführen."
        exit 1
    fi
}

check_command pct
check_command pvesh

GITHUB_REPO="${GITHUB_REPO:-hendrik-lager/homelab-orchestrator}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
GITHUB_RAW="https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}"
GITHUB_CLONE="https://github.com/${GITHUB_REPO}.git"

echo "Verfügbare Proxmox Storage:"
pvesh get /storage --output-format json 2>/dev/null | jq -r '.[] | "\(.storage) (\(.type))"' 2>/dev/null || echo "  local, local-lvm"
echo ""

read -p "Storage [local-lvm]: " STORAGE
STORAGE=${STORAGE:-local-lvm}

read -p "VM-ID [nächster freier]: " VMID
if [ -z "$VMID" ]; then
    VMID=$(pvesh get /cluster/nextid 2>/dev/null || echo "200")
fi

read -p "Hostname [homelab-orchestrator]: " HOSTNAME
HOSTNAME=${HOSTNAME:-homelab-orchestrator}

read -p "Memory in MB [2048]: " MEMORY
MEMORY=${MEMORY:-2048}

read -p "CPU Cores [2]: " CORES
CORES=${CORES:-2}

read -p "Disk Size in GB [8]: " DISK_SIZE
DISK_SIZE=${DISK_SIZE:-8}

read -p "Bridge [vmbr0]: " BRIDGE
BRIDGE=${BRIDGE:-vmbr0}

read -p "IP Adresse (CIDR) [DHCP]: " IPADDR
DHCP_MODE=true
if [ -n "$IPADDR" ]; then
    DHCP_MODE=false
fi

read -p "Startup Order [1]: " STARTUP_ORDER
STARTUP_ORDER=${STARTUP_ORDER:-1}

read -p "Automatisch installieren? (J/n): " AUTOINSTALL
AUTOINSTALL=${AUTOINSTALL:-y}

echo ""
echo "=== Konfiguration ==="
echo "  VM-ID:        $VMID"
echo "  Hostname:     $HOSTNAME"
echo "  Memory:       ${MEMORY}MB"
echo "  CPU Cores:    $CORES"
echo "  Disk Size:    ${DISK_SIZE}GB"
echo "  Storage:      $STORAGE"
echo "  Bridge:       $BRIDGE"
echo "  Network:      ${IPADDR:-DHCP}"
echo "  Auto-Install: ${AUTOINSTALL}"
echo ""

read -p "Fortfahren? (j/N): " CONFIRM
CONFIRM=${CONFIRM:-n}
if [[ ! "$CONFIRM" =~ ^[jJyY]$ ]]; then
    echo "Abbruch."
    exit 0
fi

TEMPLATE=$(pvesh get /cluster/available/os --output-format json 2>/dev/null | jq -r '.[] | select(.template | test("debian.*12")) | .template' 2>/dev/null | head -1)
if [ -z "$TEMPLATE" ]; then
    TEMPLATE="local:vztmpl/debian-12-standard_amd64.tar.gz"
fi
echo "Verwende Template: $TEMPLATE"

echo ""
echo "[1/4] Erstelle LXC Container..."
pct create "$VMID" "$TEMPLATE" \
    --hostname "$HOSTNAME" \
    --memory "$MEMORY" \
    --cores "$CORES" \
    --rootfs "$STORAGE":vm-"$VMID"-disk-0,size="${DISK_SIZE}G" \
    --net0 "name=eth0,bridge=$BRIDGE,type=veth" \
    --ostype debian \
    --unprivileged 1 \
    --features nesting=1 \
    2>&1 | grep -v "^Volume" || true

echo ""
echo "[2/4] Konfiguriere Container..."

if [ "$DHCP_MODE" = true ]; then
    pct set "$VMID" \
        --net0 "name=eth0,bridge=$BRIDGE,firewall=1,type=veth" \
        --onboot 1 \
        --startup "order=$STARTUP_ORDER,up=10" \
        2>&1 || true
else
    pct set "$VMID" \
        --net0 "name=eth0,bridge=$BRIDGE,firewall=1,hwaddr=$(openssl rand -hex 6 | sed 's/\(..\)/\1:/g' | cut -d: -f1-5):XX,ip=$IPADDR,type=veth" \
        --onboot 1 \
        --startup "order=$STARTUP_ORDER,up=10" \
        2>&1 || true
fi

echo ""
echo "[3/4] Starte Container..."
pct start "$VMID" 2>/dev/null || true
sleep 5

if [[ "${AUTOINSTALL}" =~ ^[jJyY]$ ]]; then
    echo ""
    echo "[4/4] Automatische Installation..."

    GITHUB_REPO="hendrik-lager/homelab-orchestrator"
    GITHUB_CLONE="https://github.com/${GITHUB_REPO}.git"

    INSTALL_SCRIPT='#!/bin/bash
set -euo pipefail

echo "=== HomeLab Orchestrator Installation ==="

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3.12 python3.12-venv python3-pip nodejs npm nginx sqlite3 curl git

APP_DIR="/opt/homelab-orchestrator"
APP_USER="homelab"

useradd -r -s /sbin/nologin -d "$APP_DIR" "$APP_USER" 2>/dev/null || true

mkdir -p "$APP_DIR"/{data,logs,frontend}
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

git clone "$GITHUB_CLONE" "$APP_DIR"

python3.12 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -e "$APP_DIR/backend/"

cd "$APP_DIR/backend" && "$APP_DIR/.venv/bin/alembic" upgrade head && cd ..

cd "$APP_DIR/frontend" && npm ci && npm run build && cp -r build/* "$APP_DIR/frontend/" && cd ..

if [ ! -f "$APP_DIR/.env" ]; then
    python3.12 -c "from cryptography.fernet import Fernet; print(f'\''SECRET_KEY={Fernet.generate_key().decode()}'\'')" > "$APP_DIR/.env"
    cat >> "$APP_DIR/.env" << '\''EOF'\''
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

cp "$APP_DIR/deployment/homelab-orchestrator.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable homelab-orchestrator

cp "$APP_DIR/deployment/nginx.conf" /etc/nginx/sites-available/homelab-orchestrator
ln -sf /etc/nginx/sites-available/homelab-orchestrator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl enable nginx

echo ""
echo "=== Installation abgeschlossen ==="
echo "Container ID: '"'"'$VMID'"'"'"
echo ""
echo "  WebUI:       http://$(hostname -I | awk '"'"'{print $1}'"'"')"
echo "  API:         http://$(hostname -I | awk '"'"'{print $1}'"'"'):8000"
echo ""
echo "  Services:"
echo "    systemctl status homelab-orchestrator"
echo "    systemctl status nginx"
echo ""
'

    echo "$INSTALL_SCRIPT" | pct enter "$VMID" -- bash -c 'cat > /tmp/install.sh && chmod +x /tmp/install.sh && /tmp/install.sh'

    echo ""
    echo "=== Installation abgeschlossen ==="
else
    echo ""
    echo "=== LXC Container erstellt ==="
    echo ""
    echo "Nächste Schritte im LXC Container ($VMID):"
    echo ""
    echo "  1. Shell öffnen:"
    echo "     pct enter $VMID"
    echo ""
    echo "  2. Repository klonen und installieren:"
    echo "     git clone $GITHUB_CLONE /opt/homelab-orchestrator"
    echo "     bash /opt/homelab-orchestrator/deployment/install.sh"
fi

echo ""
echo "Container ID: $VMID"
echo "Hostname:     $HOSTNAME"
