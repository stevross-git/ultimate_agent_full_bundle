# config/settings.py - SSL/TLS Configuration Updates
import os
import uuid
from pathlib import Path
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Node Configuration
    NODE_VERSION: str = "3.4.0-advanced-remote-control"
    NODE_PORT: int = 5000
    NODE_HOST: str = "127.0.0.1"  # Bind to localhost (behind Nginx)
    MANAGER_HOST: str = "srvnodes.peoplesainetwork.com"  # Use HTTPS domain
    MANAGER_PORT: int = 443  # HTTPS port
    NODE_ID: str = f"enhanced-node-{uuid.uuid4().hex[:12]}"
    
    # SSL/TLS Configuration
    USE_SSL: bool = True
    SSL_CERT_PATH: str = "/etc/letsencrypt/live/srvnodes.peoplesainetwork.com/fullchain.pem"
    SSL_KEY_PATH: str = "/etc/letsencrypt/live/srvnodes.peoplesainetwork.com/privkey.pem"
    SSL_VERIFY: bool = True
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secure-secret-key-change-this")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-this")
    ALLOWED_HOSTS: List[str] = ["srvnodes.peoplesainetwork.com", "127.0.0.1", "localhost"]
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "https://srvnodes.peoplesainetwork.com",
        "https://peoplesainetwork.com",
        "https://www.peoplesainetwork.com"
    ]
    
    # Agent Connection Settings
    AGENT_SSL_VERIFY: bool = True
    AGENT_TIMEOUT: int = 30
    AGENT_MAX_RETRIES: int = 3
    
    # Database
    DATABASE_URL: str = "sqlite:///enhanced_node_server.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Directories
    LOG_DIR: str = "logs"
    AGENT_SCRIPTS_DIR: str = "agent_scripts"
    COMMAND_HISTORY_DIR: str = "command_history"
    SSL_CERT_DIR: str = "/etc/letsencrypt/live/srvnodes.peoplesainetwork.com/"
    
    # Performance
    DEFAULT_GENERATION_INTERVAL: int = 30
    DEFAULT_MAX_PENDING_TASKS: int = 20
    HEALTH_CHECK_INTERVAL: int = 30
    COMMAND_SCHEDULER_INTERVAL: int = 10
    METRICS_PORT: int = 8091
    
    # Security Features
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_IP_WHITELIST: bool = False
    IP_WHITELIST: List[str] = []
    BLOCKED_IPS: List[str] = [
        "122.150.158.121", "122.150.158.126", 
        "122.150.158.138", "122.150.158.8"
    ]  # Block the attacking IPs we identified
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()