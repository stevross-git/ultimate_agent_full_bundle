#!/usr/bin/env python3
"""
Simple dashboard test
"""

import sys
import os
from pathlib import Path

# Add to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def test_dashboard_import():
    """Test dashboard import"""
    try:
        from ultimate_agent.dashboard.web.routes import DashboardServer
        print("✅ DashboardServer import successful")
        
        # Test if stop method exists
        if hasattr(DashboardServer, 'stop'):
            print("✅ stop method exists")
        else:
            print("❌ stop method missing")
            
        return True
    except Exception as e:
        print(f"❌ Dashboard import failed: {e}")
        return False

def test_agent_import():
    """Test agent import"""
    try:
        from ultimate_agent.core.agent1 import UltimatePainNetworkAgent
        print("✅ Agent import successful")
        return True
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        return False

def main():
    print("🧪 Simple Dashboard Test")
    print("=" * 30)
    
    dashboard_ok = test_dashboard_import()
    agent_ok = test_agent_import()
    
    if dashboard_ok and agent_ok:
        print("\n✅ All imports working! Dashboard should work now.")
        print("Try running: python main.py")
    else:
        print("\n❌ Some issues remain. Check the errors above.")

if __name__ == "__main__":
    main()
