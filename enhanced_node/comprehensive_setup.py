#!/usr/bin/env python3
"""
Comprehensive Setup and Run Script for Enhanced Node Server
Handles environment setup, dependency installation, and starts the server
"""

import sys
import subprocess
import os
import platform
from pathlib import Path
import time


def print_banner():
    """Print setup banner"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║  🚀 ENHANCED ULTIMATE PAIN NETWORK NODE - MODULAR ARCHITECTURE SETUP               ║
║  🏗️ Enterprise AI Computing Platform - Comprehensive Setup & Launch                ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

🔧 Setting up Enhanced Node Server with full modularization...
✅ All existing functionality preserved
🎮 Advanced remote control features available
🏗️ Clean modular architecture implemented
""")


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("❌ ERROR: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again.")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def check_system_requirements():
    """Check system requirements"""
    print("🖥️  Checking system requirements...")
    
    # Check operating system
    os_name = platform.system()
    print(f"   Operating System: {os_name}")
    
    # Check available space (basic check)
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        free_gb = free // (1024**3)
        print(f"   Available disk space: {free_gb} GB")
        
        if free_gb < 1:
            print("⚠️  WARNING: Low disk space (less than 1GB available)")
    except:
        print("   Could not check disk space")
    
    print("✅ System requirements check completed")


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "logs",
        "agent_scripts", 
        "command_history",
        "templates"
    ]
    
    created_count = 0
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            created_count += 1
            print(f"   Created: {directory}/")
        else:
            print(f"   Exists: {directory}/")
    
    print(f"✅ Directory setup completed ({created_count} new directories created)")


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Upgrade pip first
    print("   Upgrading pip...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print("   ✅ pip upgraded successfully")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  pip upgrade warning: {e}")
    
    # Check if requirements.txt exists
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        print("   Installing from requirements.txt...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            print("   ✅ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install requirements: {e}")
            print("   Trying individual package installation...")
            install_essential_packages()
    else:
        print("   requirements.txt not found, installing essential packages...")
        install_essential_packages()


def install_essential_packages():
    """Install essential packages individually"""
    essential_packages = [
        "Flask==2.3.2",
        "Flask-Cors==4.0.0", 
        "Flask-SocketIO==5.3.6",
        "Flask-Limiter==3.5.0",
        "requests==2.31.0",
        "SQLAlchemy==2.0.30",
        "psutil==5.9.8",
        "numpy==1.26.4",
        "pandas==2.2.2",
        "prometheus-client==0.20.0",
        "redis==5.0.3"
    ]
    
    installed_count = 0
    failed_packages = []
    
    for package in essential_packages:
        try:
            print(f"   Installing {package.split('==')[0]}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            installed_count += 1
        except subprocess.CalledProcessError:
            failed_packages.append(package)
            print(f"   ⚠️  Failed to install {package}")
    
    print(f"   ✅ {installed_count}/{len(essential_packages)} packages installed successfully")
    
    if failed_packages:
        print(f"   ❌ Failed packages: {', '.join([p.split('==')[0] for p in failed_packages])}")
        print("   The server may still work with reduced functionality.")


def verify_installation():
    """Verify the installation by importing key modules"""
    print("🔍 Verifying installation...")
    
    test_imports = [
        ("flask", "Flask web framework"),
        ("flask_cors", "Flask CORS support"),
        ("flask_socketio", "Flask WebSocket support"),
        ("sqlalchemy", "Database ORM"),
        ("psutil", "System monitoring"),
        ("prometheus_client", "Metrics collection"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data processing")
    ]
    
    successful_imports = 0
    for module_name, description in test_imports:
        try:
            __import__(module_name)
            print(f"   ✅ {description}")
            successful_imports += 1
        except ImportError:
            print(f"   ❌ {description} - Not available")
    
    print(f"✅ Verification completed: {successful_imports}/{len(test_imports)} modules available")
    
    if successful_imports < len(test_imports) * 0.8:  # Less than 80% success
        print("⚠️  WARNING: Some dependencies are missing. The server may not work properly.")
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Setup cancelled by user.")
            sys.exit(1)


def check_port_availability():
    """Check if required ports are available"""
    print("🔌 Checking port availability...")
    
    import socket
    
    ports_to_check = [
        (443, "Main server port"),
        (8091, "Metrics server port")
    ]
    
    all_available = True
    for port, description in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            print(f"   ✅ Port {port} ({description}) - Available")
        except OSError:
            print(f"   ❌ Port {port} ({description}) - In use")
            all_available = False
    
    if not all_available:
        print("⚠️  WARNING: Some ports are in use. You may need to stop other services.")
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Setup cancelled by user.")
            sys.exit(1)


def start_server():
    """Start the Enhanced Node Server"""
    print("🚀 Starting Enhanced Node Server...")
    print("=" * 90)
    
    try:
        # Import and start the server
        sys.path.insert(0, '.')
        
        print("   Loading modular components...")
        from main import main as start_main
        
        print("   All modules loaded successfully!")
        print("   Starting server...")
        
        start_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   There may be an issue with the modular structure.")
        print("   Please check that all files are in the correct locations.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        sys.exit(1)


def main():
    """Main setup function"""
    try:
        print_banner()
        
        # Step 1: Check Python version
        check_python_version()
        time.sleep(0.5)
        
        # Step 2: Check system requirements
        check_system_requirements()
        time.sleep(0.5)
        
        # Step 3: Create directories
        create_directories()
        time.sleep(0.5)
        
        # Step 4: Install dependencies
        install_dependencies()
        time.sleep(1)
        
        # Step 5: Verify installation
        verify_installation()
        time.sleep(0.5)
        
        # Step 6: Check port availability
        check_port_availability()
        time.sleep(0.5)
        
        print("\n" + "=" * 90)
        print("🎉 SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 90)
        print()
        print("🌟 Enhanced Node Server is ready to start!")
        print("📡 Dashboard will be available at: https://localhost:443")
        print("📊 Metrics will be available at: http://localhost:8091")
        print("🎮 Advanced Features: ✅ Enabled")
        print("🏗️ Modular Architecture: ✅ Enabled")
        print()
        
        response = input("Press Enter to start the server (or Ctrl+C to exit): ")
        
        # Step 7: Start the server
        start_server()
        
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()