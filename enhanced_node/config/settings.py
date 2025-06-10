#!/usr/bin/env python3
"""
Enhanced Node Configuration Settings
All constants and configuration values
"""

import uuid
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Node Configuration
    NODE_VERSION: str = "3.4.0-advanced-remote-control"
    NODE_PORT: int = 5000
    MANAGER_HOST: str = "mannodes.peoplesainetwork.com"
    MANAGER_PORT: int = 5001
    NODE_ID: str = f"enhanced-node-{uuid.uuid4().hex[:12]}"

    # Directory Configuration
    LOG_DIR: str = "logs"
    DATABASE_PATH: str = "enhanced_node_server.db"
    AGENT_SCRIPTS_DIR: str = "agent_scripts"
    COMMAND_HISTORY_DIR: str = "command_history"

    # Rate Limiting Configuration
    DEFAULT_RATE_LIMITS: list[str] = ["1000 per hour", "100 per minute"]

    # Metrics Configuration
    METRICS_PORT: int = 8091

    # Task Generation Configuration
    DEFAULT_GENERATION_INTERVAL: int = 30
    DEFAULT_MAX_PENDING_TASKS: int = 20

    # Health Monitoring Configuration
    HEALTH_CHECK_INTERVAL: int = 30
    COMMAND_SCHEDULER_INTERVAL: int = 10

    # Cleanup Configuration
    DEFAULT_CLEANUP_DAYS: int = 30

# Create directories if not already present
Path("logs").mkdir(exist_ok=True)
Path("agent_scripts").mkdir(exist_ok=True)
Path("command_history").mkdir(exist_ok=True)

# ✅ Exported singleton
settings = Settings()
