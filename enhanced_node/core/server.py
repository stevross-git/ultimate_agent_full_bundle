#!/usr/bin/env python3
"""
Enhanced Node Server - CORRECTED VERSION with Fixed Imports
Fixed all import paths and added better error handling
"""

import os
import redis
import statistics
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, Any
import socket
import threading
import time
import requests
import ssl
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Get the correct template folder path
TEMPLATE_DIR = Path(__file__).parent.parent / 'templates'
STATIC_DIR = Path(__file__).parent.parent / 'static'

print(f"🔧 Server Debug Info:")
print(f"   Template dir: {TEMPLATE_DIR}")
print(f"   Template exists: {TEMPLATE_DIR.exists()}")
print(f"   Dashboard template: {(TEMPLATE_DIR / 'enhanced_dashboard.html').exists()}")

# CORRECTED IMPORTS - Fixed all import paths
try:
    # Try direct imports (when running from enhanced_node directory)
    from config.settings import settings
    from models.agents import EnhancedAgentInfo, EnhancedAgentStatus
    from utils.logger import get_server_logger
    from utils.serialization import serialize_for_json
    print("✅ Direct imports successful")
    
except ImportError as e1:
    print(f"⚠️  Direct imports failed: {e1}")
    try:
        # Try enhanced_node prefix imports
        from enhanced_node.config.settings import settings
        from enhanced_node.models.agents import EnhancedAgentInfo, EnhancedAgentStatus
        from enhanced_node.utils.logger import get_server_logger
        from enhanced_node.utils.serialization import serialize_for_json
        print("✅ Enhanced_node imports successful")
        
    except ImportError as e2:
        print(f"❌ All imports failed: {e2}")
        # Create minimal implementations
        class MockSettings:
            NODE_ID = "enhanced-node"
            NODE_VERSION = "3.4.0-emergency"
            NODE_PORT = 5000
            MANAGER_HOST = "localhost"
            MANAGER_PORT = 8080
            DEFAULT_RATE_LIMITS = ["100 per hour"]
            METRICS_PORT = 8091
            DATABASE_URL = "sqlite:///emergency.db"
        
        settings = MockSettings()
        
        # Create basic dataclasses for agents
        from dataclasses import dataclass
        from datetime import datetime
        from typing import List, Optional
        
        @dataclass
        class EnhancedAgentInfo:
            id: str
            name: str
            host: str
            version: str
            agent_type: str = "ultimate"
            capabilities: List[str] = None
            registered_at: Optional[datetime] = None
            
            def __post_init__(self):
                if self.capabilities is None:
                    self.capabilities = []
                if self.registered_at is None:
                    self.registered_at = datetime.now()
        
        @dataclass 
        class EnhancedAgentStatus:
            id: str
            status: str = "unknown"
            cpu_percent: float = 0.0
            memory_percent: float = 0.0
            tasks_running: int = 0
            last_heartbeat: Optional[datetime] = None
        
        def get_server_logger():
            import logging
            return logging.getLogger("EnhancedNodeServer")
        
        def serialize_for_json(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for k, v in obj.__dict__.items():
                    if isinstance(v, datetime):
                        result[k] = v.isoformat()
                    else:
                        result[k] = v
                return result
            return str(obj)
        
        print("✅ Mock implementations created")

class EnhancedNodeServer:
    """Enhanced Node Server with Fixed Import Handling"""
    
    def __init__(self):
        # Configure Flask with correct template and static folders
        self.app = Flask(
            __name__,
            template_folder=str(TEMPLATE_DIR) if TEMPLATE_DIR.exists() else None,
            static_folder=str(STATIC_DIR) if STATIC_DIR.exists() else None
        )
        
        print(f"✅ Flask app created with template folder: {self.app.template_folder}")
        
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Rate limiting (with error handling)
        try:
            self.limiter = Limiter(
                app=self.app,
                key_func=get_remote_address,
                default_limits=getattr(settings, 'DEFAULT_RATE_LIMITS', ["100 per hour"])
            )
        except:
            self.limiter = None
            print("⚠️  Rate limiting disabled (redis not available)")
        
        # Setup logging
        self.logger = get_server_logger()
        
        # Initialize basic components
        self.agents: Dict[str, EnhancedAgentInfo] = {}
        self.agent_status: Dict[str, EnhancedAgentStatus] = {}
        self.registered_with_manager = False
        self.running = False
        
        # Initialize advanced components (with error handling)
        self._init_advanced_components()
        
        # Performance tracking
        self.performance_history = defaultdict(lambda: deque(maxlen=100))
        self.task_queue = deque()
        
        # Metrics (basic implementation)
        self.metrics = self._init_basic_metrics()
        
        # Redis (optional)
        self.redis_client = self._init_redis()
        
        # Manager connection info
        self.manager_url = f"http://{getattr(settings, 'MANAGER_HOST', 'localhost')}:{getattr(settings, 'MANAGER_PORT', 8080)}"
        
        # Register routes
        self._register_routes()
        
        self.logger.info(f"Enhanced Node Server {getattr(settings, 'NODE_ID', 'enhanced')} v{getattr(settings, 'NODE_VERSION', '3.4.0')} initialized")
    
    def _init_advanced_components(self):
        """Initialize advanced components with error handling"""
        try:
            # Try to import and initialize task control
            from control.task_manager import TaskControlManager
            self.task_control = TaskControlManager(self)
            print("✅ Task control initialized")
        except ImportError:
            self.task_control = None
            print("⚠️  Task control not available")
        
        try:
            # Try to import and initialize remote control
            from control.remote_manager import AdvancedRemoteControlManager
            self.advanced_remote_control = AdvancedRemoteControlManager(self)
            print("✅ Advanced remote control initialized")
        except ImportError:
            self.advanced_remote_control = None
            print("⚠️  Advanced remote control not available")
        
        try:
            # Try to import and initialize version control
            from control.version_manager import VersionControlManager
            self.version_control = VersionControlManager(self)
            print("✅ Version control initialized")
        except ImportError:
            self.version_control = None
            print("⚠️  Version control not available")
    
    def _init_basic_metrics(self):
        """Initialize basic metrics (without prometheus if not available)"""
        try:
            from prometheus_client import Counter, Histogram, Gauge, start_http_server
            
            metrics = {
                'agents_total': Gauge('node_agents_total', 'Total agents connected'),
                'agents_online': Gauge('node_agents_online', 'Online agents'),
                'tasks_running': Gauge('node_tasks_running', 'Tasks currently running'),
                'tasks_completed_total': Counter('node_tasks_completed_total', 'Total tasks completed'),
            }
            
            # Start metrics server
            try:
                start_http_server(getattr(settings, 'METRICS_PORT', 8091))
                print(f"✅ Prometheus metrics server started on port {getattr(settings, 'METRICS_PORT', 8091)}")
            except:
                print("⚠️  Metrics server could not start")
            
            return metrics
        except ImportError:
            print("⚠️  Prometheus metrics not available")
            return {}
    
    def _init_redis(self):
        """Initialize Redis with error handling"""
        try:
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            self.logger.info("Redis connected for real-time caching")
            return client
        except:
            self.logger.warning("Redis not available, using in-memory cache")
            return None
    
    def _register_routes(self):
        """Register all routes with error handling"""
        try:
            print("🔧 Registering routes...")
            
            # Try to register API routes
            routes_registered = 0
            
            try:
                # Prefer absolute import to ensure relative imports in the
                # module resolve correctly
                try:
                    from enhanced_node.routes.api_v3 import register_api_v3_routes
                except ImportError:
                    from routes.api_v3 import register_api_v3_routes
                register_api_v3_routes(self)
                routes_registered += 1
                print("✅ API v3 routes registered")
            except ImportError as e:
                print(f"⚠️  API v3 routes not available: {e}")
                self._register_basic_api_routes()
            
            try:
                try:
                    from enhanced_node.routes.api_v5_remote import register_api_v5_routes
                except ImportError:
                    from routes.api_v5_remote import register_api_v5_routes
                register_api_v5_routes(self)
                routes_registered += 1
                print("✅ API v5 remote routes registered")
            except ImportError:
                print("⚠️  API v5 remote routes not available")
            
            try:
                try:
                    from enhanced_node.routes.api_v6_version import register_api_v6_routes
                except ImportError:
                    from routes.api_v6_version import register_api_v6_routes
                register_api_v6_routes(self)
                routes_registered += 1
                print("✅ API v6 version routes registered")
            except ImportError:
                print("⚠️  API v6 version routes not available")
            
            try:
                try:
                    from enhanced_node.websocket.events import register_websocket_events
                except ImportError:
                    from websocket.events import register_websocket_events
                register_websocket_events(self)
                routes_registered += 1
                print("✅ WebSocket events registered")
            except ImportError:
                print("⚠️  WebSocket events not available")
                self._register_basic_websocket_events()
            
            print(f"✅ Route registration completed. {routes_registered} modules registered.")
            print(f"📋 Total routes: {len(self.app.url_map._rules)}")
            
        except Exception as e:
            self.logger.error(f"Route registration error: {e}")
            self._register_basic_api_routes()
    
    def _register_basic_api_routes(self):
        """Register basic API routes as fallback"""
        from flask import request, jsonify, render_template
        
        @self.app.route('/')
        def enhanced_dashboard():
            """Serve the enhanced dashboard"""
            try:
                return render_template('enhanced_dashboard.html')
            except Exception as e:
                print(f"Template error: {e}")
                return self._get_fallback_dashboard()
        
        @self.app.route('/api/v3/agents/register', methods=['POST'])
        def register_agent():
            """Register agent"""
            try:
                data = request.get_json()
                result = self.register_agent(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/v3/agents/heartbeat', methods=['POST'])
        def agent_heartbeat():
            """Process heartbeat"""
            try:
                data = request.get_json()
                result = self.process_agent_heartbeat(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/v3/agents', methods=['GET'])
        def get_agents():
            """Get agents"""
            try:
                agents_list = []
                for agent_id, agent_info in self.agents.items():
                    agent_status = self.agent_status.get(agent_id)
                    if agent_status:
                        agent_data = {
                            **serialize_for_json(agent_info),
                            **serialize_for_json(agent_status)
                        }
                        agents_list.append(agent_data)
                
                return jsonify({
                    "success": True,
                    "agents": agents_list,
                    "stats": self.get_enhanced_node_stats()
                })
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route('/api/v3/node/stats', methods=['GET'])
        def node_stats():
            """Return basic node statistics"""
            try:
                stats = self.get_enhanced_node_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check"""
            return jsonify({
                "status": "healthy",
                "node_id": getattr(settings, 'NODE_ID', 'enhanced'),
                "version": getattr(settings, 'NODE_VERSION', '3.4.0'),
                "agents": len(self.agents),
                "features": {
                    "task_control": self.task_control is not None,
                    "remote_control": self.advanced_remote_control is not None,
                    "version_control": self.version_control is not None,
                    "redis": self.redis_client is not None,
                    "metrics": len(self.metrics) > 0
                }
            })
        
        print("✅ Basic API routes registered")
    
    def _register_basic_websocket_events(self):
        """Register basic WebSocket events"""
        @self.socketio.on('connect')
        def handle_connect():
            print("Client connected")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected")
        
        print("✅ Basic WebSocket events registered")
    
    def _get_fallback_dashboard(self):
        """Enhanced fallback dashboard"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Enhanced Node Server - Full Dashboard</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    padding: 20px;
                }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 30px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    backdrop-filter: blur(20px);
                }}
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 900;
                    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 10px;
                }}
                .section {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                    backdrop-filter: blur(20px);
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    transition: transform 0.3s;
                }}
                .stat-card:hover {{ transform: translateY(-5px); }}
                .stat-value {{
                    font-size: 2rem;
                    font-weight: 700;
                    color: #4ecdc4;
                    margin-bottom: 5px;
                }}
                .stat-label {{ font-size: 0.9rem; opacity: 0.9; }}
                .btn {{
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 10px;
                    cursor: pointer;
                    font-weight: 600;
                    margin: 5px;
                    transition: transform 0.3s;
                }}
                .btn:hover {{ transform: translateY(-2px); }}
                .connection-status {{
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 10px 15px;
                    border-radius: 20px;
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                }}
                .connected {{ border: 2px solid #4caf50; }}
                .disconnected {{ border: 2px solid #f44336; }}
                .agent-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .agent-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    transition: transform 0.3s;
                }}
                .agent-card:hover {{ transform: translateY(-5px); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div id="connectionStatus" class="connection-status disconnected">
                    <span id="connectionText">Connecting...</span>
                </div>
                
                <div class="header">
                    <h1>🚀 Enhanced Node Server</h1>
                    <p>Advanced AI & Blockchain Operations Center</p>
                    <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 10px;">
                        Node ID: {getattr(settings, 'NODE_ID', 'enhanced')} |
                        Version: {getattr(settings, 'NODE_VERSION', '3.4.0')}
                    </p>
                </div>
                
                <div class="section">
                    <h2>📊 System Status</h2>
                    <div id="systemStats" class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="totalAgents">0</div>
                            <div class="stat-label">Total Agents</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="onlineAgents">0</div>
                            <div class="stat-label">Online Agents</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="tasksRunning">0</div>
                            <div class="stat-label">Tasks Running</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">✅</div>
                            <div class="stat-label">Server Status</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🤖 Connected Agents</h2>
                    <div id="agentsGrid" class="agent-grid">
                        <div style="text-align: center; padding: 40px; opacity: 0.7;">
                            <p>No agents connected yet</p>
                            <p style="font-size: 0.8rem; margin-top: 10px;">
                                Agents will appear here when they register
                            </p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>⚡ Quick Actions</h2>
                    <div style="text-align: center;">
                        <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
                        <button class="btn" onclick="testConnection()">🔌 Test Connection</button>
                        <button class="btn" onclick="window.open('/api/health', '_blank')">💚 Health Check</button>
                        <button class="btn" onclick="showInfo()">ℹ️ System Info</button>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Features Available</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                        <div style="padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                            ✅ Agent Registration
                        </div>
                        <div style="padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                            ✅ WebSocket Connection
                        </div>
                        <div style="padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                            ✅ Real-time Dashboard
                        </div>
                        <div style="padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                            {'✅' if self.task_control else '⚠️'} Task Control
                        </div>
                        <div style="padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                            {'✅' if self.advanced_remote_control else '⚠️'} Remote Control
                        </div>
                        <div style="padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                            {'✅' if self.version_control else '⚠️'} Version Control
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let socket;
                let agentData = {{}};
                
                function initSocket() {{
                    try {{
                        socket = io();
                        socket.on('connect', () => {{
                            updateConnectionStatus(true);
                            console.log('Connected to Enhanced Node Server');
                        }});
                        
                        socket.on('disconnect', () => {{
                            updateConnectionStatus(false);
                        }});
                        
                        socket.on('agent_registered', (data) => {{
                            console.log('Agent registered:', data);
                            refreshData();
                        }});
                        
                        socket.on('agent_status_update', (data) => {{
                            console.log('Agent status update:', data);
                            updateAgentStatus(data);
                        }});
                        
                    }} catch (e) {{
                        console.log('WebSocket not available:', e);
                        updateConnectionStatus(false);
                    }}
                }}
                
                function updateConnectionStatus(connected) {{
                    const status = document.getElementById('connectionStatus');
                    const text = document.getElementById('connectionText');
                    
                    if (connected) {{
                        status.className = 'connection-status connected';
                        text.innerHTML = '🟢 Connected';
                    }} else {{
                        status.className = 'connection-status disconnected';
                        text.innerHTML = '🔴 Disconnected';
                    }}
                }}
                
                async function refreshData() {{
                    try {{
                        const response = await fetch('/api/v3/agents');
                        const data = await response.json();
                        
                        if (data.success) {{
                            updateAgentsList(data.agents);
                            updateStats(data.stats);
                        }}
                    }} catch (e) {{
                        console.error('Failed to refresh data:', e);
                    }}
                }}
                
                function updateAgentsList(agents) {{
                    const agentsGrid = document.getElementById('agentsGrid');
                    
                    if (!agents || agents.length === 0) {{
                        agentsGrid.innerHTML = `
                            <div style="text-align: center; padding: 40px; opacity: 0.7;">
                                <p>No agents connected yet</p>
                                <p style="font-size: 0.8rem; margin-top: 10px;">
                                    Agents will appear here when they register
                                </p>
                            </div>
                        `;
                        return;
                    }}
                    
                    agentsGrid.innerHTML = agents.map(agent => `
                        <div class="agent-card">
                            <h3 style="color: #4ecdc4; margin-bottom: 10px;">
                                🤖 ${{agent.name || agent.id}}
                            </h3>
                            <div style="margin: 10px 0;">
                                <div><strong>ID:</strong> ${{agent.id}}</div>
                                <div><strong>Host:</strong> ${{agent.host}}</div>
                                <div><strong>Version:</strong> ${{agent.version}}</div>
                                <div><strong>Status:</strong> 
                                    <span style="color: ${{agent.status === 'online' ? '#4caf50' : '#ff9800'}};">
                                        ${{agent.status || 'unknown'}}
                                    </span>
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                                    <div style="font-weight: 600;">${{(agent.cpu_percent || 0).toFixed(1)}}%</div>
                                    <div style="font-size: 0.8rem;">CPU</div>
                                </div>
                                <div style="text-align: center; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                                    <div style="font-weight: 600;">${{agent.tasks_running || 0}}</div>
                                    <div style="font-size: 0.8rem;">Tasks</div>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }}
                
                function updateStats(stats) {{
                    if (stats) {{
                        document.getElementById('totalAgents').textContent = stats.total_agents || 0;
                        document.getElementById('onlineAgents').textContent = stats.online_agents || 0;
                        document.getElementById('tasksRunning').textContent = stats.total_tasks_running || 0;
                    }}
                }}
                
                function testConnection() {{
                    if (socket && socket.connected) {{
                        socket.emit('ping');
                        alert('Connection test sent! Check browser console for response.');
                    }} else {{
                        alert('WebSocket not connected. Check connection status.');
                    }}
                }}
                
                function showInfo() {{
                    alert(`Enhanced Node Server Information:
                    
Node ID: {getattr(settings, 'NODE_ID', 'enhanced')}
Version: {getattr(settings, 'NODE_VERSION', '3.4.0')}
Task Control: {'Available' if self.task_control else 'Not Available'}
Remote Control: {'Available' if self.advanced_remote_control else 'Not Available'}
Version Control: {'Available' if self.version_control else 'Not Available'}
Redis: {'Connected' if self.redis_client else 'Not Connected'}
Metrics: {'Enabled' if self.metrics else 'Disabled'}

Dashboard: Fully Functional
WebSocket: ${{socket && socket.connected ? 'Connected' : 'Disconnected'}}
                    `);
                }}
                
                // Initialize on page load
                document.addEventListener('DOMContentLoaded', () => {{
                    initSocket();
                    refreshData();
                    setInterval(refreshData, 30000); // Refresh every 30 seconds
                }});
                
                console.log('Enhanced Node Server Dashboard Loaded');
                console.log('Features: Real-time updates, Agent management, WebSocket communication');
            </script>
        </body>
        </html>
        """
    
    def register_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent"""
        agent_id = agent_data.get('agent_id') or agent_data.get('server_id')
        if not agent_id:
            raise ValueError("agent_id required")
        
        current_time = datetime.now()
        
        agent = EnhancedAgentInfo(
            id=agent_id,
            name=agent_data.get('name', f"agent-{agent_id}"),
            host=agent_data.get('host', '127.0.0.1'),
            version=agent_data.get('version', 'unknown'),
            agent_type=agent_data.get('agent_type', 'ultimate'),
            capabilities=agent_data.get('capabilities', []),
            registered_at=current_time
        )
        
        # Store agent
        self.agents[agent_id] = agent
        self.agent_status[agent_id] = EnhancedAgentStatus(id=agent_id)
        
        # Update metrics
        if 'agents_total' in self.metrics:
            self.metrics['agents_total'].set(len(self.agents))
        
        self.logger.info(f"Agent registered: {agent_id}")
        
        return {
            "success": True,
            "agent_id": agent_id,
            "node_id": getattr(settings, 'NODE_ID', 'enhanced'),
            "node_version": getattr(settings, 'NODE_VERSION', '3.4.0'),
            "message": "Agent registered successfully"
        }
    
    def process_agent_heartbeat(self, heartbeat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process agent heartbeat"""
        agent_id = heartbeat_data.get('server_id') or heartbeat_data.get('agent_id')
        
        if not agent_id or agent_id not in self.agents:
            raise ValueError("Agent not registered")
        
        current_time = datetime.now()
        
        # Update agent status
        status = self.agent_status[agent_id]
        status.status = heartbeat_data.get("status", "online")
        status.cpu_percent = heartbeat_data.get("cpu_percent", 0.0)
        status.memory_percent = heartbeat_data.get("memory_percent", 0.0)
        status.tasks_running = heartbeat_data.get("tasks_running", 0)
        status.last_heartbeat = current_time
        
        self.logger.info(f"Heartbeat processed for agent {agent_id}")
        
        return {
            "success": True,
            "node_id": getattr(settings, 'NODE_ID', 'enhanced'),
            "next_heartbeat": 30
        }
    
    def get_enhanced_node_stats(self) -> Dict[str, Any]:
        """Return advanced node statistics"""
        total_agents = len(self.agents)
        online_agents = sum(
            1
            for s in self.agent_status.values()
            if s.status == "online" and s.last_heartbeat and (datetime.now() - s.last_heartbeat).seconds < 120
        )

        offline_agents = total_agents - online_agents

        # Task metrics
        total_tasks_running = sum(getattr(s, "tasks_running", 0) for s in self.agent_status.values())
        total_tasks_completed = sum(getattr(s, "tasks_completed", 0) for s in self.agent_status.values())
        total_tasks_failed = sum(getattr(s, "tasks_failed", 0) for s in self.agent_status.values())
        success_rate = round((total_tasks_completed / max(total_tasks_completed + total_tasks_failed, 1)) * 100, 2)

        # System metrics
        avg_cpu = sum(getattr(s, "cpu_percent", 0.0) for s in self.agent_status.values()) / max(total_agents, 1)
        avg_memory = sum(getattr(s, "memory_percent", 0.0) for s in self.agent_status.values()) / max(total_agents, 1)
        avg_gpu = sum(getattr(s, "gpu_percent", 0.0) for s in self.agent_status.values()) / max(total_agents, 1)

        # AI metrics
        total_ai_models = sum(getattr(s, "ai_models_loaded", 0) for s in self.agent_status.values())
        total_ai_inferences = sum(getattr(s, "ai_inference_count", 0) for s in self.agent_status.values())
        agents_with_gpu = sum(1 for a in self.agents.values() if getattr(a, "gpu_available", False))

        # Blockchain metrics
        total_blockchain_balance = sum(getattr(s, "blockchain_balance", 0.0) for s in self.agent_status.values())
        total_blockchain_txs = sum(getattr(s, "blockchain_transactions", 0) for s in self.agent_status.values())
        blockchain_enabled_agents = sum(1 for a in self.agents.values() if getattr(a, "blockchain_enabled", False))

        # Performance metrics
        avg_efficiency = sum(getattr(s, "efficiency_score", 100.0) for s in self.agent_status.values()) / max(total_agents, 1)

        # Task control statistics
        mgmt_stats = self.task_control.get_task_statistics() if self.task_control else {}

        # Advanced remote control metrics
        advanced_stats = (
            self.advanced_remote_control.get_advanced_statistics() if self.advanced_remote_control else {}
        )

        def calculate_health_score() -> float:
            if total_agents == 0:
                return 100.0
            online_ratio = online_agents / total_agents
            success_ratio = total_tasks_completed / max(total_tasks_completed + total_tasks_failed, 1)
            health = (online_ratio * 40) + (avg_efficiency / 100.0 * 0.4) + (success_ratio * 20)
            return max(0.0, min(100.0, health))

        return {
            "node_id": getattr(settings, "NODE_ID", "enhanced"),
            "node_version": getattr(settings, "NODE_VERSION", "3.4.0"),
            "timestamp": datetime.now().isoformat(),

            # Agent statistics
            "total_agents": total_agents,
            "online_agents": online_agents,
            "offline_agents": offline_agents,

            # Task statistics
            "total_tasks_running": total_tasks_running,
            "total_tasks_completed": total_tasks_completed,
            "total_tasks_failed": total_tasks_failed,
            "success_rate": success_rate,

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

            # Health
            "health_score": calculate_health_score(),
            "manager_connected": self.registered_with_manager,

            # Task control
            "task_control_enabled": self.task_control is not None,
            "central_tasks": mgmt_stats,

            # Remote management
            "remote_management_enabled": self.advanced_remote_control is not None,
            "advanced_control_enabled": self.advanced_remote_control is not None,
            "advanced_control": advanced_stats,

            # Version control
            "version_control_enabled": self.version_control is not None,
        }
    
    def start(self):
        """Start the server"""
        self.running = True
        
        # Start advanced services if available
        if self.task_control:
            try:
                self.task_control.start_task_control_services()
                print("✅ Task control services started")
            except Exception as e:
                print(f"⚠️  Task control start failed: {e}")
        
        if self.advanced_remote_control:
            try:
                self.advanced_remote_control.start_advanced_services()
                print("✅ Advanced remote control services started")
            except Exception as e:
                print(f"⚠️  Advanced remote control start failed: {e}")
        
        if self.version_control:
            try:
                self.version_control.start_version_services()
                print("✅ Version control services started")
            except Exception as e:
                print(f"⚠️  Version control start failed: {e}")
        
        self.logger.info("Enhanced Node Server started")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        self.logger.info("Enhanced Node Server stopped")