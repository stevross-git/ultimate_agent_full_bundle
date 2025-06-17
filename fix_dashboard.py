#!/usr/bin/env python3
import os
import re

def fix_agent_start_method():
    """Fix the agent start method to avoid calling start() on TaskScheduler"""
    
    files_to_check = ['core/agent1.py', '__init__.py']
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Find and replace the problematic start managers code
            if 'Error starting managers' in content:
                # Replace the entire problematic block
                content = re.sub(
                    r'try:\s*\n.*?for.*?manager.*?in.*?:\s*\n.*?manager\.start\(\).*?\n.*?except.*?Error starting managers.*?\n.*?print.*?Error starting managers.*?\n',
                    '''try:
            # Only start dashboard manager if it exists and has start_server method
            if hasattr(self, 'dashboard_manager') and self.dashboard_manager:
                if hasattr(self.dashboard_manager, 'start_server'):
                    self.dashboard_manager.start_server()
                    print("✅ Dashboard server started")
                else:
                    print("ℹ️ Dashboard manager ready")
            else:
                print("⚠️ Dashboard manager not found")
        except Exception as e:
            print(f"⚠️ Warning during startup: {e}")
''',
                    content,
                    flags=re.MULTILINE | re.DOTALL
                )
                
                with open(filepath, 'w') as f:
                    f.write(content)
                
                print(f"✅ Fixed {filepath}")
                return True
    
    return False

def ensure_dashboard_manager():
    """Ensure dashboard manager is properly initialized"""
    
    agent_file = 'core/agent1.py'
    if os.path.exists(agent_file):
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check if dashboard manager initialization exists
        if 'self.dashboard_manager' not in content:
            # Add dashboard manager initialization
            init_block = '''
        
        # Initialize dashboard manager
        try:
            from ..dashboard.web.routes import DashboardServer
            self.dashboard_manager = DashboardServer(self)
            print("🌐 Dashboard manager initialized")
        except Exception as e:
            print(f"⚠️ Dashboard initialization warning: {e}")
            self.dashboard_manager = None'''
            
            # Insert before the completion message
            content = content.replace(
                'print("✅ Ultimate Pain Network Agent initialized")',
                init_block + '\n\n        print("✅ Ultimate Pain Network Agent initialized")'
            )
            
            with open(agent_file, 'w') as f:
                f.write(content)
            
            print("✅ Added dashboard manager initialization")

# Run fixes
print("🔧 Fixing dashboard and manager issues...")
fix_agent_start_method()
ensure_dashboard_manager()
print("✅ Fixes completed!")
