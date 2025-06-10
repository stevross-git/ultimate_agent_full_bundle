"""
Ultimate Agent Utilities
"""

import logging
import sys
from pathlib import Path

def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup logging for a module"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent

def handle_exception(logger, operation: str, exception: Exception, reraise: bool = False):
    """Standardized exception handling"""
    logger.error(f"❌ Error in {operation}: {exception}")
    if reraise:
        raise exception

def safe_json_serialize(obj):
    """Safely serialize objects to JSON"""
    try:
        return json.dumps(obj, default=str, indent=2)
    except Exception as e:
        return f"{{\"error\": \"Serialization failed: {str(e)}\"}}"