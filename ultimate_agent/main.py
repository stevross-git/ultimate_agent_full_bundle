#!/usr/bin/env python3
"""
Ultimate Agent Launcher
Simple launcher script that handles import path issues
"""

import sys
from pathlib import Path
import argparse

# Allow running directly via `python main.py`
if __package__ in (None, ""):
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    sys.path.insert(0, str(current_dir))


def main():
    """Launch the Ultimate Agent with proper path setup"""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Add the ultimate_agent directory to Python path
    ultimate_agent_dir = script_dir 
    if ultimate_agent_dir.exists():
        sys.path.insert(0, str(ultimate_agent_dir))
        print(f"✅ Added {ultimate_agent_dir} to Python path")
    else:
        print(f"❌ Error: {ultimate_agent_dir} not found")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Launch the Ultimate Agent")
    parser.add_argument("--node-url", help="Node URL for registration", default=None)
    parser.add_argument("--dashboard-port", type=int, help="Dashboard port", default=8080)
    args = parser.parse_args()

    try:
        from ultimate_agent import create_agent

        print("🤖 Initializing Ultimate Agent...")

        agent = create_agent(node_url=args.node_url, dashboard_port=args.dashboard_port)

        print("🚀 Starting Ultimate Agent...")
        agent.start()


        # Check if dashboard is available and get the port
        dashboard_port = args.dashboard_port or 8080
        if hasattr(agent, "modules") and "dashboard" in agent.modules:
            dashboard = agent.modules["dashboard"]
            if hasattr(dashboard, "dashboard_port"):
                dashboard_port = dashboard.dashboard_port
            print(f"🌐 Dashboard Web Server available on port {dashboard_port}")
            print(f"🌐 Access at: http://localhost:{dashboard_port}")

        else:
            print("⚠️ Dashboard not initialized")

        # Keep the main thread alive
        try:
            import threading
            import time
            
            print("✅ Ultimate Agent is running...")
            print("Press Ctrl+C to stop")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Ultimate Agent...")
            if hasattr(agent, 'stop'):
                agent.stop()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Make sure you're in the ultimate_agent_full_bundle directory")
        print("2. Run: pip install -r ultimate_agent/requirements.txt")
        print("3. Try: python -m ultimate_agent.main")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Ultimate Agent...")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()