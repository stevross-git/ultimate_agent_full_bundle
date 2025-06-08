#!/usr/bin/env python3
"""
Production Configuration for Enhanced Node Server
Environment-specific settings and optimizations
"""

import os
import uuid
from pathlib import Path

# Environment detection
NODE_ENV = os.getenv('NODE_ENV', 'development')
IS_PRODUCTION = NODE_ENV == 'production'
IS_DEVELOPMENT = NODE_ENV == 'development'
IS_TESTING = NODE_ENV == 'testing'

# Core Node Configuration
NODE_VERSION = "3.4.0-advanced-remote-control"
NODE_PORT = int(os.getenv('NODE_PORT', 5000))
NODE_ID = os.getenv('NODE_ID', f"enhanced-node-{uuid.uuid4().hex[:12]}")

# Manager Configuration
MANAGER_HOST = os.getenv('MANAGER_HOST', "mannodes.peoplesainetwork.com")
MANAGER_PORT = int(os.getenv('MANAGER_PORT', 5001))

# Database Configuration
if IS_PRODUCTION:
    # Production: PostgreSQL
    DATABASE_URL = os.getenv('DATABASE_URL', 
        f"postgresql://{os.getenv('POSTGRES_USER', 'enhanced_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'enhanced_password_2025')}@"
        f"{os.getenv('POSTGRES_HOST', 'postgres')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'enhanced_node')}"
    )
else:
    # Development/Testing: SQLite
    DATABASE_PATH = os.getenv('DATABASE_PATH', "enhanced_node_server.db")
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Redis Configuration
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}" if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Directory Configuration
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = os.getenv('LOG_DIR', str(BASE_DIR / "logs"))
DATA_DIR = os.getenv('DATA_DIR', str(BASE_DIR / "data"))
AGENT_SCRIPTS_DIR = os.getenv('AGENT_SCRIPTS_DIR', str(BASE_DIR / "agent_scripts"))
COMMAND_HISTORY_DIR = os.getenv('COMMAND_HISTORY_DIR', str(BASE_DIR / "command_history"))
BACKUP_DIR = os.getenv('BACKUP_DIR', str(BASE_DIR / "backups"))

# Create directories
for directory in [LOG_DIR, DATA_DIR, AGENT_SCRIPTS_DIR, COMMAND_HISTORY_DIR, BACKUP_DIR]:
    Path(directory).mkdir(exist_ok=True, parents=True)

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'enhanced-node-secret-key-2025-production')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'enhanced-node-jwt-secret-2025')
API_KEY_REQUIRED = os.getenv('API_KEY_REQUIRED', 'false').lower() == 'true'
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Rate Limiting Configuration
if IS_PRODUCTION:
    DEFAULT_RATE_LIMITS = ["500 per hour", "50 per minute"]
    STRICT_RATE_LIMITS = ["100 per hour", "10 per minute"]
else:
    DEFAULT_RATE_LIMITS = ["10000 per hour", "1000 per minute"]
    STRICT_RATE_LIMITS = ["1000 per hour", "100 per minute"]

# Monitoring Configuration
METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
METRICS_PORT = int(os.getenv('METRICS_PORT', 8091))
METRICS_PATH = os.getenv('METRICS_PATH', '/metrics')

# Health Check Configuration
HEALTH_CHECK_ENABLED = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', 30))
HEALTH_CHECK_TIMEOUT = int(os.getenv('HEALTH_CHECK_TIMEOUT', 10))

# Task Management Configuration
TASK_GENERATION_ENABLED = os.getenv('TASK_GENERATION_ENABLED', 'true').lower() == 'true'
TASK_GENERATION_INTERVAL = int(os.getenv('TASK_GENERATION_INTERVAL', 30))
MAX_PENDING_TASKS = int(os.getenv('MAX_PENDING_TASKS', 20))
MAX_CONCURRENT_TASKS = int(os.getenv('MAX_CONCURRENT_TASKS', 100))

# Remote Control Configuration
REMOTE_CONTROL_ENABLED = os.getenv('REMOTE_CONTROL_ENABLED', 'true').lower() == 'true'
COMMAND_SCHEDULER_ENABLED = os.getenv('COMMAND_SCHEDULER_ENABLED', 'true').lower() == 'true'
COMMAND_SCHEDULER_INTERVAL = int(os.getenv('COMMAND_SCHEDULER_INTERVAL', 10))
BULK_OPERATIONS_ENABLED = os.getenv('BULK_OPERATIONS_ENABLED', 'true').lower() == 'true'
SCRIPT_DEPLOYMENT_ENABLED = os.getenv('SCRIPT_DEPLOYMENT_ENABLED', 'true').lower() == 'true'

