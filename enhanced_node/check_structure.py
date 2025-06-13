#!/usr/bin/env python3
"""
Enhanced Node Server - File Structure Checker
Verifies that all required files and directories are in place
"""

import os
from pathlib import Path

def check_file_structure():
    """Check if all required files and directories exist"""
    print("🔍 Enhanced Node Server - File Structure Check")
    print("=" * 60)
    
    current_dir = Path.cwd()
    print(f"📁 Current Directory: {current_dir}")
    
    # Required files and directories
    required_structure = {
        "files": [
            "main.py",
            "requirements.txt",
            "core/server.py",
            "core/database.py",
            "core/health.py",
            "config/settings.py",
            "config/__init__.py",
            "control/task_manager.py",
            "control/remote_manager.py",
            "control/version_manager.py",
            "control/__init__.py",
            "models/agents.py",
            "models/tasks.py",
            "models/commands.py",
            "models/scripts.py",
            "models/versions.py",
            "models/__init__.py",
            "routes/api_v3.py",
            "routes/api_v5_remote.py",
            "routes/api_v6_version.py",
            "routes/__init__.py",
            "utils/logger.py",
            "utils/serialization.py",
            "utils/__init__.py",
            "websocket/events.py",
            "websocket/__init__.py",
            "templates/enhanced_dashboard.html",
        ],
        "directories": [
            "core",
            "config", 
            "control",
            "models",
            "routes",
            "utils",
            "websocket",
            "templates",
            "static",
            "logs",
            "test"
        ]
    }
    
    # Check directories
    print("\n📁 Directory Check:")
    missing_dirs = []
    for directory in required_structure["directories"]:
        dir_path = current_dir / directory
        exists = dir_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {directory}/")
        if not exists:
            missing_dirs.append(directory)
    
    # Check files
    print("\n📄 File Check:")
    missing_files = []
    for file_path in required_structure["files"]:
        full_path = current_dir / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            missing_files.append(file_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    
    if not missing_dirs and not missing_files:
        print("✅ All required files and directories are present!")
        return True
    else:
        print("❌ Some files or directories are missing:")
        
        if missing_dirs:
            print(f"\n📁 Missing Directories ({len(missing_dirs)}):")
            for directory in missing_dirs:
                print(f"   - {directory}/")
        
        if missing_files:
            print(f"\n📄 Missing Files ({len(missing_files)}):")
            for file_path in missing_files:
                print(f"   - {file_path}")
        
        return False

def create_missing_structure():
    """Create missing directories and placeholder files"""
    print("\n🔧 Creating Missing Structure...")
    
    current_dir = Path.cwd()
    
    # Create missing directories
    directories = [
        "core", "config", "control", "models", "routes", 
        "utils", "websocket", "templates", "static", "logs", "test"
    ]
    
    for directory in directories:
        dir_path = current_dir / directory
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}/")
            except Exception as e:
                print(f"❌ Failed to create {directory}/: {e}")
    
    # Create __init__.py files for Python packages
    init_files = [
        "core/__init__.py",
        "config/__init__.py", 
        "control/__init__.py",
        "models/__init__.py",
        "routes/__init__.py",
        "utils/__init__.py",
        "websocket/__init__.py"
    ]
    
    for init_file in init_files:
        file_path = current_dir / init_file
        if not file_path.exists():
            try:
                file_path.touch()
                print(f"✅ Created: {init_file}")
            except Exception as e:
                print(f"❌ Failed to create {init_file}: {e}")

def main():
    """Main function"""
    structure_ok = check_file_structure()
    
    if not structure_ok:
        print("\n" + "=" * 60)
        print("🔧 FIXING STRUCTURE:")
        create_missing_structure()
        
        print("\n" + "=" * 60)
        print("📋 NEXT STEPS:")
        print("1. Copy the missing files from the document contents")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run: python main.py")
    else:
        print("\n" + "=" * 60)
        print("🎉 STRUCTURE OK!")
        print("All files are in place. You can run:")
        print("1. pip install -r requirements.txt")
        print("2. python main.py")

if __name__ == "__main__":
    main()