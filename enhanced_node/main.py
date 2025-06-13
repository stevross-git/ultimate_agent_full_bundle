#!/usr/bin/env python3
"""
Ultimate Agent - Main Entry Point
Fixed version with proper imports and module structure
"""

import sys
import os
from pathlib import Path

# Add the ultimate_agent directory to Python path
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

def main():
    """Main entry point for Ultimate Agent"""
    try:
        print("🚀 Starting Ultimate Agent...")
        print("🔧 Loading components...")
        
        # Import with proper path handling
        try:
            from ultimate_agent.core.agent import UltimateAgent
        except ImportError:
            # Try alternative import path
            try:
                from core.agent import UltimateAgent
            except ImportError:
                # Try direct import
                import importlib.util
                spec = importlib.util.spec_from_file_location("agent", current_dir / "core" / "agent.py")
                if spec and spec.loader:
                    agent_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(agent_module)
                    UltimateAgent = agent_module.UltimateAgent
                else:
                    raise ImportError("Could not locate UltimateAgent class")
        
        print("✅ Ultimate Agent components loaded successfully!")
        
        # Create and start the agent
        agent = UltimateAgent()
        
        print(f"\n🌐 Ultimate Agent running on:")
        print(f"   📱 Dashboard: http://localhost:8080")
        print(f"   🔌 WebSocket: ws://localhost:8080/socket.io/")
        print(f"   📊 API: http://localhost:8080/api/")
        print("\n🎯 Press Ctrl+C to stop the agent")
        
        # Start the agent
        agent.start()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Ensure you're in the ultimate_agent_full_bundle directory")
        print("2. Check that all files are in place")
        print("3. Try: python -m ultimate_agent.main")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Ultimate Agent...")
        print("👋 Agent stopped successfully")
    except Exception as e:
        print(f"❌ Failed to start Ultimate Agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()