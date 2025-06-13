#!/usr/bin/env python3
"""
Enhanced Node Server - Modular Version
Main entry point for the Enhanced Node Server
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path (one level above enhanced_node/)
ROOT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    try:
        print("🚀 Starting Enhanced Node Server...")
        print("🏗️ Loading modular components...")

        # ✅ Correct import path
        from enhanced_node.core.server import EnhancedNodeServer

        print("✅ All modules loaded successfully!")
        print("🎮 Advanced remote control features enabled")
        print("📊 Task control system enabled")
        print("🔌 WebSocket events enabled")
        print("📈 Prometheus metrics enabled")

        # Create and start server
        server = EnhancedNodeServer()

        # Start the server
        server.start()

        port = server.app.config.get('PORT', 5000)
        print(f"\n🌐 Enhanced Node Server running on:")
        print(f"   📱 Dashboard: http://localhost:{port}")
        print(f"   📊 Metrics: http://localhost:8091/metrics")
        print(f"   🔌 WebSocket: ws://localhost:{port}/socket.io/")

        print("\n🎯 Press Ctrl+C to stop the server")

        # Run the Flask-SocketIO server
        server.socketio.run(
            server.app,
            host='0.0.0.0',
            port=port,
            debug=False,
            allow_unsafe_werkzeug=True
        )

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Ensure you're in the project root directory")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check Python version (3.7+ required)")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Node Server...")
        print("👋 Server stopped successfully")

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
