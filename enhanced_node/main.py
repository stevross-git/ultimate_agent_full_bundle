#!/usr/bin/env python3
"""
Enhanced Node Server - Fixed Main Entry Point
Fixed import paths and better error handling
"""

import sys
import os
from pathlib import Path
import traceback
from integrations.orchestrator_client import add_orchestrator_integration
orchestrator_client = add_orchestrator_integration(node_server)
orchestrator_client.register_with_orchestrator()

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
        print("🎮 Features available:")
        if hasattr(server, 'advanced_remote_control'):
            print("   📡 Advanced remote control")
        if hasattr(server, 'task_control'):
            print("   📋 Task control system")
        if hasattr(server, 'version_control'):
            print("   🔄 Version control")
        print("   🌐 WebSocket support")
        print("   📊 Real-time dashboard")
        
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
        print("👋 Server stopped successfully")
    
    except Exception as e:
        print(f"❌ Critical error starting server: {e}")
        print("\n🔧 Full error traceback:")
        traceback.print_exc()
        
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check Python version (3.7+ required)")
        print("2. Install missing dependencies:")
        print("   pip install flask flask-socketio flask-cors")
        print("3. Verify file structure is correct")
        print("4. Check for syntax errors in Python files")
        print("5. Run in emergency mode: python -c 'from main import create_basic_server; s=create_basic_server(); s.app.run()'")
        
        sys.exit(1)