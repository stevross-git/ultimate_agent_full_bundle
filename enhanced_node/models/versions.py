#!/usr/bin/env python3
"""
Enhanced Node Server - Version Control Models
Data models for agent version control, updates, and rollbacks

FILE LOCATION: enhanced_node/models/versions.py
DEPENDENCIES: None (standalone models file)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class AgentVersion:
    """Agent version information"""
    agent_id: str
    version: str
    build_number: int = 0
    commit_hash: str = ""
    build_date: Optional[datetime] = None
    
    # Capabilities and features
    capabilities: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    
    # Platform information
    platform: str = "unknown"
    architecture: str = "unknown"
    
    # Update settings
    update_channel: str = "stable"
    last_seen: Optional[datetime] = None
    
    # Version metadata
    release_notes: str = ""
    changelog: List[str] = field(default_factory=list)
    security_patches: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.build_date is None:
            self.build_date = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()


@dataclass
class UpdatePackage:
    """Update package information"""
    id: str
    version: str
    channel: str = "stable"
    release_date: Optional[datetime] = None
    
    # Update details
    update_type: str = "feature"  # security, feature, bugfix, experimental
    download_url: str = ""
    checksum: str = ""
    size_bytes: int = 0
    
    # Description and changelog
    description: str = ""
    changelog: List[str] = field(default_factory=list)
    release_notes: str = ""
    
    # Requirements and compatibility
    requirements: Dict[str, Any] = field(default_factory=dict)
    compatibility: Dict[str, List[str]] = field(default_factory=dict)
    
    # Update settings
    rollback_supported: bool = True
    critical: bool = False
    auto_install: bool = False
    
    # Timing
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.release_date is None:
            self.release_date = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AgentUpdate:
    """Agent update operation"""
    id: str
    agent_id: str
    package_id: str
    from_version: str
    to_version: str
    
    # Update configuration
    update_type: str = "feature"
    scheduled_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Status tracking
    status: str = "scheduled"  # scheduled, downloading, installing, restarting, verifying, completed, failed, rolled_back
    progress: int = 0
    error_message: Optional[str] = None
    
    # Update strategy
    strategy: str = "rolling"  # rolling, canary, blue_green, immediate, maintenance_window
    
    # Backup and rollback
    backup_path: Optional[str] = None
    auto_rollback_enabled: bool = True
    rollback_threshold_minutes: int = 30
    
    # Validation
    pre_update_checks: List[str] = field(default_factory=list)
    post_update_checks: List[str] = field(default_factory=list)
    health_checks_passed: bool = False
    
    # Metadata
    initiated_by: str = "system"
    notes: str = ""
    
    def __post_init__(self):
        if self.scheduled_time is None:
            self.scheduled_time = datetime.now()


@dataclass
class RollbackOperation:
    """Rollback operation"""
    id: str
    agent_id: str
    update_id: str
    from_version: str
    to_version: str
    
    # Rollback details
    rollback_type: str = "manual"  # manual, automatic, scheduled
    backup_path: str = ""
    initiated_by: str = "system"
    reason: str = ""
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Status
    status: str = "scheduled"  # scheduled, executing, completed, failed
    error_message: Optional[str] = None
    
    # Validation
    pre_rollback_checks: List[str] = field(default_factory=list)
    post_rollback_checks: List[str] = field(default_factory=list)
    verification_passed: bool = False
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()


@dataclass
class VersionPolicy:
    """Version control policy"""
    id: str
    name: str
    description: str
    
    # Policy rules
    auto_update: bool = False
    update_channels: List[str] = field(default_factory=lambda: ["stable"])
    update_types: List[str] = field(default_factory=lambda: ["security", "bugfix"])
    
    # Timing rules
    delay_hours: int = 24
    maintenance_window_only: bool = False
    maintenance_window: Dict[str, str] = field(default_factory=dict)
    
    # Agent targeting
    target_agents: List[str] = field(default_factory=list)
    target_platforms: List[str] = field(default_factory=list)
    target_channels: List[str] = field(default_factory=list)
    
    # Rollback settings
    auto_rollback: bool = True
    rollback_threshold_minutes: int = 30
    health_check_interval: int = 5
    
    # Approval requirements
    approval_required: bool = False
    approvers: List[str] = field(default_factory=list)
    
    # Created metadata
    created_at: Optional[datetime] = None
    created_by: str = "system"
    active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class UpdateApproval:
    """Update approval record"""
    id: str
    update_id: str
    policy_id: str
    
    # Approval details
    required_approvals: int = 1
    received_approvals: int = 0
    approved: bool = False
    
    # Approver tracking
    approvers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Timing
    created_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Comments
    comments: List[Dict[str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class VersionAudit:
    """Version control audit record"""
    id: str
    agent_id: str
    action: str  # update, rollback, policy_change, approval
    
    # Action details
    from_version: Optional[str] = None
    to_version: Optional[str] = None
    action_data: Dict[str, Any] = field(default_factory=dict)
    
    # User and timing
    performed_by: str = "system"
    performed_at: Optional[datetime] = None
    
    # Outcome
    success: bool = True
    error_message: Optional[str] = None
    
    # Context
    reason: str = ""
    notes: str = ""
    related_records: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.performed_at is None:
            self.performed_at = datetime.now()


@dataclass
class DistributionGroup:
    """Agent distribution group for staged rollouts"""
    id: str
    name: str
    description: str = ""
    
    # Group membership
    agents: List[str] = field(default_factory=list)
    agent_filters: Dict[str, Any] = field(default_factory=dict)
    
    # Rollout configuration
    rollout_percentage: int = 100
    rollout_strategy: str = "rolling"
    
    # Health monitoring
    health_check_required: bool = True
    success_threshold: float = 0.95
    failure_threshold: float = 0.1
    
    # Timing
    created_at: Optional[datetime] = None
    active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class UpdateMetrics:
    """Update operation metrics"""
    update_id: str
    agent_id: str
    
    # Performance metrics
    download_time_seconds: float = 0.0
    install_time_seconds: float = 0.0
    restart_time_seconds: float = 0.0
    verification_time_seconds: float = 0.0
    total_time_seconds: float = 0.0
    
    # Resource usage
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    network_usage_mb: float = 0.0
    
    # Success metrics
    pre_checks_passed: int = 0
    pre_checks_total: int = 0
    post_checks_passed: int = 0
    post_checks_total: int = 0
    
    # Error tracking
    errors_encountered: List[str] = field(default_factory=list)
    warnings_encountered: List[str] = field(default_factory=list)
    
    # Timing details
    measured_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.measured_at is None:
            self.measured_at = datetime.now()


@dataclass
class ChannelConfiguration:
    """Update channel configuration"""
    channel: str
    name: str
    description: str = ""
    
    # Channel settings
    auto_updates: bool = False
    update_frequency: str = "daily"  # hourly, daily, weekly, manual
    
    # Quality gates
    stability_threshold: float = 0.95
    testing_required: bool = True
    approval_required: bool = False
    
    # Distribution settings
    rollout_percentage: int = 100
    canary_percentage: int = 10
    
    # Timing
    created_at: Optional[datetime] = None
    active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


# Enums and Constants

UPDATE_TYPES = [
    "security",
    "bugfix", 
    "feature",
    "experimental",
    "hotfix",
    "rollup"
]

UPDATE_STATUSES = [
    "scheduled",
    "downloading", 
    "installing",
    "restarting",
    "verifying",
    "completed",
    "failed",
    "cancelled",
    "rolled_back"
]

ROLLBACK_TYPES = [
    "manual",
    "automatic",
    "scheduled",
    "policy_triggered",
    "health_triggered"
]

UPDATE_CHANNELS = [
    "stable",
    "beta", 
    "alpha",
    "nightly",
    "custom"
]

UPDATE_STRATEGIES = [
    "rolling",
    "canary",
    "blue_green",
    "immediate",
    "maintenance_window",
    "staged"
]

HEALTH_CHECK_TYPES = [
    "startup",
    "connectivity",
    "functionality",
    "performance",
    "security",
    "integration"
]

APPROVAL_STATUSES = [
    "pending",
    "approved",
    "rejected",
    "expired",
    "cancelled"
]

AUDIT_ACTIONS = [
    "agent_registered",
    "version_updated",
    "update_scheduled",
    "update_started",
    "update_completed",
    "update_failed",
    "rollback_initiated",
    "rollback_completed",
    "policy_created",
    "policy_updated",
    "approval_granted",
    "approval_denied",
    "health_check_failed",
    "emergency_stop"
]
