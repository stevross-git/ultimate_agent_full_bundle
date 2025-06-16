#!/bin/bash
# setup-node-orchestrator.sh - Connect Enhanced Nodes to the orchestrator

echo "🔗 Setting up Enhanced Node → Orchestrator Connection"
echo "===================================================="

# Check if we're in the enhanced_node directory
if [ ! -f "main.py" ]; then
    echo "❌ Please run this script from your enhanced_node directory"
    echo "   cd /path/to/enhanced_node"
    echo "   bash setup-node-orchestrator.sh"
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Step 1: Create the integrations directory
echo "1️⃣ Creating integrations directory..."
mkdir -p integrations
touch integrations/__init__.py

# Step 2: Create the orchestrator client
echo "2️⃣ Creating orchestrator client..."
cat > integrations/orchestrator_client.py << 'EOF'
"""
Orchestrator Integration Client for Enhanced Nodes
This module enables nodes to communicate with the Web4AI Orchestrator
"""

import requests
import json
import time
import threading
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import socket

class OrchestratorClient:
    """Client for integrating Enhanced Nodes with Web4AI Orchestrator"""
    
    def __init__(self, node_server, orchestrator_url: str = "https://orc.peoplesainetwork.com"):
        self.node_server = node_server
        self.orchestrator_url = orchestrator_url.rstrip('/')
        self.node_id = f"enhanced_node_{uuid.uuid4().hex[:8]}"
        self.registered = False
        self.heartbeat_thread = None
        self.heartbeat_interval = 30  # seconds
        self.logger = logging.getLogger(__name__)
        
        # Get node server info
        self.node_host = getattr(node_server, 'host', self._get_local_ip())
        self.node_port = getattr(node_server, 'port', 5000)
        
        # Node capabilities based on enhanced_node features
        self.capabilities = [
            "agent_management",
            "task_control", 
            "remote_management",
            "ai_operations",
            "blockchain_support",
            "websocket_communication",
            "real_time_monitoring",
            "bulk_operations",
            "script_deployment",
            "enhanced_node_v2"
        ]
        
        print(f"🔗 Orchestrator client initialized for {self.node_id}")
        print(f"🎯 Target orchestrator: {self.orchestrator_url}")
    
    def _get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def register_with_orchestrator(self) -> bool:
        """Register this node with the orchestrator"""
        try:
            # Get current node status
            node_stats = self._get_node_status()
            
            registration_data = {
                'node_id': self.node_id,
                'host': self.node_host,
                'port': self.node_port,
                'capabilities': self.capabilities,
                'agents': self._get_agent_list(),
                'node_type': 'enhanced_node',
                'version': '2.0.0',
                'api_versions': ['v3', 'v4', 'v5', 'v6'],
                'features': {
                    'task_control': hasattr(self.node_server, 'task_control'),
                    'remote_management': hasattr(self.node_server, 'advanced_remote_control'),
                    'websocket_support': True,
                    'monitoring': True,
                    'security': True
                },
                'performance': node_stats,
                'registration_time': datetime.now().isoformat(),
                'external_url': f"http://{self.node_host}:{self.node_port}"
            }
            
            print(f"📡 Attempting to register with orchestrator...")
            print(f"   Node ID: {self.node_id}")
            print(f"   Host: {self.node_host}:{self.node_port}")
            print(f"   Capabilities: {len(self.capabilities)} features")
            
            response = requests.post(
                f"{self.orchestrator_url}/api/v1/nodes/{self.node_id}/register",
                json=registration_data,
                timeout=15,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"📡 Registration response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    self.registered = True
                    self.logger.info(f"✅ Successfully registered with orchestrator: {self.node_id}")
                    print(f"✅ Successfully registered with orchestrator!")
                    print(f"   Registration ID: {result.get('registration_id', 'N/A')}")
                    self._start_heartbeat_thread()
                    return True
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self.logger.error(f"❌ Registration failed: {error_msg}")
                    print(f"❌ Registration failed: {error_msg}")
                    return False
            else:
                error_text = response.text[:200]  # First 200 chars
                self.logger.error(f"❌ Registration HTTP error: {response.status_code} - {error_text}")
                print(f"❌ Registration HTTP error: {response.status_code}")
                print(f"   Response: {error_text}")
                return False
                
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"❌ Cannot connect to orchestrator at {self.orchestrator_url}")
            print(f"❌ Cannot connect to orchestrator at {self.orchestrator_url}")
            print(f"   Error: {str(e)}")
            return False
        except requests.exceptions.Timeout as e:
            self.logger.error(f"❌ Registration timeout")
            print(f"❌ Registration timeout - orchestrator may be busy")
            return False
        except Exception as e:
            self.logger.error(f"❌ Registration error: {e}")
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to orchestrator"""
        if not self.registered:
            return False
            
        try:
            heartbeat_data = {
                'node_id': self.node_id,
                'status': 'active',
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': self._get_cpu_usage(),
                'memory_usage': self._get_memory_usage(),
                'agents_status': self._get_agents_status(),
                'load_score': self._calculate_load_score(),
                'active_tasks': self._get_active_tasks_count(),
                'performance_metrics': self._get_performance_metrics(),
                'health_status': self._get_health_status(),
                'uptime': time.time() - getattr(self.node_server, 'start_time', time.time())
            }
            
            response = requests.post(
                f"{self.orchestrator_url}/api/v1/nodes/{self.node_id}/heartbeat",
                json=heartbeat_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    self.logger.debug(f"💓 Heartbeat sent successfully")
                    return True
                else:
                    self.logger.warning(f"⚠️ Heartbeat rejected: {result.get('error', 'Unknown error')}")
                    return False
            else:
                self.logger.warning(f"⚠️ Heartbeat HTTP error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"⚠️ Heartbeat network error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Heartbeat error: {e}")
            return False
    
    def _start_heartbeat_thread(self):
        """Start the heartbeat thread"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            return
            
        def heartbeat_worker():
            print(f"💓 Starting heartbeat thread (every {self.heartbeat_interval}s)")
            while self.registered:
                try:
                    success = self.send_heartbeat()
                    if success:
                        print(f"💓 Heartbeat sent successfully")
                    else:
                        print(f"⚠️ Heartbeat failed - will retry")
                    time.sleep(self.heartbeat_interval)
                except Exception as e:
                    self.logger.error(f"Heartbeat thread error: {e}")
                    time.sleep(5)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()
        self.logger.info("💓 Heartbeat thread started")
    
    def stop_heartbeat(self):
        """Stop heartbeat and unregister"""
        print(f"🛑 Stopping orchestrator integration...")
        self.registered = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        self.logger.info("🛑 Heartbeat stopped")
    
    def _get_node_status(self) -> Dict[str, Any]:
        """Get comprehensive node status"""
        return {
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
            'load_score': self._calculate_load_score(),
            'agents_count': len(getattr(self.node_server, 'agents', {})),
            'active_tasks': self._get_active_tasks_count(),
            'uptime': time.time() - getattr(self.node_server, 'start_time', time.time())
        }
    
    def _get_agent_list(self) -> List[Dict[str, Any]]:
        """Get list of agents managed by this node"""
        agents = []
        node_agents = getattr(self.node_server, 'agents', {})
        
        for agent_id, agent_info in node_agents.items():
            agents.append({
                'agent_id': agent_id,
                'name': agent_info.get('name', 'Unknown') if isinstance(agent_info, dict) else str(agent_info),
                'agent_type': agent_info.get('agent_type', 'ultimate') if isinstance(agent_info, dict) else 'ultimate',
                'status': self._get_agent_status(agent_id),
                'capabilities': agent_info.get('capabilities', []) if isinstance(agent_info, dict) else [],
                'version': agent_info.get('version', '1.0.0') if isinstance(agent_info, dict) else '1.0.0',
                'host': agent_info.get('host', self.node_host) if isinstance(agent_info, dict) else self.node_host,
                'port': agent_info.get('port', 8080) if isinstance(agent_info, dict) else 8080
            })
        return agents
    
    def _get_agent_status(self, agent_id: str) -> str:
        """Get status of a specific agent"""
        agent_status = getattr(self.node_server, 'agent_status', {})
        if agent_id in agent_status:
            status_info = agent_status[agent_id]
            if isinstance(status_info, dict):
                return status_info.get('status', 'unknown')
            else:
                return str(status_info)
        return 'unknown'
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def _get_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        node_agents = getattr(self.node_server, 'agents', {})
        agent_status = getattr(self.node_server, 'agent_status', {})
        
        status_summary = {
            'total_agents': len(node_agents),
            'online_agents': 0,
            'offline_agents': 0,
            'busy_agents': 0,
            'error_agents': 0
        }
        
        for agent_id in node_agents.keys():
            status = self._get_agent_status(agent_id)
            if status == 'online':
                status_summary['online_agents'] += 1
            elif status == 'offline':
                status_summary['offline_agents'] += 1
            elif status == 'busy':
                status_summary['busy_agents'] += 1
            else:
                status_summary['error_agents'] += 1
        
        return status_summary
    
    def _calculate_load_score(self) -> float:
        """Calculate node load score (0-100, lower is better)"""
        try:
            cpu_weight = 0.4
            memory_weight = 0.3
            task_weight = 0.3
            
            cpu_usage = self._get_cpu_usage()
            memory_usage = self._get_memory_usage()
            
            # Task load (assuming max 10 concurrent tasks)
            active_tasks = self._get_active_tasks_count()
            task_load = min(active_tasks * 10, 100)
            
            load_score = (cpu_usage * cpu_weight + 
                         memory_usage * memory_weight + 
                         task_load * task_weight)
            
            return round(load_score, 2)
        except:
            return 50.0  # Default moderate load
    
    def _get_active_tasks_count(self) -> int:
        """Get count of active tasks"""
        try:
            if hasattr(self.node_server, 'task_control') and self.node_server.task_control:
                return len(getattr(self.node_server.task_control, 'active_tasks', {}))
            return 0
        except:
            return 0
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        try:
            return {
                'requests_per_minute': getattr(self.node_server, 'requests_per_minute', 0),
                'avg_response_time': getattr(self.node_server, 'avg_response_time', 0.0),
                'success_rate': getattr(self.node_server, 'success_rate', 100.0),
                'error_rate': getattr(self.node_server, 'error_rate', 0.0),
                'websocket_connections': getattr(self.node_server, 'websocket_connections', 0)
            }
        except:
            return {}
    
    def _get_health_status(self) -> str:
        """Get overall health status"""
        try:
            cpu_usage = self._get_cpu_usage()
            memory_usage = self._get_memory_usage()
            
            if cpu_usage > 90 or memory_usage > 90:
                return 'critical'
            elif cpu_usage > 70 or memory_usage > 70:
                return 'warning'
            else:
                return 'healthy'
        except:
            return 'unknown'


