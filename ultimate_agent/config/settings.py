"""
Ultimate Agent Configuration Settings
"""

import os
from typing import Dict, Any

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration values"""
    required_keys = ['host', 'port', 'secret_key']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration: {key}")
    
    if not isinstance(config['port'], int) or config['port'] < 1 or config['port'] > 65535:
        raise ValueError("Port must be between 1 and 65535")
    
    return True

def get_config() -> Dict[str, Any]:
    """Get configuration dictionary"""
    config = {
        # Core settings
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        
        # Module toggles
        'ai_enabled': os.getenv('AI_ENABLED', 'true').lower() == 'true',
        'tasks_enabled': os.getenv('TASKS_ENABLED', 'true').lower() == 'true',
        'dashboard_enabled': os.getenv('DASHBOARD_ENABLED', 'true').lower() == 'true',
        'blockchain_enabled': os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true',
        
        # Network settings
        'host': os.getenv('HOST', '0.0.0.0'),
        'port': int(os.getenv('PORT', '5000')),
        
        # Database settings
        'database_url': os.getenv('DATABASE_URL', 'sqlite:///ultimate_agent.db'),
        
        # AI settings
        'ai_model_path': os.getenv('AI_MODEL_PATH', './models'),
        'max_ai_workers': int(os.getenv('MAX_AI_WORKERS', '4')),
        
        # Task settings
        'max_concurrent_tasks': int(os.getenv('MAX_CONCURRENT_TASKS', '10')),
        'task_timeout': int(os.getenv('TASK_TIMEOUT', '300')),
        
        # Security settings
        'api_key': os.getenv('API_KEY'),
        'secret_key': os.getenv('SECRET_KEY', 'dev-secret-key'),
    }
    
    # Validate configuration before returning
    validate_config(config)
    return config

# Legacy compatibility
LOG_DIR = "logs"
DATABASE_PATH = "ultimate_agent.db"

# ✅ Now define settings without importing it prematurely
settings = get_config()
