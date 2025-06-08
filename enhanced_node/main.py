#!/usr/bin/env python3
"""
Enhanced Node Server Main Entry Point
Boots the complete modular system
"""

import signal
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.server import EnhancedNodeServer
from routes.api_v3 import register_api_v3_routes
from routes.api_v5_remote import register_api_v5_routes
from websocket.events import register_websocket_events
from config.settings import NODE_PORT, NODE_VERSION, NODE_ID


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Received shutdown signal, stopping Enhanced Node Server...")
    sys.exit(0)


if __name__ == "__main__":
    print(f"""
====================================================================================================
🚀 ENHANCED ULTIMATE PAIN NETWORK NODE v{NODE_VERSION}
🏗️ MODULAR ARCHITECTURE - Enterprise AI Computing Platform  
====================================================================================================
📆 Starting Enhanced Node Server {NODE_ID}...
✅ All existing functionality preserved
🎮 Advanced remote control features available
🚀 Comprehensive agent management system
====================================================================================================
""")

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and configure server
    server = EnhancedNodeServer()
    
    # Register routes
    register_api_v3_routes(server)
    register_api_v5_routes(server)
    
    # Register WebSocket events
    register_websocket_events(server)
    
    # Start the server
    try:
        server.start()
        
        print(f"""
🌟 Enhanced Node Server is running!
📡 Dashboard: http://localhost:{NODE_PORT}
📊 Metrics: http://localhost:8091
🎮 Advanced Features: ✅ Enabled
        """)
        
        # Run the Flask-SocketIO server
        server.socketio.run(
            server.app, 
            host="0.0.0.0", 
            port=NODE_PORT,
            debug=False,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Node Server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    finally:
        server.stop()
        print("✅ Enhanced Node Server stopped gracefully")