#!/usr/bin/env python3
"""
Enhanced Node Server - Fixed Main Entry Point with Orchestrator Integration
Fixed import paths and better error handling
"""

import sys
import os
from pathlib import Path
import traceback

# Add current directory to sys.path for imports
ROOT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR.parent))

def debug_environment():
    """Debug the environment setup"""
    print("🔧 Environment Debug Information:")
    print(f"   Python version: {sys.version}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Script location: {ROOT_DIR}")
    print(f"   Python path: {sys.path[:3]}...")
    
    # Check critical files
    critical_files = [
        'core/server.py',
        'routes/api_v3.py',
        'templates/enhanced_dashboard.html',
        'config/settings.py'
    ]
    
    print("📁 File Structure Check:")
    for file_path in critical_files:
        full_path = ROOT_DIR / file_path
        exists = full_path.exists()
        print(f"   {file_path}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        if exists and file_path.endswith('.py'):
            try:
                with open(full_path, 'r') as f:
                    lines = len(f.readlines())
                print(f"      ({lines} lines)")
            except:
                print("      (could not read)")

def try_import_server():
    """Try different methods to import the server"""
    server = None
    
    print("🔄 Attempting to import Enhanced Node Server...")
    
    # Method 1: Direct import
    try:
        from core.server import EnhancedNodeServer
        print("✅ Method 1: Direct import successful")
        server = EnhancedNodeServer()
        return server
    except Exception as e1:
        print(f"⚠️  Method 1 failed: {e1}")
    
    # Method 2: Enhanced node import
    try:
        from enhanced_node.core.server import EnhancedNodeServer
        print("✅ Method 2: Enhanced node import successful")
        server = EnhancedNodeServer()
        return server
    except Exception as e2:
        print(f"⚠️  Method 2 failed: {e2}")
    
    # Method 3: Manual path manipulation
    try:
        core_dir = ROOT_DIR / "core"
        if core_dir.exists():
            sys.path.insert(0, str(core_dir))
        
        import server as server_module
        EnhancedNodeServer = server_module.EnhancedNodeServer
        print("✅ Method 3: Manual path import successful")
        server = EnhancedNodeServer()
        return server
    except Exception as e3:
        print(f"⚠️  Method 3 failed: {e3}")
    
    # Method 4: Create basic server
    try:
        print("🔄 Creating basic fallback server...")
        server = create_basic_server()
        print("✅ Method 4: Basic server created successfully")
        return server
    except Exception as e4:
        print(f"❌ Method 4 failed: {e4}")
    
    return None

def create_basic_server():
    """Create a basic server as fallback"""
    from flask import Flask, jsonify, render_template_string
    from flask_socketio import SocketIO
    
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @app.route('/')
    def dashboard():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced Node Server - Emergency Mode</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; min-height: 100vh; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; background: rgba(255,255,255,0.1); 
                         padding: 30px; border-radius: 20px; margin-bottom: 30px; }
                .status { background: rgba(255,255,255,0.1); padding: 20px; 
                         border-radius: 15px; margin: 20px 0; }
                .btn { background: #4caf50; color: white; padding: 10px 20px; 
                      border: none; border-radius: 5px; margin: 5px; cursor: pointer; }
                .btn:hover { background: #45a049; }
                .error { background: rgba(244, 67, 54, 0.2); border: 2px solid #f44336; }
                .success { background: rgba(76, 175, 80, 0.2); border: 2px solid #4caf50; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Enhanced Node Server</h1>
                    <h2>Emergency Mode Dashboard</h2>
                    <p>Server is running in emergency mode due to import issues</p>
                </div>
                
                <div class="status success">
                    <h3>✅ Server Status</h3>
                    <p>Flask server is running and responding to requests</p>
                    <p>Emergency dashboard is functional</p>
                </div>
                
                <div class="status error">
                    <h3>⚠️ Issues Detected</h3>
                    <p>The main Enhanced Node Server could not be imported properly</p>
                    <p>This is likely due to missing dependencies or import path issues</p>
                </div>
                
                <div class="status">
                    <h3>🔧 Troubleshooting Steps</h3>
                    <ol>
                        <li>Check if all required files exist in the correct locations</li>
                        <li>Verify Python dependencies are installed</li>
                        <li>Check for syntax errors in imported files</li>
                        <li>Run the debug script to identify specific issues</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <button class="btn" onclick="window.location.href='/health'">Health Check</button>
                    <button class="btn" onclick="window.location.href='/debug'">Debug Info</button>
                    <button class="btn" onclick="window.location.reload()">Refresh</button>
                </div>
            </div>
        </body>
        </html>
        """)
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "emergency_mode",
            "message": "Server running in emergency mode",
            "timestamp": "2024-01-01T00:00:00Z"
        })
    
    @app.route('/debug')
    def debug():
        return jsonify({
            "mode": "emergency",
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "python_path": sys.path[:5],
            "available_routes": [str(rule) for rule in app.url_map.iter_rules()]
        })
    
    # Create a simple server object
    class BasicServer:
        def __init__(self):
            self.app = app
            self.socketio = socketio
            self.agents = {}
        
        def start(self):
            print("🚀 Basic server starting...")
        
        def register_agent(self, data):
            agent_id = data.get('agent_id', 'unknown')
            self.agents[agent_id] = data
            return {"success": True, "agent_id": agent_id}
    
    return BasicServer()

def setup_orchestrator_integration(server):
    """Setup orchestrator integration with the node server"""
    try:
        print("\n🔗 Setting up Orchestrator Integration...")
        print("=" * 50)
        
        import requests
        import json
        import time
        import threading
        import uuid
        from datetime import datetime
        
        node_id = f"enhanced_node_{uuid.uuid4().hex[:8]}"
        orchestrator_url = "https://orc.peoplesainetwork.com"
        node_host = "172.31.8.129"  # Your server IP from the logs
        node_port = 5000
        registered = False
        
        print(f"🆔 Node ID: {node_id}")
        print(f"🌐 Node Address: {node_host}:{node_port}")
        print(f"🎯 Orchestrator: {orchestrator_url}")
        
        def register_with_orchestrator():
            """Register this node with the orchestrator"""
            nonlocal registered
            try:
                registration_data = {
                    'node_id': node_id,
                    'host': node_host,
                    'port': node_port,
                    'capabilities': [
                        "agent_management",
                        "task_control", 
                        "remote_management",
                        "websocket_communication",
                        "real_time_monitoring",
                        "enhanced_node_v2",
                        "dashboard_support"
                    ],
                    'agents': [],
                    'node_type': 'enhanced_node',
                    'version': '2.0.0',
                    'api_versions': ['v3', 'v4', 'v5'],
                    'features': {
                        'websocket_support': True,
                        'monitoring': True,
                        'dashboard': True,
                        'task_control': hasattr(server, 'task_control'),
                        'remote_management': hasattr(server, 'advanced_remote_control')
                    },
                    'registration_time': datetime.now().isoformat(),
                    'external_url': f"http://{node_host}:{node_port}",
                    'health_status': 'healthy'
                }
                
                print(f"📡 Attempting registration...")
                
                response = requests.post(
                    f"{orchestrator_url}/api/v1/nodes/{node_id}/register",
                    json=registration_data,
                    timeout=15,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"📡 Response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        registered = True
                        print("✅ Successfully registered with orchestrator!")
                        print(f"   Registration confirmed for {node_id}")
                        start_heartbeat()
                        return True
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        print(f"❌ Registration failed: {error_msg}")
                        return False
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    if response.text:
                        print(f"   Response: {response.text[:200]}...")
                    return False
                    
            except requests.exceptions.ConnectionError:
                print("❌ Cannot connect to orchestrator")
                print("   Make sure https://orc.peoplesainetwork.com is accessible")
                return False
            except requests.exceptions.Timeout:
                print("❌ Registration timeout")
                print("   Orchestrator may be busy, will retry later")
                return False
            except Exception as e:
                print(f"❌ Registration error: {e}")
                return False
        
        def send_heartbeat():
            """Send heartbeat to orchestrator"""
            if not registered:
                return False
            
            try:
                # Get system metrics
                try:
                    import psutil
                    cpu_usage = psutil.cpu_percent(interval=1)
                    memory_usage = psutil.virtual_memory().percent
                except ImportError:
                    cpu_usage = 15.0  # Default values if psutil not available
                    memory_usage = 25.0
                
                heartbeat_data = {
                    'node_id': node_id,
                    'status': 'active',
                    'timestamp': datetime.now().isoformat(),
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'load_score': (cpu_usage + memory_usage) / 2,  # Simple load calculation
                    'active_tasks': 0,  # You can enhance this later
                    'health_status': 'healthy',
                    'uptime': time.time() - start_time,
                    'agents_count': len(getattr(server, 'agents', {}))
                }
                
                response = requests.post(
                    f"{orchestrator_url}/api/v1/nodes/{node_id}/heartbeat",
                    json=heartbeat_data,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        print("💓 Heartbeat sent successfully")
                        return True
                    else:
                        print(f"⚠️ Heartbeat rejected: {result.get('error', 'Unknown')}")
                        return False
                else:
                    print(f"⚠️ Heartbeat failed: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"⚠️ Heartbeat error: {e}")
                return False
        
        def start_heartbeat():
            """Start the heartbeat thread"""
            def heartbeat_worker():
                print("💓 Starting heartbeat thread (every 30 seconds)")
                while registered:
                    try:
                        send_heartbeat()
                        time.sleep(30)  # Heartbeat every 30 seconds
                    except Exception as e:
                        print(f"💓 Heartbeat thread error: {e}")
                        time.sleep(30)
            
            heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
            heartbeat_thread.start()
        
        # Store start time for uptime calculation
        start_time = time.time()
        
        # Attempt registration
        registration_success = register_with_orchestrator()
        
        if registration_success:
            print("🎉 Orchestrator integration successful!")
            print(f"   Node registered as: {node_id}")
            print(f"   Check dashboard: {orchestrator_url}")
            print(f"   Streamlit dashboard: http://3.25.107.210:8501")
            
            # Store orchestrator info on server for later use
            if hasattr(server, '__dict__'):
                server.orchestrator_node_id = node_id
                server.orchestrator_url = orchestrator_url
                server.orchestrator_registered = True
        else:
            print("⚠️ Registration failed, but server will continue running")
            print("   You can check the orchestrator status manually")
            print("   The node will still function independently")
        
        return registration_success
        
    except ImportError as e:
        print(f"❌ Missing dependencies for orchestrator integration: {e}")
        print("   Install with: pip install requests psutil")
        return False
    except Exception as e:
        print(f"❌ Orchestrator integration error: {e}")
        print("   Server will continue without orchestrator integration")
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced Node Server...")
    print("=" * 60)
    
    try:
        # Debug environment
        debug_environment()
        print("=" * 60)
        
        # Try to import and create server
        server = try_import_server()
        
        if server is None:
            print("❌ Failed to create any server instance")
            print("\n🔧 Troubleshooting suggestions:")
            print("1. Check that all required files exist")
            print("2. Verify Python dependencies are installed")
            print("3. Check for syntax errors in imported files")
            print("4. Run: python -c 'import enhanced_node.core.server'")
            sys.exit(1)
        
        print("\n✅ Server instance created successfully!")
        
        # Setup orchestrator integration
        orchestrator_success = setup_orchestrator_integration(server)
        
        print("\n🎮 Features available:")
        if hasattr(server, 'advanced_remote_control'):
            print("   📡 Advanced remote control")
        if hasattr(server, 'task_control'):
            print("   📋 Task control system")
        if hasattr(server, 'version_control'):
            print("   🔄 Version control")
        print("   🌐 WebSocket support")
        print("   📊 Real-time dashboard")
        if orchestrator_success:
            print("   🔗 Orchestrator integration")
        
        # Start the server
        server.start()
        
        # Get port from settings or use default
        try:
            from config.settings import NODE_PORT
            port = NODE_PORT
        except ImportError:
            port = 5000
        
        print(f"\n🌐 Enhanced Node Server running on:")
        print(f"   📱 Dashboard: http://localhost:{port}")
        print(f"   📊 Health Check: http://localhost:{port}/health")
        print(f"   🔍 Debug Info: http://localhost:{port}/debug")
        print(f"   🔌 WebSocket: ws://localhost:{port}/socket.io/")
        
        if orchestrator_success:
            print(f"\n🎛️ Orchestrator Integration:")
            print(f"   🌐 Orchestrator Dashboard: https://orc.peoplesainetwork.com")
            print(f"   📊 Streamlit Dashboard: http://3.25.107.210:8501")
            print(f"   🆔 Node ID: {getattr(server, 'orchestrator_node_id', 'Unknown')}")
        
        print(f"\n🎯 Press Ctrl+C to stop the server")
        
        # Run the server
        try:
            server.socketio.run(
                server.app,
                host='0.0.0.0',
                port=port,
                debug=False,
                allow_unsafe_werkzeug=True
            )
        except AttributeError:
            # Fallback if no socketio
            server.app.run(
                host='0.0.0.0',
                port=port,
                debug=False
            )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Node Server...")
        if 'server' in locals() and server:
            if hasattr(server, 'stop'):
                server.stop()
            # Stop orchestrator integration
            if hasattr(server, 'orchestrator_registered'):
                print("🔗 Disconnecting from orchestrator...")
        print("👋 Server stopped successfully")
    
    except Exception as e:
        print(f"❌ Critical error starting server: {e}")
        print("\n🔧 Full error traceback:")
        traceback.print_exc()
        
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check Python version (3.7+ required)")
        print("2. Install missing dependencies:")
        print("   pip install flask flask-socketio flask-cors requests psutil")
        print("3. Verify file structure is correct")
        print("4. Check for syntax errors in Python files")
        print("5. Run in emergency mode: python -c 'from main import create_basic_server; s=create_basic_server(); s.app.run()'")
        
        sys.exit(1)