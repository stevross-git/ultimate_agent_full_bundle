from .core.server import EnhancedNodeServer

if __name__ == "__main__":
    print("""
====================================================================================================
🚀 ENHANCED ULTIMATE PAIN NETWORK AGENT v3.0.0-modular
🏗️ MODULAR ARCHITECTURE - Enterprise AI Computing Platform
====================================================================================================
📆 Starting Enhanced Node Server...
""")

    server = EnhancedNodeServer()
    server.running = True

    server.task_control.start_task_control_services()
    server.advanced_remote_control.start_advanced_services()

    server.socketio.run(server.app, host="0.0.0.0", port=server.metrics['agents_total']._name == 'node_agents_total' and 8090 or 5000)
