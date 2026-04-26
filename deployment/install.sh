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
