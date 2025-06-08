# Enhanced Node Server - Modular Architecture

## 🏗️ Modular Architecture Implementation

This is a fully modularized version of the Enhanced Node Server v3.4.0-advanced-remote-control, split from a monolithic script into a clean, maintainable modular structure.

## 📁 Project Structure

```
enhanced_node/
├── main.py                    # Entry point
├── setup_and_run.py          # Setup and run script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── config/
│   ├── __init__.py
│   └── settings.py            # All configuration constants
│
├── core/
│   ├── __init__.py
│   ├── server.py              # EnhancedNodeServer class
│   ├── database.py            # SQLAlchemy models & database manager
│   ├── scheduler.py           # Scheduled command logic
│   └── health.py              # Health checks & recovery
│
├── control/
│   ├── __init__.py
│   ├── task_manager.py        # TaskControlManager
│   └── remote_manager.py      # AdvancedRemoteControlManager
│
├── models/
│   ├── __init__.py
│   ├── agents.py              # EnhancedAgentInfo, EnhancedAgentStatus
│   ├── tasks.py               # CentralTask
│   ├── commands.py            # AgentCommand, AgentConfiguration
│   └── scripts.py             # ScheduledCommand, BulkOperation, etc.
│
├── routes/
│   ├── __init__.py
│   ├── api_v3.py              # Registration, heartbeat, dashboard
│   └── api_v5_remote.py       # Advanced remote control APIs
│
├── websocket/
│   ├── __init__.py
│   └── events.py              # SocketIO event handlers
│
├── utils/
│   ├── __init__.py
│   ├── serialization.py       # JSON serialization utilities
│   └── logger.py              # Logging setup
│
├── templates/                 # HTML templates (optional)
├── logs/                      # Log files
├── agent_scripts/             # Deployed agent scripts
└── command_history/           # Command execution history
```

## ✅ All Features Preserved

### Core Features
- **Agent Registration & Management** - Complete agent lifecycle management
- **Real-time Monitoring** - WebSocket-based live updates
- **Task Control System** - Centralized task assignment and tracking
- **Advanced Analytics** - Comprehensive statistics and metrics
- **Health Monitoring** - Agent health checks and auto-recovery

### Advanced Remote Control Features
- **Bulk Operations** - Execute commands across multiple agents
- **Command Scheduling** - Schedule commands for future execution
- **Script Deployment** - Deploy and execute custom scripts
- **Health Monitoring** - Comprehensive agent health tracking
- **Command History** - Track and replay command executions
- **Auto-Recovery** - Automatic agent recovery actions

### Technical Features
- **Prometheus Metrics** - Performance monitoring and alerting
- **Redis Caching** - Real-time data caching (optional)
- **SQLite Database** - Persistent data storage
- **Rate Limiting** - API protection and throttling
- **CORS Support** - Cross-origin resource sharing

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)

```bash
# Clone or download the modular code
cd enhanced_node

# Run the automated setup script
python setup_and_run.py
```

### Method 2: Manual Setup

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the server
python -m enhanced_node.main
```

### Method 3: Direct Execution

```bash
# If you have all dependencies installed
python -m enhanced_node.main
```

## 🌐 Access Points

Once running, the server provides:

- **Dashboard**: http://localhost:5000
- **Metrics**: http://localhost:8091
- **API v3**: http://localhost:5000/api/v3/
- **API v5**: http://localhost:5000/api/v5/remote/

## 📋 Dependencies

```txt
Flask==2.3.2
Flask-Cors==4.0.0
Flask-SocketIO==5.3.6
Flask-Limiter==3.5.0
requests==2.31.0
SQLAlchemy==2.0.30
psutil==5.9.8
numpy==1.26.4
pandas==2.2.2
prometheus-client==0.20.0
redis==5.0.3
```

## 🏗️ Architecture Details

### Modular Benefits

1. **Separation of Concerns** - Each module has a specific responsibility
2. **Maintainability** - Easy to update individual components
3. **Testability** - Modules can be tested independently
4. **Scalability** - Components can be scaled or replaced individually
5. **Readability** - Clear structure and organization

### Key Components

#### Core Server (`core/server.py`)
- Main server class managing all components
- Flask and SocketIO integration
- Metrics collection and health monitoring

#### Database Layer (`core/database.py`)
- SQLAlchemy models for all data structures
- Database operations and migrations
- Data cleanup and maintenance

#### Control Systems (`control/`)
- **Task Manager**: Centralized task control and assignment
- **Remote Manager**: Advanced remote control capabilities

#### API Routes (`routes/`)
- **API v3**: Core agent management endpoints
- **API v5**: Advanced remote control endpoints

#### WebSocket Events (`websocket/events.py`)
- Real-time communication with agents and dashboard
- Event-driven architecture for live updates

#### Models (`models/`)
- Data classes and structures
- Type definitions and validation

#### Utilities (`utils/`)
- Shared functionality and helpers
- Logging and serialization utilities

## 🔧 Configuration

All configuration is centralized in `config/settings.py`:

```python
# Node Configuration
NODE_VERSION = "3.4.0-advanced-remote-control"
NODE_PORT = 5000
NODE_ID = f"enhanced-node-{uuid.uuid4().hex[:12]}"

