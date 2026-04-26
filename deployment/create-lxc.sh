#!/usr/bin/env bash
source <(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/misc/build.func)
# Copyright (c) 2025 HomeLab
# License: MIT
# Source: https://github.com/hendrik-lager/homelab-orchestrator

APP="HomeLab-Orchestrator"
var_tags="${var_tags:-homelab}"
var_cpu="${var_cpu:-2}"
var_ram="${var_ram:-2048}"
var_disk="${var_disk:-8}"
var_os="${var_os:-debian}"
var_version="${var_version:-12}"
var_unprivileged="${var_unprivileged:-1}"
var_nesting="${var_nesting:-1}"

header_info "$APP"
variables
color
catch_errors

function update_script() {
  header_info
  check_container_storage
  check_container_resources
  msg_info "Updating HomeLab Orchestrator"
  $STD apt update
  $STD apt upgrade -y
  msg_ok "Updated successfully!"
  exit
}

start
build_container

msg_info "Installing HomeLab Orchestrator..."

export DEBIAN_FRONTEND=noninteractive
$STD apt update
$STD apt install -y python3 python3-venv python3-pip nodejs npm nginx sqlite3 curl git

APP_DIR="/opt/homelab-orchestrator"
APP_USER="homelab"

$STD useradd -r -s /sbin/nologin -d "$APP_DIR" "$APP_USER" 2>/dev/null || true

$STD mkdir -p "$APP_DIR"/{data,logs,frontend}
$STD chown -R "$APP_USER:$APP_USER" "$APP_DIR"

GITHUB_REPO="hendrik-lager/homelab-orchestrator"
GITHUB_CLONE="https://github.com/${GITHUB_REPO}.git"

if [ ! -d "$APP_DIR/.git" ]; then
  msg_info "Cloning repository..."
  rm -rf "$APP_DIR"
  $STD git clone "$GITHUB_CLONE" "$APP_DIR"
fi

$STD python3 -m venv "$APP_DIR/.venv"
$STD "$APP_DIR/.venv/bin/pip" install --upgrade pip
$STD "$APP_DIR/.venv/bin/pip" install fastapi uvicorn sqlalchemy aiosqlite alembic pydantic-settings httpx asyncssh apscheduler cryptography aiosmtplib

if [ ! -f "$APP_DIR/.env" ]; then
  python3 -c "from cryptography.fernet import Fernet; print(f'SECRET_KEY={Fernet.generate_key().decode()}')" > "$APP_DIR/.env"
  tee -a "$APP_DIR/.env" <<'ENVEOF'
DATABASE_URL=sqlite+aiosqlite:////opt/homelab-orchestrator/data/homelab.db
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
ENVEOF
  chmod 600 "$APP_DIR/.env"
  chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
fi

set -a; . "$APP_DIR/.env"; set +a
cd "$APP_DIR/backend" && $STD "$APP_DIR/.venv/bin/alembic" upgrade head

$STD cd "$APP_DIR/frontend" && $STD npm ci && $STD npm run build && $STD cp -r build/* "$APP_DIR/frontend/"

$STD cp "$APP_DIR/deployment/homelab-orchestrator.service" /etc/systemd/system/
$STD systemctl daemon-reload
$STD systemctl enable homelab-orchestrator

$STD cp "$APP_DIR/deployment/nginx.conf" /etc/nginx/sites-available/homelab-orchestrator
$STD ln -sf /etc/nginx/sites-available/homelab-orchestrator /etc/nginx/sites-enabled/
$STD rm -f /etc/nginx/sites-enabled/default
$STD systemctl enable nginx

description

msg_ok "Completed successfully!\n"
echo -e "${CREATING}${GN}${APP} setup has been successfully initialized!${CL}"
echo -e "${INFO}${YW}Access the WebUI at:${CL}"
echo -e "${TAB}${GATEWAY}${BGN}http://\${IP}${CL}"
