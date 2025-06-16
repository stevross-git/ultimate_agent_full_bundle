# config/orchestrator_settings.py
"""
Orchestrator Integration Settings
Add this to your enhanced_node configuration
"""

# Orchestrator Connection Settings
ORCHESTRATOR_ENABLED = True
ORCHESTRATOR_URL = "http://localhost:9000"
ORCHESTRATOR_HEARTBEAT_INTERVAL = 30  # seconds
ORCHESTRATOR_REGISTRATION_TIMEOUT = 10  # seconds
ORCHESTRATOR_AUTO_RETRY = True
ORCHESTRATOR_RETRY_INTERVAL = 60  # seconds

# Node Identity Settings
NODE_ID_PREFIX = "enhanced_node"
NODE_CAPABILITIES = [
    "agent_management",
    "task_control", 
    "remote_management",
    "ai_operations",
    "blockchain_support",
    "websocket_communication",
    "real_time_monitoring",
    "bulk_operations",
    "script_deployment"
]

# Performance Monitoring
PERFORMANCE_MONITORING_ENABLED = True
HEALTH_CHECK_INTERVAL = 60  # seconds
LOAD_BALANCING_ENABLED = True

# Security Settings
ORCHESTRATOR_API_KEY = None  # Set if orchestrator requires authentication
SECURE_COMMUNICATION = False  # Set to True for HTTPS

# Logging
ORCHESTRATOR_LOG_LEVEL = "INFO"
ORCHESTRATOR_LOG_FILE = "logs/orchestrator_integration.log"

# --- Integration Script ---
# enhanced_node/setup_orchestrator_integration.py
"""
Setup script to integrate Enhanced Node with Web4AI Orchestrator
Run this script to enable orchestrator integration
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_orchestrator_integration():
    """Setup orchestrator integration for enhanced node"""
    
    print("🔧 Setting up Web4AI Orchestrator Integration...")
    
    # Check if in correct directory
    if not os.path.exists('main.py'):
        print("❌ Error: Please run this script from the enhanced_node/ directory")
        return False
    
    # Create integrations directory if it doesn't exist
    os.makedirs('integrations', exist_ok=True)
    
    # Create __init__.py for integrations module
    init_file = Path('integrations/__init__.py')
    if not init_file.exists():
        init_file.write_text('# Integrations module\n')
    
    print("✅ Created integrations module structure")
    
    # Update main.py to include orchestrator client
    try:
        main_py_path = Path('main.py')
        if main_py_path.exists():
            main_content = main_py_path.read_text()
            
            # Check if orchestrator integration is already added
            if 'orchestrator_client' not in main_content:
                # Add orchestrator integration
                integration_code = '''
# Orchestrator Integration
try:
    from integrations.orchestrator_client import add_orchestrator_integration
    
    # Add orchestrator integration if enabled
    if getattr(settings, 'ORCHESTRATOR_ENABLED', False):
        orchestrator_client = add_orchestrator_integration(
            node_server, 
            getattr(settings, 'ORCHESTRATOR_URL', 'http://localhost:9000')
        )
        
        # Attempt registration
        if orchestrator_client.register_with_orchestrator():
            print("✅ Successfully integrated with Web4AI Orchestrator")
        else:
            print("⚠️ Orchestrator integration enabled but registration failed")
            print("   Make sure the orchestrator is running and accessible")
except ImportError:
    print("⚠️ Orchestrator integration module not found")
except Exception as e:
    print(f"⚠️ Orchestrator integration error: {e}")
'''
                
                # Find the right place to insert the code
                if 'if __name__ == "__main__":' in main_content:
                    # Insert before the main block
                    main_content = main_content.replace(
                        'if __name__ == "__main__":',
                        integration_code + '\nif __name__ == "__main__":'
                    )
                else:
                    # Append to the end
                    main_content += integration_code
                
                # Write updated main.py
                main_py_path.write_text(main_content)
                print("✅ Updated main.py with orchestrator integration")
            else:
                print("✅ Orchestrator integration already present in main.py")
    
    except Exception as e:
        print(f"⚠️ Warning: Could not update main.py automatically: {e}")
        print("   You'll need to manually add the orchestrator integration code")
    
    # Update settings.py to include orchestrator settings
    try:
        settings_path = Path('config/settings.py')
        if settings_path.exists():
            settings_content = settings_path.read_text()
            
            if 'ORCHESTRATOR_ENABLED' not in settings_content:
                orchestrator_settings = '''
# Orchestrator Integration Settings
ORCHESTRATOR_ENABLED = True
ORCHESTRATOR_URL = "http://localhost:9000"
ORCHESTRATOR_HEARTBEAT_INTERVAL = 30
ORCHESTRATOR_REGISTRATION_TIMEOUT = 10
ORCHESTRATOR_AUTO_RETRY = True
ORCHESTRATOR_RETRY_INTERVAL = 60

NODE_CAPABILITIES = [
    "agent_management",
    "task_control", 
    "remote_management",
    "ai_operations",
    "blockchain_support",
    "websocket_communication",
    "real_time_monitoring",
    "bulk_operations",
    "script_deployment"
]
'''
                settings_content += orchestrator_settings
                settings_path.write_text(settings_content)
                print("✅ Updated settings.py with orchestrator configuration")
            else:
                print("✅ Orchestrator settings already present in settings.py")
                
    except Exception as e:
        print(f"⚠️ Warning: Could not update settings.py automatically: {e}")
        print("   You'll need to manually add the orchestrator settings")
    
    # Create systemd service file template
    create_systemd_service()
    
    # Create docker-compose integration
    create_docker_compose()
    
    print("\n🎉 Orchestrator integration setup complete!")
    print("\n📋 Next Steps:")
    print("1. Make sure the Web4AI Orchestrator is running on port 9000")
    print("2. Start your enhanced node: python main.py")
    print("3. Check the logs for successful registration")
    print("4. Visit the orchestrator dashboard to see your node")
    
    return True

def create_systemd_service():
    """Create systemd service file for production deployment"""
    service_content = '''[Unit]
Description=Enhanced Node with Orchestrator Integration
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/enhanced_node
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/path/to/enhanced_node

[Install]
WantedBy=multi-user.target
'''
    
    os.makedirs('deployment', exist_ok=True)
    with open('deployment/enhanced-node.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Created systemd service template: deployment/enhanced-node.service")

def create_docker_compose():
    """Create docker-compose file for container deployment"""
    compose_content = '''version: '3.8'
services:
  enhanced-node:
    build: .
    ports:
      - "5000:5000"
    environment:
      - NODE_ID=enhanced_node_1
      - ORCHESTRATOR_URL=http://orchestrator:9000
      - ORCHESTRATOR_ENABLED=true
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - web4ai-network
    depends_on:
      - orchestrator
    restart: unless-stopped

  orchestrator:
    image: web4ai/orchestrator:latest
    ports:
      - "9000:9000"
    environment:
      - ORCHESTRATOR_CONFIG=/app/config/orchestrator_config.yaml
    volumes:
      - ./orchestrator_config:/app/config
      - ./orchestrator_data:/app/data
    networks:
      - web4ai-network
    restart: unless-stopped

networks:
  web4ai-network:
    driver: bridge
'''
    
    dockerfile_content = '''FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
'''
    
    os.makedirs('deployment', exist_ok=True)
    
    with open('deployment/docker-compose.yml', 'w') as f:
        f.write(compose_content)
    
    with open('deployment/Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created Docker deployment files: deployment/docker-compose.yml")

if __name__ == "__main__":
    setup_orchestrator_integration()