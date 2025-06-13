#!/usr/bin/env python3
"""
Ultimate Agent - Advanced AI Agent System
Main entry point for the Ultimate Agent
"""

import sys
from pathlib import Path

# Allow running directly via `python main.py`
if __package__ in (None, ""):
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    sys.path.insert(0, str(current_dir))


def main():
    """Main entry point for Ultimate Agent"""
    try:
        from ultimate_agent.core.agent import UltimateAgent
        from ultimate_agent.config.settings import get_config

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
