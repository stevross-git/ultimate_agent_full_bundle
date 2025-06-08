#!/usr/bin/env python3
"""
ultimate_agent/dashboard/web/routes/__init__.py
Web dashboard and API routes
"""

import threading
import secrets
try:
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit
except Exception:  # pragma: no cover - optional dependency
    Flask = None
    CORS = lambda *a, **k: None
    SocketIO = emit = None
from typing import Dict, Any


class DashboardManager:
    """Manages web dashboard and API routes"""
    
    def __init__(self, agent):
        self.agent = agent
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(16)
        CORS(self.app)
        
        # WebSocket setup
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Dashboard state
        self.running = False
        self.server_thread = None
        
        # Setup routes and WebSocket events
        self._setup_api_routes()
        self._setup_websocket_events()
        
        print("🌐 Dashboard manager initialized")
    
    def _setup_api_routes(self):
        """Setup API routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return self._get_dashboard_html()
        
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
            enhanced_stats.update({
                'ai_training_enabled': hasattr(self.agent.ai_manager, 'training_engine'),
                'task_control_enabled': hasattr(self.agent, 'task_control_client'),
                'blockchain_enhanced': hasattr(self.agent.blockchain_manager, 'smart_contract_manager'),
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
                blockchain_status = self.agent.blockchain_manager.get_status()
                return jsonify(blockchain_status)
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
        def handle_connect():
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
                            <div id="dashboardStatus"><span class="status-indicator status-online"></span>Active</div>
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
                            console.log('Connected to modular agent dashboard');
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
                            <div class="stat-value">${{stats.advanced_features ? '✨ Enhanced' : '📦 Basic'}}</div>
                            <div>Feature Set</div>
                        </div>
                    `;
                }}
                
                function updateRealTimeDisplay(data) {{
                    document.getElementById('systemStatus').innerHTML = `
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                            <div><strong>CPU:</strong> ${{data.cpu_percent?.toFixed(1) || 0}}%</div>
                            <div><strong>Memory:</strong> ${{data.memory_percent?.toFixed(1) || 0}}%</div>
                            <div><strong>Tasks:</strong> ${{data.tasks_running || 0}}</div>
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
            print(f"🌐 Dashboard server starting on port {self.agent.dashboard_port}")
    
    def _run_server(self):
        """Run the dashboard server"""
        try:
            self.socketio.run(
                self.app,
                host='127.0.0.1',
                port=self.agent.dashboard_port,
                debug=False,
                use_reloader=False
            )
        except Exception as e:
            print(f"❌ Dashboard server error: {e}")
    
    def stop(self):
        """Stop dashboard server"""
        self.running = False
        print("🌐 Dashboard server stopped")