# Directory Configuration  
LOG_DIR = "logs"
DATABASE_PATH = "enhanced_node_server.db"
AGENT_SCRIPTS_DIR = "agent_scripts"
COMMAND_HISTORY_DIR = "command_history"

# Service Configuration
METRICS_PORT = 8091
DEFAULT_RATE_LIMITS = ["1000 per hour", "100 per minute"]
```

## 🎮 Advanced Features Usage

### Bulk Operations
```python
# Send bulk command to multiple agents
POST /api/v5/remote/bulk-operation
{
    "operation_type": "restart_agent",
    "target_agents": ["agent1", "agent2", "agent3"],
    "parameters": {"delay_seconds": 5}
}
```

### Command Scheduling
```python
# Schedule a command for future execution
POST /api/v5/remote/schedule-command
{
    "agent_id": "agent1",
    "command_type": "backup_data", 
    "scheduled_time": "2025-06-08T15:30:00Z",
    "repeat_interval": 3600,
    "max_repeats": 5
}
```

### Script Deployment
```python
# Deploy custom script to agents
POST /api/v5/remote/deploy-script
{
    "script_name": "system_check",
    "script_content": "print('System check complete')",
    "script_type": "python",
    "target_agents": ["agent1", "agent2"]
}
```

## 📊 Monitoring & Metrics

The server provides comprehensive monitoring:

- **Prometheus Metrics** on port 8091
- **Real-time Dashboard** with live agent status
- **Health Checks** with automatic recovery
- **Performance Tracking** and history
- **Command Execution** logs and replay

## 🛠️ Development

### Adding New Features

1. **Models**: Add data structures in `models/`
2. **Database**: Add tables in `core/database.py`
3. **API Routes**: Add endpoints in `routes/`
4. **WebSocket Events**: Add real-time events in `websocket/events.py`
5. **Business Logic**: Add controllers in `control/`

### Testing

Each module can be tested independently:

```python
# Test database models
from core.database import EnhancedNodeDatabase
db = EnhancedNodeDatabase(":memory:")

# Test task manager
from control.task_manager import TaskControlManager
task_manager = TaskControlManager(mock_server)

# Test remote control
from control.remote_manager import AdvancedRemoteControlManager
remote_manager = AdvancedRemoteControlManager(mock_server)
```

## 🔄 Migration from Monolithic

This modular version maintains 100% compatibility with the original monolithic script:

- ✅ All API endpoints preserved
- ✅ All WebSocket events maintained  
- ✅ All database schemas identical
- ✅ All advanced features working
- ✅ All configuration options available

## 🚀 Production Deployment

For production use:

1. **Environment Variables**: Set configuration via environment
2. **External Database**: Use PostgreSQL instead of SQLite
3. **Redis**: Enable Redis for better caching
4. **Reverse Proxy**: Use nginx or similar
5. **Process Manager**: Use systemd, supervisor, or PM2
6. **Monitoring**: Set up Prometheus and Grafana

## 📝 Logs

Logs are organized by component:

- `logs/enhanced_node_server_advanced.log` - Main server logs
- `logs/task_control.log` - Task management logs  
- `logs/advanced_remote_control.log` - Remote control logs

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the enhanced_node/ directory
2. **Port Conflicts**: Change NODE_PORT in config/settings.py
3. **Database Errors**: Delete existing .db file to reset
4. **Permission Errors**: Check write access to logs/ directory

### Getting Help

1. Check the logs in the `logs/` directory
2. Verify all dependencies are installed
3. Ensure Python 3.7+ is being used
4. Check that all required directories exist

## 🎉 Success!

You now have a fully modular, maintainable, and scalable version of the Enhanced Node Server with all original functionality preserved and organized in a clean architectural structure.

The system provides enterprise-grade agent management, advanced remote control capabilities, and comprehensive monitoring - all in a modular design that's easy to understand, maintain, and extend.
