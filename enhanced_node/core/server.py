import os
import redis
import statistics
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, Any

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, Gauge, start_http_server

from config.settings import (
    NODE_ID, NODE_VERSION, NODE_PORT, DATABASE_PATH,
    MANAGER_HOST, MANAGER_PORT, DEFAULT_RATE_LIMITS, METRICS_PORT
)
from core.database import EnhancedNodeDatabase
from control.task_manager import TaskControlManager
from control.remote_manager import AdvancedRemoteControlManager
from models.agents import EnhancedAgentInfo, EnhancedAgentStatus
from utils.logger import get_server_logger
from utils.serialization import serialize_for_json


class EnhancedNodeServer:
    """Enhanced Node Server with Advanced Remote Control"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=DEFAULT_RATE_LIMITS
        )
        
        # Setup logging
        self.logger = get_server_logger()
        
        # Initialize components
        self.db = EnhancedNodeDatabase(DATABASE_PATH)
        self.agents: Dict[str, EnhancedAgentInfo] = {}
        self.agent_status: Dict[str, EnhancedAgentStatus] = {}
        self.registered_with_manager = False
        self.running = False
        
        # Control managers
        self.task_control = TaskControlManager(self)
        self.advanced_remote_control = AdvancedRemoteControlManager(self)
        
        # Performance tracking
        self.performance_history = defaultdict(lambda: deque(maxlen=100))
        self.task_queue = deque()
        
        # Prometheus metrics
        self.metrics = {
            'agents_total': Gauge('node_agents_total', 'Total agents connected'),
            'agents_online': Gauge('node_agents_online', 'Online agents'),
            'tasks_running': Gauge('node_tasks_running', 'Tasks currently running'),
            'tasks_completed_total': Counter('node_tasks_completed_total', 'Total tasks completed'),
            'ai_models_total': Gauge('node_ai_models_total', 'Total AI models loaded'),
            'blockchain_balance_total': Gauge('node_blockchain_balance_total', 'Total blockchain balance'),
            'avg_efficiency': Gauge('node_avg_efficiency', 'Average agent efficiency'),
            'commands_total': Counter('node_commands_total', 'Total remote commands sent'),
            'configurations_deployed': Counter('node_configurations_deployed', 'Total configurations deployed'),
            'bulk_operations_total': Counter('node_bulk_operations_total', 'Total bulk operations'),
            'health_checks_total': Counter('node_health_checks_total', 'Total health checks'),
            'scripts_deployed_total': Counter('node_scripts_deployed_total', 'Total scripts deployed')
        }
        
        # Redis for real-time data
        self.redis_client = self._init_redis()
        
        # Manager connection info
        self.manager_url = f"http://{MANAGER_HOST}:{MANAGER_PORT}"
        
        # Start metrics server
        self._start_metrics_server()
        
        self.logger.info(f"Enhanced Node Server {NODE_ID} v{NODE_VERSION} initialized")
        self.logger.info("✅ Modular architecture enabled")
        self.logger.info("🎮 Advanced remote control features available")
    
    def _init_redis(self):
        """Initialize Redis for real-time caching"""
        try:
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            self.logger.info("Redis connected for real-time caching")
            return client
        except:
            self.logger.warning("Redis not available, using in-memory cache")
            return None
    
    def _start_metrics_server(self):
        """Start Prometheus metrics server"""
        try:
            start_http_server(METRICS_PORT)
            self.logger.info(f"Prometheus metrics server started on :{METRICS_PORT}")
        except Exception as e:
            self.logger.warning(f"Metrics server failed: {e}")
    
    def get_enhanced_node_stats(self) -> Dict[str, Any]:
        """Calculate enhanced node statistics"""
        total_agents = len(self.agents)
        online_agents = sum(1 for s in self.agent_status.values() 
                           if s.status == "online" and s.last_heartbeat and 
                           (datetime.now() - s.last_heartbeat).seconds < 120)
        
        # Task statistics
        total_tasks_running = sum(s.tasks_running for s in self.agent_status.values())
        total_tasks_completed = sum(s.tasks_completed for s in self.agent_status.values())
        total_tasks_failed = sum(s.tasks_failed for s in self.agent_status.values())
        
        # System metrics
        avg_cpu = sum(s.cpu_percent for s in self.agent_status.values()) / max(total_agents, 1)
        avg_memory = sum(s.memory_percent for s in self.agent_status.values()) / max(total_agents, 1)
        avg_gpu = sum(s.gpu_percent for s in self.agent_status.values()) / max(total_agents, 1)
        
        # AI metrics
        total_ai_models = sum(s.ai_models_loaded for s in self.agent_status.values())
        total_ai_inferences = sum(s.ai_inference_count for s in self.agent_status.values())
        agents_with_gpu = sum(1 for a in self.agents.values() if a.gpu_available)
        
        # Blockchain metrics
        total_blockchain_balance = sum(s.blockchain_balance for s in self.agent_status.values())
        total_blockchain_txs = sum(s.blockchain_transactions for s in self.agent_status.values())
        blockchain_enabled_agents = sum(1 for a in self.agents.values() if a.blockchain_enabled)
        
        # Performance metrics
        avg_efficiency = sum(s.efficiency_score for s in self.agent_status.values()) / max(total_agents, 1)
        
        # Task control metrics
        task_stats = self.task_control.get_task_statistics()
        
        # Advanced remote control metrics
        advanced_stats = self.advanced_remote_control.get_advanced_statistics()
        
        return {
            "node_id": NODE_ID,
            "node_version": NODE_VERSION,
            "timestamp": datetime.now().isoformat(),
            
            # Agent statistics
            "total_agents": total_agents,
            "online_agents": online_agents,
            "offline_agents": total_agents - online_agents,
            
            # Task statistics
            "total_tasks_running": total_tasks_running,
            "total_tasks_completed": total_tasks_completed,
            "total_tasks_failed": total_tasks_failed,
            "success_rate": round((total_tasks_completed / max(total_tasks_completed + total_tasks_failed, 1)) * 100, 2),
            
            # System metrics
            "avg_cpu_percent": round(avg_cpu, 2),
            "avg_memory_percent": round(avg_memory, 2),
            "avg_gpu_percent": round(avg_gpu, 2),
            
            # AI metrics
            "total_ai_models": total_ai_models,
            "total_ai_inferences": total_ai_inferences,
            "agents_with_gpu": agents_with_gpu,
            "gpu_utilization": round(avg_gpu, 2),
            
            # Blockchain metrics
            "total_blockchain_balance": round(total_blockchain_balance, 6),
            "total_blockchain_transactions": total_blockchain_txs,
            "blockchain_enabled_agents": blockchain_enabled_agents,
            
            # Performance metrics
            "avg_efficiency_score": round(avg_efficiency, 2),
            
            # Health indicators
            "health_score": self.calculate_health_score(),
            "manager_connected": self.registered_with_manager,
            
            # Task control metrics
            "task_control_enabled": True,
            "central_tasks": task_stats,
            
            # Remote management metrics
            "remote_management_enabled": True,
            
            # Advanced remote control metrics
            "advanced_control_enabled": True,
            "advanced_control": advanced_stats
        }
    
    def get_ai_summary(self) -> Dict[str, Any]:
        """Get AI capabilities summary"""
        ai_models = defaultdict(int)
        inference_counts = []
        training_active = 0
        
        for agent in self.agents.values():
            for model in agent.ai_models:
                ai_models[model] += 1
        
        for status in self.agent_status.values():
            if status.ai_inference_count > 0:
                inference_counts.append(status.ai_inference_count)
            if status.neural_training_active:
                training_active += 1
        
        return {
            "total_unique_models": len(ai_models),
            "model_distribution": dict(ai_models),
            "total_inferences": sum(inference_counts),
            "avg_inferences_per_agent": statistics.mean(inference_counts) if inference_counts else 0,
            "agents_training": training_active,
            "gpu_agents": sum(1 for a in self.agents.values() if a.gpu_available)
        }
    
    def get_blockchain_summary(self) -> Dict[str, Any]:
        """Get blockchain capabilities summary"""
        total_balance = sum(s.blockchain_balance for s in self.agent_status.values())
        total_transactions = sum(s.blockchain_transactions for s in self.agent_status.values())
        enabled_agents = sum(1 for a in self.agents.values() if a.blockchain_enabled)
        
        wallet_addresses = [s.wallet_address for s in self.agent_status.values() if s.wallet_address]
        
        return {
            "enabled_agents": enabled_agents,
            "total_balance": round(total_balance, 6),
            "total_transactions": total_transactions,
            "unique_wallets": len(set(wallet_addresses)),
            "avg_balance_per_agent": round(total_balance / max(enabled_agents, 1), 6)
        }
    
    def calculate_health_score(self) -> float:
        """Calculate overall node health score"""
        if not self.agents:
            return 100.0
        
        online_ratio = len([s for s in self.agent_status.values() if s.status == "online"]) / len(self.agents)
        avg_efficiency = sum(s.efficiency_score for s in self.agent_status.values()) / len(self.agent_status)
        
        total_completed = sum(s.tasks_completed for s in self.agent_status.values())
        total_failed = sum(s.tasks_failed for s in self.agent_status.values())
        success_rate = total_completed / max(total_completed + total_failed, 1)
        
        health_score = (online_ratio * 40 + avg_efficiency * 0.4 + success_rate * 20)
        return min(100.0, max(0.0, health_score))
    
    def _update_prometheus_metrics(self):
        """Update Prometheus metrics"""
        stats = self.get_enhanced_node_stats()
        
        self.metrics['agents_total'].set(stats['total_agents'])
        self.metrics['agents_online'].set(stats['online_agents'])
        self.metrics['tasks_running'].set(stats['total_tasks_running'])
        self.metrics['ai_models_total'].set(stats['total_ai_models'])
        self.metrics['blockchain_balance_total'].set(stats['total_blockchain_balance'])
        self.metrics['avg_efficiency'].set(stats['avg_efficiency_score'])
    
    def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent"""
        agent_id = agent_data.get('agent_id') or agent_data.get('server_id')
        if not agent_id:
            raise ValueError("agent_id required")
        
        current_time = datetime.now()
        
        agent = EnhancedAgentInfo(
            id=agent_id,
            name=agent_data.get('name', f"ultimate-agent-{agent_id}"),
            host=agent_data.get('host', '127.0.0.1'),
            version=agent_data.get('version', 'unknown'),
            agent_type=agent_data.get('agent_type', 'ultimate'),
            capabilities=agent_data.get('capabilities', []),
            ai_models=agent_data.get('ai_models', []),
            plugins=agent_data.get('plugins', []),
            features=agent_data.get('features', []),
            gpu_available=agent_data.get('gpu_available', False),
            blockchain_enabled=agent_data.get('blockchain_enabled', False),
            cloud_enabled=agent_data.get('cloud_enabled', False),
            security_enabled=agent_data.get('security_enabled', False),
            registered_at=current_time
        )
        
        # Store agent
        self.agents[agent_id] = agent
        self.agent_status[agent_id] = EnhancedAgentStatus(id=agent_id)
        
        # Store in database
        from core.database import Agent
        db_agent = Agent(
            id=agent.id,
            name=agent.name,
            host=agent.host,
            version=agent.version,
            agent_type=agent.agent_type,
            capabilities=agent.capabilities,
            ai_models=agent.ai_models,
            plugins=agent.plugins,
            features=agent.features,
            gpu_available=agent.gpu_available,
            blockchain_enabled=agent.blockchain_enabled,
            cloud_enabled=agent.cloud_enabled,
            security_enabled=agent.security_enabled,
            registered_at=current_time,
            last_seen=current_time
        )
        
        self.db.session.merge(db_agent)
        self.db.session.commit()
        
        # Update metrics
        self.metrics['agents_total'].set(len(self.agents))
        
        # Cache in Redis
        if self.redis_client:
            agent_serializable = serialize_for_json(agent)
            self.redis_client.setex(f'agent:{agent_id}', 3600, str(agent_serializable))
        
        self.logger.info(f"Agent registered: {agent_id} v{agent.version}")
        
        # Broadcast update
        self.socketio.emit('ultimate_agent_registered', {
            'agent_id': agent_id,
            'agent_type': agent.agent_type,
            'features': agent.features,
            'timestamp': current_time.isoformat()
        }, room='dashboard')
        
        return {
            "success": True,
            "agent_id": agent_id,
            "node_id": NODE_ID,
            "node_version": NODE_VERSION,
            "message": "Agent registered successfully",
            "features_supported": ["ai", "blockchain", "cloud", "security", "plugins"],
            "task_control_available": True,
            "remote_management_available": True,
            "advanced_control_available": True
        }
    
    def process_agent_heartbeat(self, heartbeat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent heartbeat"""
        agent_id = heartbeat_data.get('server_id') or heartbeat_data.get('agent_id')
        
        if not agent_id or agent_id not in self.agents:
            raise ValueError("Agent not registered")
        
        current_time = datetime.now()
        
        # Update enhanced agent status
        status = self.agent_status[agent_id]
        status.status = heartbeat_data.get("status", "online")
        status.cpu_percent = heartbeat_data.get("cpu_percent", 0.0)
        status.memory_mb = heartbeat_data.get("memory_mb", 0.0)
        status.memory_percent = heartbeat_data.get("memory_percent", 0.0)
        status.gpu_percent = heartbeat_data.get("gpu_percent", 0.0)
        status.network_io = heartbeat_data.get("network_io", 0.0)
        status.tasks_running = heartbeat_data.get("tasks_running", 0)
        status.tasks_completed = heartbeat_data.get("tasks_completed", 0)
        status.tasks_failed = heartbeat_data.get("tasks_failed", 0)
        status.current_tasks = heartbeat_data.get("current_tasks", {})
        status.ai_models_loaded = heartbeat_data.get("ai_models_loaded", 0)
        status.ai_inference_count = heartbeat_data.get("ai_inference_count", 0)
        status.neural_training_active = heartbeat_data.get("neural_training_active", False)
        status.blockchain_balance = heartbeat_data.get("blockchain_balance", 0.0)
        status.blockchain_transactions = heartbeat_data.get("blockchain_transactions", 0)
        status.wallet_address = heartbeat_data.get("wallet_address", "")
        status.performance_prediction = heartbeat_data.get("performance_prediction", 80.0)
        status.efficiency_score = heartbeat_data.get("efficiency_score", 100.0)
        status.last_heartbeat = current_time
        
        # Store enhanced heartbeat
        from core.database import AgentHeartbeat, Agent
        heartbeat = AgentHeartbeat(
            agent_id=agent_id,
            timestamp=current_time,
            status=status.status,
            cpu_percent=status.cpu_percent,
            memory_mb=status.memory_mb,
            memory_percent=status.memory_percent,
            gpu_percent=status.gpu_percent,
            network_io=status.network_io,
            tasks_running=status.tasks_running,
            tasks_completed=status.tasks_completed,
            tasks_failed=status.tasks_failed,
            current_tasks=status.current_tasks,
            ai_models_loaded=status.ai_models_loaded,
            ai_inference_count=status.ai_inference_count,
            neural_training_active=status.neural_training_active,
            blockchain_balance=status.blockchain_balance,
            blockchain_transactions=status.blockchain_transactions,
            performance_prediction=status.performance_prediction,
            efficiency_score=status.efficiency_score
        )
        
        self.db.session.add(heartbeat)
        
        # Update agent last_seen
        agent_record = self.db.session.query(Agent).filter_by(id=agent_id).first()
        if agent_record:
            agent_record.last_seen = current_time
            agent_record.total_tasks_completed = status.tasks_completed
            agent_record.total_tasks_failed = status.tasks_failed
            agent_record.efficiency_score = status.efficiency_score
        
        self.db.session.commit()
        
        # Update performance history
        self.performance_history[agent_id].append({
            'timestamp': current_time.isoformat(),
            'cpu': status.cpu_percent,
            'memory': status.memory_percent,
            'efficiency': status.efficiency_score
        })
        
        # Update metrics
        self._update_prometheus_metrics()
        
        # Cache in Redis
        if self.redis_client:
            status_serializable = serialize_for_json(status)
            self.redis_client.setex(f'status:{agent_id}', 120, str(status_serializable))
        
        # Broadcast real-time update
        self.socketio.emit('ultimate_agent_status_update', {
            'agent_id': agent_id,
            'status': serialize_for_json(status),
            'timestamp': current_time.isoformat()
        }, room='dashboard')
        
        return {
            "success": True,
            "node_id": NODE_ID,
            "next_heartbeat": 30,
            "supported_features": ["ai", "blockchain", "cloud", "security"],
            "task_control_available": True,
            "remote_management_available": True,
            "advanced_control_available": True
        }
    
    def start(self):
        """Start the node server"""
        self.running = True
        
        # Start background services
        self.task_control.start_task_control_services()
        self.advanced_remote_control.start_advanced_services()
        
        self.logger.info("Enhanced Node Server started with advanced capabilities")
    
    def stop(self):
        """Stop the node server"""
        self.running = False
        self.advanced_remote_control.scheduler_running = False
        self.advanced_remote_control.health_monitor_running = False
        
        if self.db:
            self.db.close()
        
        self.logger.info("Enhanced Node Server stopped")