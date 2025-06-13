#!/usr/bin/env python3
"""
Debug Startup Script for Enhanced Node Server
Helps identify and fix common issues preventing dashboard loading
"""

import sys
import os
from pathlib import Path
import traceback

def debug_environment():
    """Debug the environment and file structure"""
    print("🔍 Enhanced Node Server - Debug Startup")
    print("=" * 60)
    
    # Check Python version
    print(f"🐍 Python Version: {sys.version}")
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current Directory: {current_dir}")
    
    # Check project root
    script_dir = Path(__file__).parent
    print(f"📁 Script Directory: {script_dir}")
    
    # Check for key files
    key_files = [
        "main.py",
        "core/server.py",
        "templates/enhanced_dashboard.html",
        "routes/api_v3.py",
        "config/settings.py"
    ]
    
    print("\n📋 File Structure Check:")
    for file_path in key_files:
        full_path = script_dir / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path} - {full_path}")
    
    # Check templates directory
    templates_dir = script_dir / "templates"
    print(f"\n📁 Templates Directory: {templates_dir}")
    print(f"   Exists: {templates_dir.exists()}")
    
    if templates_dir.exists():
        template_files = list(templates_dir.glob("*.html"))
        print(f"   HTML Files: {len(template_files)}")
        for template_file in template_files:
            print(f"   - {template_file.name}")
    
    # Check imports
    print("\n🔗 Import Test:")
    try:
        sys.path.insert(0, str(script_dir))
        
        # Test core imports
        try:
            from enhanced_node.config.settings import NODE_ID, NODE_VERSION
            print(f"✅ Settings imported - Node ID: {NODE_ID}, Version: {NODE_VERSION}")
        except ImportError as e:
            print(f"❌ Settings import failed: {e}")
        
        # Test Flask import
        try:
            from flask import Flask
            print("✅ Flask imported successfully")
        except ImportError as e:
            print(f"❌ Flask import failed: {e}")
        
        # Test server import
        try:
            from enhanced_node.core.server import EnhancedNodeServer
            print("✅ EnhancedNodeServer imported successfully")
        except ImportError as e:
            print(f"❌ EnhancedNodeServer import failed: {e}")
            print(f"   Error details: {traceback.format_exc()}")
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
    
    return True

def fix_common_issues():
    """Fix common issues"""
    print("\n🔧 Attempting to fix common issues...")
    
    script_dir = Path(__file__).parent
    
    # Create missing directories
    directories_to_create = [
        "logs",
        "templates", 
        "static",
        "agent_scripts",
        "command_history"
    ]
    
    for dir_name in directories_to_create:
        dir_path = script_dir / dir_name
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {dir_name}")
            except Exception as e:
                print(f"❌ Failed to create directory {dir_name}: {e}")
        else:
            print(f"✅ Directory exists: {dir_name}")
    
    # Check template file
    template_file = script_dir / "templates" / "enhanced_dashboard.html"
    if not template_file.exists():
        print(f"❌ Template file missing: {template_file}")
        print("   This could be why the dashboard is not loading")
    else:
        print(f"✅ Template file exists: {template_file}")
        # Check file size
        file_size = template_file.stat().st_size
        print(f"   File size: {file_size} bytes")
        if file_size < 1000:
            print("   ⚠️  Template file seems very small - may be incomplete")

def test_server_startup():
    """Test server startup"""
    print("\n🚀 Testing Server Startup...")
    
    try:
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))
        
        # Mock some imports to avoid issues
        try:
            from enhanced_node.core.server import EnhancedNodeServer
            
            print("✅ Attempting to create server instance...")
            
            # Create server instance
            server = EnhancedNodeServer()
            print("✅ Server instance created successfully")
            
            # Check Flask app
            if hasattr(server, 'app'):
                print("✅ Flask app created")
                
                # Check template folder
                if hasattr(server.app, 'template_folder'):
                    print(f"✅ Template folder configured: {server.app.template_folder}")
                    
                    # Check if template folder exists
                    template_path = Path(server.app.template_folder)
                    if template_path.exists():
                        print("✅ Template folder exists")
                        
                        # List template files
                        template_files = list(template_path.glob("*.html"))
                        print(f"✅ Found {len(template_files)} template files")
                        for template_file in template_files:
                            print(f"   - {template_file.name}")
                    else:
                        print(f"❌ Template folder does not exist: {template_path}")
                else:
                    print("❌ Template folder not configured")
            else:
                print("❌ Flask app not created")
            
            # Check routes
            if hasattr(server, 'app'):
                routes = [str(rule) for rule in server.app.url_map.iter_rules()]
                print(f"✅ Registered {len(routes)} routes")
                
                # Check for dashboard route
                dashboard_routes = [r for r in routes if r == "/"]
                if dashboard_routes:
                    print("✅ Dashboard route (/) registered")
                else:
                    print("❌ Dashboard route (/) not found")
            
            print("✅ Server startup test completed successfully")
            
        except Exception as e:
            print(f"❌ Server startup failed: {e}")
            print(f"   Error details: {traceback.format_exc()}")
            
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")

def main():
    """Main debug function"""
    try:
        debug_environment()
        fix_common_issues()
        test_server_startup()
        
        print("\n" + "=" * 60)
        print("🎯 Debug Summary:")
        print("1. Check that all files exist and are in the correct locations")
        print("2. Ensure template files are properly created")
        print("3. Verify that imports are working correctly")
        print("4. Check that Flask template folder is configured")
        print("\n💡 If dashboard still not loading:")
        print("1. Run: python enhanced_node/main.py")
        print("2. Check browser console for JavaScript errors")
        print("3. Check server logs for error messages")
        print("4. Try accessing: http://localhost:5000")
        print("\n🔧 For further debugging:")
        print("1. Check the server logs in the logs/ directory")
        print("2. Verify that port 5000 is not blocked")
        print("3. Try a different browser or incognito mode")
        
    except Exception as e:
        print(f"❌ Debug script failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")

if __name__ == "__main__":
    main()