#!/bin/bash

# Enhanced Node Server Docker Startup Script
# Handles initialization, dependency checks, and service startup

set -e

echo "🚀 Starting Enhanced Node Server in Docker..."
echo "=============================================="

# Environment setup
export PYTHONPATH="/app:$PYTHONPATH"
export NODE_ENV=${NODE_ENV:-production}
export NODE_PORT=${NODE_PORT:-443}
export METRICS_PORT=${METRICS_PORT:-8091}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-30}
    
    echo "⏳ Waiting for $service_name ($host:$port)..."
    
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        echo "   Attempt $i/$timeout - $service_name not ready yet..."
        sleep 1
    done
    
    echo "❌ $service_name failed to start within $timeout seconds"
    return 1
}

# Function to check Python dependencies
check_dependencies() {
    echo "🔍 Checking Python dependencies..."
    
    python -c "
import sys
required = ['flask', 'flask_socketio', 'sqlalchemy', 'redis', 'prometheus_client']
missing = []

for package in required:
    try:
        __import__(package)
        print(f'✅ {package}')
    except ImportError:
        missing.append(package)
        print(f'❌ {package}')

if missing:
    print(f'Missing packages: {missing}')
    sys.exit(1)
else:
    print('✅ All required packages available')
"
}

# Function to initialize database
init_database() {
    echo "💾 Initializing database..."
    
    python -c "
import sys
sys.path.insert(0, '/app')

try:
    from core.database import EnhancedNodeDatabase
    from config.settings import DATABASE_PATH
    
    db = EnhancedNodeDatabase(DATABASE_PATH)
    print('✅ Database initialized successfully')
    db.close()
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    sys.exit(1)
"
}

# Function to create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    
    directories=(
        "/app/logs"
        "/app/data"
        "/app/agent_scripts"
        "/app/command_history"
        "/app/templates"
        "/app/backups"
    )
    
    for dir in "${directories[@]}"; do
        if mkdir -p "$dir" 2>/dev/null; then
            echo "✅ Created $dir"
        else
            echo "⚠️ Could not create $dir (may already exist)"
        fi
    done
    
    # Set permissions
    chmod 755 /app/logs /app/data /app/agent_scripts /app/command_history 2>/dev/null || true
}

# Function to start background services
start_background_services() {
    echo "🔧 Starting background services..."
    
    # Start Redis if not external
    if [ "$REDIS_HOST" = "localhost" ] || [ -z "$REDIS_HOST" ]; then
        if command -v redis-server >/dev/null 2>&1; then
            echo "🔴 Starting Redis server..."
            redis-server --daemonize yes --port ${REDIS_PORT:-6379} --maxmemory 256mb
        else
            echo "⚠️ Redis not available, using in-memory cache"
        fi
    fi
}

# Function to perform health checks
health_check() {
    echo "🏥 Performing health checks..."
    
    # Check Python version
    python_version=$(python --version 2>&1)
    echo "🐍 Python: $python_version"
    
    # Check disk space
    df_output=$(df -h /app | tail -1)
    echo "💽 Disk space: $df_output"
    
    # Check memory
    if command -v free >/dev/null 2>&1; then
        memory_info=$(free -h | grep "^Mem:")
        echo "🧠 Memory: $memory_info"
    fi
    
    # Check network connectivity
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        echo "🌐 Network: Connected"
    else
        echo "⚠️ Network: Limited connectivity"
    fi
}

# Function to validate configuration
validate_config() {
    echo "⚙️ Validating configuration..."
    
    python -c "
import sys
sys.path.insert(0, '/app')

try:
    from config.settings import *
    print(f'✅ Node ID: {NODE_ID}')
    print(f'✅ Node Version: {NODE_VERSION}')
    print(f'✅ Node Port: {NODE_PORT}')
    print(f'✅ Metrics Port: {METRICS_PORT}')
    print(f'✅ Database Path: {DATABASE_PATH}')
    print('✅ Configuration valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"
}

# Main startup sequence
main() {
    echo "🎯 Enhanced Node Server Startup Sequence"
    echo "Node Environment: $NODE_ENV"
    echo "Node Port: $NODE_PORT"
    echo "Metrics Port: $METRICS_PORT"
    echo "=============================================="
    
    # Step 1: Create directories
    create_directories
    
    # Step 2: Health checks
    health_check
    
    # Step 3: Validate configuration
    validate_config
    
    # Step 4: Check dependencies
    check_dependencies
    
    # Step 5: Wait for external services
    if [ "$REDIS_HOST" ] && [ "$REDIS_HOST" != "localhost" ]; then
        wait_for_service "$REDIS_HOST" "${REDIS_PORT:-6379}" "Redis" 30
    fi
    
    if [ "$POSTGRES_HOST" ]; then
        wait_for_service "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}" "PostgreSQL" 30
    fi
    
    # Step 6: Start background services
    start_background_services
    
    # Step 7: Initialize database
    init_database
    
    # Step 8: Final checks
    echo "🔍 Final startup checks..."
    
    # Verify ports are available
    if ss -tulpn | grep ":$NODE_PORT " >/dev/null 2>&1; then
        echo "⚠️ Port $NODE_PORT already in use"
    else
        echo "✅ Port $NODE_PORT available"
    fi
    
    if ss -tulpn | grep ":$METRICS_PORT " >/dev/null 2>&1; then
        echo "⚠️ Port $METRICS_PORT already in use"
    else
        echo "✅ Port $METRICS_PORT available"
    fi
    
    echo "=============================================="
    echo "✅ Startup checks complete!"
    echo "🚀 Launching Enhanced Node Server..."
    echo "=============================================="
    
    # Launch the application
    exec "$@"
}

# Handle signals gracefully
trap 'echo "🛑 Received shutdown signal, stopping services..."; exit 0' SIGINT SIGTERM

# Install netcat if not available (for service checks)
if ! command -v nc >/dev/null 2>&1; then
    echo "📦 Installing netcat..."
    apk add --no-cache netcat-openbsd 2>/dev/null || \
    apt-get update && apt-get install -y netcat 2>/dev/null || \
    echo "⚠️ Could not install netcat, skipping service checks"
fi

# Run main function with all arguments
main "$@"
