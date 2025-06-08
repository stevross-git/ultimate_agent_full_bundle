from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any


@dataclass
class CentralTask:
    """Centralized task definition for task control"""
    id: str
    task_type: str
    priority: int = 5
    assigned_agent: Optional[str] = None
    status: str = "pending"
    
    config: Dict[str, Any] = None
    requirements: Dict[str, Any] = None
    
    created_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    progress: float = 0.0
    result: Dict[str, Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    reward: float = 0.0
    estimated_duration: int = 60
    actual_duration: Optional[float] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.requirements is None:
            self.requirements = {}
        if self.result is None:
            self.result = {}
        if self.created_at is None:
            self.created_at = datetime.now()
