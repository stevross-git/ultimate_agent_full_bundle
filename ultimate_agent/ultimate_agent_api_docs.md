# 🚀 Ultimate Agent API Documentation

## Overview

The Enhanced Ultimate Pain Network Agent provides a comprehensive REST API and WebSocket interface for managing AI training, blockchain operations, task execution, and system monitoring. This API follows RESTful principles and supports both JSON and real-time communication.

**Base URL:** `http://localhost:8080/api`
**API Version:** v4 (latest), with backward compatibility for v3 and v1
**Content-Type:** `application/json`

---

## 📚 Table of Contents

1. [Authentication](#authentication)
2. [Agent Status & Info](#agent-status--info)
3. [Task Management](#task-management)
4. [AI Operations](#ai-operations)
5. [Blockchain Operations](#blockchain-operations)
6. [System Monitoring](#system-monitoring)
7. [Remote Management](#remote-management)
8. [Database Operations](#database-operations)
9. [WebSocket Events](#websocket-events)
10. [Error Handling](#error-handling)
11. [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

### API Key Authentication
```http
Authorization: Bearer <api_key>
```

### Generate API Token
```http
POST /api/auth/token
Content-Type: application/json

{
  "agent_id": "agent-123",
  "permissions": ["read", "write", "admin"]
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "permissions": ["read", "write", "admin"]
}
```

---

## 📊 Agent Status & Info

### Get Basic Agent Status
```http
GET /api/stats
```

**Response:**
```json
{
  "agent_id": "ultimate-a1b2c3d4",
  "running": true,
  "registered": true,
  "current_tasks": 2,
  "tasks_completed": 157,
  "tasks_failed": 3,
  "total_earnings": 0.2847,
  "uptime_hours": 48.7,
  "ai_models_loaded": 7,
  "modular_architecture": true
}
```

### Get Enhanced Agent Status
```http
GET /api/v3/stats/enhanced
```

**Response:**
```json
{
  "agent_id": "ultimate-a1b2c3d4",
  "running": true,
  "registered": true,
  "current_tasks": 2,
  "stats": {
    "tasks_completed": 157,
    "tasks_failed": 3,
    "total_earnings": 0.2847,
    "start_time": 1640995200
  },
  "ai_status": {
    "models_loaded": 7,
    "gpu_available": true,
    "training_engine_active": true,
    "active_training_sessions": 1
  },
  "blockchain_status": {
    "wallet_initialized": true,
    "smart_contracts_enabled": true,
    "connected_networks": 3,
    "transaction_pool_size": 5
  },
  "modular_architecture": true,
  "advanced_features": true,
  "dashboard_connected": true
}
```

### Get System Information
```http
GET /api/system
```

**Response:**
```json
{
  "cpu_percent": 23.5,
  "memory_percent": 45.2,
  "memory_mb": 2048.7,
  "status": "online",
  "platform": "Windows",
  "python_version": "3.9.7",
  "architecture": "AMD64"
}
```

### Get Agent Capabilities
```http
GET /api/capabilities
```

**Response:**
```json
{
  "agent_id": "ultimate-a1b2c3d4",
  "name": "ultimate-agent-a1b2c3d4",
  "host": "DESKTOP-ABC123",
  "version": "3.0.0-enhanced",
  "agent_type": "ultimate",
  "capabilities": ["ai", "blockchain", "cloud", "security"],
  "ai_models": ["sentiment", "classification", "regression", "transformer", "cnn"],
  "gpu_available": true,
  "blockchain_enabled": true,
  "enhanced_features": true,
  "task_types": ["neural_network_training", "blockchain_transaction", "data_processing"],
  "dashboard_enabled": true,
  "websocket_enabled": true,
  "api_version": "v4",
  "modular_architecture": true
}
```

### Get Current Activity
```http
GET /api/activity
```

**Response:**
```json
{
  "tasks_running": 2,
  "tasks_completed": 157,
  "tasks_failed": 3,
  "activity_level": "high",
  "uptime_hours": 48.7
}
```

### Get Network Status
```http
GET /api/network
```

**Response:**
```json
{
  "node_url": "http://srvnodes.peoplesainetwork.com:5000",
  "registered": true,
  "network_status": "connected",
  "agent_id": "ultimate-a1b2c3d4",
  "connection_quality": "good"
}
```

---

## 🎯 Task Management

### Get Current Tasks
```http
GET /api/tasks
```

**Response:**
```json
{
  "current_tasks": {
    "task-1640995300-1234": {
      "task_id": "task-1640995300-1234",
      "task_type": "neural_network_training",
      "status": "running",
      "progress": 67.5,
      "start_time": "2023-12-31T15:30:00Z",
      "ai_workload": true,
      "details": {
        "epoch": 7,
        "total_epochs": 10,
        "training_loss": 0.342,
        "validation_loss": 0.289,
        "accuracy": 0.897
      }
    }
  },
  "completed_tasks": 157,
  "scheduler_status": {
    "current_tasks": 1,
    "queued_tasks": 0,
    "max_concurrent_tasks": 3,
    "scheduler_running": true
  }
}
```

### Start New Task
```http
POST /api/start_task
Content-Type: application/json

{
  "type": "neural_network_training",
  "config": {
    "epochs": 10,
    "batch_size": 32,
    "learning_rate": 0.001,
    "dataset_size": 5000
  }
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "task-1640995400-5678",
  "task_type": "neural_network_training",
  "estimated_duration": 180,
  "status": "started"
}
```

### Cancel Task
```http
POST /api/cancel_task/task-1640995400-5678
```

**Response:**
```json
{
  "success": true,
  "task_id": "task-1640995400-5678",
  "status": "cancelled"
}
```

### Available Task Types
- `neural_network_training` - Deep neural network training
- `transformer_training` - Transformer model training
- `cnn_training` - Convolutional neural network training
- `reinforcement_learning` - RL agent training
- `federated_learning` - Distributed training
- `hyperparameter_optimization` - Automated hyperparameter tuning
- `gradient_computation` - Gradient computation tasks
- `model_inference_batch` - Batch inference operations
- `blockchain_transaction` - Standard blockchain transactions
- `smart_contract_execution` - Smart contract operations
- `data_preprocessing` - Data preprocessing pipeline
- `sentiment_analysis` - Text sentiment analysis
- `data_processing` - General data processing

---

## 🧠 AI Operations

### Get AI Capabilities
```http
GET /api/v3/ai/capabilities
```

**Response:**
```json
{
  "models_loaded": 7,
  "gpu_available": true,
  "training_engine_active": true,
  "inference_engine_active": true,
  "active_training_sessions": 1,
  "model_types": ["nlp", "vision", "tabular", "rl"],
  "total_model_size": 3,
  "available_models": [
    {
      "name": "sentiment",
      "type": "nlp",
      "status": "loaded",
      "size": "small",
      "accuracy": 0.85
    },
    {
      "name": "classification", 
      "type": "vision",
      "status": "loaded",
      "size": "medium",
      "accuracy": 0.92
    }
  ],
  "training_capabilities": [
    "neural_network_training",
    "transformer_training", 
    "cnn_training",
    "reinforcement_learning"
  ]
}
```

### Get Training Status
```http
GET /api/training
```

**Response:**
```json
{
  "models_training": 1,
  "total_models": 7,
  "training_active": true,
  "gpu_available": true,
  "training_capabilities": [
    "neural_network_training",
    "transformer_training",
    "cnn_training",
    "reinforcement_learning"
  ],
  "advanced_training_enabled": true
}
```

### Run AI Inference
```http
POST /api/ai/inference
Content-Type: application/json

{
  "model": "sentiment",
  "input": "This modular architecture is amazing!",
  "options": {
    "return_confidence": true,
    "return_details": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "model_name": "sentiment",
  "prediction": "positive",
  "confidence": 0.94,
  "sentiment_scores": {
    "positive": 0.94,
    "negative": 0.04,
    "neutral": 0.02
  },
  "processing_time": 0.156,
  "cached": false
}
```

---

## 💰 Blockchain Operations

### Get Enhanced Blockchain Status
```http
GET /api/v3/blockchain/enhanced
```

**Response:**
```json
{
  "wallet": "0xa1b2c3d4e5f6789012345678901234567890abcd",
  "balance": {
    "ETH": 0.2847,
    "PAIN": 150.75,
    "AI": 45.2,
    "BTC": 0.0023,
    "USDC": 25.80
  },
  "connected_networks": 3,
  "smart_contracts": 5,
  "transaction_pool_size": 3,
  "smart_contracts_enabled": true,
  "multi_currency_support": true,
  "network_connections": {
    "ethereum": "connected",
    "polygon": "connected", 
    "binance": "connected"
  }
}
```

### Get Wallet Balance
```http
GET /api/blockchain/balance
```

**Response:**
```json
{
  "balances": {
    "ETH": 0.2847,
    "PAIN": 150.75,
    "AI": 45.2
  },
  "total_value_usd": 487.23,
  "wallet_address": "0xa1b2c3d4e5f6789012345678901234567890abcd"
}
```

### Get Transaction History
```http
GET /api/blockchain/transactions?limit=10&currency=ETH
```

**Response:**
```json
{
  "transactions": [
    {
      "hash": "0x1a2b3c4d5e6f7890123456789012345678901234567890abcdef1234567890abcd",
      "amount": 0.05,
      "currency": "ETH",
      "task_id": "task-1640995300-1234",
      "timestamp": "2023-12-31T16:45:00Z",
      "status": "confirmed",
      "gas_used": 21000,
      "block_number": 18750000
    }
  ],
  "total_count": 157,
  "page": 1,
  "limit": 10
}
```

### Execute Smart Contract
```http
POST /api/blockchain/smart-contract/execute
Content-Type: application/json

{
  "contract_type": "task_rewards",
  "method": "claimReward",
  "params": {
    "amount": 0.25,
    "task_id": "task-1640995400-5678"
  }
}
```

**Response:**
```json
{
  "success": true,
  "transaction_hash": "0x9f8e7d6c5b4a3918273645567890abcdef1234567890abcdef1234567890abcd",
  "gas_used": 45000,
  "block_number": 18750001,
  "contract_address": "0x1234567890abcdef1234567890abcdef12345678",
  "execution_result": {
    "reward_claimed": 0.25,
    "task_id": "task-1640995400-5678",
    "recipient": "0xa1b2c3d4e5f6789012345678901234567890abcd",
    "claim_timestamp": 1640995500
  }
}
```

---

## 📊 System Monitoring

### Get Performance Metrics
```http
GET /api/performance/metrics
```

**Response:**
```json
{
  "timestamp": "2023-12-31T17:00:00Z",
  "cpu_percent": 23.5,
  "memory_percent": 45.2,
  "gpu_percent": 67.8,
  "disk_usage_percent": 78.3,
  "network_io": {
    "bytes_sent": 1048576,
    "bytes_recv": 2097152
  },
  "process": {
    "cpu_percent": 15.2,
    "memory_mb": 512.7,
    "threads": 28,
    "open_files": 45
  },
  "gpu": {
    "available": true,
    "name": "NVIDIA RTX 3080",
    "memory_used_mb": 4096,
    "memory_total_mb": 10240,
    "temperature": 72
  },
  "tasks_running": 2,
  "health_score": 87.5
}
```

### Get Database Statistics
```http
GET /api/database/stats
```

**Response:**
```json
{
  "task_records": 157,
  "performance_metrics": 2880,
  "earnings_records": 89,
  "ai_training_records": 23,
  "database_size_mb": 45.7,
  "tables": [
    "task_records",
    "performance_metrics", 
    "earnings",
    "ai_training_sessions"
  ]
}
```

### Get Health Status
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "health_score": 87.5,
  "components": {
    "cpu": 92.5,
    "memory": 85.0,
    "disk": 78.5,
    "gpu": 89.2
  },
  "alerts": [
    {
      "type": "disk_space",
      "severity": "warning", 
      "message": "Disk usage above 75%",
      "value": 78.3,
      "threshold": 75.0
    }
  ],
  "uptime_seconds": 175320,
  "last_updated": "2023-12-31T17:00:00Z"
}
```

---

## 🎮 Remote Management

### Execute Remote Command
```http
POST /api/v4/remote/command
Content-Type: application/json

{
  "command_type": "restart_agent",
  "parameters": {
    "delay": 5
  },
  "command_id": "cmd-12345"
}
```

**Response:**
```json
{
  "success": true,
  "command_id": "cmd-12345",
  "result": {
    "action": "restart_scheduled",
    "delay": 5,
    "scheduled_at": "2023-12-31T17:05:00Z"
  }
}
```

### Get Available Remote Commands
```http
GET /api/v4/remote/capabilities
```

**Response:**
```json
{
  "commands": [
    "restart_agent",
    "shutdown_agent", 
    "get_status",
    "start_task",
    "cancel_task",
    "update_config",
    "set_cpu_limit",
    "enable_gpu",
    "run_diagnostics",
    "backup_data",
    "update_agent"
  ]
}
```

### Available Remote Commands

#### Lifecycle Management
- `restart_agent` - Restart the agent with optional delay
- `shutdown_agent` - Gracefully shutdown the agent
- `get_status` - Get detailed agent status

#### Task Operations
- `start_task` - Start a new task
- `cancel_task` - Cancel running task
- `pause_task` - Pause task execution
- `resume_task` - Resume paused task
- `set_task_priority` - Change task priority

#### Configuration
- `update_config` - Update configuration values
- `reload_config` - Reload configuration from file
- `deploy_configuration` - Deploy new configuration

#### Performance Tuning
- `set_cpu_limit` - Set CPU usage limit
- `set_memory_limit` - Set memory usage limit
- `enable_gpu` - Enable/disable GPU usage
- `optimize_performance` - Run performance optimization

#### Diagnostics & Maintenance
- `get_detailed_status` - Get comprehensive system status
- `get_logs` - Retrieve recent log entries
- `run_diagnostics` - Run system diagnostics
- `monitor_resources` - Monitor resources for specified duration
- `cleanup_logs` - Clean up old log files
- `backup_data` - Create data backup
- `clear_cache` - Clear system caches
- `update_agent` - Update agent from git repository

---

## 🗄️ Database Operations

### Get Task Records
```http
GET /api/database/tasks?limit=50&task_type=neural_network_training
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "rec-1640995400",
      "task_id": "task-1640995300-1234",
      "task_type": "neural_network_training",
      "start_time": "2023-12-31T15:30:00Z",
      "end_time": "2023-12-31T15:33:00Z",
      "duration": 180.5,
      "success": true,
      "reward": 0.05,
      "ai_result": {
        "final_loss": 0.234,
        "accuracy": 0.897,
        "epochs": 10
      },
      "blockchain_tx": "0x1a2b3c..."
    }
  ],
  "total_count": 157,
  "filtered_count": 23
}
```

### Get Performance History
```http
GET /api/database/performance?hours=24
```

**Response:**
```json
{
  "metrics": [
    {
      "timestamp": "2023-12-31T16:00:00Z",
      "cpu_percent": 25.3,
      "memory_percent": 42.1,
      "gpu_percent": 0.0,
      "task_count": 1,
      "efficiency_score": 92.5
    }
  ],
  "timeframe_hours": 24,
  "data_points": 1440
}
```

---

## 🌐 WebSocket Events

### Connection
```javascript
const socket = io('http://localhost:8080');

socket.on('connect', () => {
    console.log('Connected to Ultimate Agent');
});
```

### Event Types

#### Agent Events
- `connected` - Agent connection established
- `stats_update` - Real-time statistics update
- `enhanced_stats_update` - Enhanced statistics update
- `system_alert` - System alert notification

#### Task Events
- `task_progress` - Task progress update
- `task_completed` - Task completion notification
- `task_assignment` - New task assignment
- `task_assignment_response` - Task assignment response

#### Real-time Data
- `real_time_data` - Real-time system metrics
- `performance_update` - Performance metrics update

### WebSocket API

#### Request Statistics
```javascript
socket.emit('request_stats');
socket.emit('request_enhanced_stats');
```

#### Request Real-time Data
```javascript
socket.emit('request_real_time_data');

socket.on('real_time_data', (data) => {
    console.log('CPU:', data.cpu_percent);
    console.log('Memory:', data.memory_percent);
    console.log('Tasks:', data.tasks_running);
});
```

#### Handle Task Progress
```javascript
socket.on('task_progress', (data) => {
    console.log(`Task ${data.task_id}: ${data.progress}%`);
    if (data.details) {
        console.log('Details:', data.details);
    }
});
```

#### Handle Task Completion
```javascript
socket.on('task_completed', (data) => {
    console.log(`Task ${data.task_id} completed:`, data.success);
    if (data.reward) {
        console.log('Reward earned:', data.reward);
    }
});
```

#### Handle System Alerts
```javascript
socket.on('system_alert', (alert) => {
    console.log(`Alert [${alert.severity}]: ${alert.message}`);
});
```

#### Execute Remote Commands
```javascript
socket.emit('remote_command', {
    command_type: 'get_status',
    parameters: {},
    command_id: 'cmd-' + Date.now()
});

socket.on('remote_command_response', (response) => {
    console.log('Command result:', response);
});
```

---

## ❌ Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "TASK_NOT_FOUND", 
  "details": {
    "task_id": "task-123",
    "timestamp": "2023-12-31T17:00:00Z"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_REQUEST` | Malformed request data | 400 |
| `UNAUTHORIZED` | Authentication required | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `TASK_NOT_FOUND` | Specified task not found | 404 |
| `MODEL_NOT_FOUND` | AI model not found | 404 |
| `RATE_LIMITED` | Rate limit exceeded | 429 |
| `INTERNAL_ERROR` | Internal server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

### Error Examples

#### Task Not Found
```json
{
  "success": false,
  "error": "Task not found",
  "error_code": "TASK_NOT_FOUND",
  "details": {
    "task_id": "invalid-task-123"
  }
}
```

#### Validation Error
```json
{
  "success": false,
  "error": "Invalid task configuration",
  "error_code": "INVALID_REQUEST",
  "details": {
    "field": "epochs",
    "message": "Must be between 1 and 1000"
  }
}
```

#### Rate Limit Error
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_code": "RATE_LIMITED",
  "details": {
    "limit": 100,
    "window": 3600,
    "reset_time": "2023-12-31T18:00:00Z"
  }
}
```

---

## 🚦 Rate Limiting

### Default Limits
- **General API:** 1000 requests per hour
- **Task Operations:** 100 requests per hour  
- **Remote Commands:** 50 requests per hour
- **WebSocket Connections:** 10 per IP

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640999999
X-RateLimit-Window: 3600
```

### Rate Limit Response
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_code": "RATE_LIMITED",
  "details": {
    "limit": 1000,
    "window_seconds": 3600,
    "reset_time": "2023-12-31T18:00:00Z",
    "retry_after": 1800
  }
}
```

---

## 📋 Request/Response Examples

### Complete Task Lifecycle

#### 1. Start Neural Network Training
```bash
curl -X POST http://localhost:8080/api/start_task \
  -H "Content-Type: application/json" \
  -d '{
    "type": "neural_network_training",
    "config": {
      "epochs": 10,
      "batch_size": 32,
      "learning_rate": 0.001,
      "input_dim": 784,
      "hidden_dim": 128,
      "output_dim": 10
    }
  }'
```

#### 2. Monitor Progress (WebSocket)
```javascript
socket.on('task_progress', (data) => {
    // data.task_id, data.progress, data.details
    updateProgressBar(data.progress);
    updateTrainingMetrics(data.details);
});
```

#### 3. Check Task Status
```bash
curl http://localhost:8080/api/tasks
```

#### 4. Handle Completion
```javascript
socket.on('task_completed', (data) => {
    if (data.success) {
        console.log('Training completed successfully!');
        console.log('Final accuracy:', data.result.accuracy);
        console.log('Reward earned:', data.reward);
    }
});
```

### AI Inference Pipeline

#### 1. Check Available Models
```bash
curl http://localhost:8080/api/v3/ai/capabilities
```

#### 2. Run Sentiment Analysis
```bash
curl -X POST http://localhost:8080/api/ai/inference \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sentiment",
    "input": "This API documentation is comprehensive and helpful!",
    "options": {
      "return_confidence": true,
      "return_details": true
    }
  }'
```

### Blockchain Integration

#### 1. Check Wallet Balance
```bash
curl http://localhost:8080/api/v3/blockchain/enhanced
```

#### 2. Execute Smart Contract
```bash
curl -X POST http://localhost:8080/api/blockchain/smart-contract/execute \
  -H "Content-Type: application/json" \
  -d '{
    "contract_type": "task_rewards",
    "method": "claimReward",
    "params": {
      "amount": 0.1,
      "task_id": "task-1640995400-5678"
    }
  }'
```

---

## 🛠️ SDK Examples

### Python SDK Example
```python
import requests
import websocket
import json

class UltimateAgentClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_status(self):
        """Get agent status"""
        response = self.session.get(f"{self.base_url}/api/v3/stats/enhanced")
        return response.json()
    
    def start_task(self, task_type, config=None):
        """Start a new task"""
        data = {"type": task_type}
        if config:
            data["config"] = config
        
        response = self.session.post(
            f"{self.base_url}/api/start_task",
            json=data
        )
        return response.json()
    
    def run_inference(self, model, input_data, options=None):
        """Run AI inference"""
        data = {"model": model, "input": input_data}
        if options:
            data["options"] = options
        
        response = self.session.post(
            f"{self.base_url}/api/ai/inference",
            json=data
        )
        return response.json()

# Usage
client = UltimateAgentClient()

# Check status
status = client.get_status()
print(f"Agent running: {status['running']}")

# Start training task
task = client.start_task("neural_network_training", {
    "epochs": 5,
    "learning_rate": 0.01
})
print(f"Task started: {task['task_id']}")

# Run sentiment analysis
result = client.run_inference("sentiment", "This is great!")
print(f"Sentiment: {result['prediction']} ({result['confidence']:.2f})")
```

### JavaScript SDK Example
```javascript
class UltimateAgentClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
        this.socket = null;
    }
    
    async getStatus() {
        const response = await fetch(`${this.baseUrl}/api/v3/stats/enhanced`);
        return await response.json();
    }
    
    async startTask(taskType, config = {}) {
        const response = await fetch(`${this.baseUrl}/api/start_task`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type: taskType, config})
        });
        return await response.json();
    }
    
    connectWebSocket() {
        this.socket = io(this.baseUrl);
        
        this.socket.on('task_progress', (data) => {
            console.log(`Task ${data.task_id}: ${data.progress}%`);
        });
        
        this.socket.on('task_completed', (data) => {
            console.log(`Task completed: ${data.task_id}`);
        });
        
        return this.socket;
    }
}

