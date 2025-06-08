from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class EnhancedAgentInfo:
    """Enhanced information about connected Ultimate agents"""
    id: str
    name: str
    host: str
    version: str
    agent_type: str = "ultimate"
    
    # Capabilities
    capabilities: List[str] = None
    ai_models: List[str] = None
    plugins: List[str] = None
    features: List[str] = None
    
    # System info
    gpu_available: bool = False
    blockchain_enabled: bool = False
    cloud_enabled: bool = False
    security_enabled: bool = False
    
    # Registration info
    registered_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    
    # Statistics
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    ai_tasks_completed: int = 0
    blockchain_transactions: int = 0
    total_earnings: float = 0.0
    uptime_hours: float = 0.0
    efficiency_score: float = 100.0
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.ai_models is None:
            self.ai_models = []
        if self.plugins is None:
            self.plugins = []
        if self.features is None:
            self.features = []


@dataclass 
class EnhancedAgentStatus:
    """Enhanced current status of an Ultimate agent"""
    id: str
    status: str = "unknown"
    
    # System metrics
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    gpu_percent: float = 0.0
    network_io: float = 0.0
    
    # Task metrics
    tasks_running: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    current_tasks: Dict = None
    
    # AI metrics
    ai_models_loaded: int = 0
    ai_inference_count: int = 0
    neural_training_active: bool = False
    
    # Blockchain metrics
    blockchain_balance: float = 0.0
    blockchain_transactions: int = 0
    wallet_address: str = ""
    
    # Performance metrics
    performance_prediction: float = 80.0
    efficiency_score: float = 100.0
    
    # Timing
    last_heartbeat: Optional[datetime] = None
    
    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = {}