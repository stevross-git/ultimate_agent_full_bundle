#!/usr/bin/env python3
"""
ultimate_agent/core/agent1.py
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
        # Pass blockchain manager so tasks can submit earnings
        self.task_scheduler = TaskScheduler(self.ai_manager, self.blockchain_manager)
        self.network_manager = NetworkManager(self.config_manager)
        
        # FIX: Get URLs from config for DiscoveryClient instead of passing ConfigManager
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
        
        # Set node URL
        self.node_url = node_url or self.config_manager.get('DEFAULT', 'node_url')
        
        # Network stats
        self.stats = {
            'total_earnings': 0.0,
            'tasks_completed': 0,
            'uptime': 0.0,
            'current_balance': 0.0
        }

        self.dashboard_port = dashboard_port or 8080
        
        # Add Local AI initialization (PROPERLY INSIDE __init__)
        self._initialize_local_ai()
        
        print(f"✅ Ultimate Pain Network Agent initialized")
        print(f"🌐 Node URL: {self.node_url}")
        print(f"📊 Dashboard will be available on port {dashboard_port or 8080}")

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
            
            # Create Local AI Conversation Manager
            self.local_ai_conversation_manager = create_local_ai_conversation_manager(self.config_manager)
            
            print("✅ Local AI components initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Local AI initialization failed: {e}")
            self.local_ai_manager = None
            self.local_ai_conversation_manager = None

    def _get_or_create_agent_id(self) -> str:
        """Get existing agent ID or create new one"""
        agent_id_file = "agent_id.txt"
        
        if os.path.exists(agent_id_file):
            with open(agent_id_file, 'r') as f:
                agent_id = f.read().strip()
                if agent_id:
                    return agent_id
        
        # Create new agent ID
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        with open(agent_id_file, 'w') as f:
            f.write(agent_id)
        
        return agent_id

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
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
                'network_manager': True
            }
        }
        
        # Add local AI status if available
        if hasattr(self, 'local_ai_manager') and self.local_ai_manager:
            status['local_ai'] = {
                'enabled': True,
                'manager_available': True
            }
        else:
            status['local_ai'] = {
                'enabled': False,
                'manager_available': False
            }
        
        return status

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities"""
        capabilities = {
            'ai_training': True,
            'blockchain_operations': True,
            'task_scheduling': True,
            'data_processing': True,
            'network_communication': True,
            'security_features': True,
            'monitoring': True,
            'plugin_support': True,
            'remote_management': True
        }
        
        # Add local AI capabilities
        if hasattr(self, 'local_ai_manager') and self.local_ai_manager:
            capabilities['local_ai_inference'] = True
            capabilities['local_conversation'] = True
        
        return capabilities

    def start_task(self, task_type: str, task_config: Dict[str, Any]) -> str:
        """Start a new task"""
        return self.task_scheduler.start_task(task_type, task_config)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        return self.task_scheduler.cancel_task(task_id)

    def execute_remote_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute remote management command"""
        return self.remote_command_handler.handle_command(command_data)

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

    def chat_with_ai(self, message: str, conversation_id: str = None, model_type: str = 'general') -> Dict[str, Any]:
        """Chat with the AI assistant"""
        if not hasattr(self, 'local_ai_conversation_manager') or self.local_ai_conversation_manager is None:
            return {
                'success': False,
                'error': 'Conversation manager not available',
                'response': 'Chat functionality is not currently available.'
            }
        
        try:
            # Create new conversation if needed
            if not conversation_id:
                conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            
            # Process message using local AI
            result = self.local_ai_conversation_manager.process_message(
                conversation_id, 
                message, 
                model_type=model_type
            )
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': 'I apologize, but I encountered an error. Please try again.'
            }

    def _save_stats(self):
        """Save current statistics"""
        try:
            stats_file = "agent_stats.json"
            import json
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save stats: {e}")

    def _load_stats(self):
        """Load saved statistics"""
        try:
            stats_file = "agent_stats.json"
            if os.path.exists(stats_file):
                import json
                with open(stats_file, 'r') as f:
                    loaded_stats = json.load(f)
                    self.stats.update(loaded_stats)
        except Exception as e:
            print(f"⚠️ Failed to load stats: {e}")

    def start(self) -> bool:
        """Start the agent"""
        print(f"\n🚀 Starting Enhanced Ultimate Pain Network Agent")
        print(f"🆔 Agent ID: {self.agent_id}")
        print(f"🌐 Node URL: {self.node_url}")
        
        # Load saved stats
        self._load_stats()
        
        self.running = True
        
        # Start all managers
        try:
            self.task_scheduler.start()
            if hasattr(self.dashboard_manager, "start_server"):
                self.dashboard_manager.start_server()
            print("✅ All managers started successfully")
        except Exception as e:
            print(f"❌ Error starting managers: {e}")
            return False
        
        print(f"🎯 Agent started successfully!")
        print(f"📊 Dashboard: http://localhost:8080")
        print(f"🎛️ Control Room: http://localhost:8080/control-room")
        
        # Main loop
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
        try:
            self.database_manager.close()
            self.task_scheduler.stop()
            self.dashboard_manager.stop()
            print("✅ All managers stopped successfully")
        except Exception as e:
            print(f"⚠️ Error stopping managers: {e}")
        
        print("🎯 Agent stopped successfully")

    def get_enhanced_status(self):
        """Get enhanced status with Local AI information"""
        status = self.get_status()  # Original status method
        
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
                        'current_model': local_ai_stats.get('current_model')
                    }
                })
            except Exception as e:
                status['local_ai'] = {'enabled': True, 'error': str(e)}
        else:
            status['local_ai'] = {'enabled': False}
        
        return status


# Integration decorator for Local AI
def integrate_local_ai_with_agent(agent_class):
    """Decorator to integrate Local AI with the main agent"""
    
    def __init_enhanced__(self, *args, **kwargs):
        # Call original __init__
        original_init = agent_class.__init__
        original_init(self, *args, **kwargs)
        
        # Initialize Local AI components
        self._initialize_local_ai()
    
    def _initialize_local_ai_decorator(self):
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
                from ..ai.models.enhanced_ai_manager import EnhancedAIModelManager
                self.ai_manager = EnhancedAIModelManager(
                    self.config_manager,
                    self.local_ai_manager
                )
            
            # Enhance conversation manager
            if hasattr(self, 'conversation_manager'):
                from ..ai.chat.enhanced_conversation_manager import EnhancedConversationManager
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
    
    def get_enhanced_status_decorator(self):
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
    agent_class._initialize_local_ai = _initialize_local_ai_decorator
    agent_class.get_enhanced_status = get_enhanced_status_decorator
    
    return agent_class