#!/usr/bin/env python3
"""
Ultimate Agent Launcher
Simple launcher script that handles import path issues
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the Ultimate Agent with proper path setup"""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Add the ultimate_agent directory to Python path
    ultimate_agent_dir = script_dir / "ultimate_agent"
    if ultimate_agent_dir.exists():
        sys.path.insert(0, str(ultimate_agent_dir))
        print(f"✅ Added {ultimate_agent_dir} to Python path")
    else:
        print(f"❌ Error: {ultimate_agent_dir} not found")
        sys.exit(1)
    
    try:
        # Import and run the agent
        print("🤖 Importing Ultimate Agent...")
        from core.agent import UltimateAgent
        from config.settings import get_config
        
        print("⚙️ Loading configuration...")
        config = get_config()
        
        print("🚀 Starting Ultimate Agent...")
        agent = UltimateAgent(config)
        agent.start()
        
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