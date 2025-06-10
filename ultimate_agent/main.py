#!/usr/bin/env python3
"""
Ultimate Agent - Advanced AI Agent System
Main entry point for the Ultimate Agent
"""

import sys
import os
from pathlib import Path

# Add the ultimate_agent directory to Python path  
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point for Ultimate Agent"""
    try:
        from core.agent import UltimateAgent
        from config.settings import get_config

        print("🤖 Initializing Ultimate Agent...")
        config = get_config()
        agent = UltimateAgent(config)

        print("🚀 Starting Ultimate Agent...")
        agent.start()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Ultimate Agent...")
    except Exception as e:
        print(f"❌ Failed to start agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()