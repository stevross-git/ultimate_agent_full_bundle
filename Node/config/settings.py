#!/usr/bin/env python3
"""
Enhanced Node Configuration Settings
All constants and configuration values
"""

import uuid
from pathlib import Path

# Node Configuration
NODE_VERSION = "3.4.0-advanced-remote-control"
NODE_PORT = 5000
MANAGER_HOST = "mannodes.peoplesainetwork.com"
MANAGER_PORT = 5001
NODE_ID = f"enhanced-node-{uuid.uuid4().hex[:12]}"

# Directory Configuration
LOG_DIR = "logs"
DATABASE_PATH = "enhanced_node_server.db"
AGENT_SCRIPTS_DIR = "agent_scripts"
COMMAND_HISTORY_DIR = "command_history"

# Create directories
Path(LOG_DIR).mkdir(exist_ok=True)
Path(AGENT_SCRIPTS_DIR).mkdir(exist_ok=True)
Path(COMMAND_HISTORY_DIR).mkdir(exist_ok=True)

# Rate Limiting Configuration
DEFAULT_RATE_LIMITS = ["1000 per hour", "100 per minute"]

# Metrics Configuration
METRICS_PORT = 8091

# Task Generation Configuration
DEFAULT_GENERATION_INTERVAL = 30
DEFAULT_MAX_PENDING_TASKS = 20

# Health Monitoring Configuration
HEALTH_CHECK_INTERVAL = 30
COMMAND_SCHEDULER_INTERVAL = 10

# Cleanup Configuration
DEFAULT_CLEANUP_DAYS = 30