import sys
import logging
from pathlib import Path
from config.settings import LOG_DIR


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Setup a logger with both file and console handlers"""
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(LOG_DIR) / log_file
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_server_logger() -> logging.Logger:
    """Get the main server logger"""
    return setup_logger("EnhancedNodeServerAdvanced", "enhanced_node_server_advanced.log")


def get_task_logger() -> logging.Logger:
    """Get the task control logger"""
    return setup_logger("TaskControlManager", "task_control.log")


def get_remote_logger() -> logging.Logger:
    """Get the remote control logger"""
    return setup_logger("AdvancedRemoteControlManager", "advanced_remote_control.log")
