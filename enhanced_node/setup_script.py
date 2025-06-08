#!/usr/bin/env python3
"""
Setup and Run Script for Enhanced Node Server
Handles environment setup and starts the server
"""

import sys
import subprocess
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Upgrade pip first
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install requirements
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
    else:
        # Install essential packages if requirements.txt is missing
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
        
        for package in essential_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError:
                print(f"⚠️ Failed to install {package}, continuing...")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "logs",
        "agent_scripts", 
        "command_history",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} is compatible")

def main():
    """Main setup and run function"""
    print("""
====================================================================================================
🚀 ENHANCED ULTIMATE PAIN NETWORK NODE - MODULAR SETUP
🏗️ MODULAR ARCHITECTURE - Enterprise AI Computing Platform  
====================================================================================================
🔧 Setting up Enhanced Node Server...
    """)
    
    try:
        # Check Python version
        check_python_version()
        
        # Create directories
        create_directories()
        
        # Install dependencies
        install_dependencies()
        
        print("""
✅ Setup completed successfully!

🚀 Starting Enhanced Node Server...
====================================================================================================
        """)
        
        # Import and start the server
        from main import main as start_server
        start_server()
        
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
