# config/settings.py - FIXED VERSION that allows extra fields
import os
import uuid
from pathlib import Path
from typing import List

try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # Configuration to allow extra fields (fixes the debug error)
    model_config = ConfigDict(extra='ignore')  # This allows extra fields in .env
    
    # Node Configuration
    NODE_VERSION: str = "3.4.0-advanced-remote-control"
    NODE_PORT: int = 5000
    NODE_HOST: str = "127.0.0.1"
    MANAGER_HOST: str = "srvnodes.peoplesainetwork.com"
    MANAGER_PORT: int = 443
    NODE_ID: str = f"enhanced-node-{uuid.uuid4().hex[:12]}"
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secure-secret-key-change-this")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-this")
    
    # Lists - JSON format expected
    ALLOWED_HOSTS: List[str] = ["srvnodes.peoplesainetwork.com", "127.0.0.1", "localhost"]
    CORS_ORIGINS: List[str] = [
        "https://srvnodes.peoplesainetwork.com",
        "https://peoplesainetwork.com", 
        "https://www.peoplesainetwork.com"
    ]
    BLOCKED_IPS: List[str] = [
        "122.150.158.121", "122.150.158.126", 
        "122.150.158.138", "122.150.158.8"
    ]
    IP_WHITELIST: List[str] = []
    DEFAULT_RATE_LIMITS: List[str] = ["100 per hour", "10 per minute"]
    
    # SSL/TLS Configuration
    USE_SSL: bool = True
    SSL_CERT_PATH: str = "/etc/letsencrypt/live/srvnodes.peoplesainetwork.com/fullchain.pem"
    SSL_KEY_PATH: str = "/etc/letsencrypt/live/srvnodes.peoplesainetwork.com/privkey.pem"
    SSL_VERIFY: bool = True
    
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
    
    # Optional debug field (now it won't cause errors)
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # For older pydantic versions:
        extra = "ignore"  # This also allows extra fields

# Create settings instance
settings = Settings()