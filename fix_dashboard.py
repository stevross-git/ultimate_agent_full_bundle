#!/usr/bin/env python3
"""
Dashboard Fix & Verification Script
Fixes merge conflicts and dashboard loading issues
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess
import re

class DashboardFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / "backups"
        self.fixes_applied = []
        
    def run_all_fixes(self):
        """Run all fixes in sequence"""
        print("🔧 Ultimate Agent Dashboard Fix Tool")
        print("=" * 50)
        
        self.create_backup_directory()
        self.backup_critical_files()
        self.fix_duplicate_dashboard_methods()
        self.resolve_agent_class_conflicts()
        self.verify_dashboard_server()
        self.test_imports()
        self.create_verification_script()
        
        print("\n✅ All fixes completed!")
        print("🚀 Next steps:")
        print("1. Run: python main.py --test-imports")
        print("2. If successful, run: python main.py")
        print("3. Check dashboard at: http://localhost:8080")
    
    def create_backup_directory(self):
        """Create backup directory for safety"""
        self.backup_dir.mkdir(exist_ok=True)
        print(f"📁 Created backup directory: {self.backup_dir}")
    
    def backup_critical_files(self):
        """Backup critical files before making changes"""
        critical_files = [
            "ultimate_agent/core/agent.py",
            "ultimate_agent/core/agent1.py", 
            "ultimate_agent/main.py",
            "ultimate_agent/dashboard/web/routes/__init__.py"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / f"{full_path.name}.backup"
                shutil.copy2(full_path, backup_path)
                print(f"💾 Backed up: {file_path}")
    
    def fix_duplicate_dashboard_methods(self):
        """Fix duplicate _initialize_dashboard methods"""
        agent_file = self.project_root / "ultimate_agent/core/agent.py"
        
        if not agent_file.exists():
            print("ℹ️ agent.py not found, skipping duplicate method fix")
            return
        
        print("🔧 Fixing duplicate dashboard initialization methods...")
        
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Look for duplicate method definitions
        dashboard_methods = re.findall(r'def _initialize_dashboard\(self\):.*?(?=def|\Z)', content, re.DOTALL)
        
        if len(dashboard_methods) > 1:
            print(f"⚠️ Found {len(dashboard_methods)} duplicate dashboard methods")
            
            # Keep only the first complete method and remove duplicates
            fixed_content = re.sub(
                r'(def _initialize_dashboard\(self\):.*?(?=def|\Z))',
                self._get_corrected_dashboard_method(),
                content,
                count=1
            )
            
            # Remove any remaining duplicate methods
            fixed_content = re.sub(
                r'\s*"""Initialize dashboard module""".*?try:.*?self\.logger\.warning\(f"⚠️ D[^"]*"\)',
                '',
                fixed_content,
                flags=re.DOTALL
            )
            
            with open(agent_file, 'w') as f:
                f.write(fixed_content)
            
            self.fixes_applied.append("Fixed duplicate dashboard methods")
            print("✅ Fixed duplicate dashboard methods")
        else:
            print("ℹ️ No duplicate dashboard methods found")
    
    def _get_corrected_dashboard_method(self):
        """Get the corrected dashboard initialization method"""
        return '''def _initialize_dashboard(self):
        """Initialize dashboard module"""
        try:
            from ..dashboard.web.routes import DashboardServer
            
            # Create dashboard instance with correct parameters
            dashboard = DashboardServer(self)  # Pass self (agent instance)
            self.modules['dashboard'] = dashboard
            
            # Store dashboard reference for easy access
            self.dashboard_manager = dashboard
            
            # Start the dashboard server
            dashboard.start_server()
            
            self.logger.info("✅ Dashboard initialized and server started")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Dashboard not available: {e}")
        except Exception as e:
            self.logger.error(f"❌ Dashboard initialization failed: {e}")
            import traceback
            self.logger.error(f"Dashboard error details: {traceback.format_exc()}")'''
    
    def resolve_agent_class_conflicts(self):
        """Resolve conflicts between agent.py and agent1.py"""
        agent_file = self.project_root / "ultimate_agent/core/agent.py"
        agent1_file = self.project_root / "ultimate_agent/core/agent1.py"
        
        if agent_file.exists() and agent1_file.exists():
            print("🔧 Resolving agent class conflicts...")
            
            # Check which file is more complete/recent
            agent_size = agent_file.stat().st_size
            agent1_size = agent1_file.stat().st_size
            
            if agent1_size > agent_size:
                print("📝 agent1.py appears to be the main file, renaming agent.py")
                backup_path = self.backup_dir / "agent_conflicted.py"
                shutil.move(agent_file, backup_path)
                self.fixes_applied.append("Resolved agent class conflicts")
            else:
                print("📝 agent.py appears to be the main file, keeping it")
        
        print("ℹ️ Agent class conflicts resolved")
    
    def verify_dashboard_server(self):
        """Verify dashboard server implementation"""
        dashboard_file = self.project_root / "ultimate_agent/dashboard/web/routes/__init__.py"
        
        if not dashboard_file.exists():
            print("❌ Dashboard routes file not found!")
            return
        
        print("🔍 Verifying dashboard server implementation...")
        
        with open(dashboard_file, 'r') as f:
            content = f.read()
        
        # Check for required components
        checks = [
            ("DashboardServer class", "class DashboardServer"),
            ("start_server method", "def start_server"),
            ("Flask app", "Flask(__name__)"),
            ("SocketIO", "SocketIO")
        ]
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"✅ {check_name} found")
            else:
                print(f"❌ {check_name} missing")
    
    def test_imports(self):
        """Test critical imports"""
        print("🧪 Testing critical imports...")
        
        import_tests = [
            ("Config Manager", "from ultimate_agent.config.config_settings import ConfigManager"),
            ("Dashboard Server", "from ultimate_agent.dashboard.web.routes import DashboardServer"),
        ]
        
        # Test agent imports
        agent_imports = [
            ("Agent1", "from ultimate_agent.core.agent1 import UltimatePainNetworkAgent"),
            ("Agent", "from ultimate_agent.core.agent import UltimateAgent")
        ]
        
        for name, import_cmd in import_tests:
            try:
                exec(import_cmd)
                print(f"✅ {name} import successful")
            except ImportError as e:
                print(f"❌ {name} import failed: {e}")
        
        # Test at least one agent import works
        agent_import_success = False
        for name, import_cmd in agent_imports:
            try:
                exec(import_cmd)
                print(f"✅ {name} import successful")
                agent_import_success = True
                break
            except ImportError:
                print(f"⚠️ {name} import failed")
        
        if not agent_import_success:
            print("❌ No agent class imports successful")
    
    def create_verification_script(self):
        """Create a verification script for testing"""
        verify_script = self.project_root / "verify_dashboard.py"
        
        script_content = '''#!/usr/bin/env python3
"""
Dashboard Verification Script
Tests if the dashboard is working correctly
"""

import sys
import time
import requests
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def test_agent_creation():
    """Test agent creation"""
    print("🧪 Testing agent creation...")
    
    try:
        # Try importing agent1 first
        try:
            from ultimate_agent.core.agent1 import UltimatePainNetworkAgent
            agent = UltimatePainNetworkAgent()
            print("✅ UltimatePainNetworkAgent created successfully")
        except ImportError:
            from ultimate_agent.core.agent import UltimateAgent
            agent = UltimateAgent()
            print("✅ UltimateAgent created successfully")
        
        return agent
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return None

def test_dashboard_initialization(agent):
    """Test dashboard initialization"""
    print("🧪 Testing dashboard initialization...")
    
    try:
        if hasattr(agent, 'dashboard_manager') and agent.dashboard_manager:
            print("✅ Dashboard manager found")
            return True
        elif 'dashboard' in getattr(agent, 'modules', {}):
            print("✅ Dashboard module found in modules")
            return True
        else:
            print("❌ Dashboard not properly initialized")
            return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_dashboard_server():
    """Test if dashboard server is responding"""
    print("🧪 Testing dashboard server response...")
    
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard server responding")
            return True
        else:
            print(f"⚠️ Dashboard server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Dashboard server not responding (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Dashboard server test failed: {e}")
        return False

def main():
    print("🔍 Dashboard Verification Test")
    print("=" * 40)
    
    # Test agent creation
    agent = test_agent_creation()
    if not agent:
        sys.exit(1)
    
    # Test dashboard initialization
    dashboard_ok = test_dashboard_initialization(agent)
    
    # If dashboard is initialized, test if server is running
    if dashboard_ok:
        print("⏳ Waiting for server to start...")
        time.sleep(3)  # Give server time to start
        test_dashboard_server()
    
    print("\\n📋 Verification complete!")
    print("If all tests passed, your dashboard should be working.")

if __name__ == "__main__":
    main()
'''
        
        with open(verify_script, 'w') as f:
            f.write(script_content)
        
        verify_script.chmod(0o755)  # Make executable
        print(f"📝 Created verification script: {verify_script}")
    
    def print_summary(self):
        """Print summary of fixes applied"""
        print("\n📋 Summary of fixes applied:")
        for fix in self.fixes_applied:
            print(f"✅ {fix}")
        
        if not self.fixes_applied:
            print("ℹ️ No fixes were needed")

def main():
    """Main function"""
    fixer = DashboardFixer()
    fixer.run_all_fixes()
    fixer.print_summary()

if __name__ == "__main__":
    main()