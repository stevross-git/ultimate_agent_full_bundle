#!/bin/bash

# Enhanced Node Server Deployment Script
# Comprehensive production deployment automation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="enhanced-node"
APP_USER="enhanced-node"
APP_GROUP="enhanced-node"
INSTALL_DIR="/opt/enhanced-node"
SERVICE_NAME="enhanced-node"
BACKUP_DIR="/var/backups/enhanced-node"
LOG_DIR="/var/log/enhanced-node"

# Version information
SCRIPT_VERSION="1.0.0"
NODE_VERSION="3.4.0-advanced-remote-control"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

info() {
    echo -e "${CYAN}ℹ️ $1${NC}"
}

# Help function
show_help() {
    cat << EOF
Enhanced Node Server Deployment Script v${SCRIPT_VERSION}

Usage: $0 [OPTIONS] COMMAND

Commands:
    install         Install Enhanced Node Server
    update          Update existing installation
    uninstall       Remove Enhanced Node Server
    restart         Restart the service
    status          Show service status
    backup          Create system backup
    restore         Restore from backup
    logs            Show service logs
    health          Check system health
    setup-ssl       Setup SSL certificates
    setup-monitoring Setup monitoring stack

Options:
    -h, --help      Show this help message
    -v, --version   Show version information
    -d, --dev       Development mode installation
    -f, --force     Force installation (overwrite existing)
    --no-backup     Skip backup during update
    --no-ssl        Skip SSL setup
    --no-monitoring Skip monitoring setup

Examples:
    $0 install                 # Full production install
    $0 install --dev           # Development install
    $0 update --no-backup      # Update without backup
    $0 setup-ssl               # Setup SSL certificates
    $0 health                  # System health check

EOF
}

# Version information
show_version() {
    cat << EOF
Enhanced Node Server Deployment Script
Version: ${SCRIPT_VERSION}
Target Node Version: ${NODE_VERSION}
Author: Enhanced Node Server Team
EOF
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Check OS compatibility
check_os() {
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot determine OS version"
    fi
    
    source /etc/os-release
    
    case $ID in
        ubuntu|debian)
            PACKAGE_MANAGER="apt"
            ;;
        centos|rhel|fedora)
            PACKAGE_MANAGER="yum"
            if command -v dnf >/dev/null 2>&1; then
                PACKAGE_MANAGER="dnf"
            fi
            ;;
        *)
            error "Unsupported OS: $ID"
            ;;
    esac
    
    success "OS detected: $PRETTY_NAME"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    case $PACKAGE_MANAGER in
        apt)
            apt update
            apt install -y python3 python3-pip python3-venv python3-dev \
                          nginx postgresql postgresql-contrib redis-server \
                          supervisor curl wget git unzip \
                          build-essential libssl-dev libffi-dev \
                          certbot python3-certbot-nginx
            ;;
        yum|dnf)
            $PACKAGE_MANAGER update -y
            $PACKAGE_MANAGER install -y python3 python3-pip python3-venv python3-devel \
                                       nginx postgresql postgresql-server postgresql-contrib \
                                       redis supervisor curl wget git unzip \
                                       gcc openssl-devel libffi-devel \
                                       certbot python3-certbot-nginx
            ;;
    esac
    
    success "System dependencies installed"
}

# Create application user
create_user() {
    if ! id "$APP_USER" &>/dev/null; then
        log "Creating application user: $APP_USER"
        useradd --system --shell /bin/bash --home-dir "$INSTALL_DIR" \
                --create-home --user-group "$APP_USER"
        success "User $APP_USER created"
    else
        info "User $APP_USER already exists"
    fi
}

# Setup directories
setup_directories() {
    log "Setting up directories..."
    
    # Create directories
    mkdir -p "$INSTALL_DIR"/{logs,data,backups,agent_scripts,command_history,templates}
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p /etc/enhanced-node
    
    # Set permissions
    chown -R "$APP_USER:$APP_GROUP" "$INSTALL_DIR"
    chown -R "$APP_USER:$APP_GROUP" "$BACKUP_DIR"
    chown -R "$APP_USER:$APP_GROUP" "$LOG_DIR"
    
    chmod 755 "$INSTALL_DIR"
    chmod 750 "$INSTALL_DIR"/{logs,data,backups}
    chmod 755 "$INSTALL_DIR"/{agent_scripts,command_history,templates}
    
    success "Directories created and configured"
}

# Install Python application
install_application() {
    log "Installing Enhanced Node Server application..."
    
    # Get current directory (where the script is run from)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SOURCE_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Copy application files
    rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
          "$SOURCE_DIR/" "$INSTALL_DIR/"
    
    # Set ownership
    chown -R "$APP_USER:$APP_GROUP" "$INSTALL_DIR"
    
    # Create virtual environment
    sudo -u "$APP_USER" python3 -m venv "$INSTALL_DIR/venv"
    
    # Install Python dependencies
    sudo -u "$APP_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo -u "$APP_USER" "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    success "Application installed"
}

