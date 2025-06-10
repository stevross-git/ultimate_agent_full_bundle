#!/usr/bin/env python3
"""
Enhanced Node Server - Modular Version
Main entry point for the Enhanced Node Server
"""

import sys
import os
from pathlib import Path

# Add the enhanced_node directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    try:
        from core.server import EnhancedNodeServerAdvanced

        print("🚀 Starting Enhanced Node Server...")
        server = EnhancedNodeServerAdvanced()
        server.run()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enhanced Node Server...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)