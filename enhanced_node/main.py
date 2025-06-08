#!/usr/bin/env python3
"""
Enhanced Node Server Main Entry Point
Boots the complete modular system with all advanced features
"""

import signal
import sys
import os
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).resolve().parent
# Ensure package imports work when running as a script
if __package__ in (None, ""):
    sys.path.insert(0, str(current_dir.parent))
    __package__ = current_dir.name

# Import modular components
try:
    from .core.server import EnhancedNodeServer
    from .routes.api_v3 import register_api_v3_routes
    from .routes.api_v5_remote import register_api_v5_routes
    from .websocket.events import register_websocket_events
    from .config.settings import NODE_PORT, NODE_VERSION, NODE_ID
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("   Please ensure you're running from the enhanced_node/ directory")
    print("   and all dependencies are installed.")
    sys.exit(1)


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Received shutdown signal, stopping Enhanced Node Server...")
    sys.exit(0)


def main():
    """Main application entry point"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🚀 ENHANCED ULTIMATE PAIN NETWORK NODE v{NODE_VERSION}                            ║  
║  🏗️ MODULAR ARCHITECTURE - Enterprise AI Computing Platform                        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

📆 Starting Enhanced Node Server {NODE_ID}...
✅ All existing functionality preserved and enhanced
🎮 Advanced remote control features available  
🚀 Comprehensive agent management system
🏗️ Clean modular architecture implemented

Features Available:
├── 🧠 AI Orchestration & Management
├── 💰 Blockchain Transaction Processing  
├── ☁️ Cloud Integration & Services
├── 🔒 Advanced Security Features
├── 📊 Real-time Analytics & Monitoring
├── 🔌 Extensible Plugin Ecosystem
├── 🎯 Centralized Task Control
├── 🎮 Advanced Remote Agent Control
├── ⚙️ Configuration Management
├── 📡 Live Monitoring & Health Checks
├── 🚀 Bulk Operations & Automation
├── ⏰ Command Scheduling & Replay
├── 🔄 Automatic Recovery Systems
└── 📋 Script Deployment & Management

╔══════════════════════════════════════════════════════════════════════════════════════╗
║  Architecture: Fully Modularized | Status: Production Ready | Control: Advanced    ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
""")

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        print("🏗️ Initializing modular components...")
        
        # Create and configure the enhanced server
        server = EnhancedNodeServer()
        print("   ✅ Core server initialized")
        
        # Register API routes
        print("🔗 Registering API routes...")
        register_api_v3_routes(server)
        print("   ✅ API v3 routes registered (agent management)")
        
        register_api_v5_routes(server)
        print("   ✅ API v5 routes registered (advanced remote control)")
        
        # Register WebSocket events
        print("📡 Registering WebSocket events...")
        register_websocket_events(server)
        print("   ✅ WebSocket events registered (real-time communication)")
        
        # Start the server
        print("🚀 Starting Enhanced Node Server...")
        server.start()
        print("   ✅ Background services started")
        print("   ✅ Task control manager active")
        print("   ✅ Advanced remote control manager active")
        print("   ✅ Health monitoring active")
        print("   ✅ Command scheduler active")
        
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🌟 ENHANCED NODE SERVER IS RUNNING!                                                ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  📡 Dashboard:        http://localhost:{NODE_PORT}                                     ║
║  📊 Metrics:          http://localhost:8091                                         ║  
║  🎮 Advanced Control: ✅ Enabled                                                     ║
║  🏗️ Architecture:     ✅ Modular                                                     ║
║  📈 Monitoring:       ✅ Real-time                                                   ║
║  🔄 Auto-Recovery:    ✅ Active                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

🎯 Ready to manage Ultimate Pain Network agents with advanced capabilities!
🎮 Access the dashboard to start controlling your agent network.
📊 Monitor performance and health in real-time.
🚀 Deploy scripts and execute bulk operations with ease.

Press Ctrl+C to stop the server gracefully.
        """)
        
        # Run the Flask-SocketIO server
        server.socketio.run(
            server.app, 
            host="0.0.0.0", 
            port=NODE_PORT,
            debug=False,
            use_reloader=False,
            log_output=False  # Reduce verbose output
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Node Server...")
    except ImportError as e:
        print(f"❌ Module Import Error: {e}")
        print("   Please check that all modular components are properly installed.")
        print("   You may need to run the setup script: python setup_and_run.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server Error: {e}")
        print("   Check the logs for more details.")
        sys.exit(1)
    finally:
        try:
            server.stop()
            print("✅ Enhanced Node Server stopped gracefully")
            print("🎉 Thank you for using the Enhanced Ultimate Pain Network Node!")
        except:
            pass


if __name__ == "__main__":
    main()