# enhanced_node/integrations/orchestrator_client.py
"""
Orchestrator Integration Client for Enhanced Nodes
This module enables nodes to communicate with the Web4AI Orchestrator
"""

import requests
import json
import time
import threading
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import psutil
import uuid

class OrchestratorClient:
    """Client for integrating Enhanced Nodes with Web4AI Orchestrator"""
    
    def __init__(self, node_server, orchestrator_url: str = "http://localhost:9000"):
        self.node_server = node_server
        self.orchestrator_url = orchestrator_url.rstrip('/')
        self.node_id = f"enhanced_node_{uuid.uuid4().hex[:8]}"
        self.registered = False
        self.heartbeat_thread = None
        self.heartbeat_interval = 30  # seconds
        self.logger = logging.getLogger(__name__)
        
        # Node capabilities based on enhanced_node features
        self.capabilities = [
            "agent_management",
            "task_control", 
            "remote_management",
            "ai_operations",
            "blockchain_support",
            "websocket_communication",
            "real_time_monitoring",
            "bulk_operations",
            "script_deployment"
        ]
    
    def register_with_orchestrator(self) -> bool:
        """Register this node with the orchestrator"""
        try:
            # Get current node status
            node_stats = self._get_node_status()
            
            registration_data = {
                'node_id': self.node_id,
                'host': self.node_server.config.get('NODE_HOST', 'localhost'),
                'port': self.node_server.config.get('NODE_PORT', 5000),
                'capabilities': self.capabilities,
                'agents': self._get_agent_list(),
                'node_type': 'enhanced_node',
                'version': self.node_server.config.get('NODE_VERSION', '1.0.0'),
                'api_versions': ['v3', 'v4', 'v5', 'v6'],
                'features': {
                    'task_control': True,
                    'remote_management': True,
                    'websocket_support': True,
                    'monitoring': True,
                    'security': True
                },
                'performance': node_stats
            }
            
            response = requests.post(
                f"{self.orchestrator_url}/api/v1/nodes/{self.node_id}/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    self.registered = True
                    self.logger.info(f"✅ Successfully registered with orchestrator: {self.node_id}")
                    self._start_heartbeat_thread()
                    return True
                else:
                    self.logger.error(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
                    return False
            else:
                self.logger.error(f"❌ Registration HTTP error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.logger.error(f"❌ Cannot connect to orchestrator at {self.orchestrator_url}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Registration error: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to orchestrator"""
        if not self.registered:
            return False
            
        try:
            heartbeat_data = {
                'node_id': self.node_id,
                'status': 'active',
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': self._get_cpu_usage(),
                'memory_usage': self._get_memory_usage(),
                'agents_status': self._get_agents_status(),
                'load_score': self._calculate_load_score(),
                'active_tasks': self._get_active_tasks_count(),
                'performance_metrics': self._get_performance_metrics(),
                'health_status': self._get_health_status()
            }
            
            response = requests.post(
                f"{self.orchestrator_url}/api/v1/nodes/{self.node_id}/heartbeat",
                json=heartbeat_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    self.logger.debug(f"💓 Heartbeat sent successfully")
                    return True
                else:
                    self.logger.warning(f"⚠️ Heartbeat rejected: {result.get('error', 'Unknown error')}")
                    return False
            else:
                self.logger.warning(f"⚠️ Heartbeat HTTP error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"⚠️ Heartbeat network error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Heartbeat error: {e}")
            return False
    
    def _start_heartbeat_thread(self):
        """Start the heartbeat thread"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            return
            
        def heartbeat_worker():
            while self.registered:
                try:
                    self.send_heartbeat()
                    time.sleep(self.heartbeat_interval)
                except Exception as e:
                    self.logger.error(f"Heartbeat thread error: {e}")
                    time.sleep(5)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()
        self.logger.info("💓 Heartbeat thread started")
    
    def stop_heartbeat(self):
        """Stop heartbeat and unregister"""
        self.registered = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        self.logger.info("🛑 Heartbeat stopped")
    
    def _get_node_status(self) -> Dict[str, Any]:
        """Get comprehensive node status"""
        return {
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
            'load_score': self._calculate_load_score(),
            'agents_count': len(self.node_server.agents),
            'active_tasks': self._get_active_tasks_count(),
            'uptime': time.time() - getattr(self.node_server, 'start_time', time.time())
        }
    
    def _get_agent_list(self) -> List[Dict[str, Any]]:
        """Get list of agents managed by this node"""
        agents = []
        for agent_id, agent_info in self.node_server.agents.items():
            agents.append({
                'agent_id': agent_id,
                'name': agent_info.get('name', 'Unknown'),
                'agent_type': agent_info.get('agent_type', 'ultimate'),
                'status': self.node_server.agent_status.get(agent_id, {}).get('status', 'unknown'),
                'capabilities': agent_info.get('capabilities', []),
                'version': agent_info.get('version', '1.0.0'),
                'host': agent_info.get('host', 'localhost'),
                'port': agent_info.get('port', 8080)
            })
        return agents
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def _get_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status_summary = {
            'total_agents': len(self.node_server.agents),
            'online_agents': 0,
            'offline_agents': 0,
            'busy_agents': 0,
            'error_agents': 0
        }
        
        for agent_id in self.node_server.agents.keys():
            agent_status = self.node_server.agent_status.get(agent_id, {}).get('status', 'unknown')
            if agent_status == 'online':
                status_summary['online_agents'] += 1
            elif agent_status == 'offline':
                status_summary['offline_agents'] += 1
            elif agent_status == 'busy':
                status_summary['busy_agents'] += 1
            else:
                status_summary['error_agents'] += 1
        
        return status_summary
    
    def _calculate_load_score(self) -> float:
        """Calculate node load score (0-100, lower is better)"""
        try:
            cpu_weight = 0.4
            memory_weight = 0.3
            task_weight = 0.3
            
            cpu_usage = self._get_cpu_usage()
            memory_usage = self._get_memory_usage()
            
            # Task load (assuming max 10 concurrent tasks)
            active_tasks = self._get_active_tasks_count()
            task_load = min(active_tasks * 10, 100)
            
            load_score = (cpu_usage * cpu_weight + 
                         memory_usage * memory_weight + 
                         task_load * task_weight)
            
            return round(load_score, 2)
        except:
            return 50.0  # Default moderate load
    
    def _get_active_tasks_count(self) -> int:
        """Get count of active tasks"""
        try:
            if hasattr(self.node_server, 'task_control') and self.node_server.task_control:
                return len(getattr(self.node_server.task_control, 'active_tasks', {}))
            return 0
        except:
            return 0
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        try:
            return {
                'requests_per_minute': getattr(self.node_server, 'requests_per_minute', 0),
                'avg_response_time': getattr(self.node_server, 'avg_response_time', 0.0),
                'success_rate': getattr(self.node_server, 'success_rate', 100.0),
                'error_rate': getattr(self.node_server, 'error_rate', 0.0),
                'websocket_connections': getattr(self.node_server, 'websocket_connections', 0)
            }
        except:
            return {}
    
    def _get_health_status(self) -> str:
        """Get overall health status"""
        try:
            cpu_usage = self._get_cpu_usage()
            memory_usage = self._get_memory_usage()
            
            if cpu_usage > 90 or memory_usage > 90:
                return 'critical'
            elif cpu_usage > 70 or memory_usage > 70:
                return 'warning'
            else:
                return 'healthy'
        except:
            return 'unknown'

# Integration helper functions
def add_orchestrator_integration(node_server, orchestrator_url: str = None):
    """Add orchestrator integration to an existing node server"""
    if orchestrator_url is None:
        orchestrator_url = node_server.config.get('ORCHESTRATOR_URL', 'http://localhost:9000')
    
    # Create orchestrator client
    orchestrator_client = OrchestratorClient(node_server, orchestrator_url)
    node_server.orchestrator_client = orchestrator_client
    
    # Add shutdown handler
    original_shutdown = getattr(node_server, 'shutdown', None)
    
    def enhanced_shutdown():
        if hasattr(node_server, 'orchestrator_client'):
            node_server.orchestrator_client.stop_heartbeat()
        if original_shutdown:
            original_shutdown()
    
    node_server.shutdown = enhanced_shutdown
    
    return orchestrator_client