def add_orchestrator_integration(node_server, orchestrator_url: str = None):
    """Add orchestrator integration to an existing node server"""
    if orchestrator_url is None:
        orchestrator_url = "https://orc.peoplesainetwork.com"
    
    print(f"🔗 Adding orchestrator integration...")
    print(f"   Orchestrator URL: {orchestrator_url}")
    
    # Create orchestrator client
    orchestrator_client = OrchestratorClient(node_server, orchestrator_url)
    node_server.orchestrator_client = orchestrator_client
    
    # Add shutdown handler
    original_shutdown = getattr(node_server, 'shutdown', None)
    
    def enhanced_shutdown():
        print(f"🛑 Shutting down with orchestrator integration...")
        if hasattr(node_server, 'orchestrator_client'):
            node_server.orchestrator_client.stop_heartbeat()
        if original_shutdown:
            original_shutdown()
    
    node_server.shutdown = enhanced_shutdown
    
    return orchestrator_client
EOF

echo "✅ Orchestrator client created"

# Step 3: Update configuration
echo "3️⃣ Updating node configuration..."

# Check if config directory exists
if [ -d "config" ]; then
    CONFIG_FILE="config/settings.py"
else
    CONFIG_FILE="settings.py"
fi

# Add orchestrator settings to config file
if [ -f "$CONFIG_FILE" ]; then
    # Check if orchestrator settings already exist
    if ! grep -q "ORCHESTRATOR_URL" "$CONFIG_FILE"; then
        echo "" >> "$CONFIG_FILE"
        echo "# Orchestrator Integration Settings" >> "$CONFIG_FILE"
        echo "ORCHESTRATOR_ENABLED = True" >> "$CONFIG_FILE"
        echo "ORCHESTRATOR_URL = \"https://orc.peoplesainetwork.com\"" >> "$CONFIG_FILE"
        echo "ORCHESTRATOR_HEARTBEAT_INTERVAL = 30" >> "$CONFIG_FILE"
        echo "ORCHESTRATOR_AUTO_REGISTER = True" >> "$CONFIG_FILE"
        echo "ORCHESTRATOR_RETRY_ATTEMPTS = 3" >> "$CONFIG_FILE"
        echo "ORCHESTRATOR_RETRY_DELAY = 60" >> "$CONFIG_FILE"
        echo "" >> "$CONFIG_FILE"
        echo "✅ Updated $CONFIG_FILE with orchestrator settings"
    else
        echo "ℹ️ Orchestrator settings already exist in $CONFIG_FILE"
    fi