// Usage
const client = new UltimateAgentClient();

// Get status
client.getStatus().then(status => {
    console.log('Agent Status:', status);
});

// Start task and monitor progress
client.connectWebSocket();
client.startTask('neural_network_training', {
    epochs: 10,
    batch_size: 32
}).then(result => {
    console.log('Task started:', result.task_id);
});
```

---

## 📈 Performance Guidelines

### Optimal Request Patterns
- Use WebSocket for real-time updates instead of polling
- Batch similar operations when possible
- Cache results locally for frequently accessed data
- Use appropriate pagination for large datasets

### Request Optimization
```javascript
// Good: Use WebSocket for real-time updates
socket.emit('request_real_time_data');

// Avoid: Polling for updates
// setInterval(() => fetch('/api/stats'), 1000); // DON'T DO THIS
```

### Error Retry Logic
```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session
```

---

## 🔒 Security Best Practices

### Authentication
- Always use HTTPS in production
- Rotate API keys regularly
- Use short-lived tokens for sensitive operations
- Implement proper session management

### Input Validation
- Validate all input parameters
- Sanitize file uploads
- Use parameterized queries
- Implement request size limits

### Rate Limiting
- Implement adaptive rate limiting
- Use different limits for different endpoints
- Monitor and alert on suspicious activity
- Implement graceful degradation

---

This comprehensive API documentation provides developers with everything needed to integrate with the Enhanced Ultimate Pain Network Agent. For additional examples, tutorials, and advanced usage patterns, visit our [GitHub repository](https://github.com/ultimate-agent/modular) or join our [community Discord](https://discord.gg/ultimate-agent).