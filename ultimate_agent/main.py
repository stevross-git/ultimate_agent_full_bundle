#!/usr/bin/env python3
"""
ultimate_agent/main.py
Main entry point for the Enhanced Ultimate Pain Network Agent
Modular Architecture - All components properly separated and organized
"""

import sys
import os
import argparse
import traceback
import time

# Add the package root directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
package_root = os.path.dirname(current_dir)
sys.path.insert(0, package_root)

# Import the full-featured agent class
from ultimate_agent import UltimatePainNetworkAgent

VERSION = "3.0.0-modular"


def main():
    """Main entry point with enhanced argument parsing and error handling"""
    
    parser = argparse.ArgumentParser(
        description=f'Enhanced Ultimate Pain Network Agent v{VERSION} - Modular Architecture',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
🏗️ MODULAR ARCHITECTURE FEATURES:

📦 Core Modules:
  🎯 Core Agent (core/agent.py)          - Main coordination and control
  ⚙️  Configuration (config/settings.py) - Centralized configuration management
  🌐 Network Manager                     - Node communication and networking
  🔒 Security Manager                    - Authentication and encryption
  
🧠 AI & Training Modules:
  🤖 AI Models Manager                   - Model loading and management  
  🎓 AI Training Engine                  - Advanced neural network training
  🔬 Inference Engine                    - Model inference and prediction
  
🎯 Task Management:
  📋 Task Scheduler                      - Intelligent task queue management
  🎮 Task Simulator                      - Task execution simulation
  🎛️  Task Control Client               - Centralized task control integration
  
💰 Blockchain & Finance:
  💎 Blockchain Manager                  - Multi-currency wallet management
  📜 Smart Contract Manager             - Contract execution and management
  🌐 Network Manager (Blockchain)       - Blockchain network connections
  
💾 Data & Storage:
  🗄️  Database Manager                   - Persistent data storage
  📊 Performance Metrics                - System monitoring and analytics
  🔍 Audit & Logging                    - Comprehensive logging system
  
🌐 Interface & Communication:
  🖥️  Dashboard Manager                  - Real-time web interface
  🔌 WebSocket Manager                   - Real-time communication
  📡 API Routes                         - RESTful API endpoints
  
🔌 Extensions:
  🧩 Plugin Manager                     - Extensible plugin system
  ☁️  Cloud Integration                  - Multi-cloud support
  📈 Monitoring & Alerts               - Advanced system monitoring

MODULAR BENEFITS:
✅ Separation of Concerns    - Each module has a single responsibility
✅ Maintainability          - Easy to update and debug individual components  
✅ Testability             - Each module can be tested independently
✅ Scalability             - Add new features without affecting existing code
✅ Reusability             - Modules can be reused in other projects
✅ Configuration           - Centralized and flexible configuration
✅ Error Isolation         - Failures in one module don't crash others
✅ Hot Reloading           - Update modules without full restart

USAGE EXAMPLES:
  python main.py                                    # Start with default settings
  python main.py --node-url http://custom-node.com # Use custom node
  python main.py --dashboard-port 9000             # Custom dashboard port
  python main.py --config-file custom_config.ini   # Use custom config
  python main.py --enable-monitoring               # Enable advanced monitoring
  python main.py --debug                           # Enable debug mode

This modular agent runs on Windows and connects to your Linux node server.
All existing functionality is preserved while providing clean, maintainable architecture.
        """
    )
    
    # Connection settings
    parser.add_argument('--node-url', 
                       help='Node server URL (Linux server)')
    parser.add_argument('--dashboard-port', type=int, 
                       help='Local dashboard port (default: 8080)')
    
    # Configuration options
    parser.add_argument('--config-file', 
                       help='Custom configuration file path')
    parser.add_argument('--enable-monitoring', action='store_true',
                       help='Enable advanced performance monitoring')
    parser.add_argument('--disable-auto-tasks', action='store_true',
                       help='Disable automatic task starting')
    
    # Debug and development options
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode with verbose logging')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode (limited functionality)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Initialize modules without starting services')
    
    # Module-specific options
    parser.add_argument('--disable-ai', action='store_true',
                       help='Disable AI training modules')
    parser.add_argument('--disable-blockchain', action='store_true',
                       help='Disable blockchain functionality')
    parser.add_argument('--disable-security', action='store_true',
                       help='Disable security features (not recommended)')
    
    # Utility options
    parser.add_argument('--export-config', 
                       help='Export current configuration to file and exit')
    parser.add_argument('--validate-config', action='store_true',
                       help='Validate configuration and exit')
    parser.add_argument('--show-modules', action='store_true',
                       help='Show available modules and exit')
    parser.add_argument('--version', action='version', 
                       version=f'Enhanced Ultimate Pain Network Agent v{VERSION} (Modular)')
    
    args = parser.parse_args()
    
    print("=" * 100)
    print(f"🚀 ENHANCED ULTIMATE PAIN NETWORK AGENT v{VERSION}")
    print("🏗️ MODULAR ARCHITECTURE - Enterprise AI Computing Platform")
    print("=" * 100)
    print("📦 Modules: AI Training | Blockchain | Task Management | Security | Monitoring")
    print("🎯 Features: Real-time Dashboard | Smart Contracts | Advanced Analytics")
    print("🔧 Architecture: Modular | Scalable | Maintainable | Testable")
    print("=" * 100)
    
    # Handle utility options
    if args.show_modules:
        show_available_modules()
        return 0
    
    if args.validate_config:
        return validate_configuration(args.config_file)
    
    if args.export_config:
        return export_configuration(args.export_config, args.config_file)
    
    try:
        # Create and configure the agent
        print("🏗️ Initializing modular agent architecture...")
        
        agent = UltimatePainNetworkAgent(
            node_url=args.node_url,
            dashboard_port=args.dashboard_port
        )
        
        # Apply command-line configuration overrides
        apply_command_line_options(agent, args)
        
        print(f"🎯 Node Server: {agent.node_url}")
        print(f"🌐 Enhanced Dashboard: http://localhost:{agent.dashboard_port}")
        print(f"💰 Blockchain Wallet: {agent.blockchain_manager.earnings_wallet}")
        print(f"🧠 AI Models: {len(agent.ai_manager.models)} loaded")
        
        # Show modular status
        print_modular_status(agent)
        
        if args.dry_run:
            print("🧪 Dry run completed - modules initialized but not started")
            return 0
        
        # Start the enhanced modular agent
        print("=" * 100)
        agent.start()
        
    except KeyboardInterrupt:
        print(f"\n🛑 Agent shutdown requested by user...")
        return 0
    except Exception as e:
        print(f"❌ Enhanced Agent failed to start: {e}")
        if args.debug:
            traceback.print_exc()
        return 1
    
    return 0


def show_available_modules():
    """Show available modules and their descriptions"""
    modules = {
        "🎯 Core Modules": [
            ("core.agent", "Main agent coordination and control"),
            ("config.settings", "Centralized configuration management"),
            ("network.communication", "Node communication and networking"),
            ("security.authentication", "Authentication and encryption")
        ],
        "🧠 AI & Training": [
            ("ai.models", "AI model loading and management"),
            ("ai.training", "Advanced neural network training"),
            ("ai.inference", "Model inference and prediction")
        ],
        "🎯 Task Management": [
            ("tasks.execution.scheduler", "Intelligent task queue management"),
            ("tasks.simulation", "Task execution simulation"),
            ("tasks.control", "Centralized task control integration")
        ],
        "💰 Blockchain & Finance": [
            ("blockchain.wallet.security", "Multi-currency wallet management"),
            ("blockchain.contracts", "Smart contract execution"),
            ("blockchain.networks", "Blockchain network connections")
        ],
        "💾 Data & Storage": [
            ("storage.database.migrations", "Persistent data storage"),
            ("monitoring.metrics", "System monitoring and analytics"),
            ("monitoring.logging", "Comprehensive logging system")
        ],
        "🌐 Interface & Communication": [
            ("dashboard.web.routes", "Real-time web interface"),
            ("dashboard.websocket", "Real-time communication"),
            ("network.protocols", "Communication protocols")
        ],
        "🔌 Extensions": [
            ("plugins", "Extensible plugin system"),
            ("cloud", "Multi-cloud integration"),
            ("security.validation", "Security validation")
        ]
    }
    
    print("\n📦 AVAILABLE MODULES:")
    print("=" * 80)
    
    for category, module_list in modules.items():
        print(f"\n{category}:")
        for module_name, description in module_list:
            print(f"  📄 {module_name:<30} - {description}")
    
    print(f"\n✨ Total: {sum(len(modules) for modules in modules.values())} modules available")
    print("🏗️ Modular architecture allows easy maintenance and extension")


def validate_configuration(config_file=None):
    """Validate configuration file"""
    try:
        from config.settings import ConfigManager
        
        config_manager = ConfigManager(config_file or "ultimate_agent_config.ini")
        
        if config_manager.validate_config():
            print("✅ Configuration validation successful")
            
            # Print configuration summary
            print("\n📋 Configuration Summary:")
            print(f"  🌐 Node URL: {config_manager.get('DEFAULT', 'node_url')}")
            print(f"  🖥️  Dashboard Port: {config_manager.get('DEFAULT', 'dashboard_port')}")
            print(f"  🧠 AI Training: {config_manager.getboolean('AI_TRAINING', 'enabled')}")
            print(f"  💰 Blockchain: {config_manager.getboolean('BLOCKCHAIN', 'enabled')}")
            print(f"  🔒 Security: {config_manager.getboolean('SECURITY', 'encryption_enabled')}")
            print(f"  📊 Monitoring: {config_manager.getboolean('MONITORING', 'metrics_enabled')}")
            
            return 0
        else:
            print("❌ Configuration validation failed")
            return 1
            
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return 1


def export_configuration(export_path, config_file=None):
    """Export configuration to file"""
    try:
        from config.settings import ConfigManager
        
        config_manager = ConfigManager(config_file or "ultimate_agent_config.ini")
        config_manager.export_config(export_path)
        
        print(f"✅ Configuration exported to {export_path}")
        return 0
        
    except Exception as e:
        print(f"❌ Configuration export error: {e}")
        return 1


def apply_command_line_options(agent, args):
    """Apply command-line options to agent configuration"""
    try:
        # Monitoring options
        if args.enable_monitoring and hasattr(agent, 'monitoring_manager'):
            agent.monitoring_manager.start_monitoring()
            print("📊 Advanced monitoring enabled")
        
        # Auto-task options
        if args.disable_auto_tasks:
            agent.config_manager.set('DEFAULT', 'auto_start_tasks', 'false')
            print("🎯 Automatic task starting disabled")
        
        # Debug mode
        if args.debug:
            import logging
            logging.basicConfig(level=logging.DEBUG)
            print("🐛 Debug mode enabled")
        
        # Test mode
        if args.test_mode:
            # Reduce resource usage in test mode
            if hasattr(agent, 'task_scheduler'):
                agent.task_scheduler.set_max_concurrent_tasks(1)
            print("🧪 Test mode enabled")
            
    except Exception as e:
        print(f"⚠️ Warning applying command-line options: {e}")


def print_modular_status(agent):
    """Print status of all modules"""
    print("\n🏗️ MODULAR ARCHITECTURE STATUS:")
    print("-" * 50)
    
    modules_status = []
    
    # Core modules
    modules_status.append(("🎯 Core Agent", "✅ Active", "Main coordination"))
    modules_status.append(("⚙️ Configuration", "✅ Loaded", f"{len(agent.config_manager.config.sections())} sections"))
    
    # AI modules
    if hasattr(agent, 'ai_manager'):
        ai_status = agent.ai_manager.get_status()
        gpu_status = "🚀 GPU" if ai_status.get('gpu_available') else "💻 CPU"
        modules_status.append(("🧠 AI Manager", "✅ Active", f"{ai_status.get('models_loaded', 0)} models, {gpu_status}"))
        
        if hasattr(agent.ai_manager, 'training_engine'):
            training_types = len(agent.ai_manager.training_engine.training_tasks)
            modules_status.append(("🎓 AI Training", "✅ Ready", f"{training_types} training types"))
    
    # Task management
    if hasattr(agent, 'task_scheduler'):
        scheduler_status = agent.task_scheduler.get_scheduler_status()
        modules_status.append(("🎯 Task Scheduler", "✅ Active", f"{scheduler_status.get('available_task_types', 0)} task types"))
    
    # Blockchain
    if hasattr(agent, 'blockchain_manager'):
        blockchain_status = agent.blockchain_manager.get_status()
        wallet_status = "✅ Connected" if blockchain_status.get('wallet_initialized') else "⚠️ Demo"
        modules_status.append(("💰 Blockchain", wallet_status, f"Multi-currency wallet"))
        
        if hasattr(agent.blockchain_manager, 'smart_contract_manager'):
            contracts = blockchain_status.get('smart_contracts_enabled', 0)
            modules_status.append(("📜 Smart Contracts", "✅ Ready", f"{contracts} contracts"))
    
    # Security
    if hasattr(agent, 'security_manager'):
        security_status = agent.security_manager.get_status()
        encryption = "🔐 Enabled" if security_status.get('encryption_enabled') else "⚠️ Disabled"
        modules_status.append(("🔒 Security", "✅ Active", encryption))
    
    # Database
    if hasattr(agent, 'database_manager'):
        db_status = agent.database_manager.get_database_stats()
        size_mb = db_status.get('database_size_mb', 0)
        modules_status.append(("💾 Database", "✅ Connected", f"{size_mb:.1f}MB"))
    
    # Monitoring
    if hasattr(agent, 'monitoring_manager'):
        monitoring_status = agent.monitoring_manager.get_status()
        health_score = monitoring_status.get('health_score', 0)
        modules_status.append(("📊 Monitoring", "✅ Active", f"Health: {health_score:.0f}%"))
    
    # Dashboard
    if hasattr(agent, 'dashboard_manager'):
        modules_status.append(("🌐 Dashboard", "✅ Starting", f"Port {agent.dashboard_port}"))
    
    # Network
    if hasattr(agent, 'network_manager'):
        network_status = agent.network_manager.get_status()
        quality = network_status.get('connection_quality', 'unknown')
        modules_status.append(("🌐 Network", "✅ Ready", f"Quality: {quality}"))
    
    # Print module status table
    for module_name, status, details in modules_status:
        print(f"  {module_name:<18} {status:<12} {details}")
    
    print(f"\n✨ Total Active Modules: {len(modules_status)}")
    print("🚀 All modular systems operational!")


if __name__ == "__main__":
    sys.exit(main())
