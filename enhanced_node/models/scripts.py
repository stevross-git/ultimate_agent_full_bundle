from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import hashlib

from .commands import AgentCommand


@dataclass
class ScheduledCommand:
    """Scheduled command execution"""
    id: str
    command: AgentCommand
    scheduled_time: datetime
    repeat_interval: Optional[int] = None  # seconds
    max_repeats: int = 1
    current_repeats: int = 0
    status: str = "scheduled"  # scheduled, executing, completed, failed, cancelled
    
    def __post_init__(self):
        if not self.id:
            self.id = f"sched-{uuid.uuid4().hex[:8]}"


@dataclass
class BulkOperation:
    """Bulk operation for multiple agents"""
    id: str
    operation_type: str
    target_agents: List[str]
    parameters: Dict[str, Any] = None
    
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    status: str = "pending"  # pending, executing, completed, failed, partial
    results: Dict[str, Any] = None
    success_count: int = 0
    failure_count: int = 0
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.results is None:
            self.results = {}
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AgentHealthCheck:
    """Agent health monitoring"""
    agent_id: str
    timestamp: datetime
    status: str  # healthy, warning, critical, offline
    
    # Health metrics
    cpu_health: str = "unknown"
    memory_health: str = "unknown"
    disk_health: str = "unknown"
    network_health: str = "unknown"
    task_health: str = "unknown"
    
    # Detailed metrics
    health_score: float = 0.0
    response_time: float = 0.0
    last_error: Optional[str] = None
    
    # Recovery actions
    recovery_needed: bool = False
    recovery_actions: List[str] = field(default_factory=list)


@dataclass
class AgentScript:
    """Agent script deployment"""
    id: str
    name: str
    version: str
    script_type: str  # update, patch, config, task
    
    script_content: str
    checksum: str
    target_agents: List[str] = field(default_factory=list)
    
    created_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    status: str = "draft"  # draft, deploying, deployed, failed
    
    deployment_results: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if not self.checksum:
            self.checksum = hashlib.sha256(self.script_content.encode()).hexdigest()
