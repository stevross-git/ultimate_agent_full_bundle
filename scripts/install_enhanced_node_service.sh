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

# Create service file from template
cat "$REPO_DIR/systemd_service.txt" > "$SERVICE_FILE"

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"

# Start service
systemctl restart "${SERVICE_NAME}"

# Show status
systemctl status "${SERVICE_NAME}" --no-pager