# Setup configuration
setup_configuration() {
    log "Setting up configuration..."
    
    # Copy environment file
    if [[ ! -f /etc/enhanced-node/.env ]]; then
        cp "$INSTALL_DIR/.env.example" /etc/enhanced-node/.env
        
        # Generate secure keys
        SECRET_KEY=$(openssl rand -base64 32)
        JWT_SECRET_KEY=$(openssl rand -base64 32)
        
        # Update configuration
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" /etc/enhanced-node/.env
        sed -i "s/your-jwt-secret-key-change-this-too/$JWT_SECRET_KEY/" /etc/enhanced-node/.env
        sed -i "s/NODE_ENV=production/NODE_ENV=production/" /etc/enhanced-node/.env
        
        chown "$APP_USER:$APP_GROUP" /etc/enhanced-node/.env
        chmod 600 /etc/enhanced-node/.env
        
        success "Configuration created with secure keys"
    else
        info "Configuration already exists"
    fi
    
    # Create symlink
    ln -sf /etc/enhanced-node/.env "$INSTALL_DIR/.env"
}

# Setup database
setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Initialize PostgreSQL if needed
    if [[ ! -d /var/lib/postgresql/data/base ]]; then
        case $PACKAGE_MANAGER in
            apt)
                sudo -u postgres initdb -D /var/lib/postgresql/data
                ;;
            yum|dnf)
                postgresql-setup initdb
                ;;
        esac
    fi
    
    # Start PostgreSQL
    systemctl enable postgresql
    systemctl start postgresql
    
    # Create database and user
    sudo -u postgres psql -c "CREATE USER enhanced_user WITH PASSWORD 'enhanced_password_2025';" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE enhanced_node OWNER enhanced_user;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE enhanced_node TO enhanced_user;" 2>/dev/null || true
    
    success "Database configured"
}

# Setup Redis
setup_redis() {
    log "Setting up Redis..."
    
    # Configure Redis
    if [[ -f /etc/redis/redis.conf ]]; then
        sed -i 's/^# maxmemory <bytes>/maxmemory 512mb/' /etc/redis/redis.conf
        sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    fi
    
    # Start Redis
    systemctl enable redis
    systemctl start redis
    
    success "Redis configured"
}

# Setup systemd service
setup_service() {
    log "Setting up systemd service..."
    
    # Copy service file
    cp "$INSTALL_DIR/deploy/enhanced-node.service" /etc/systemd/system/
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    success "Systemd service configured"
}

