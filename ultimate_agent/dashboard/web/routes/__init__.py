#!/usr/bin/env python3
"""
ultimate_agent/dashboard/web/routes/__init__.py
Web dashboard and API routes
"""

from .local_ai_routes import add_local_ai_routes
import threading
import secrets
import time
import os
try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit
except Exception:  # pragma: no cover - optional dependency
    Flask = None
    CORS = lambda *a, **k: None
    SocketIO = emit = None
from typing import Dict, Any


class DashboardServer:  # Changed from DashboardManager to DashboardServer
    """Manages web dashboard and API routes"""

    def __init__(self, agent):
        if Flask is None:
            raise ImportError(
                "The 'flask' package is required for the dashboard. "
                "Please install dependencies with `pip install -r "
                "ultimate_agent/requirements.txt`."
            )

        self.agent = agent
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(16)
        CORS(self.app)
        
        # WebSocket setup
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Dashboard state
        self.running = False
        self.server_thread = None
        self.dashboard_port = 8080  # Fixed port to 8080
        
        # Setup routes and WebSocket events
        self._setup_api_routes()
        self._setup_websocket_events()
        
        print("🌐 Dashboard manager initialized")
    
    def _setup_api_routes(self):
        """Setup API routes"""
        

        @self.app.route('/favicon.ico')
        def favicon():
            return send_from_directory(
                os.path.join(os.path.dirname(__file__), 'static'),
                'favicon.ico',
                mimetype='image/vnd.microsoft.icon'
            )


        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return self._get_dashboard_html()

        @self.app.route('/control-room')
        def control_room():
            """Sleek control room GUI"""
            return self._get_control_room_html()
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get agent statistics"""
            return jsonify(self.agent.get_status())
        
        @self.app.route('/api/v3/stats')
        def get_v3_stats():
            """Get v3 compatible statistics"""
            return jsonify(self.agent.get_status())
        
        @self.app.route('/api/v3/stats/enhanced')
        def get_enhanced_stats():
            """Get enhanced statistics with additional info"""
            enhanced_stats = self.agent.get_status()
            blockchain_mgr = getattr(self.agent, 'blockchain_manager', None)
            enhanced_stats.update({
                'ai_training_enabled': hasattr(self.agent.ai_manager, 'training_engine'),
                'task_control_enabled': hasattr(self.agent, 'task_control_client'),
                'blockchain_enhanced': hasattr(blockchain_mgr, 'smart_contract_manager'),
                'advanced_features': True,
                'modular_architecture': True
            })
            return jsonify(enhanced_stats)
        
        @self.app.route('/api/system')
        def get_system():
            """Get system information"""
            import psutil
            import platform
            
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            return jsonify({
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_mb": memory.used / (1024 * 1024),
                "status": "online",
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "architecture": platform.machine()
            })
        
        @self.app.route('/api/activity')
        def get_activity():
            """Get current activity"""
            current_tasks = len(self.agent.current_tasks) if hasattr(self.agent, 'current_tasks') else 0
            
            return jsonify({
                "tasks_running": current_tasks,
                "tasks_completed": self.agent.stats.get("tasks_completed", 0),
                "tasks_failed": self.agent.stats.get("tasks_failed", 0),
                "activity_level": "high" if current_tasks > 2 else "normal",
                "uptime_hours": (time.time() - self.agent.stats.get("start_time", time.time())) / 3600
            })
        
        @self.app.route('/api/training')
        def get_training():
            """Get AI training information"""
            ai_status = self.agent.ai_manager.get_status()
            
            return jsonify({
                "models_training": ai_status.get('active_training_sessions', 0),
                "total_models": ai_status.get('models_loaded', 0),
                "training_active": ai_status.get('active_training_sessions', 0) > 0,
                "gpu_available": ai_status.get('gpu_available', False),
                "training_capabilities": ai_status.get('training_capabilities', []),
                "advanced_training_enabled": ai_status.get('training_engine_active', False)
            })
        
        @self.app.route('/api/network')
        def get_network():
            """Get network status"""
            return jsonify({
                "node_url": self.agent.node_url,
                "registered": self.agent.registered,
                "network_status": "connected" if self.agent.registered else "disconnected",
                "agent_id": self.agent.agent_id,
                "connection_quality": "good" if self.agent.registered else "poor"
            })
        
        @self.app.route('/api/tasks')
        def get_tasks():
            """Get current tasks"""
            scheduler_status = {}
            if hasattr(self.agent, 'task_scheduler'):
                scheduler_status = self.agent.task_scheduler.get_scheduler_status()
            
            return jsonify({
                'current_tasks': getattr(self.agent, 'current_tasks', {}),
                'completed_tasks': len(getattr(self.agent, 'completed_tasks', [])),
                'scheduler_status': scheduler_status
            })
        
        @self.app.route('/api/start_task', methods=['POST'])
        def start_task():
            """Start a new task"""
            try:
                data = request.get_json()
                task_type = data.get('type', 'data_processing')
                task_config = data.get('config', {})
                
                if hasattr(self.agent, 'task_scheduler'):
                    task_id = self.agent.task_scheduler.start_task(task_type, task_config)
                    return jsonify({'success': True, 'task_id': task_id})
                else:
                    # Fallback to agent method
                    task_id = self.agent.start_task(task_type, task_config)
                    return jsonify({'success': True, 'task_id': task_id})
                    
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/cancel_task/<task_id>', methods=['POST'])
        def cancel_task(task_id):
            """Cancel a running task"""
            try:
                if hasattr(self.agent, 'task_scheduler'):
                    success = self.agent.task_scheduler.cancel_task(task_id)
                    return jsonify({'success': success})
                else:
                    return jsonify({'success': False, 'error': 'Task scheduler not available'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/v4/remote/command', methods=['POST'])
        def remote_command():
            """Execute a remote management command"""
            try:
                data = request.get_json() or {}
                result = self.agent.execute_remote_command(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @self.app.route('/api/v4/remote/capabilities')
        def remote_capabilities():
            """List available remote management commands"""
            return jsonify({'commands': list(self.agent.remote_command_handler.command_handlers.keys())})
        
        # Enhanced API endpoints
        @self.app.route('/api/v3/blockchain/enhanced')
        def get_blockchain_enhanced():
            """Get enhanced blockchain information"""
            try:
                blockchain_mgr = getattr(self.agent, 'blockchain_manager', None)
                if blockchain_mgr:
                    blockchain_status = blockchain_mgr.get_status()
                    return jsonify(blockchain_status)
                else:
                    return jsonify({'error': 'Blockchain manager not available'})
            except Exception as e:
                return jsonify({'error': f'Blockchain error: {str(e)}'})
        
        @self.app.route('/api/v3/ai/capabilities')
        def get_ai_capabilities():
            """Get AI capabilities"""
            try:
                ai_status = self.agent.ai_manager.get_status()
                model_stats = self.agent.ai_manager.get_model_stats()
                
                capabilities = {
                    **ai_status,
                    **model_stats
                }
                
                return jsonify(capabilities)
            except Exception as e:
                return jsonify({'error': f'AI capabilities error: {str(e)}'})
        
        @self.app.route('/api/v4/task-control/status')
        def get_task_control_status():
            """Get task control status"""
            try:
                if hasattr(self.agent, 'task_control_client'):
                    return jsonify(self.agent.task_control_client.get_status())
                else:
                    return jsonify({'enabled': False, 'error': 'Task control not available'})
            except Exception as e:
                return jsonify({'error': f'Task control error: {str(e)}'})
        
        @self.app.route('/api/capabilities')
        def get_capabilities():
            """Get detailed agent capabilities"""
            try:
                capabilities = self.agent.get_capabilities()
                
                # Add dashboard-specific capabilities
                capabilities.update({
                    'dashboard_enabled': True,
                    'websocket_enabled': True,
                    'api_version': 'v4',
                    'modular_architecture': True,
                    'real_time_monitoring': True
                })
                
                return jsonify(capabilities)
            except Exception as e:
                return jsonify({'error': f'Capabilities error: {str(e)}'})
        
        @self.app.route('/api/database/stats')
        def get_database_stats():
            """Get database statistics"""
            try:
                if hasattr(self.agent, 'database_manager'):
                    return jsonify(self.agent.database_manager.get_database_stats())
                else:
                    return jsonify({'error': 'Database manager not available'})
            except Exception as e:
                return jsonify({'error': f'Database error: {str(e)}'})
        
        @self.app.route('/api/performance/metrics')
        def get_performance_metrics():
            """Get performance metrics"""
            try:
                if hasattr(self.agent, 'monitoring_manager'):
                    return jsonify(self.agent.monitoring_manager.get_current_metrics())
                else:
                    return jsonify({'error': 'Monitoring manager not available'})
            except Exception as e:
                return jsonify({'error': f'Monitoring error: {str(e)}'})
    
    def _setup_websocket_events(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect(auth=None): 
            """Handle client connection"""
            emit('connected', {
                'agent_id': self.agent.agent_id,
                'version': getattr(self.agent, 'VERSION', '3.0.0-modular'),
                'status': 'online',
                'enhanced_features': True,
                'modular_architecture': True,
                'timestamp': time.time()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print("📱 Dashboard client disconnected")
        
        @self.socketio.on('request_stats')
        def handle_stats_request():
            """Handle stats request"""
            emit('stats_update', self.agent.get_status())
        
        @self.socketio.on('request_enhanced_stats')
        def handle_enhanced_stats_request():
            """Handle enhanced stats request"""
            enhanced_stats = self.agent.get_status()
            enhanced_stats.update({
                'modular_architecture': True,
                'dashboard_connected': True,
                'real_time_updates': True
            })
            emit('enhanced_stats_update', enhanced_stats)
        
        @self.socketio.on('task_assignment')
        def handle_task_assignment(data):
            """Handle centralized task assignment"""
            try:
                if hasattr(self.agent, 'task_control_client'):
                    success = self.agent.task_control_client.handle_task_assignment(data)
                    emit('task_assignment_response', {
                        'success': success, 
                        'task_id': data.get('task_id')
                    })
                else:
                    emit('task_assignment_response', {
                        'success': False, 
                        'error': 'Task control not available'
                    })
            except Exception as e:
                emit('task_assignment_response', {
                    'success': False, 
                    'error': str(e)
                })
        
        @self.socketio.on('request_real_time_data')
        def handle_real_time_data_request():
            """Handle real-time data request"""
            import psutil
            
            real_time_data = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'tasks_running': len(getattr(self.agent, 'current_tasks', {})),
                'timestamp': time.time()
            }
            
            if hasattr(self.agent, 'task_scheduler'):
                scheduler_status = self.agent.task_scheduler.get_scheduler_status()
                real_time_data['scheduler'] = scheduler_status
            
            emit('real_time_data', real_time_data)

        @self.socketio.on('remote_command')
        def handle_remote_command(data):
            """Handle remote command execution"""
            try:
                result = self.agent.execute_remote_command(data)
                emit('remote_command_response', result)
            except Exception as e:
                emit('remote_command_response', {'success': False, 'error': str(e)})
    
    def broadcast_task_progress(self, task_id: str, progress: float, details: Dict = None):
        """Broadcast task progress to connected clients"""
        self.socketio.emit('task_progress', {
            'task_id': task_id,
            'progress': progress,
            'details': details,
            'timestamp': time.time()
        })
    
    def broadcast_task_completion(self, task_id: str, completion_data: Dict):
        """Broadcast task completion to connected clients"""
        self.socketio.emit('task_completed', {
            'task_id': task_id,
            **completion_data,
            'timestamp': time.time()
        })
    
    def broadcast_system_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Broadcast system alert to connected clients"""
        self.socketio.emit('system_alert', {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': time.time()
        })
    
    def _get_dashboard_html(self):
        """Generate dashboard HTML"""
        agent_id = getattr(self.agent, 'agent_id', 'unknown')
        node_url = getattr(self.agent, 'node_url', 'unknown')
        version = getattr(self.agent, 'VERSION', '3.0.0-modular')
        
    def add_local_ai_routes(app, agent):
        """Add Local AI API routes to the dashboard"""
    
    from flask import request, jsonify, Response
    import json
    import asyncio
    
    @app.route('/api/v4/local-ai/status')
    def local_ai_status():
        """Get local AI system status"""
        try:
            if hasattr(agent, 'local_ai_manager'):
                status = agent.local_ai_manager.get_status()
                hardware_info = agent.local_ai_manager.get_hardware_info()
                stats = agent.local_ai_manager.get_stats()
                
                return jsonify({
                    'success': True,
                    'status': status,
                    'hardware': hardware_info,
                    'performance': stats,
                    'api_version': '4.1'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Local AI not initialized',
                    'available': False
                })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/v4/local-ai/models')
    def list_local_models():
        """List available local AI models"""
        try:
            if hasattr(agent, 'local_ai_manager'):
                models = agent.local_ai_manager.list_available_models()
                return jsonify({
                    'success': True,
                    'models': models
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Local AI not available'
                })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/v4/local-ai/models/download', methods=['POST'])
    def download_local_model():
        """Download a local AI model"""
        try:
            data = request.get_json() or {}
            model_name = data.get('model_name')
            
            if not model_name:
                return jsonify({
                    'success': False,
                    'error': 'model_name is required'
                })
            
            if not hasattr(agent, 'local_ai_manager'):
                return jsonify({
                    'success': False,
                    'error': 'Local AI not available'
                })
            
            # Start download asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                agent.local_ai_manager.download_model(model_name)
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/v4/local-ai/inference', methods=['POST'])
    def local_ai_inference():
        """Run inference using local AI"""
        try:
            data = request.get_json() or {}
            prompt = data.get('prompt', data.get('input', ''))
            
            if not prompt:
                return jsonify({
                    'success': False,
                    'error': 'prompt or input is required'
                })
            
            if not hasattr(agent, 'local_ai_manager'):
                return jsonify({
                    'success': False,
                    'error': 'Local AI not available'
                })
            
            # Extract options
            options = {
                'task_type': data.get('task_type', 'general'),
                'temperature': data.get('temperature', 0.7),
                'max_tokens': data.get('max_tokens', 1000),
                'top_p': data.get('top_p', 0.9)
            }
            
            # Run inference
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                agent.local_ai_manager.generate_response(prompt, **options)
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/v4/local-ai/inference/stream', methods=['POST'])
    def local_ai_inference_stream():
        """Stream inference using local AI"""
        try:
            data = request.get_json() or {}
            prompt = data.get('prompt', data.get('input', ''))
            
            if not prompt:
                return jsonify({
                    'success': False,
                    'error': 'prompt or input is required'
                })
            
            if not hasattr(agent, 'local_ai_manager'):
                return jsonify({
                    'success': False,
                    'error': 'Local AI not available'
                })
            
            # Extract options
            options = {
                'task_type': data.get('task_type', 'general'),
                'temperature': data.get('temperature', 0.7),
                'max_tokens': data.get('max_tokens', 1000)
            }
            
            async def generate():
                try:
                    async for chunk in agent.local_ai_manager.generate_stream(prompt, **options):
                        yield f"data: {json.dumps(chunk)}\n\n"
                        if chunk.get('done'):
                            break
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
            
            # Run generator
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            def run_async_generator():
                async def async_gen():
                    async for item in generate():
                        yield item
                
                gen = async_gen()
                try:
                    while True:
                        yield loop.run_until_complete(gen.__anext__())
                except StopAsyncIteration:
                    pass
            
            return Response(
                run_async_generator(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
        
    
    
    @app.route('/api/v4/local-ai/chat', methods=['POST'])
    def local_ai_chat():
        """Enhanced chat endpoint using local AI"""
        try:
            data = request.get_json() or {}
            message = data.get('input', data.get('message', ''))
            conversation_id = data.get('conversation_id')
            
            if not message:
                return jsonify({
                    'success': False,
                    'error': 'message is required'
                })
            
            if not hasattr(agent, 'local_ai_conversation_manager'):
                return jsonify({
                    'success': False,
                    'error': 'Local AI chat not available'
                })
            
            # Generate conversation ID if needed
            if not conversation_id:
                import uuid
                conversation_id = f"local_conv_{uuid.uuid4().hex[:12]}"
            
            # Process message
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                agent.local_ai_conversation_manager.process_message(
                    conversation_id=conversation_id,
                    message=message,
                    context_aware=data.get('context_aware', True),
                    temperature=data.get('temperature', 0.7),
                    max_tokens=data.get('max_tokens', 1000)
                )
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/v4/local-ai/hardware')
    def local_ai_hardware():
        """Get detailed hardware information"""
        try:
            if hasattr(agent, 'local_ai_manager'):
                hardware_info = agent.local_ai_manager.get_hardware_info()
                return jsonify({
                    'success': True,
                    'hardware': hardware_info
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Local AI not available'
                })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
        
    class EnhancedAIModelManager:
        """Enhanced AI Model Manager with Local AI integration"""
    
    def __init__(self, config, local_ai_manager=None):
        # Initialize existing AI manager
        from ..models.ai_models import AIModelManager
        self.base_ai_manager = AIModelManager(config)
        
        # Add local AI capabilities
        self.local_ai_manager = local_ai_manager
        self.local_ai_enabled = local_ai_manager is not None
        
        # Combine model lists
        self._update_combined_models()
    
    def _update_combined_models(self):
        """Update combined model list with local AI models"""
        if self.local_ai_enabled:
            # Add local AI models to the model registry
            local_models = self.local_ai_manager.list_available_models()
            
            for model_info in local_models.get('recommended_models', []):
                model_name = f"local_{model_info['name'].lower().replace(' ', '_')}"
                self.base_ai_manager.models[model_name] = {
                    'type': 'local_llm',
                    'status': 'available' if model_info['available'] else 'needs_download',
                    'size': 'variable',
                    'accuracy': 0.90,
                    'local_ai': True,
                    'display_name': model_info['name'],
                    'full_name': model_info['full_name'],
                    'memory_gb': model_info['memory_gb'],
                    'tags': model_info['tags']
                }
    
    async def run_inference(self, model_name: str, input_data: Any, **kwargs) -> Dict[str, Any]:
        """Enhanced inference with local AI support"""
        try:
            # Check if it's a local AI model
            if model_name.startswith('local_') and self.local_ai_enabled:
                # Use local AI for inference
                task_type = kwargs.get('task_type', 'general')
                result = await self.local_ai_manager.generate_response(
                    str(input_data),
                    task_type=task_type,
                    **kwargs
                )
                
                if result['success']:
                    return {
                        'success': True,
                        'prediction': result['response'],
                        'confidence': 0.90,  # Local AI confidence
                        'model_used': result['model_used'],
                        'processing_time': result['processing_time'],
                        'tokens_per_second': result.get('tokens_per_second', 0),
                        'inference_type': 'local_ai',
                        'hardware_type': result.get('hardware_type'),
                        'local_ai': True
                    }
                else:
                    # Fallback to base AI manager
                    return self.base_ai_manager.run_inference(model_name, input_data)
            
            # Use base AI manager for traditional models
            return self.base_ai_manager.run_inference(model_name, input_data)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model_attempted': model_name
            }
    
    def list_models(self) -> List[str]:
        """List all available models including local AI"""
        models = self.base_ai_manager.list_models()
        
        if self.local_ai_enabled:
            local_models = self.local_ai_manager.list_available_models()
            for model_info in local_models.get('recommended_models', []):
                model_name = f"local_{model_info['name'].lower().replace(' ', '_')}"
                if model_name not in models:
                    models.append(model_name)
        
        return models
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed model information"""
        if model_name.startswith('local_') and self.local_ai_enabled:
            # Get local AI model info
            local_models = self.local_ai_manager.list_available_models()
            for model_info in local_models.get('recommended_models', []):
                if f"local_{model_info['name'].lower().replace(' ', '_')}" == model_name:
                    return {
                        'name': model_info['name'],
                        'type': 'local_llm',
                        'memory_gb': model_info['memory_gb'],
                        'tags': model_info['tags'],
                        'description': model_info['description'],
                        'available': model_info['available'],
                        'hardware_compatible': True,
                        'local_ai': True
                    }
        
        return self.base_ai_manager.get_model(model_name)
    
    def get_status(self) -> Dict[str, Any]:
        """Enhanced status with local AI information"""
        base_status = self.base_ai_manager.get_status()
        
        if self.local_ai_enabled:
            local_status = self.local_ai_manager.get_status()
            local_stats = self.local_ai_manager.get_stats()
            
            base_status.update({
                'local_ai_enabled': True,
                'local_ai_status': local_status,
                'local_ai_performance': local_stats['inference_stats'],
                'hardware_type': local_stats['hardware_info']['type'],
                'local_models_available': local_status.get('models_loaded', 0)
            })
        else:
            base_status['local_ai_enabled'] = False
        
        return base_status


# ============================================================================
# 3. Enhanced Conversation Manager Integration
# ============================================================================

class EnhancedConversationManager:
    """Enhanced conversation manager with local AI support"""
    
    def __init__(self, ai_manager, config_manager, local_ai_conversation_manager=None):
        # Initialize base conversation manager
        from ..chat.conversation_manager import ConversationManager
        self.base_conversation_manager = ConversationManager(ai_manager, config_manager)
        
        # Add local AI conversation support
        self.local_ai_conversation_manager = local_ai_conversation_manager
        self.local_ai_enabled = local_ai_conversation_manager is not None
        
        # Configuration
        self.prefer_local_ai = True  # Prefer local AI when available
        self.fallback_enabled = True  # Fallback to base AI if local fails
    
    async def process_message(self, conversation_id: str, user_message: str,
                            context_aware: bool = True, use_local_ai: bool = None) -> Dict[str, Any]:
        """Process message with local AI preference"""
        
        # Determine whether to use local AI
        should_use_local = (
            use_local_ai if use_local_ai is not None 
            else (self.prefer_local_ai and self.local_ai_enabled)
        )
        
        if should_use_local and self.local_ai_enabled:
            try:
                # Try local AI first
                result = await self.local_ai_conversation_manager.process_message(
                    conversation_id=conversation_id,
                    message=user_message,
                    context_aware=context_aware
                )
                
                if result['success']:
                    result['ai_type'] = 'local'
                    return result
                
                # Log local AI failure
                print(f"⚠️ Local AI failed: {result.get('error')}")
                
            except Exception as e:
                print(f"⚠️ Local AI error: {e}")
        
        # Fallback to base conversation manager
        if self.fallback_enabled:
            try:
                result = await self.base_conversation_manager.process_message(
                    conversation_id, user_message, context_aware
                )
                result['ai_type'] = 'cloud'
                result['local_ai_attempted'] = should_use_local
                return result
                
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'conversation_id': conversation_id,
                    'local_ai_attempted': should_use_local
                }
        else:
            return {
                'success': False,
                'error': 'Local AI failed and fallback disabled',
                'conversation_id': conversation_id
            }
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get enhanced conversation statistics"""
        base_stats = self.base_conversation_manager.get_chat_statistics()
        
        enhanced_stats = {
            **base_stats,
            'local_ai_enabled': self.local_ai_enabled,
            'prefer_local_ai': self.prefer_local_ai,
            'fallback_enabled': self.fallback_enabled
        }
        
        if self.local_ai_enabled:
            # Add local AI specific stats
            local_stats = self.local_ai_conversation_manager.local_ai.get_stats()
            enhanced_stats.update({
                'local_ai_performance': local_stats['inference_stats'],
                'local_ai_hardware': local_stats['hardware_info'],
                'local_ai_model': local_stats['current_model']
            })
        
        return enhanced_stats


        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced Ultimate Agent v{version} - Modular</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }}
                .container {{ max-width: 1400px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .modular-badge {{ background: rgba(255, 255, 255, 0.2); padding: 8px 16px; 
                                 border-radius: 20px; margin: 5px; display: inline-block; font-size: 0.9em; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                         gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
                .enhanced-section {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .task-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }}
                .task-item {{ border: 1px solid #ddd; padding: 15px; border-radius: 8px; }}
                .task-progress {{ background: #eee; height: 12px; border-radius: 6px; margin: 8px 0; }}
                .task-progress-bar {{ background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 6px; transition: width 0.3s; }}
                .controls {{ text-align: center; margin: 20px 0; }}
                .control-group {{ margin: 10px 0; }}
                button {{ background: #667eea; color: white; border: none; padding: 12px 24px; 
                         border-radius: 6px; cursor: pointer; margin: 5px; font-size: 14px; }}
                button:hover {{ background: #5a67d8; }}
                .modular-btn {{ background: linear-gradient(135deg, #ff6b6b, #4ecdc4); }}
                .modular-btn:hover {{ background: linear-gradient(135deg, #ff5252, #26a69a); }}
                .feature-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
                .feature-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }}
                .status-indicator {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
                .status-online {{ background: #28a745; }}
                .status-offline {{ background: #dc3545; }}
                .real-time-data {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .port-display {{ background: rgba(255, 255, 255, 0.3); padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Enhanced Ultimate Agent v{version} - Modular Architecture</h1>
                    <div class="modular-badge">🏗️ Modular Design</div>
                    <div class="modular-badge">🧠 Advanced AI</div>
                    <div class="modular-badge">💰 Smart Contracts</div>
                    <div class="modular-badge">🎯 Task Control</div>
                    <div class="modular-badge">📊 Real-time Monitoring</div>
                    <div class="port-display">🌐 Port: 8080</div>
                    <p>Agent ID: {agent_id}</p>
                    <p>Connected to: {node_url}</p>
                </div>
                
                <div class="real-time-data" id="realTimeData">
                    <h3>📊 Real-time System Status</h3>
                    <div id="systemStatus">Loading...</div>
                </div>
                
                <div class="stats" id="stats">
                    <!-- Stats will be populated by JavaScript -->
                </div>
                
                <div class="enhanced-section">
                    <h2>🎯 Modular Task Controls</h2>
                    <div class="controls">
                        <div class="control-group">
                            <h3>🧠 AI Training Tasks</h3>
                            <button onclick="startTask('neural_network_training')" class="modular-btn">Neural Network Training</button>
                            <button onclick="startTask('transformer_training')" class="modular-btn">Transformer Training</button>
                            <button onclick="startTask('cnn_training')" class="modular-btn">CNN Training</button>
                            <button onclick="startTask('reinforcement_learning')" class="modular-btn">Reinforcement Learning</button>
                        </div>
                        <div class="control-group">
                            <h3>🔬 Advanced AI Tasks</h3>
                            <button onclick="startTask('federated_learning')">Federated Learning</button>
                            <button onclick="startTask('hyperparameter_optimization')">Hyperparameter Opt</button>
                            <button onclick="startTask('gradient_computation')">Gradient Computation</button>
                            <button onclick="startTask('model_inference_batch')">Batch Inference</button>
                        </div>
                        <div class="control-group">
                            <h3>💰 Blockchain Tasks</h3>
                            <button onclick="startTask('blockchain_transaction')">Standard Transaction</button>
                            <button onclick="startTask('smart_contract_execution')" class="modular-btn">Smart Contract</button>
                        </div>
                        <div class="control-group">
                            <h3>📊 Data Tasks</h3>
                            <button onclick="startTask('data_preprocessing')">Data Preprocessing</button>
                            <button onclick="startTask('sentiment_analysis')">Sentiment Analysis</button>
                            <button onclick="startTask('data_processing')">Data Processing</button>
                        </div>
                        <div class="control-group">
                            <button onclick="refreshStats()" style="background: #28a745;">🔄 Refresh Stats</button>
                            <button onclick="showModularStatus()" style="background: #17a2b8;">🏗️ Show Modular Status</button>
                        </div>
                    </div>
                </div>
                
                <div class="enhanced-section">
                    <h2>🏃‍♂️ Active Tasks</h2>
                    <div class="task-grid" id="currentTasks">No tasks running</div>
                </div>
                
                <div class="enhanced-section" id="modularStatus" style="display: none;">
                    <h2>🏗️ Modular Architecture Status</h2>
                    <div class="feature-list">
                        <div class="feature-card">
                            <h4>🧠 AI Models Manager</h4>
                            <p>Advanced neural network training and inference</p>
                            <div id="aiModelsStatus">Loading...</div>
                        </div>
                        <div class="feature-card">
                            <h4>🎯 Task Scheduler</h4>
                            <p>Intelligent task queue and execution management</p>
                            <div id="taskSchedulerStatus">Loading...</div>
                        </div>
                        <div class="feature-card">
                            <h4>💰 Blockchain Manager</h4>
                            <p>Smart contracts and multi-currency wallet</p>
                            <div id="blockchainStatus">Loading...</div>
                        </div>
                        <div class="feature-card">
                            <h4>💾 Database Manager</h4>
                            <p>Persistent data storage and analytics</p>
                            <div id="databaseStatus">Loading...</div>
                        </div>
                        <div class="feature-card">
                            <h4>📊 Monitoring Manager</h4>
                            <p>Real-time performance monitoring</p>
                            <div id="monitoringStatus">Loading...</div>
                        </div>
                        <div class="feature-card">
                            <h4>🌐 Dashboard Manager</h4>
                            <p>Web interface and real-time updates</p>
                            <div id="dashboardStatus"><span class="status-indicator status-online"></span>Active on Port 8080</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let socket;
                let modularStatusVisible = false;
                
                // Initialize
                document.addEventListener('DOMContentLoaded', () => {{
                    initSocket();
                    refreshStats();
                    updateRealTimeData();
                    setInterval(refreshStats, 5000);
                    setInterval(updateRealTimeData, 2000);
                }});
                
                function initSocket() {{
                    try {{
                        socket = io();
                        socket.on('connect', () => {{
                            console.log('Connected to modular agent dashboard on port 8080');
                            socket.emit('request_enhanced_stats');
                        }});
                        socket.on('stats_update', updateStats);
                        socket.on('enhanced_stats_update', updateEnhancedStats);
                        socket.on('task_progress', updateTaskProgress);
                        socket.on('task_completed', onTaskCompleted);
                        socket.on('real_time_data', updateRealTimeDisplay);
                        socket.on('system_alert', showSystemAlert);
                    }} catch (e) {{
                        console.log('WebSocket not available');
                    }}
                }}
                
                async function refreshStats() {{
                    try {{
                        const response = await fetch('/api/v3/stats/enhanced');
                        const stats = await response.json();
                        updateStats(stats);
                        
                        const tasksResponse = await fetch('/api/tasks');
                        const tasks = await tasksResponse.json();
                        updateTasks(tasks.current_tasks || {{}});
                        
                    }} catch (error) {{
                        console.error('Failed to refresh stats:', error);
                    }}
                }}
                
                function updateRealTimeData() {{
                    if (socket) {{
                        socket.emit('request_real_time_data');
                    }}
                }}
                
                function updateStats(stats) {{
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${{stats.tasks_completed || 0}}</div>
                            <div>Tasks Completed</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.tasks_running || 0}}</div>
                            <div>Tasks Running</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{(stats.total_earnings || 0).toFixed(4)}}</div>
                            <div>Total Earnings (ETH)</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.ai_models_loaded || 0}}</div>
                            <div>AI Models</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{(stats.uptime_hours || 0).toFixed(1)}}h</div>
                            <div>Uptime</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.registered ? '🟢 Online' : '🔴 Offline'}}</div>
                            <div>Node Status</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.modular_architecture ? '🏗️ Modular' : '📦 Monolithic'}}</div>
                            <div>Architecture</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">🌐 8080</div>
                            <div>Dashboard Port</div>
                        </div>
                    `;
                }}
                
                function updateRealTimeDisplay(data) {{
                    document.getElementById('systemStatus').innerHTML = `
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                            <div><strong>CPU:</strong> ${{data.cpu_percent?.toFixed(1) || 0}}%</div>
                            <div><strong>Memory:</strong> ${{data.memory_percent?.toFixed(1) || 0}}%</div>
                            <div><strong>Tasks:</strong> ${{data.tasks_running || 0}}</div>
                            <div><strong>Port:</strong> 8080</div>
                            <div><strong>Updated:</strong> ${{new Date().toLocaleTimeString()}}</div>
                        </div>
                    `;
                }}
                
                function updateTasks(tasks) {{
                    const tasksDiv = document.getElementById('currentTasks');
                    
                    if (Object.keys(tasks).length === 0) {{
                        tasksDiv.innerHTML = '<div class="task-item" style="text-align: center; color: #666;">No tasks currently running</div>';
                        return;
                    }}
                    
                    tasksDiv.innerHTML = Object.entries(tasks).map(([id, task]) => `
                        <div class="task-item">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <strong>${{task.name || task.task_type}}</strong>
                                <span style="background: ${{task.ai_workload ? '#e3f2fd' : task.blockchain_task ? '#fff3e0' : '#f3e5f5'}}; 
                                           padding: 4px 8px; border-radius: 12px; font-size: 0.8em;">
                                    ${{task.ai_workload ? '🧠 AI' : task.blockchain_task ? '💰 Blockchain' : '📊 Data'}}
                                </span>
                            </div>
                            <div style="font-size: 0.9em; color: #666; margin-bottom: 8px;">
                                Progress: ${{(task.progress || 0).toFixed(1)}}%
                                ${{task.details ? ` | ${{Object.keys(task.details).length}} metrics` : ''}}
                            </div>
                            <div class="task-progress">
                                <div class="task-progress-bar" style="width: ${{task.progress || 0}}%;"></div>
                            </div>
                            ${{task.details ? `
                                <div style="font-size: 0.8em; color: #888; margin-top: 8px;">
                                    ${{Object.entries(task.details).slice(0, 3).map(([k, v]) => 
                                        `${{k}}: ${{typeof v === 'number' ? v.toFixed(2) : v}}`).join(' | ')}}
                                </div>
                            ` : ''}}
                        </div>
                    `).join('');
                }}
                
                async function startTask(taskType) {{
                    try {{
                        const response = await fetch('/api/start_task', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ type: taskType }})
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            console.log('Modular task started:', result.task_id, 'Type:', taskType);
                            showTaskFeedback(event.target, '✅ Started!', '#28a745');
                        }} else {{
                            console.error('Failed to start task:', result.error);
                            showTaskFeedback(event.target, '❌ Failed!', '#dc3545');
                        }}
                    }} catch (error) {{
                        console.error('Error starting task:', error);
                        showTaskFeedback(event.target, '❌ Error!', '#dc3545');
                    }}
                }}
                
                function showTaskFeedback(button, text, color) {{
                    const originalText = button.textContent;
                    const originalColor = button.style.background;
                    button.textContent = text;
                    button.style.background = color;
                    setTimeout(() => {{
                        button.textContent = originalText;
                        button.style.background = originalColor;
                    }}, 2000);
                }}
                
                async function showModularStatus() {{
                    const statusDiv = document.getElementById('modularStatus');
                    modularStatusVisible = !modularStatusVisible;
                    
                    if (modularStatusVisible) {{
                        statusDiv.style.display = 'block';
                        event.target.textContent = '🔽 Hide Modular Status';
                        await updateModularStatus();
                    }} else {{
                        statusDiv.style.display = 'none';
                        event.target.textContent = '🏗️ Show Modular Status';
                    }}
                }}
                
                async function updateModularStatus() {{
                    try {{
                        // Update each module status
                        const [aiResponse, dbResponse, capabilitiesResponse] = await Promise.all([
                            fetch('/api/v3/ai/capabilities'),
                            fetch('/api/database/stats'),
                            fetch('/api/capabilities')
                        ]);
                        
                        const aiData = await aiResponse.json();
                        const dbData = await dbResponse.json();
                        const capData = await capabilitiesResponse.json();
                        
                        document.getElementById('aiModelsStatus').innerHTML = `
                            <span class="status-indicator status-online"></span>
                            Models: ${{aiData.models_loaded || 0}} | GPU: ${{aiData.gpu_available ? 'Yes' : 'No'}}
                        `;
                        
                        document.getElementById('databaseStatus').innerHTML = `
                            <span class="status-indicator status-online"></span>
                            Records: ${{dbData.task_records || 0}} | Size: ${{(dbData.database_size_mb || 0).toFixed(1)}}MB
                        `;
                        
                        document.getElementById('taskSchedulerStatus').innerHTML = `
                            <span class="status-indicator status-online"></span>
                            Active: ${{capData.tasks_running || 0}} | Types: ${{(capData.task_types || []).length}}
                        `;
                        
                        document.getElementById('blockchainStatus').innerHTML = `
                            <span class="status-indicator status-online"></span>
                            Enhanced: ${{capData.blockchain_enhanced ? 'Yes' : 'No'}} | Wallet: Active
                        `;
                        
                        document.getElementById('monitoringStatus').innerHTML = `
                            <span class="status-indicator status-online"></span>
                            Real-time: Active | Metrics: Collecting
                        `;
                        
                    }} catch (error) {{
                        console.error('Failed to update modular status:', error);
                    }}
                }}
                
                function updateTaskProgress(data) {{
                    console.log('Modular task progress:', data);
                    refreshStats();
                }}
                
                function onTaskCompleted(data) {{
                    console.log('Modular task completed:', data);
                    refreshStats();
                }}
                
                function showSystemAlert(alert) {{
                    console.log('System alert:', alert);
                    // Could implement toast notifications here
                }}
                
                function updateEnhancedStats(stats) {{
                    console.log('Enhanced modular stats:', stats);
                    updateStats(stats);
                }}
                
                console.log('🏗️ Enhanced Modular Agent Dashboard Ready');
                console.log('✨ Features: Modular Architecture, Real-time Updates, Advanced Monitoring');
                console.log('🌐 Running on Port 8080');
            </script>
        </body>
        </html>
        """

    def _get_control_room_html(self):
        """Return a simple futuristic control room interface"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ultimate Agent Control Room - Port 8080</title>
            <style>
                body { font-family: Arial, sans-serif; background: radial-gradient(circle at center, #1e1e2f, #0d0d15); color: #e0e0ff; height: 100vh; margin: 0; display: flex; align-items: center; justify-content: center; }
                .panel { background: rgba(20,20,40,0.8); border: 1px solid #555; border-radius: 10px; padding: 40px; box-shadow: 0 0 15px #00f0ff; width: 80%; max-width: 900px; }
                .screens { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px,1fr)); gap: 20px; margin-top: 20px; }
                .screen { background: rgba(10,10,25,0.9); border: 1px solid #3a3a55; border-radius: 8px; padding: 20px; box-shadow: 0 0 8px #00e0ff; }
                .screen h2 { margin-top: 0; font-size: 1.1em; }
                .glow { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { box-shadow: 0 0 5px #00e0ff; } 50% { box-shadow: 0 0 15px #00e0ff; } 100% { box-shadow: 0 0 5px #00e0ff; } }
                .port-display { text-align: center; background: rgba(0, 240, 255, 0.1); padding: 10px; border-radius: 8px; margin: 10px 0; }
                .access-info { background: rgba(0, 255, 0, 0.1); padding: 15px; border-radius: 8px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="panel">
                <h1>Ultimate Agent Control Room</h1>
                <div class="port-display">
                    <h3>🌐 Dashboard Port: 8080</h3>
                    <p>Listening on all interfaces (0.0.0.0:8080)</p>
                </div>
                <div class="access-info">
                    <h4>🔗 Access URLs:</h4>
                    <p>Local: http://localhost:8080</p>
                    <p>External: http://[your-server-ip]:8080</p>
                    <p><strong>Make sure port 8080 is open in your firewall!</strong></p>
                </div>
                <div class="screens">
                    <div class="screen glow">
                        <h2>Network</h2>
                        <p id="network">Connecting...</p>
                    </div>
                    <div class="screen glow">
                        <h2>Blockchain Rewards</h2>
                        <p id="rewards">0 PAIN</p>
                    </div>
                    <div class="screen glow">
                        <h2>Real-Time Monitoring</h2>
                        <p id="monitoring">CPU 0%</p>
                    </div>
                    <div class="screen glow">
                        <h2>Port Status</h2>
                        <p id="port">Port 8080: Active</p>
                    </div>
                </div>
            </div>
            <script>
                let val = 0;
                setInterval(function() {
                    val = (val + 5) % 100;
                    document.getElementById('monitoring').textContent = 'CPU ' + val + '%';
                }, 500);
                
                document.getElementById('network').textContent = 'Connected - External Access Enabled';
                document.getElementById('port').innerHTML = '<span style="color: #00ff00">●</span> Port 8080: Listening on 0.0.0.0';
            </script>
        </body>
        </html>
        """
    
    def start_server(self):
        """Start dashboard server in separate thread"""
        if not self.running:
            self.running = True
            self.server_thread = threading.Thread(
                target=self._run_server, 
                daemon=True, 
                name="DashboardServer"
            )
            self.server_thread.start()
            print(f"🌐 Dashboard server starting on port {self.dashboard_port} (accessible externally)")
    
    def _run_server(self):
        """Run the dashboard server"""
        try:
            self.socketio.run(
                self.app,
                host='0.0.0.0',  # Changed to accept external connections
                port=self.dashboard_port,  # Now uses the fixed port 8080
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            print(f"❌ Dashboard server error: {e}")
    
    def stop(self):
        """Stop dashboard server"""
        self.running = False
        print("🌐 Dashboard server stopped")


# For backward compatibility, create an alias
DashboardManager = DashboardServer