# Auto-Recovery Configuration
AUTO_RECOVERY_ENABLED = os.getenv('AUTO_RECOVERY_ENABLED', 'true').lower() == 'true'
RECOVERY_ATTEMPTS = int(os.getenv('RECOVERY_ATTEMPTS', 3))
RECOVERY_DELAY = int(os.getenv('RECOVERY_DELAY', 60))

# Cleanup Configuration
CLEANUP_ENABLED = os.getenv('CLEANUP_ENABLED', 'true').lower() == 'true'
CLEANUP_INTERVAL_HOURS = int(os.getenv('CLEANUP_INTERVAL_HOURS', 24))
DEFAULT_CLEANUP_DAYS = int(os.getenv('DEFAULT_CLEANUP_DAYS', 30))
LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 7))

# Performance Configuration
WORKER_THREADS = int(os.getenv('WORKER_THREADS', 4))
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', 1000))
CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', 30))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 60))

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = os.getenv('LOG_FORMAT', 
    '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
LOG_ROTATION_SIZE = os.getenv('LOG_ROTATION_SIZE', '10MB')
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

# WebSocket Configuration
WEBSOCKET_PING_TIMEOUT = int(os.getenv('WEBSOCKET_PING_TIMEOUT', 60))
WEBSOCKET_PING_INTERVAL = int(os.getenv('WEBSOCKET_PING_INTERVAL', 25))
MAX_WEBSOCKET_CONNECTIONS = int(os.getenv('MAX_WEBSOCKET_CONNECTIONS', 1000))

# Agent Configuration
MAX_AGENTS = int(os.getenv('MAX_AGENTS', 1000))
AGENT_TIMEOUT = int(os.getenv('AGENT_TIMEOUT', 120))
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', 30))
AGENT_RECONNECT_ATTEMPTS = int(os.getenv('AGENT_RECONNECT_ATTEMPTS', 5))

# Feature Flags
FEATURES = {
    'ai_orchestration': os.getenv('FEATURE_AI_ORCHESTRATION', 'true').lower() == 'true',
    'blockchain_management': os.getenv('FEATURE_BLOCKCHAIN', 'true').lower() == 'true',
    'cloud_integration': os.getenv('FEATURE_CLOUD', 'true').lower() == 'true',
    'security_features': os.getenv('FEATURE_SECURITY', 'true').lower() == 'true',
    'advanced_analytics': os.getenv('FEATURE_ANALYTICS', 'true').lower() == 'true',
    'plugin_ecosystem': os.getenv('FEATURE_PLUGINS', 'true').lower() == 'true',
    'bulk_operations': BULK_OPERATIONS_ENABLED,
    'command_scheduling': COMMAND_SCHEDULER_ENABLED,
    'script_deployment': SCRIPT_DEPLOYMENT_ENABLED,
    'health_monitoring': HEALTH_CHECK_ENABLED,
    'auto_recovery': AUTO_RECOVERY_ENABLED,
    'real_time_monitoring': os.getenv('FEATURE_REALTIME', 'true').lower() == 'true'
}

# Production Optimizations
if IS_PRODUCTION:
    # Enable production optimizations
    PRELOAD_MODELS = True
    CACHE_TEMPLATES = True
    COMPRESS_RESPONSES = True
    ENABLE_ASYNC = True
    
    # Security hardening
    SECURE_HEADERS = True
    FORCE_HTTPS = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
    HSTS_MAX_AGE = int(os.getenv('HSTS_MAX_AGE', 31536000))
    
    # Performance settings
    GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', 4))
    GUNICORN_THREADS = int(os.getenv('GUNICORN_THREADS', 2))
    GUNICORN_TIMEOUT = int(os.getenv('GUNICORN_TIMEOUT', 30))
    GUNICORN_KEEPALIVE = int(os.getenv('GUNICORN_KEEPALIVE', 2))

else:
    # Development settings
    PRELOAD_MODELS = False
    CACHE_TEMPLATES = False
    COMPRESS_RESPONSES = False
    ENABLE_ASYNC = False
    SECURE_HEADERS = False
    FORCE_HTTPS = False

# External Service URLs
EXTERNAL_SERVICES = {
    'prometheus': f"http://prometheus:{os.getenv('PROMETHEUS_PORT', 9090)}",
    'grafana': f"http://grafana:{os.getenv('GRAFANA_PORT', 3000)}",
    'elasticsearch': f"http://elasticsearch:{os.getenv('ELASTICSEARCH_PORT', 9200)}",
    'kibana': f"http://kibana:{os.getenv('KIBANA_PORT', 5601)}"
}

# Backup Configuration
BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', 24))
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 7))
BACKUP_COMPRESSION = os.getenv('BACKUP_COMPRESSION', 'gzip')

