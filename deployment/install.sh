#!/bin/bash
set -euo pipefail

GITHUB_REPO="${GITHUB_REPO:-hendrik-lager/homelab-orchestrator}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
GITHUB_CLONE="https://github.com/${GITHUB_REPO}.git"

APP_DIR="/opt/homelab-orchestrator"
APP_USER="homelab"

echo "=== HomeLab Orchestrator Install ==="

if [ ! -d "$APP_DIR/.git" ]; then
    echo "Klone Repository..."
    git clone "$GITHUB_CLONE" "$APP_DIR"
fi

cd "$APP_DIR"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv python3-pip nodejs npm nginx sqlite3 curl git

useradd -r -s /sbin/nologin -d "$APP_DIR" "$APP_USER" 2>/dev/null || true

mkdir -p "$APP_DIR"/{data,logs,frontend}
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -e "$APP_DIR/backend/"

cd "$APP_DIR/backend" && "$APP_DIR/.venv/bin/alembic" upgrade head && cd ..

cd "$APP_DIR/frontend" && npm ci && npm run build && cp -r build/* "$APP_DIR/frontend/" && cd ..

if [ ! -f "$APP_DIR/.env" ]; then
    python3 -c "from cryptography.fernet import Fernet; print(f'SECRET_KEY={Fernet.generate_key().decode()}')" > "$APP_DIR/.env"
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

cp "$APP_DIR/deployment/homelab-orchestrator.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable homelab-orchestrator

cp "$APP_DIR/deployment/nginx.conf" /etc/nginx/sites-available/homelab-orchestrator
ln -sf /etc/nginx/sites-available/homelab-orchestrator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl enable nginx

echo ""
echo "=== Installation abgeschlossen ==="
echo "WebUI:       http://$(hostname -I | awk '{print $1}')"
echo "API:         http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "  .env bearbeiten:   nano $APP_DIR/.env"
echo "  Services:"
echo "    systemctl status homelab-orchestrator"
echo "    systemctl status nginx"
