# config/settings.py - REPLACE CURRENT VERSION
import os
import uuid
from pathlib import Path
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Node Configuration
    NODE_VERSION: str = "3.4.0-advanced-remote-control"
    NODE_PORT: int = 5000
    MANAGER_HOST: str = "mannodes.peoplesainetwork.com"
    MANAGER_PORT: int = 5001
    NODE_ID: str = f"enhanced-node-{uuid.uuid4().hex[:12]}"

    # Security
    SECRET_KEY: str = "change-in-production"
    JWT_SECRET_KEY: str = "change-in-production"

    # Database
    DATABASE_URL: str = "sqlite:///enhanced_node_server.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Directories
    LOG_DIR: str = "logs"
    AGENT_SCRIPTS_DIR: str = "agent_scripts"
    COMMAND_HISTORY_DIR: str = "command_history"

    # Performance
    DEFAULT_GENERATION_INTERVAL: int = 30
    DEFAULT_MAX_PENDING_TASKS: int = 20
    HEALTH_CHECK_INTERVAL: int = 30
    COMMAND_SCHEDULER_INTERVAL: int = 10
    METRICS_PORT: int = 8091

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create directories
for directory in ["logs", "agent_scripts", "command_history", "templates"]:
    Path(directory).mkdir(exist_ok=True)

settings = Settings()