else
    # Create a basic config file
    cat > config/settings.py << 'EOF'
# Enhanced Node Configuration with Orchestrator Integration

# Node Settings
NODE_HOST = "0.0.0.0"
NODE_PORT = 5000
NODE_ID = "enhanced_node_1"
NODE_VERSION = "2.0.0"

# Orchestrator Integration Settings
ORCHESTRATOR_ENABLED = True
ORCHESTRATOR_URL = "https://orc.peoplesainetwork.com"
ORCHESTRATOR_HEARTBEAT_INTERVAL = 30
ORCHESTRATOR_AUTO_REGISTER = True
ORCHESTRATOR_RETRY_ATTEMPTS = 3
ORCHESTRATOR_RETRY_DELAY = 60

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/enhanced_node.log"

# Features
TASK_CONTROL_ENABLED = True
REMOTE_MANAGEMENT_ENABLED = True
WEBSOCKET_ENABLED = True
MONITORING_ENABLED = True
EOF
    echo "✅ Created $CONFIG_FILE with orchestrator settings"
fi

# Step 4: Create integration script
echo "4️⃣ Creating integration startup script..."
cat > start_with_orchestrator.py << 'EOF'
#!/usr/bin/env python3
"""
Enhanced Node Startup with Orchestrator Integration
This script starts the enhanced node and connects it to the orchestrator
"""

