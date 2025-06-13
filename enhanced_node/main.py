#!/usr/bin/env python3
"""
Enhanced Node Server - Fixed Main Entry Point
Fixed import paths for running from within enhanced_node directory
"""

import sys
import os
from pathlib import Path

# Add current directory to sys.path for imports
ROOT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(ROOT_DIR))

# Also add parent directory in case we need it
sys.path.insert(0, str(ROOT_DIR.parent))

if __name__ == "__main__":
    try:
        print("🚀 Starting Enhanced Node Server...")
        print("🏗️ Loading modular components...")
        print(f"📁 Running from: {ROOT_DIR}")

        # Try different import paths
        server = None
        
        # Method 1: Direct import (running from enhanced_node directory)
        try:
            from core.server import EnhancedNodeServer
            print("✅ Imported using direct path")
            server = EnhancedNodeServer()
        except ImportError as e1:
            print(f"⚠️  Direct import failed: {e1}")
            
            # Method 2: Enhanced node import (running from parent directory)
            try:
                from enhanced_node.core.server import EnhancedNodeServer
                print("✅ Imported using enhanced_node path")
                server = EnhancedNodeServer()
            except ImportError as e2:
                print(f"⚠️  Enhanced node import failed: {e2}")
                
                # Method 3: Explicit path manipulation
                try:
                    # Add the core directory to path
                    core_dir = ROOT_DIR / "core"
                    if core_dir.exists():
                        sys.path.insert(0, str(core_dir))
                    
                    # Try importing server directly
                    import server as server_module
                    EnhancedNodeServer = server_module.EnhancedNodeServer
                    print("✅ Imported using explicit path")
                    server = EnhancedNodeServer()
                except ImportError as e3:
                    print(f"❌ All import methods failed!")
                    print(f"   Error 1: {e1}")
                    print(f"   Error 2: {e2}")
                    print(f"   Error 3: {e3}")
                    
                    print("\n🔧 Troubleshooting:")
                    print("1. Check if you're in the correct directory")
                    print("2. Verify all required files exist")
                    print("3. Check for syntax errors in imported files")
                    print("4. Run the debug script: python debug_startup.py")
                    sys.exit(1)

        if server is None:
            print("❌ Failed to create server instance")
            sys.exit(1)

        print("✅ All modules loaded successfully!")
        print("🎮 Advanced remote control features enabled")
        print("📊 Task control system enabled")
        print("🔌 WebSocket events enabled")
        print("📈 Prometheus metrics enabled")
        print("🔄 Version control system enabled")

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
        print(f"   📊 Metrics: http://localhost:8091/metrics")
        print(f"   🔌 WebSocket: ws://localhost:{port}/socket.io/")
        print(f"   🔍 Debug Info: http://localhost:{port}/api/health")

        print("\n🎯 Press Ctrl+C to stop the server")

        # Run the Flask-SocketIO server
        server.socketio.run(
            server.app,
            host='0.0.0.0',
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Node Server...")
        if 'server' in locals() and server:
            server.stop()
        print("👋 Server stopped successfully")

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Run: python debug_startup.py")
        print("2. Check that all required files exist")
        print("3. Verify Python version (3.7+ required)")
        print("4. Install missing dependencies: pip install -r requirements.txt")
        print("5. Check for syntax errors in imported files")
        
        sys.exit(1)