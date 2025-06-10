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