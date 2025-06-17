
"""
Ultimate Agent Core - Main Agent Coordination
"""

import asyncio
import logging
import json
import time
import os
import uuid
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None

from ..config.settings import get_config
from ..utils import setup_logging

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

try:
    from ..ai.local_models.local_ai_manager import (
        create_local_ai_manager,
        create_local_ai_conversation_manager,
    )
    LOCAL_AI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    LOCAL_AI_AVAILABLE = False
    print("⚠️ Local AI not available")

def serialize_for_json(obj):
    """Serialize object for JSON response"""
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return str(obj)

class UltimateAgent:
    """Main Ultimate Agent coordination class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_config()
        self.logger = setup_logging("UltimateAgent")
        self.running = False
        self.modules = {}

        # ✅ Add these
        self.agent_id = self.config.get("agent_id", "agent-001")
        self.ai_manager = None
        self.registered = False
        self.stats = {
            "start_time": time.time(),
            "tasks_completed": 0,
            "tasks_failed": 0
        }
        self.current_tasks = {}
        self.completed_tasks = []

        # Remote command handler
        from ..remote.handler import RemoteCommandHandler
        self._command_handler = RemoteCommandHandler()
        self._command_handler.set_shutdown_callback(self.stop)

        # Remote command handler provides basic commands like 'ping'
        # already initialised above
        
    def start(self):
        """Start the Ultimate Agent"""
        self.logger.info("🚀 Ultimate Agent starting...")
        self.running = True
        
        # Initialize core modules
        self._initialize_modules()
        
        # Start main event loop
        try:
            asyncio.run(self._main_loop())
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the Ultimate Agent"""
        self.logger.info("🛑 Ultimate Agent stopping...")
        self.running = False
        
        # Cleanup modules
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'stop'):
                    module.stop()
                self.logger.info(f"✅ Stopped {module_name}")
            except Exception as e:
                self.logger.error(f"❌ Error stopping {module_name}: {e}")
    
    def _initialize_modules(self):
        """Initialize all agent modules"""
        self.logger.info("📦 Initializing modules...")
        
        # Initialize modules based on configuration
        if self.config.get('ai_enabled', True):
            self._initialize_ai_modules()
        
        if self.config.get('tasks_enabled', True):
            self._initialize_task_modules()
            
        if self.config.get('dashboard_enabled', True):
            self._initialize_dashboard()
            
    
    def _initialize_ai_modules(self):
        """Initialize AI-related modules"""
        try:
            from ..ai.models import AIModelManager
            self.modules['ai_models'] = AIModelManager(self.config)
            self.logger.info("✅ AI modules initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ AI modules not available: {e}")
    
    def _initialize_task_modules(self):
        """Initialize task management modules"""
        try:
            from ..tasks.execution.scheduler import TaskScheduler
            self.modules['task_scheduler'] = TaskScheduler(self.config)
            self.logger.info("✅ Task modules initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Task modules not available: {e}")
    
    def _initialize_dashboard(self):
        """Initialize dashboard module"""
        try:
            from ..dashboard.web.routes import DashboardServer
            dashboard = DashboardServer(self)
            self.modules['dashboard'] = dashboard
            dashboard.start_server()  # ✅ START IT HERE
            self.logger.info("✅ Dashboard initialized and server started")
        except ImportError as e:
            self.logger.warning(f"⚠️ Dashboard not available: {e}")

        """Initialize dashboard module"""
        try:
            from ..dashboard.web.routes import DashboardServer
            self.modules['dashboard'] = DashboardServer(self.config)
            self.logger.info("✅ Dashboard initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Dashboard not available: {e}")
    
    async def _main_loop(self):
        """Main agent event loop"""
        self.logger.info("🔄 Starting main event loop...")
        
        while self.running:
            try:
                # Process agent tasks
                await self._process_tasks()
                
                # Health checks
                await self._health_check()
                
                # Sleep briefly to prevent CPU spinning
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_tasks(self):
        """Process pending tasks"""
        if 'task_scheduler' in self.modules:
            try:
                await self.modules['task_scheduler'].process_pending()
            except Exception as e:
                self.logger.error(f"❌ Task processing error: {e}")
    
    async def _health_check(self):
        """Perform health checks on modules"""
        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'health_check'):
                    healthy = await module.health_check()
                    if not healthy:
                        self.logger.warning(f"⚠️ Module {module_name} health check failed")
            except Exception as e:
                self.logger.error(f"❌ Health check error for {module_name}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'running': self.running,
            'modules': list(self.modules.keys()),
            'config': self.config
        }

    def handle_command(self, command: str, **params: Any) -> Dict[str, Any]:
        """Execute a simple remote command.

        This delegates to :class:`~ultimate_agent.remote.handler.RemoteCommandHandler`
        which knows how to handle basic commands like ``ping`` or ``shutdown``.
        Additional keyword arguments are passed to the command handler.
        """

        result = self._command_handler.execute(command, **params)
        if command == "ping" and result.get("status") == "pong":
            return {"message": "pong"}
        return result