import sys
import time
import signal
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/orchestrator_integration.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main startup function"""
    print("🚀 Starting Enhanced Node with Orchestrator Integration")
    print("=" * 60)
    
    # Setup logging
    Path("logs").mkdir(exist_ok=True)
    setup_logging()
    
    try:
        # Import the main node server
        if Path("main.py").exists():
            print("📁 Found main.py - importing node server...")
            import main
            node_server = getattr(main, 'node_server', None) or getattr(main, 'server', None)
        else:
            print("❌ main.py not found - please run this from the enhanced_node directory")
            return 1
        
        if not node_server:
            print("❌ Could not find node_server object in main.py")
            return 1
        
        print(f"✅ Node server found: {type(node_server).__name__}")
        
        # Add orchestrator integration
        print("🔗 Adding orchestrator integration...")
        from integrations.orchestrator_client import add_orchestrator_integration
        
        orchestrator_client = add_orchestrator_integration(node_server)
        
        # Attempt registration
        print("📡 Attempting to register with orchestrator...")
        registration_success = orchestrator_client.register_with_orchestrator()
        
        if registration_success:
            print("🎉 Successfully registered with orchestrator!")
            print(f"   Node ID: {orchestrator_client.node_id}")
            print(f"   Orchestrator: {orchestrator_client.orchestrator_url}")
            print("💓 Heartbeat thread started")
        else:
            print("⚠️ Failed to register with orchestrator")
            print("   Node will continue running without orchestrator integration")
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down...")
            if hasattr(node_server, 'shutdown'):
                node_server.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("✅ Enhanced Node is running with orchestrator integration")
        print("   Press Ctrl+C to stop")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            if hasattr(node_server, 'shutdown'):
                node_server.shutdown()
        
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
        return 1
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x start_with_orchestrator.py
echo "✅ Integration startup script created"

# Step 5: Create test script
echo "5️⃣ Creating test script..."
cat > test_orchestrator_connection.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for orchestrator connection
"""