# Notification Configuration
NOTIFICATIONS_ENABLED = os.getenv('NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
EMAIL_NOTIFICATIONS = os.getenv('EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Debugging Configuration
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true' and not IS_PRODUCTION
PROFILING_ENABLED = os.getenv('PROFILING_ENABLED', 'false').lower() == 'true'
DETAILED_ERRORS = DEBUG_MODE or IS_DEVELOPMENT

# API Documentation
API_DOCS_ENABLED = os.getenv('API_DOCS_ENABLED', 'true').lower() == 'true'
SWAGGER_UI_ENABLED = API_DOCS_ENABLED and os.getenv('SWAGGER_UI_ENABLED', 'true').lower() == 'true'

def get_config_summary():
    """Get configuration summary for logging"""
    return {
        'environment': NODE_ENV,
        'node_id': NODE_ID,
        'node_version': NODE_VERSION,
        'database_type': 'PostgreSQL' if 'postgresql' in DATABASE_URL else 'SQLite',
        'redis_enabled': REDIS_ENABLED,
        'features_enabled': sum(1 for f in FEATURES.values() if f),
        'total_features': len(FEATURES),
        'production_mode': IS_PRODUCTION,
        'debug_mode': DEBUG_MODE
    }

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check required environment variables for production
    if IS_PRODUCTION:
        required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")
    
    # Validate port ranges
    if not (1024 <= NODE_PORT <= 65535):
        errors.append(f"NODE_PORT must be between 1024-65535, got {NODE_PORT}")
    
    if not (1024 <= METRICS_PORT <= 65535):
        errors.append(f"METRICS_PORT must be between 1024-65535, got {METRICS_PORT}")
    
    # Validate directories
    try:
        for directory in [LOG_DIR, DATA_DIR, AGENT_SCRIPTS_DIR]:
            Path(directory).mkdir(exist_ok=True, parents=True)
    except Exception as e:
        errors.append(f"Cannot create directories: {e}")
    
    return errors

# Configuration validation on import
_config_errors = validate_config()
if _config_errors:
    import sys
    print("❌ Configuration errors detected:")
    for error in _config_errors:
        print(f"   - {error}")
    if IS_PRODUCTION:
        sys.exit(1)
    else:
        print("⚠️ Continuing in development mode...")

# Export common settings for backward compatibility
locals().update({
    'NODE_VERSION': NODE_VERSION,
    'NODE_PORT': NODE_PORT,
    'MANAGER_HOST': MANAGER_HOST,
    'MANAGER_PORT': MANAGER_PORT,
    'NODE_ID': NODE_ID,
    'LOG_DIR': LOG_DIR,
    'DATABASE_PATH': DATABASE_PATH if 'DATABASE_PATH' in locals() else None,
    'AGENT_SCRIPTS_DIR': AGENT_SCRIPTS_DIR,
    'COMMAND_HISTORY_DIR': COMMAND_HISTORY_DIR,
    'DEFAULT_RATE_LIMITS': DEFAULT_RATE_LIMITS,
    'METRICS_PORT': METRICS_PORT,
    'DEFAULT_GENERATION_INTERVAL': TASK_GENERATION_INTERVAL,
    'DEFAULT_MAX_PENDING_TASKS': MAX_PENDING_TASKS,
    'HEALTH_CHECK_INTERVAL': HEALTH_CHECK_INTERVAL,
    'COMMAND_SCHEDULER_INTERVAL': COMMAND_SCHEDULER_INTERVAL,
    'DEFAULT_CLEANUP_DAYS': DEFAULT_CLEANUP_DAYS
})
