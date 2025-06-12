from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
from ..control.version_manager import VersionControlManager

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


class AgentVersionRecord(Base):
    __tablename__ = 'agent_versions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, index=True)
    version = Column(String)
    build_number = Column(Integer, default=0)
    commit_hash = Column(String)
    build_date = Column(DateTime)
    
    # Capabilities and features
    capabilities = Column(JSON)
    dependencies = Column(JSON)
    features = Column(JSON)
    
    # Platform information
    platform = Column(String)
    architecture = Column(String)
    
    # Update settings
    update_channel = Column(String, default='stable')
    last_seen = Column(DateTime)
    
    # Version metadata
    release_notes = Column(Text)
    changelog = Column(JSON)
    security_patches = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class UpdatePackageRecord(Base):
    __tablename__ = 'update_packages'
    
    id = Column(String, primary_key=True)
    version = Column(String)
    channel = Column(String, default='stable')
    release_date = Column(DateTime)
    
    # Update details
    update_type = Column(String)
    download_url = Column(String)
    checksum = Column(String)
    size_bytes = Column(Integer)
    
    # Description and changelog
    description = Column(Text)
    changelog = Column(JSON)
    release_notes = Column(Text)
    
    # Requirements and compatibility
    requirements = Column(JSON)
    compatibility = Column(JSON)
    
    # Update settings
    rollback_supported = Column(Boolean, default=True)
    critical = Column(Boolean, default=False)
    auto_install = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)


class AgentUpdateRecord(Base):
    __tablename__ = 'agent_updates'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    package_id = Column(String)
    from_version = Column(String)
    to_version = Column(String)
    
    # Update configuration
    update_type = Column(String)
    scheduled_time = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Status tracking
    status = Column(String, default='scheduled')
    progress = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Update strategy
    strategy = Column(String, default='rolling')
    
    # Backup and rollback
    backup_path = Column(String)
    auto_rollback_enabled = Column(Boolean, default=True)
    rollback_threshold_minutes = Column(Integer, default=30)
    
    # Validation
    pre_update_checks = Column(JSON)
    post_update_checks = Column(JSON)
    health_checks_passed = Column(Boolean, default=False)
    
    # Metadata
    initiated_by = Column(String, default='system')
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)


class RollbackOperationRecord(Base):
    __tablename__ = 'rollback_operations'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    update_id = Column(String)
    from_version = Column(String)
    to_version = Column(String)
    
    # Rollback details
    rollback_type = Column(String, default='manual')
    backup_path = Column(String)
    initiated_by = Column(String, default='system')
    reason = Column(Text)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Status
    status = Column(String, default='scheduled')
    error_message = Column(Text)
    
    # Validation
    pre_rollback_checks = Column(JSON)
    post_rollback_checks = Column(JSON)
    verification_passed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)


class VersionPolicyRecord(Base):
    __tablename__ = 'version_policies'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    
    # Policy rules
    auto_update = Column(Boolean, default=False)
    update_channels = Column(JSON)
    update_types = Column(JSON)
    
    # Timing rules
    delay_hours = Column(Integer, default=24)
    maintenance_window_only = Column(Boolean, default=False)
    maintenance_window = Column(JSON)
    
    # Agent targeting
    target_agents = Column(JSON)
    target_platforms = Column(JSON)
    target_channels = Column(JSON)
    
    # Rollback settings
    auto_rollback = Column(Boolean, default=True)
    rollback_threshold_minutes = Column(Integer, default=30)
    health_check_interval = Column(Integer, default=5)
    
    # Approval requirements
    approval_required = Column(Boolean, default=False)
    approvers = Column(JSON)
    
    # Status
    active = Column(Boolean, default=True)
    created_by = Column(String, default='system')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)


class UpdateApprovalRecord(Base):
    __tablename__ = 'update_approvals'
    
    id = Column(String, primary_key=True)
    update_id = Column(String)
    policy_id = Column(String)
    
    # Approval details
    required_approvals = Column(Integer, default=1)
    received_approvals = Column(Integer, default=0)
    approved = Column(Boolean, default=False)
    
    # Approver tracking
    approvers = Column(JSON)
    
    # Timing
    approved_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Comments
    comments = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)


class VersionAuditRecord(Base):
    __tablename__ = 'version_audits'
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, index=True)
    action = Column(String)
    
    # Action details
    from_version = Column(String)
    to_version = Column(String)
    action_data = Column(JSON)
    
    # User and timing
    performed_by = Column(String, default='system')
    performed_at = Column(DateTime, default=datetime.now)
    
    # Outcome
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Context
    reason = Column(Text)
    notes = Column(Text)
    related_records = Column(JSON)


class DistributionGroupRecord(Base):
    __tablename__ = 'distribution_groups'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    
    # Group membership
    agents = Column(JSON)
    agent_filters = Column(JSON)
    
    # Rollout configuration
    rollout_percentage = Column(Integer, default=100)
    rollout_strategy = Column(String, default='rolling')
    
    # Health monitoring
    health_check_required = Column(Boolean, default=True)
    success_threshold = Column(Float, default=0.95)
    failure_threshold = Column(Float, default=0.1)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)