import requests
import json
import sys
from pathlib import Path

ORCHESTRATOR_URL = "https://orc.peoplesainetwork.com"

def test_orchestrator_connection():
    """Test connection to orchestrator"""
    print("🧪 Testing Orchestrator Connection")
    print("=" * 40)
    
    # Test health endpoint
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/api/v1/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Health: {data.get('status', 'unknown')}")
            print("   ✅ Health endpoint working")
        else:
            print(f"   ❌ Health endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health endpoint error: {e}")
        return False
    
    # Test nodes endpoint
    print("2️⃣ Testing nodes endpoint...")
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/api/v1/nodes", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            nodes = data.get('nodes', {})
            print(f"   Nodes registered: {len(nodes)}")
            print("   ✅ Nodes endpoint working")
        else:
            print(f"   ❌ Nodes endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Nodes endpoint error: {e}")
    
    # Test registration endpoint
    print("3️⃣ Testing registration endpoint...")
    test_data = {
        'node_id': 'test_node_123',
        'host': 'localhost',
        'port': 5000,
        'capabilities': ['test'],
        'agents': [],
        'node_type': 'test',
        'version': '1.0.0'
    }
    
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/api/v1/nodes/test_node_123/register",
            json=test_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Registration endpoint working")
        else:
            print(f"   ⚠️ Registration response: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Registration endpoint error: {e}")
    
    print("\n🎯 Connection test completed")
    return True

if __name__ == "__main__":
    test_orchestrator_connection()
EOF

chmod +x test_orchestrator_connection.py
echo "✅ Test script created"

# Step 6: Install required dependencies
echo "6️⃣ Installing required dependencies..."
if command -v pip &> /dev/null; then
    pip install requests psutil
    echo "✅ Dependencies installed"
else
    echo "⚠️ pip not found - please install requests and psutil manually"
fi

# Step 7: Test the connection
echo "7️⃣ Testing orchestrator connection..."
python test_orchestrator_connection.py

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "🚀 To start your Enhanced Node with orchestrator integration:"
echo "   python start_with_orchestrator.py"
echo ""
echo "📋 Or manually add to your existing main.py:"
echo "   from integrations.orchestrator_client import add_orchestrator_integration"
echo "   orchestrator_client = add_orchestrator_integration(node_server)"
echo "   orchestrator_client.register_with_orchestrator()"
echo ""
echo "🔍 To test the connection:"
echo "   python test_orchestrator_connection.py"
echo ""
echo "🎛️ Check your orchestrator dashboard at:"
echo "   https://orc.peoplesainetwork.com"
echo "   http://3.25.107.210:8501 (Streamlit dashboard)"
echo ""
echo "📋 Files created:"
echo "   ✅ integrations/orchestrator_client.py"
echo "   ✅ start_with_orchestrator.py" 
echo "   ✅ test_orchestrator_connection.py"
echo "   ✅ Updated configuration files"
echo ""
echo "🎊 Your Enhanced Node is ready to connect to the orchestrator!"
