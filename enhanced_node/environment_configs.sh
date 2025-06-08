# Enhanced Node Server Environment Configuration
# Copy this file to .env and modify values as needed

# =============================================================================
# CORE CONFIGURATION
# =============================================================================

# Environment type (development, testing, production)
NODE_ENV=production

# Node identification
NODE_ID=enhanced-node-production-001
NODE_VERSION=3.4.0-advanced-remote-control

# Network configuration
NODE_PORT=5000
METRICS_PORT=8091

# Manager configuration
MANAGER_HOST=mannodes.peoplesainetwork.com
MANAGER_PORT=5001

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# SQLite (Development/Testing)
DATABASE_PATH=/app/data/enhanced_node_server.db

# PostgreSQL (Production)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=enhanced_node
POSTGRES_USER=enhanced_user
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://enhanced_user:your_secure_password_here@postgres:5432/enhanced_node

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================

REDIS_ENABLED=true
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password_here
REDIS_URL=redis://:your_redis_password_here@redis:6379/0

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Encryption keys (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too

# API security
API_KEY_REQUIRED=false
API_KEY=your-api-key-here

# CORS settings
CORS_ORIGINS=*

# HTTPS settings
FORCE_HTTPS=false
HSTS_MAX_AGE=31536000

# =============================================================================
# DIRECTORIES
# =============================================================================

LOG_DIR=/app/logs
DATA_DIR=/app/data
AGENT_SCRIPTS_DIR=/app/agent_scripts
COMMAND_HISTORY_DIR=/app/command_history
BACKUP_DIR=/app/backups

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Core features
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true
REMOTE_CONTROL_ENABLED=true
TASK_GENERATION_ENABLED=true

# Advanced features
COMMAND_SCHEDULER_ENABLED=true
BULK_OPERATIONS_ENABLED=true
SCRIPT_DEPLOYMENT_ENABLED=true
AUTO_RECOVERY_ENABLED=true

# Feature toggles
FEATURE_AI_ORCHESTRATION=true
FEATURE_BLOCKCHAIN=true
FEATURE_CLOUD=true
FEATURE_SECURITY=true
FEATURE_ANALYTICS=true
FEATURE_PLUGINS=true
FEATURE_REALTIME=true

# =============================================================================
# PERFORMANCE CONFIGURATION
# =============================================================================

# Rate limiting
DEFAULT_RATE_LIMITS=500 per hour,50 per minute
STRICT_RATE_LIMITS=100 per hour,10 per minute

# Task management
TASK_GENERATION_INTERVAL=30
MAX_PENDING_TASKS=20
MAX_CONCURRENT_TASKS=100

# Health monitoring
HEALTH_CHECK_INTERVAL=30
COMMAND_SCHEDULER_INTERVAL=10

# Connection settings
WORKER_THREADS=4
MAX_CONNECTIONS=1000
CONNECTION_TIMEOUT=30
REQUEST_TIMEOUT=60

# WebSocket settings
WEBSOCKET_PING_TIMEOUT=60
WEBSOCKET_PING_INTERVAL=25
MAX_WEBSOCKET_CONNECTIONS=1000

# Agent settings
MAX_AGENTS=1000
AGENT_TIMEOUT=120
HEARTBEAT_INTERVAL=30
AGENT_RECONNECT_ATTEMPTS=5

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s
LOG_ROTATION_SIZE=10MB
LOG_BACKUP_COUNT=5
LOG_RETENTION_DAYS=7

# =============================================================================
# CLEANUP CONFIGURATION
# =============================================================================

CLEANUP_ENABLED=true
CLEANUP_INTERVAL_HOURS=24
DEFAULT_CLEANUP_DAYS=30

# Auto-recovery settings
RECOVERY_ATTEMPTS=3
RECOVERY_DELAY=60

# =============================================================================
# MONITORING & ALERTING
# =============================================================================

# External services
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
ELASTICSEARCH_PORT=9200
KIBANA_PORT=5601

# Notifications
NOTIFICATIONS_ENABLED=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
EMAIL_NOTIFICATIONS=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# =============================================================================
# BACKUP CONFIGURATION
# =============================================================================

BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=7
BACKUP_COMPRESSION=gzip

# =============================================================================
# DEVELOPMENT/DEBUG SETTINGS
# =============================================================================

DEBUG_MODE=false
PROFILING_ENABLED=false
DETAILED_ERRORS=false

# API Documentation
API_DOCS_ENABLED=true
SWAGGER_UI_ENABLED=true

# =============================================================================
# PRODUCTION OPTIMIZATIONS
# =============================================================================

# Gunicorn settings (for production deployment)
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=30
GUNICORN_KEEPALIVE=2

# Performance flags
PRELOAD_MODELS=true
CACHE_TEMPLATES=true
COMPRESS_RESPONSES=true
ENABLE_ASYNC=true
SECURE_HEADERS=true

# =============================================================================
# EXTERNAL INTEGRATIONS
# =============================================================================

# Optional external services
EXTERNAL_MONITORING_URL=
EXTERNAL_LOGGING_URL=
EXTERNAL_BACKUP_URL=

# Third-party APIs
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Blockchain settings
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your-infura-key
ETHEREUM_PRIVATE_KEY=your-ethereum-private-key
BLOCKCHAIN_NETWORK=mainnet

# Cloud provider settings
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket

GOOGLE_CLOUD_PROJECT=your-gcp-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

AZURE_STORAGE_ACCOUNT=your-azure-account
AZURE_STORAGE_KEY=your-azure-key

# =============================================================================
# CUSTOM SETTINGS
# =============================================================================

# Add your custom environment variables here
CUSTOM_SETTING_1=value1
CUSTOM_SETTING_2=value2