class UltimatePainNetworkAgent(UltimateAgent):
    """Enhanced agent combining all functionality."""

    def __init__(self, node_url: str = None, dashboard_port: int = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(config=config)

        print("🚀 Initializing Enhanced Ultimate Pain Network Agent")

        # Initialize core configuration
        self.config_manager = ConfigManager()
        self.agent_id = self._get_or_create_agent_id()

        # Initialize all managers
        self.security_manager = SecurityManager(self.config_manager)
        self.blockchain_manager = BlockchainManager(self.config_manager)
        self.ai_manager = AIModelManager(self.config_manager)
        self.monitoring_manager = MonitoringManager()
        self.plugin_manager = PluginManager()
        self.database_manager = DatabaseManager()
        self.task_scheduler = TaskScheduler(self.ai_manager, self.blockchain_manager)
        self.network_manager = NetworkManager(self.config_manager)

        node_service_url = self.config_manager.get('DEFAULT', 'node_url', fallback='https://srvnodes.peoplesainetwork.com')
        manager_service_url = self.config_manager.get('DISCOVERY', 'manager_service', fallback='http://mannodes.peoplesainetwork.com')
        self.discovery_client = DiscoveryClient(node_service_url, manager_service_url)

        self.remote_command_handler = RemoteCommandHandler(self)

        # Initialize dashboard
        self.dashboard_manager = DashboardManager(self)

        # State management
        self.running = False
        self.current_tasks = {}
        self.completed_tasks = []
        self.start_time = time.time()

        self.node_url = node_url or self.config_manager.get('DEFAULT', 'node_url')
        self.stats = {
            'total_earnings': 0.0,
            'tasks_completed': 0,
            'uptime': 0.0,
            'current_balance': 0.0,
        }

        self.dashboard_port = dashboard_port or 8080

        self._initialize_local_ai()

        print("✅ Ultimate Pain Network Agent initialized")
        print(f"🌐 Node URL: {self.node_url}")
        print(f"📊 Dashboard will be available on port {self.dashboard_port}")

    def _initialize_local_ai(self):
        """Initialize Local AI components"""
        if not LOCAL_AI_AVAILABLE:
            self.local_ai_manager = None
            self.local_ai_conversation_manager = None
            return

        try:
            print("🧠 Initializing Local AI...")
            self.local_ai_manager = create_local_ai_manager(self.config_manager)
            self.local_ai_conversation_manager = create_local_ai_conversation_manager(self.config_manager)
            print("✅ Local AI components initialized successfully")
        except Exception as e:
            print(f"⚠️ Local AI initialization failed: {e}")
            self.local_ai_manager = None
            self.local_ai_conversation_manager = None

    def _get_or_create_agent_id(self) -> str:
        agent_id_file = "agent_id.txt"
        if os.path.exists(agent_id_file):
            with open(agent_id_file, 'r') as f:
                agent_id = f.read().strip()
                if agent_id:
                    return agent_id
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        with open(agent_id_file, 'w') as f:
            f.write(agent_id)
        return agent_id

    def get_status(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        status = {
            'agent_id': self.agent_id,
            'node_url': self.node_url,
            'running': self.running,
            'uptime': uptime,
            'current_tasks': len(self.current_tasks),
            'completed_tasks': len(self.completed_tasks),
            'stats': self.stats.copy(),
            'modules': {
                'ai_manager': True,
                'blockchain_manager': True,
                'task_scheduler': True,
                'security_manager': True,
                'database_manager': True,
                'monitoring_manager': True,
                'dashboard_manager': True,
                'network_manager': True,
            },
        }

        if hasattr(self, 'local_ai_manager') and self.local_ai_manager:
            status['local_ai'] = {
                'enabled': True,
                'manager_available': True,
            }
        else:
            status['local_ai'] = {
                'enabled': False,
                'manager_available': False,
            }
        return status

    def get_capabilities(self) -> Dict[str, Any]:
        capabilities = {
            'ai_training': True,
            'blockchain_operations': True,
            'task_scheduling': True,
            'data_processing': True,
            'network_communication': True,
            'security_features': True,
            'monitoring': True,
            'plugin_support': True,
            'remote_management': True,
        }
        if hasattr(self, 'local_ai_manager') and self.local_ai_manager:
            capabilities['local_ai_inference'] = True
            capabilities['local_conversation'] = True
        return capabilities

    def start_task(self, task_type: str, task_config: Dict[str, Any]) -> str:
        return self.task_scheduler.start_task(task_type, task_config)

    def cancel_task(self, task_id: str) -> bool:
        return self.task_scheduler.cancel_task(task_id)

    def execute_remote_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.remote_command_handler.handle_command(command_data)

    def get_local_ai_status(self) -> Dict[str, Any]:
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
                'current_model': hardware.get('current_model'),
            }
        except Exception as e:
            return {'enabled': True, 'error': str(e)}

    def chat_with_ai(self, message: str, conversation_id: str = None, model_type: str = 'general') -> Dict[str, Any]:
        if not hasattr(self, 'local_ai_conversation_manager') or self.local_ai_conversation_manager is None:
            return {
                'success': False,
                'error': 'Conversation manager not available',
                'response': 'Chat functionality is not currently available.',
            }
        try:
            if not conversation_id:
                conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            return self.local_ai_conversation_manager.process_message(conversation_id, message, model_type=model_type)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': 'I apologize, but I encountered an error. Please try again.',
            }

    def _save_stats(self):
        try:
            stats_file = "agent_stats.json"
            import json
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save stats: {e}")

    def _load_stats(self):
        try:
            stats_file = "agent_stats.json"
            if os.path.exists(stats_file):
                import json
                with open(stats_file, 'r') as f:
                    loaded_stats = json.load(f)
                    self.stats.update(loaded_stats)
        except Exception as e:
            print(f"⚠️ Failed to load stats: {e}")

    def start_async(self):
        super().start()

    def start(self) -> bool:
        print(f"\n🚀 Starting Enhanced Ultimate Pain Network Agent")
        print(f"🆔 Agent ID: {self.agent_id}")
        print(f"🌐 Node URL: {self.node_url}")

        self._load_stats()
        self.running = True

        try:
            self.task_scheduler.start()
            if hasattr(self.dashboard_manager, 'start_server'):
                self.dashboard_manager.start_server()
            print("✅ All managers started successfully")
        except Exception as e:
            print(f"❌ Error starting managers: {e}")
            return False

        print("🎯 Agent started successfully!")
        print("📊 Dashboard: http://localhost:8080")
        print("🎛️ Control Room: http://localhost:8080/control-room")

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Agent shutdown initiated...")
            self.stop()

        return True

    def stop(self):
        print("🛑 Stopping Enhanced Ultimate Pain Network Agent...")
        self.running = False

        self._save_stats()

        try:
            self.database_manager.close()
            self.task_scheduler.stop()
            self.dashboard_manager.stop()
            print("✅ All managers stopped successfully")
        except Exception as e:
            print(f"⚠️ Error stopping managers: {e}")

        print("🎯 Agent stopped successfully")

    def get_enhanced_status(self):
        status = self.get_status()
        if hasattr(self, 'local_ai_manager') and self.local_ai_manager:
            try:
                local_ai_status = self.local_ai_manager.get_status()
                local_ai_stats = self.local_ai_manager.get_stats()
                status.update({
                    'local_ai': {
                        'enabled': True,
                        'status': local_ai_status,
                        'performance': local_ai_stats.get('inference_stats', {}),
                        'hardware': local_ai_stats.get('hardware_info', {}),
                        'current_model': local_ai_stats.get('current_model'),
                    }
                })
            except Exception as e:
                status['local_ai'] = {'enabled': True, 'error': str(e)}
        else:
            status['local_ai'] = {'enabled': False}
        return status


# Alias for compatibility
__all__ = ["UltimateAgent", "UltimatePainNetworkAgent"]
