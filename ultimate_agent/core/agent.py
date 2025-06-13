
"""
Ultimate Agent Core - Main Agent Coordination
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional
from ..config.settings import get_config
from ..utils import setup_logging

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

        self.config = config or get_config()
        self.logger = setup_logging("UltimateAgent")
        self.running = False
        self.modules = {}
        # Remote command handler provides basic commands like 'ping'
        from ..remote.handler import RemoteCommandHandler
        self._command_handler = RemoteCommandHandler()
        self._command_handler.set_shutdown_callback(self.stop)
        
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
            from ..ai.models.ai_models import AIModelManager
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
# Alias for compatibility
UltimatePainNetworkAgent = UltimateAgent