#!/bin/bash
# install_enhanced_node_service.sh - Install Enhanced Node as a systemd service

set -e

SERVICE_NAME="enhanced-node"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)/enhanced_node"

# Ensure script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" >&2
    exit 1
fi

SERVICE_USER="${SUDO_USER:-$(whoami)}"

# Create virtual environment if needed
if [ ! -d "$REPO_DIR/venv" ]; then
    python3 -m venv "$REPO_DIR/venv"
    "$REPO_DIR/venv/bin/pip" install --upgrade pip
    if [ -f "$REPO_DIR/requirements.txt" ]; then
        "$REPO_DIR/venv/bin/pip" install -r "$REPO_DIR/requirements.txt"
    fi
fi

# Generate service file
cat > "$SERVICE_FILE" <<SERVICE
[Unit]
Description=Enhanced Ultimate Pain Network Node Server
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${REPO_DIR}
ExecStart=${REPO_DIR}/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"

# Start service
systemctl restart "${SERVICE_NAME}"

# Show status
systemctl status "${SERVICE_NAME}" --no-pager