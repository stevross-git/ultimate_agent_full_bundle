from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any


@dataclass
class AgentCommand:
    """Remote agent command"""
    id: str
    agent_id: str
    command_type: str
    parameters: Dict[str, Any] = None
    
    created_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    status: str = "pending"  # pending, executing, completed, failed
    result: Dict[str, Any] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.result is None:
            self.result = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AgentConfiguration:
    """Agent configuration profile"""
    agent_id: str
    config_name: str
    config_data: Dict[str, Any]
    version: int = 1
    
    created_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    status: str = "draft"  # draft, deployed, active, reverted
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
