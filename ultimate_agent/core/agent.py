
"""
Ultimate Agent Core - Main Agent Coordination
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from ..config.settings import get_config
from ..utils import setup_logging

class UltimateAgent:
    """Main Ultimate Agent coordination class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_config()
        self.logger = setup_logging("UltimateAgent")
        self.running = False
        self.modules = {}
        
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