# Setup Nginx
setup_nginx() {
    log "Setting up Nginx reverse proxy..."
    
    # Copy Nginx configuration
    cp "$INSTALL_DIR/deploy/nginx.conf" /etc/nginx/sites-available/enhanced-node
    
    # Enable site
    ln -sf /etc/nginx/sites-available/enhanced-node /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    # Start Nginx
    systemctl enable nginx
    systemctl reload nginx
    
    success "Nginx configured"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Create self-signed certificate for now
    mkdir -p /etc/nginx/ssl
    
    if [[ ! -f /etc/nginx/ssl/enhancednode.com.crt ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/enhancednode.com.key \
            -out /etc/nginx/ssl/enhancednode.com.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=enhancednode.com"
        
        chmod 600 /etc/nginx/ssl/enhancednode.com.key
        chmod 644 /etc/nginx/ssl/enhancednode.com.crt
        
        success "Self-signed SSL certificate created"
        warning "Replace with proper SSL certificate for production"
    else
        info "SSL certificate already exists"
    fi
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring stack..."
    
    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        systemctl enable docker
        systemctl start docker
        usermod -aG docker "$APP_USER"
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
             -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Start monitoring stack
    cd "$INSTALL_DIR"
    docker-compose -f docker-compose.yml up -d prometheus grafana
    
    success "Monitoring stack configured"
}

# Initialize database
initialize_database() {
    log "Initializing application database..."
    
    cd "$INSTALL_DIR"
    sudo -u "$APP_USER" "$INSTALL_DIR/venv/bin/python" -c "
from core.database import EnhancedNodeDatabase
db = EnhancedNodeDatabase('/opt/enhanced-node/data/enhanced_node_server.db')
print('Database initialized successfully')
db.close()
"
    
    success "Database initialized"
}

# Start services
start_services() {
    log "Starting Enhanced Node Server..."
    
    systemctl start "$SERVICE_NAME"
    systemctl status "$SERVICE_NAME" --no-pager
    
    success "Enhanced Node Server started"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait for service to start
    sleep 10
    
    # Check service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Service is running"
    else
        error "Service is not running"
    fi
    
    # Check HTTP endpoint
    if curl -f http://localhost:5000/api/v3/node/stats &>/dev/null; then
        success "HTTP endpoint is responding"
    else
        warning "HTTP endpoint is not responding"
    fi
    
    # Check metrics endpoint
    if curl -f http://localhost:8091/metrics &>/dev/null; then
        success "Metrics endpoint is responding"
    else
        warning "Metrics endpoint is not responding"
    fi
    
    success "Health check completed"
}

# Create backup
create_backup() {
    log "Creating system backup..."
    
    BACKUP_NAME="enhanced-node-backup-$(date +%Y%m%d-%H%M%S)"
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME.tar.gz"
    
    # Stop service
    systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    
    # Create backup
    tar -czf "$BACKUP_PATH" \
        -C / \
        opt/enhanced-node/data \
        opt/enhanced-node/logs \
        opt/enhanced-node/agent_scripts \
        opt/enhanced-node/command_history \
        etc/enhanced-node \
        etc/systemd/system/enhanced-node.service \
        etc/nginx/sites-available/enhanced-node 2>/dev/null || true
    
    # Start service
    systemctl start "$SERVICE_NAME" 2>/dev/null || true
    
    success "Backup created: $BACKUP_PATH"
}

# Main installation function
install_main() {
    log "Starting Enhanced Node Server installation..."
    
    check_root
    check_os
    
    install_dependencies
    create_user
    setup_directories
    install_application
    setup_configuration
    setup_database
    setup_redis
    setup_service
    setup_nginx
    
    if [[ "${SKIP_SSL:-false}" != "true" ]]; then
        setup_ssl
    fi
    
    if [[ "${SKIP_MONITORING:-false}" != "true" ]]; then
        setup_monitoring
    fi
    
    initialize_database
    start_services
    health_check
    
    success "Enhanced Node Server installation completed!"
    
    cat << EOF

🚀 Enhanced Node Server v${NODE_VERSION} Installation Complete!

Dashboard: https://localhost (or your domain)
API: https://localhost/api/v3/
Metrics: http://localhost:8091/metrics
Monitoring: http://localhost:3000 (Grafana)

Service Management:
  sudo systemctl start enhanced-node
  sudo systemctl stop enhanced-node
  sudo systemctl restart enhanced-node
  sudo systemctl status enhanced-node

Logs:
  sudo journalctl -u enhanced-node -f
  sudo tail -f /var/log/enhanced-node/enhanced_node_server_advanced.log

Configuration:
  /etc/enhanced-node/.env

Next Steps:
1. Update /etc/enhanced-node/.env with your settings
2. Setup proper SSL certificate (replace self-signed)
3. Configure firewall rules
4. Setup monitoring alerts
5. Configure backup schedule

EOF
}

# Parse command line arguments
COMMAND=""
DEV_MODE=false
FORCE_INSTALL=false
SKIP_BACKUP=false
SKIP_SSL=false
SKIP_MONITORING=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        -d|--dev)
            DEV_MODE=true
            shift
            ;;
        -f|--force)
            FORCE_INSTALL=true
            shift
            ;;
        --no-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --no-ssl)
            SKIP_SSL=true
            shift
            ;;
        --no-monitoring)
            SKIP_MONITORING=true
            shift
            ;;
        install|update|uninstall|restart|status|backup|restore|logs|health|setup-ssl|setup-monitoring)
            COMMAND=$1
            shift
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Execute command
case $COMMAND in
    install)
        install_main
        ;;
    update)
        if [[ "$SKIP_BACKUP" != "true" ]]; then
            create_backup
        fi
        install_main
        ;;
    uninstall)
        log "Uninstalling Enhanced Node Server..."
        systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        rm -f /etc/systemd/system/enhanced-node.service
        rm -f /etc/nginx/sites-enabled/enhanced-node
        systemctl daemon-reload
        systemctl reload nginx
        warning "Data preserved in $INSTALL_DIR"
        success "Enhanced Node Server uninstalled"
        ;;
    restart)
        systemctl restart "$SERVICE_NAME"
        success "Service restarted"
        ;;
    status)
        systemctl status "$SERVICE_NAME" --no-pager
        ;;
    backup)
        create_backup
        ;;
    logs)
        journalctl -u "$SERVICE_NAME" -f
        ;;
    health)
        health_check
        ;;
    setup-ssl)
        setup_ssl
        systemctl reload nginx
        ;;
    setup-monitoring)
        setup_monitoring
        ;;
    *)
        error "No command specified. Use --help for usage information."
        ;;
esac
