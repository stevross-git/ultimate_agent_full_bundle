from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta

Base = declarative_base()


# Agent Models
class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    host = Column(String)
    version = Column(String)
    agent_type = Column(String, default='ultimate')
    capabilities = Column(JSON)
    ai_models = Column(JSON)
    plugins = Column(JSON)
    features = Column(JSON)
    
    gpu_available = Column(Boolean, default=False)
    blockchain_enabled = Column(Boolean, default=False)
    cloud_enabled = Column(Boolean, default=False)
    security_enabled = Column(Boolean, default=False)
    
    registered_at = Column(DateTime)
    last_seen = Column(DateTime)
    
    total_tasks_completed = Column(Integer, default=0)
    total_tasks_failed = Column(Integer, default=0)
    ai_tasks_completed = Column(Integer, default=0)
    blockchain_transactions = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=100.0)


class AgentHeartbeat(Base):
    __tablename__ = 'agent_heartbeats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String)
    timestamp = Column(DateTime)
    status = Column(String)
    
    # System metrics
    cpu_percent = Column(Float)
    memory_mb = Column(Float)
    memory_percent = Column(Float)
    gpu_percent = Column(Float)
    network_io = Column(Float)
    
    # Task metrics
    tasks_running = Column(Integer)
    tasks_completed = Column(Integer)
    tasks_failed = Column(Integer)
    current_tasks = Column(JSON)
    
    # AI metrics
    ai_models_loaded = Column(Integer)
    ai_inference_count = Column(Integer)
    neural_training_active = Column(Boolean, default=False)
    
    # Blockchain metrics
    blockchain_balance = Column(Float)
    blockchain_transactions = Column(Integer)
    
    # Performance metrics
    performance_prediction = Column(Float)
    efficiency_score = Column(Float)


# Task Models
class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String)
    task_type = Column(String)
    task_category = Column(String)
    status = Column(String)
    
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    duration = Column(Float)
    result = Column(JSON)
    reward = Column(Float)
    
    model_used = Column(String)
    training_epochs = Column(Integer)
    inference_count = Column(Integer)
    
    transaction_hash = Column(String)
    gas_used = Column(Integer)


class CentralTaskRecord(Base):
    __tablename__ = 'central_tasks'
    
    id = Column(String, primary_key=True)
    task_type = Column(String)
    priority = Column(Integer)
    assigned_agent = Column(String)
    status = Column(String)
    
    config = Column(JSON)
    requirements = Column(JSON)
    
    created_at = Column(DateTime)
    assigned_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    progress = Column(Float)
    result = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer)
    
    reward = Column(Float)
    estimated_duration = Column(Integer)
    actual_duration = Column(Float)


# Node Metrics
class NodeMetrics(Base):
    __tablename__ = 'node_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    
    total_agents = Column(Integer)
    online_agents = Column(Integer)
    total_tasks_running = Column(Integer)
    total_tasks_completed = Column(Integer)
    
    avg_cpu_percent = Column(Float)
    avg_memory_percent = Column(Float)
    avg_gpu_percent = Column(Float)
    
    total_ai_models = Column(Integer)
    total_blockchain_balance = Column(Float)
    total_earnings = Column(Float)
    
    avg_efficiency_score = Column(Float)


# Remote Management Models
class AgentCommandRecord(Base):
    __tablename__ = 'agent_commands'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String)
    command_type = Column(String)
    parameters = Column(JSON)
    
    created_at = Column(DateTime)
    executed_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    status = Column(String)
    result = Column(JSON)
    error_message = Column(Text)


class AgentConfigurationRecord(Base):
    __tablename__ = 'agent_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String)
    config_name = Column(String)
    config_data = Column(JSON)
    version = Column(Integer)
    
    created_at = Column(DateTime)
    applied_at = Column(DateTime)
    status = Column(String)


class AgentLog(Base):
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String)
    log_level = Column(String)
    message = Column(Text)
    category = Column(String)
    
    timestamp = Column(DateTime)
    log_data = Column(JSON)


# Advanced Remote Control Models
class ScheduledCommandRecord(Base):
    __tablename__ = 'scheduled_commands'
    
    id = Column(String, primary_key=True)
    command_id = Column(String)
    agent_id = Column(String)
    command_type = Column(String)
    parameters = Column(JSON)
    
    scheduled_time = Column(DateTime)
    repeat_interval = Column(Integer)
    max_repeats = Column(Integer)
    current_repeats = Column(Integer)
    
    status = Column(String)
    created_at = Column(DateTime)
    last_executed = Column(DateTime)


class BulkOperationRecord(Base):
    __tablename__ = 'bulk_operations'
    
    id = Column(String, primary_key=True)
    operation_type = Column(String)
    target_agents = Column(JSON)
    parameters = Column(JSON)
    
    created_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    status = Column(String)
    results = Column(JSON)
    success_count = Column(Integer)
    failure_count = Column(Integer)


class AgentHealthRecord(Base):
    __tablename__ = 'agent_health'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String)
    timestamp = Column(DateTime)
    status = Column(String)
    
    cpu_health = Column(String)
    memory_health = Column(String)
    disk_health = Column(String)
    network_health = Column(String)
    task_health = Column(String)
    
    health_score = Column(Float)
    response_time = Column(Float)
    last_error = Column(Text)
    
    recovery_needed = Column(Boolean)
    recovery_actions = Column(JSON)


class AgentScriptRecord(Base):
    __tablename__ = 'agent_scripts'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    version = Column(String)
    script_type = Column(String)
    
    script_content = Column(Text)
    checksum = Column(String)
    target_agents = Column(JSON)
    
    created_at = Column(DateTime)
    deployed_at = Column(DateTime)
    status = Column(String)
    
    deployment_results = Column(JSON)


# Database Manager
class EnhancedNodeDatabase:
    """Enhanced database manager with advanced remote control features"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Cleanup old heartbeats
        self.session.query(AgentHeartbeat).filter(
            AgentHeartbeat.timestamp < cutoff
        ).delete()
        
        # Cleanup old health records
        self.session.query(AgentHealthRecord).filter(
            AgentHealthRecord.timestamp < cutoff
        ).delete()
        
        # Clean up completed scheduled commands
        self.session.query(ScheduledCommandRecord).filter(
            ScheduledCommandRecord.status == 'completed',
            ScheduledCommandRecord.last_executed < cutoff
        ).delete()
        
        # Cleanup old node metrics
        self.session.query(NodeMetrics).filter(
            NodeMetrics.timestamp < cutoff
        ).delete()
        
        self.session.commit()
    
    def get_agent_by_id(self, agent_id: str) -> Agent:
        """Get agent by ID"""
        return self.session.query(Agent).filter_by(id=agent_id).first()
    
    def get_all_agents(self) -> list:
        """Get all agents"""
        return self.session.query(Agent).all()
    
    def get_recent_heartbeats(self, agent_id: str, limit: int = 10) -> list:
        """Get recent heartbeats for an agent"""
        return self.session.query(AgentHeartbeat).filter_by(agent_id=agent_id)\
            .order_by(AgentHeartbeat.timestamp.desc()).limit(limit).all()
    
    def get_agent_health_history(self, agent_id: str, hours: int = 24) -> list:
        """Get agent health history"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.session.query(AgentHealthRecord).filter(
            AgentHealthRecord.agent_id == agent_id,
            AgentHealthRecord.timestamp >= cutoff
        ).order_by(AgentHealthRecord.timestamp.desc()).all()
    
    def close(self):
        """Close database connection"""
        self.session.close()
