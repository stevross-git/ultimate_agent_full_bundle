#!/usr/bin/env python3
"""
ultimate_agent/core/agent.py
Main agent class - coordinates all modules
"""
# Local AI Integration
try:
    from ..ai.local_models.local_ai_manager import (
        create_local_ai_manager,
        create_local_ai_conversation_manager
    )
    LOCAL_AI_AVAILABLE = True
except ImportError:
    LOCAL_AI_AVAILABLE = False
    print("⚠️ Local AI not available")
import time
import threading
import platform
import uuid
import hashlib
import secrets
try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None
import os
from datetime import datetime
from typing import Dict, Any, Optional

from ..config.config_settings import ConfigManager
from ..ai.models import AIModelManager
from ..blockchain.wallet.security import BlockchainManager
from ..tasks.execution.task_scheduler import TaskScheduler
from ..security.authentication import SecurityManager
from ..storage.database.migrations import DatabaseManager
from ..monitoring.metrics import MonitoringManager
from ..dashboard.web.routes import DashboardManager
from ..network.communication import NetworkManager
from ..network.discovery.service_discovery import DiscoveryClient
from ..plugins import PluginManager
from ..remote.command_handler import RemoteCommandHandler


class UltimatePainNetworkAgent:
    """Main agent class that coordinates all modules"""
    
    def __init__(self, *args, **kwargs):
    # Your existing __init__ code
        super().__init__(*args, **kwargs)
    
    # Add Local AI initialization
    self._initialize_local_ai()

def _initialize_local_ai(self):
    """Initialize Local AI components"""
    if not LOCAL_AI_AVAILABLE:
        self.local_ai_manager = None
        self.local_ai_conversation_manager = None
        return
    
    try:
        print("🧠 Initializing Local AI...")
        
        # Create Local AI Manager
        self.local_ai_manager = create_local_ai_manager(self.config_manager)
        self.local_ai_conversation_manager = create_local_ai_conversation_manager(self.config_manager)
        
        # Enhance existing AI manager if available
        if hasattr(self, 'ai_manager'):
            self._enhance_ai_manager_with_local_ai()
        
        print("✅ Local AI initialized successfully")
        
        # Log hardware info
        hw_info = self.local_ai_manager.get_hardware_info()
        print(f"🖥️ Hardware detected: {hw_info['hardware_type']}")
        
    except Exception as e:
        print(f"⚠️ Local AI initialization failed: {e}")
        self.local_ai_manager = None
        self.local_ai_conversation_manager = None

def _enhance_ai_manager_with_local_ai(self):
    """Enhance existing AI manager with Local AI capabilities"""
    original_run_inference = self.ai_manager.run_inference
    
    async def enhanced_run_inference(model_name: str, input_data, **kwargs):
        # Try Local AI first for certain models or requests
        if (kwargs.get('use_local_ai', True) and 
            self.local_ai_manager and 
            (model_name.startswith('local_') or kwargs.get('prefer_local', False))):
            
            try:
                result = await self.local_ai_manager.generate_response(
                    str(input_data),
                    task_type=kwargs.get('task_type', 'general'),
                    **kwargs
                )
                
                if result['success']:
                    return {
                        'success': True,
                        'prediction': result['response'],
                        'confidence': 0.90,
                        'model_used': result['model_used'],
                        'processing_time': result['processing_time'],
                        'inference_type': 'local_ai',
                        'local_ai': True
                    }
            except Exception as e:
                print(f"Local AI inference failed, falling back: {e}")
        
        # Fallback to original method
        return original_run_inference(model_name, input_data)
    
    # Replace the method
    self.ai_manager.run_inference = enhanced_run_inference

def get_local_ai_status(self) -> Dict[str, Any]:
    """Get Local AI status for API endpoints"""
    if not self.local_ai_manager:
        return {'enabled': False, 'error': 'Local AI not available'}
    
    try:
        status = self.local_ai_manager.get_status()
        stats = self.local_ai_manager.get_stats()
        hardware = self.local_ai_manager.get_hardware_info()
        
        return {
            'enabled': True,
            'status': status,
            'performance': stats['inference_stats'],
            'hardware': {
                'type': hardware['hardware_type'],
                'memory_gb': round(hardware['system_info']['memory_gb'], 1),
                'gpu_available': hardware['system_info']['gpu_info']['available'],
            },
            'current_model': hardware.get('current_model')
        }
        
    except Exception as e:
        return {'enabled': True, 'error': str(e)}
    
    def __init__(self, node_url: str = None, dashboard_port: int = None):
        print(f"🚀 Initializing Enhanced Ultimate Pain Network Agent")
        
        # Initialize core configuration
        self.config_manager = ConfigManager()
        self.agent_id = self._get_or_create_agent_id()
        
        # Initialize all managers
        self.security_manager = SecurityManager(self.config_manager)
        self.blockchain_manager = BlockchainManager(self.config_manager)
        # Pass configuration manager so AIModelManager can access settings
        self.ai_manager = AIModelManager(self.config_manager)
        self.monitoring_manager = MonitoringManager()
        self.plugin_manager = PluginManager()
        self.database_manager = DatabaseManager()
        self.task_scheduler = TaskScheduler(self.ai_manager, self.blockchain_manager)
        self.network_manager = NetworkManager(self.config_manager)
        self.discovery_client = DiscoveryClient()
        self.dashboard_manager = DashboardManager(self)
        self.remote_command_handler = RemoteCommandHandler(self)
        
        # Configuration
        if node_url is None:
            discovered = self.discovery_client.get_best_node(self.network_manager.test_connection)
            node_url = discovered.get('url') if discovered else None

        self.node_url = (
            node_url
            or self.config_manager.get(
                'DEFAULT',
                'node_url',
                fallback='https://srvnodes.peoplesainetwork.com'
            )
        ).rstrip('/')

        self.network_manager.set_node_url(self.node_url)
        self.dashboard_port = (dashboard_port or 
                              int(self.config_manager.get('DEFAULT', 'dashboard_port', fallback='8080')))
        
        # State management
        self.running = False
        self.registered = False
        self.current_tasks = {}
        self.stats = self._load_stats()
        
        print(f"🎯 Enhanced Ultimate Agent {self.agent_id} initialized")
    
    def _get_or_create_agent_id(self) -> str:
        """Generate or load agent ID"""
        agent_file = "ultimate_agent_id.txt"
        
        if os.path.exists(agent_file):
            with open(agent_file, 'r') as f:
                return f.read().strip()
        else:
            mac_address = hex(uuid.getnode())[2:]
            hostname = platform.node()
            random_component = secrets.token_hex(4)
            
            system_string = f"{mac_address}-{hostname}-{random_component}"
            agent_hash = hashlib.sha256(system_string.encode()).hexdigest()[:16]
            agent_id = f"ultimate-{agent_hash}"
            
            with open(agent_file, 'w') as f:
                f.write(agent_id)
            
            return agent_id
    
    def _load_stats(self) -> Dict:
        """Load agent statistics"""
        return self.database_manager.load_agent_stats()
    
    def _save_stats(self):
        """Save agent statistics"""
        self.database_manager.save_agent_stats(self.stats)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            'agent_id': self.agent_id,
            'running': self.running,
            'registered': self.registered,
            'current_tasks': len(self.current_tasks),
            'stats': self.stats,
            'ai_status': self.ai_manager.get_status(),
            'blockchain_status': self.blockchain_manager.get_status(),
            'network_status': self.network_manager.get_status(),
            'security_status': self.security_manager.get_status(),
            'remote_commands': list(self.remote_command_handler.command_handlers.keys())
        }
    
    def register_with_node(self) -> bool:
        """Register agent with node server"""
        return self.network_manager.register_agent(self.agent_id, self.get_capabilities())
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities for registration"""
        return {
            "agent_id": self.agent_id,
            "name": f"ultimate-agent-{self.agent_id}",
            "host": platform.node(),
            "version": "3.0.0-enhanced",
            "agent_type": "ultimate",
            "capabilities": ["ai", "blockchain", "cloud", "security"],
            "ai_models": list(self.ai_manager.models.keys()),
            "gpu_available": self.ai_manager.gpu_available,
            "blockchain_enabled": True,
            "enhanced_features": True,
            "task_types": list(self.task_scheduler.get_available_task_types())
        }

    def execute_remote_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a remote management command."""
        return self.remote_command_handler.handle_command(command)
    
    def start_task(self, task_type: str, task_config: Dict = None) -> str:
        """Start a new task"""
        return self.task_scheduler.start_task(task_type, task_config or {})
    
    def _heartbeat_loop(self):
        """Background heartbeat loop"""
        while self.running:
            try:
                if not self.registered:
                    if self.register_with_node():
                        print("✅ Successfully registered with node")
                else:
                    if not self.network_manager.send_heartbeat(self.agent_id, self.get_status()):
                        print("⚠️ Heartbeat failed, attempting to re-register")
                        self.registered = False
                
                time.sleep(30)  # Heartbeat interval
            except Exception as e:
                print(f"❌ Heartbeat loop error: {e}")
                time.sleep(60)
    
    def _auto_task_loop(self):
        """Background auto task loop"""
        while self.running:
            try:
                if (self.config_manager.get('DEFAULT', 'auto_start_tasks', fallback='true').lower() == 'true' and
                    len(self.current_tasks) < int(self.config_manager.get('DEFAULT', 'max_concurrent_tasks', fallback='3'))):
                    
                    # Auto-start tasks based on configuration
                    self.task_scheduler.auto_start_tasks()
                
                time.sleep(30)
            except Exception as e:
                print(f"❌ Auto task loop error: {e}")
                time.sleep(60)
                
    
    
    def start(self):
        """Start the agent"""
        print(f"\n🚀 Starting Enhanced Ultimate Pain Network Agent")
        print(f"   Node URL: {self.node_url}")
        print(f"   Dashboard: http://localhost:{self.dashboard_port}")
        
        self.running = True
        
        # Start background services
        services = [
            ("Heartbeat", self._heartbeat_loop),
            ("Auto Tasks", self._auto_task_loop),
            ("Dashboard", self.dashboard_manager.start_server)
        ]
        
        for service_name, service_func in services:
            thread = threading.Thread(target=service_func, daemon=True, name=service_name)
            thread.start()
            print(f"✅ {service_name} service started")
        
        print("🚀 All systems online!")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Agent shutdown initiated...")
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the agent"""
        print("🛑 Stopping Enhanced Ultimate Pain Network Agent...")
        self.running = False
        
        # Save state
        self._save_stats()
        
        # Stop all managers
        self.database_manager.close()
        self.task_scheduler.stop()
        self.dashboard_manager.stop()
        
        print("🎯 Agent stopped successfully")
        
    def integrate_local_ai_with_agent(agent_class):
        """Decorator to integrate Local AI with the main agent"""
    
    def __init_enhanced__(self, *args, **kwargs):
        # Call original __init__
        original_init = agent_class.__init__
        original_init(self, *args, **kwargs)
        
        # Initialize Local AI components
        self._initialize_local_ai()
    
    def _initialize_local_ai(self):
        """Initialize Local AI components"""
        try:
            # Create Local AI Manager
            from ..ai.local_models.local_ai_manager import (
                create_local_ai_manager,
                create_local_ai_conversation_manager
            )
            
            self.local_ai_manager = create_local_ai_manager(self.config_manager)
            self.local_ai_conversation_manager = create_local_ai_conversation_manager(self.config_manager)
            
            # Enhance existing AI manager
            if hasattr(self, 'ai_manager'):
                self.ai_manager = EnhancedAIModelManager(
                    self.config_manager,
                    self.local_ai_manager
                )
            
            # Enhance conversation manager
            if hasattr(self, 'conversation_manager'):
                self.conversation_manager = EnhancedConversationManager(
                    self.ai_manager,
                    self.config_manager,
                    self.local_ai_conversation_manager
                )
            
            print("✅ Local AI integration completed successfully")
            
        except Exception as e:
            print(f"⚠️ Local AI integration failed: {e}")
            # Continue without local AI
            self.local_ai_manager = None
            self.local_ai_conversation_manager = None
    
    def get_enhanced_status(self):
        """Get enhanced status with Local AI information"""
        status = self.get_status()  # Original status method
        
        if hasattr(self, 'local_ai_manager') and self.local_ai_manager:
            local_ai_status = self.local_ai_manager.get_status()
            local_ai_stats = self.local_ai_manager.get_stats()
            
            status.update({
                'local_ai': {
                    'enabled': True,
                    'status': local_ai_status,
                    'performance': local_ai_stats['inference_stats'],
                    'hardware': local_ai_stats['hardware_info'],
                    'current_model': local_ai_stats['current_model']
                }
            })
        else:
            status['local_ai'] = {'enabled': False}
        
        return status
    
    # Replace methods
    agent_class.__init__ = __init_enhanced__
    agent_class._initialize_local_ai = _initialize_local_ai
    agent_class.get_enhanced_status = get_enhanced_status
    
    return agent_class