class UpdateMetricsRecord(Base):
    __tablename__ = 'update_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    update_id = Column(String, index=True)
    agent_id = Column(String, index=True)
    
    # Performance metrics
    download_time_seconds = Column(Float, default=0.0)
    install_time_seconds = Column(Float, default=0.0)
    restart_time_seconds = Column(Float, default=0.0)
    verification_time_seconds = Column(Float, default=0.0)
    total_time_seconds = Column(Float, default=0.0)
    
    # Resource usage
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    disk_usage_mb = Column(Float, default=0.0)
    network_usage_mb = Column(Float, default=0.0)
    
    # Success metrics
    pre_checks_passed = Column(Integer, default=0)
    pre_checks_total = Column(Integer, default=0)
    post_checks_passed = Column(Integer, default=0)
    post_checks_total = Column(Integer, default=0)
    
    # Error tracking
    errors_encountered = Column(JSON)
    warnings_encountered = Column(JSON)
    
    # Timestamps
    measured_at = Column(DateTime, default=datetime.now)


class ChannelConfigurationRecord(Base):
    __tablename__ = 'channel_configurations'
    
    channel = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    
    # Channel settings
    auto_updates = Column(Boolean, default=False)
    update_frequency = Column(String, default='daily')
    
    # Quality gates
    stability_threshold = Column(Float, default=0.95)
    testing_required = Column(Boolean, default=True)
    approval_required = Column(Boolean, default=False)
    
    # Distribution settings
    rollout_percentage = Column(Integer, default=100)
    canary_percentage = Column(Integer, default=10)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)


# Add these methods to the EnhancedNodeDatabase class:

def get_agent_version_history(self, agent_id: str, limit: int = 10) -> list:
    """Get version history for an agent"""
    return self.session.query(AgentVersionRecord).filter_by(agent_id=agent_id)\
        .order_by(AgentVersionRecord.created_at.desc()).limit(limit).all()

def get_agent_updates(self, agent_id: str = None, status: str = None, limit: int = 50) -> list:
    """Get agent updates with optional filtering"""
    query = self.session.query(AgentUpdateRecord)
    
    if agent_id:
        query = query.filter_by(agent_id=agent_id)
    if status:
        query = query.filter_by(status=status)
    
    return query.order_by(AgentUpdateRecord.created_at.desc()).limit(limit).all()

def get_available_updates(self, channel: str = None) -> list:
    """Get available update packages"""
    query = self.session.query(UpdatePackageRecord)
    
    if channel:
        query = query.filter_by(channel=channel)
    
    return query.order_by(UpdatePackageRecord.release_date.desc()).all()

def get_rollback_history(self, agent_id: str = None, limit: int = 20) -> list:
    """Get rollback operation history"""
    query = self.session.query(RollbackOperationRecord)
    
    if agent_id:
        query = query.filter_by(agent_id=agent_id)
    
    return query.order_by(RollbackOperationRecord.created_at.desc()).limit(limit).all()

def get_version_audit_log(self, agent_id: str = None, action: str = None, days: int = 30) -> list:
    """Get version control audit log"""
    cutoff = datetime.now() - timedelta(days=days)
    query = self.session.query(VersionAuditRecord).filter(
        VersionAuditRecord.performed_at >= cutoff
    )
    
    if agent_id:
        query = query.filter_by(agent_id=agent_id)
    if action:
        query = query.filter_by(action=action)
    
    return query.order_by(VersionAuditRecord.performed_at.desc()).all()

def get_update_metrics(self, update_id: str = None, agent_id: str = None) -> list:
    """Get update performance metrics"""
    query = self.session.query(UpdateMetricsRecord)
    
    if update_id:
        query = query.filter_by(update_id=update_id)
    if agent_id:
        query = query.filter_by(agent_id=agent_id)
    
    return query.order_by(UpdateMetricsRecord.measured_at.desc()).all()

def cleanup_old_version_data(self, days: int = 90):
    """Clean up old version control data"""
    cutoff = datetime.now() - timedelta(days=days)
    
    # Cleanup old audit records
    self.session.query(VersionAuditRecord).filter(
        VersionAuditRecord.performed_at < cutoff
    ).delete()
    
    # Cleanup old metrics
    self.session.query(UpdateMetricsRecord).filter(
        UpdateMetricsRecord.measured_at < cutoff
    ).delete()
    
    # Cleanup completed updates older than cutoff
    self.session.query(AgentUpdateRecord).filter(
        AgentUpdateRecord.status.in_(['completed', 'failed']),
        AgentUpdateRecord.completed_at < cutoff
    ).delete()
    
    # Cleanup old rollback operations
    self.session.query(RollbackOperationRecord).filter(
        RollbackOperationRecord.status.in_(['completed', 'failed']),
        RollbackOperationRecord.completed_at < cutoff
    ).delete()
    
    self.session.commit()

# Database Manager
class EnhancedNodeDatabase:
    """Enhanced database manager with advanced remote control features"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.version_control = VersionControlManager(self)
        self.logger.info("✅ Version control system enabled")
    
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
