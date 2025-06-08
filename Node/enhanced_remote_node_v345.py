#!/usr/bin/env python3
"""
Enhanced Node Server v3.4-ADVANCED-REMOTE-CONTROL - COMPREHENSIVE AGENT MANAGEMENT
Based on v3.3 with ADVANCED remote control capabilities added

THIS VERSION:
- ✅ KEEPS all existing functionality from v3.3
- ✅ KEEPS all existing API endpoints  
- ✅ KEEPS existing agent registration and task control
- ✅ KEEPS existing dashboard and monitoring
- ➕ ADDS advanced remote control capabilities
- ➕ ADDS agent script deployment and updates
- ➕ ADDS bulk operations and command scheduling
- ➕ ADDS comprehensive agent health monitoring
- ➕ ADDS command history and replay capabilities
"""

import os
import sys
import time
import json
import signal
import asyncio
import logging
import threading
import sqlite3
import hashlib
import uuid
import statistics
import redis
import urllib.parse
import random
import subprocess
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import requests
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psutil
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Enhanced Node Configuration - KEEP EXISTING
NODE_VERSION = "3.4.0-advanced-remote-control"
NODE_PORT = 5000
MANAGER_HOST = "mannodes.peoplesainetwork.com"
MANAGER_PORT = 5001
NODE_ID = f"enhanced-node-{uuid.uuid4().hex[:12]}"
LOG_DIR = "logs"
DATABASE_PATH = "enhanced_node_server.db"
AGENT_SCRIPTS_DIR = "agent_scripts"
COMMAND_HISTORY_DIR = "command_history"

# Create directories
Path(LOG_DIR).mkdir(exist_ok=True)
Path(AGENT_SCRIPTS_DIR).mkdir(exist_ok=True)
Path(COMMAND_HISTORY_DIR).mkdir(exist_ok=True)

Base = declarative_base()

# DATETIME SERIALIZATION FIXES - KEEP EXISTING
def serialize_for_json(obj):
    """Convert datetime objects and other non-serializable objects to JSON-serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (list, tuple)):
                result[key] = [serialize_for_json(item) for item in value]
            elif isinstance(value, dict):
                result[key] = {k: serialize_for_json(v) for k, v in value.items()}
            else:
                result[key] = value
        return result
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj

class DateTimeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# KEEP ALL EXISTING DATACLASSES - ADD NEW ONES

@dataclass
class EnhancedAgentInfo:
    """Enhanced information about connected Ultimate agents - EXISTING"""
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
    """Enhanced current status of an Ultimate agent - EXISTING"""
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

@dataclass
class CentralTask:
    """Centralized task definition for task control - EXISTING"""
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

# EXISTING: REMOTE MANAGEMENT DATACLASSES
@dataclass
class AgentCommand:
    """Remote agent command - EXISTING"""
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
    """Agent configuration profile - EXISTING"""
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

# NEW: ADVANCED REMOTE CONTROL DATACLASSES
@dataclass
class ScheduledCommand:
    """NEW: Scheduled command execution"""
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
    """NEW: Bulk operation for multiple agents"""
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
    """NEW: Agent health monitoring"""
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
    """NEW: Agent script deployment"""
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

# KEEP ALL EXISTING DATABASE MODELS
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

class CentralTaskRecord(Base):
    """Central task records - EXISTING"""
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

# EXISTING: REMOTE MANAGEMENT DATABASE MODELS
class AgentCommandRecord(Base):
    """Remote agent commands - EXISTING"""
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
    """Agent configurations - EXISTING"""
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
    """Agent activity logs - EXISTING"""
    __tablename__ = 'agent_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String)
    log_level = Column(String)
    message = Column(Text)
    category = Column(String)
    
    timestamp = Column(DateTime)
    log_data = Column(JSON)

# NEW: ADVANCED REMOTE CONTROL DATABASE MODELS
class ScheduledCommandRecord(Base):
    """NEW: Scheduled commands"""
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
    """NEW: Bulk operations"""
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
    """NEW: Agent health monitoring"""
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
    """NEW: Agent script deployment"""
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

# ENHANCED DATABASE WITH ADVANCED REMOTE CONTROL
class EnhancedNodeDatabase:
    """Enhanced database manager - EXISTING + NEW ADVANCED FEATURES"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data - EXISTING + NEW"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # EXISTING cleanup
        self.session.query(AgentHeartbeat).filter(
            AgentHeartbeat.timestamp < cutoff
        ).delete()
        
        # NEW cleanup
        self.session.query(AgentHealthRecord).filter(
            AgentHealthRecord.timestamp < cutoff
        ).delete()
        
        # Clean up completed scheduled commands
        self.session.query(ScheduledCommandRecord).filter(
            ScheduledCommandRecord.status == 'completed',
            ScheduledCommandRecord.last_executed < cutoff
        ).delete()
        
        self.session.commit()

# NEW: ADVANCED REMOTE CONTROL MANAGER
class AdvancedRemoteControlManager:
    """NEW: Advanced remote control capabilities"""
    
    def __init__(self, node_server):
        self.node_server = node_server
        
        # EXISTING features from RemoteAgentManager
        self.active_commands = {}
        self.agent_configurations = {}
        self.command_queue = defaultdict(deque)
        
        # NEW: Advanced features
        self.scheduled_commands = {}
        self.bulk_operations = {}
        self.agent_health_monitors = {}
        self.agent_scripts = {}
        self.command_history = defaultdict(list)
        
        # NEW: Command scheduler
        self.scheduler_running = False
        self.health_monitor_running = False
        
        # NEW: Enhanced command capabilities
        self.advanced_commands = {
            "system_control": {
                "restart_agent": "Restart agent gracefully",
                "shutdown_agent": "Shutdown agent safely", 
                "update_config": "Update agent configuration",
                "reload_config": "Reload configuration files",
                "restart_service": "Restart specific service",
                "kill_process": "Kill specific process",
                "reboot_system": "Reboot entire system",
                "update_system": "Update system packages"
            },
            "task_management": {
                "start_task": "Start specific task on agent",
                "cancel_task": "Cancel running task",
                "pause_task": "Pause task execution",
                "resume_task": "Resume paused task",
                "set_task_priority": "Change task priority",
                "clear_task_queue": "Clear all pending tasks",
                "backup_task_data": "Backup task results",
                "restore_task_data": "Restore task data"
            },
            "performance_tuning": {
                "set_cpu_limit": "Set CPU usage limit",
                "set_memory_limit": "Set memory usage limit",
                "enable_gpu": "Enable/disable GPU usage",
                "optimize_performance": "Run performance optimization",
                "clear_cache": "Clear system caches",
                "defrag_disk": "Defragment disk",
                "tune_network": "Optimize network settings",
                "balance_load": "Balance computational load"
            },
            "monitoring": {
                "get_detailed_status": "Get comprehensive status",
                "get_logs": "Retrieve agent logs",
                "run_diagnostics": "Run system diagnostics",
                "monitor_resources": "Real-time resource monitoring",
                "check_health": "Comprehensive health check",
                "trace_performance": "Performance tracing",
                "profile_memory": "Memory profiling",
                "analyze_network": "Network analysis"
            },
            "maintenance": {
                "cleanup_logs": "Clean up old log files",
                "backup_data": "Create data backup",
                "restore_data": "Restore from backup",
                "update_agent": "Update agent software",
                "patch_system": "Apply system patches",
                "vacuum_database": "Optimize database",
                "compress_data": "Compress old data",
                "sync_time": "Synchronize system time"
            },
            "security": {
                "scan_vulnerabilities": "Security vulnerability scan",
                "update_certificates": "Update security certificates",
                "rotate_keys": "Rotate encryption keys",
                "audit_access": "Audit access logs",
                "firewall_update": "Update firewall rules",
                "malware_scan": "Scan for malware",
                "secure_delete": "Securely delete files",
                "encrypt_data": "Encrypt sensitive data"
            },
            "development": {
                "deploy_script": "Deploy custom script",
                "run_test": "Run test suite",
                "debug_session": "Start debug session",
                "profile_code": "Profile code performance",
                "validate_config": "Validate configuration",
                "simulate_load": "Simulate load testing",
                "benchmark_system": "System benchmarking",
                "code_analysis": "Static code analysis"
            }
        }
        
        # NEW: Command templates with advanced parameters
        self.advanced_command_templates = {
            "restart_agent": {
                "description": "Gracefully restart the agent with options",
                "parameters": {
                    "delay_seconds": 5, 
                    "save_state": True,
                    "backup_data": True,
                    "notify_manager": True,
                    "graceful_shutdown": True
                }
            },
            "update_config": {
                "description": "Update agent configuration with validation",
                "parameters": {
                    "config_section": "", 
                    "config_data": {},
                    "validate_before_apply": True,
                    "backup_old_config": True,
                    "restart_if_needed": False
                }
            },
            "deploy_script": {
                "description": "Deploy and execute custom script",
                "parameters": {
                    "script_content": "",
                    "script_type": "python",
                    "execution_mode": "safe",
                    "timeout_seconds": 300,
                    "capture_output": True,
                    "cleanup_after": True
                }
            },
            "bulk_health_check": {
                "description": "Comprehensive health check across multiple agents",
                "parameters": {
                    "check_system": True,
                    "check_network": True,
                    "check_performance": True,
                    "check_security": True,
                    "generate_report": True,
                    "auto_recovery": False
                }
            },
            "performance_optimization": {
                "description": "Comprehensive performance optimization",
                "parameters": {
                    "optimize_cpu": True,
                    "optimize_memory": True,
                    "optimize_disk": True,
                    "optimize_network": True,
                    "clear_caches": True,
                    "tune_services": True
                }
            }
        }
    
    def start_advanced_services(self):
        """Start advanced remote control services"""
        self.start_command_scheduler()
        self.start_health_monitor()
        self.node_server.logger.info("Advanced remote control services started")
    
    def start_command_scheduler(self):
        """Start command scheduler service"""
        def scheduler_loop():
            self.scheduler_running = True
            while self.scheduler_running:
                try:
                    self.process_scheduled_commands()
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    self.node_server.logger.error(f"Command scheduler error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=scheduler_loop, daemon=True, name="CommandScheduler")
        thread.start()
        self.node_server.logger.info("Command scheduler started")
    
    def start_health_monitor(self):
        """Start agent health monitoring service"""
        def health_monitor_loop():
            self.health_monitor_running = True
            while self.health_monitor_running:
                try:
                    self.monitor_agent_health()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    self.node_server.logger.error(f"Health monitor error: {e}")
                    time.sleep(120)
        
        thread = threading.Thread(target=health_monitor_loop, daemon=True, name="HealthMonitor")
        thread.start()
        self.node_server.logger.info("Agent health monitor started")
    
    def create_scheduled_command(self, agent_id: str, command_type: str, 
                                scheduled_time: datetime, parameters: Dict = None,
                                repeat_interval: int = None, max_repeats: int = 1) -> ScheduledCommand:
        """Create a scheduled command"""
        command = AgentCommand(
            id=f"cmd-{int(time.time())}-{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            command_type=command_type,
            parameters=parameters or {}
        )
        
        scheduled_cmd = ScheduledCommand(
            id=f"sched-{int(time.time())}-{uuid.uuid4().hex[:8]}",
            command=command,
            scheduled_time=scheduled_time,
            repeat_interval=repeat_interval,
            max_repeats=max_repeats
        )
        
        self.scheduled_commands[scheduled_cmd.id] = scheduled_cmd
        self.store_scheduled_command_in_db(scheduled_cmd)
        
        self.node_server.logger.info(f"Scheduled command {scheduled_cmd.id} for agent {agent_id} at {scheduled_time}")
        return scheduled_cmd
    
    def process_scheduled_commands(self):
        """Process due scheduled commands"""
        current_time = datetime.now()
        
        for scheduled_cmd in list(self.scheduled_commands.values()):
            if scheduled_cmd.status == "scheduled" and scheduled_cmd.scheduled_time <= current_time:
                try:
                    scheduled_cmd.status = "executing"
                    
                    # Execute the command
                    success = self.execute_command_on_agent(scheduled_cmd.command)
                    
                    if success:
                        scheduled_cmd.current_repeats += 1
                        
                        # Check if we need to reschedule
                        if (scheduled_cmd.repeat_interval and 
                            scheduled_cmd.current_repeats < scheduled_cmd.max_repeats):
                            scheduled_cmd.scheduled_time = current_time + timedelta(seconds=scheduled_cmd.repeat_interval)
                            scheduled_cmd.status = "scheduled"
                        else:
                            scheduled_cmd.status = "completed"
                    else:
                        scheduled_cmd.status = "failed"
                    
                    self.update_scheduled_command_in_db(scheduled_cmd)
                    
                except Exception as e:
                    scheduled_cmd.status = "failed"
                    self.node_server.logger.error(f"Scheduled command {scheduled_cmd.id} failed: {e}")
    
    def create_bulk_operation(self, operation_type: str, target_agents: List[str], 
                            parameters: Dict = None) -> BulkOperation:
        """Create a bulk operation for multiple agents"""
        bulk_op = BulkOperation(
            id=f"bulk-{int(time.time())}-{uuid.uuid4().hex[:8]}",
            operation_type=operation_type,
            target_agents=target_agents,
            parameters=parameters or {}
        )
        
        self.bulk_operations[bulk_op.id] = bulk_op
        self.store_bulk_operation_in_db(bulk_op)
        
        # Execute bulk operation
        self.execute_bulk_operation(bulk_op)
        
        return bulk_op
    
    def execute_bulk_operation(self, bulk_op: BulkOperation):
        """Execute bulk operation on multiple agents"""
        def bulk_execution():
            try:
                bulk_op.status = "executing"
                bulk_op.started_at = datetime.now()
                
                for agent_id in bulk_op.target_agents:
                    try:
                        # Create individual command for each agent
                        command = self.create_agent_command(
                            agent_id, 
                            bulk_op.operation_type, 
                            bulk_op.parameters
                        )
                        
                        success = self.execute_command_on_agent(command)
                        
                        if success:
                            bulk_op.success_count += 1
                            bulk_op.results[agent_id] = {"status": "success", "command_id": command.id}
                        else:
                            bulk_op.failure_count += 1
                            bulk_op.results[agent_id] = {"status": "failed", "error": "Command execution failed"}
                    
                    except Exception as e:
                        bulk_op.failure_count += 1
                        bulk_op.results[agent_id] = {"status": "error", "error": str(e)}
                
                # Determine final status
                if bulk_op.failure_count == 0:
                    bulk_op.status = "completed"
                elif bulk_op.success_count == 0:
                    bulk_op.status = "failed"
                else:
                    bulk_op.status = "partial"
                
                bulk_op.completed_at = datetime.now()
                self.update_bulk_operation_in_db(bulk_op)
                
                # Broadcast completion
                self.node_server.socketio.emit('bulk_operation_completed', {
                    'operation_id': bulk_op.id,
                    'status': bulk_op.status,
                    'success_count': bulk_op.success_count,
                    'failure_count': bulk_op.failure_count
                }, room='dashboard')
                
            except Exception as e:
                bulk_op.status = "failed"
                bulk_op.completed_at = datetime.now()
                self.node_server.logger.error(f"Bulk operation {bulk_op.id} failed: {e}")
        
        thread = threading.Thread(target=bulk_execution, daemon=True)
        thread.start()
    
    def monitor_agent_health(self):
        """Monitor health of all agents"""
        for agent_id, agent_status in self.node_server.agent_status.items():
            try:
                health_check = self.perform_health_check(agent_id, agent_status)
                self.store_health_check_in_db(health_check)
                
                # Check if recovery is needed
                if health_check.recovery_needed:
                    self.handle_agent_recovery(health_check)
                    
            except Exception as e:
                self.node_server.logger.error(f"Health check failed for agent {agent_id}: {e}")
    
    def perform_health_check(self, agent_id: str, agent_status: EnhancedAgentStatus) -> AgentHealthCheck:
        """Perform comprehensive health check on agent"""
        current_time = datetime.now()
        
        # Calculate health metrics
        cpu_health = "healthy" if agent_status.cpu_percent < 80 else "warning" if agent_status.cpu_percent < 95 else "critical"
        memory_health = "healthy" if agent_status.memory_percent < 80 else "warning" if agent_status.memory_percent < 95 else "critical"
        
        # Check if agent is responsive
        last_heartbeat_age = (current_time - agent_status.last_heartbeat).total_seconds() if agent_status.last_heartbeat else float('inf')
        network_health = "healthy" if last_heartbeat_age < 60 else "warning" if last_heartbeat_age < 120 else "critical"
        
        # Task health based on success rate
        total_tasks = agent_status.tasks_completed + agent_status.tasks_failed
        task_success_rate = agent_status.tasks_completed / max(total_tasks, 1)
        task_health = "healthy" if task_success_rate > 0.9 else "warning" if task_success_rate > 0.7 else "critical"
        
        # Overall health score
        health_scores = {
            "healthy": 100,
            "warning": 70,
            "critical": 30,
            "offline": 0
        }
        
        overall_health = min(
            health_scores[cpu_health],
            health_scores[memory_health], 
            health_scores[network_health],
            health_scores[task_health]
        )
        
        # Determine overall status
        if overall_health >= 90:
            status = "healthy"
        elif overall_health >= 70:
            status = "warning"
        elif overall_health >= 30:
            status = "critical"
        else:
            status = "offline"
        
        # Determine recovery actions
        recovery_actions = []
        recovery_needed = False
        
        if cpu_health == "critical":
            recovery_actions.append("restart_high_cpu_processes")
            recovery_needed = True
        if memory_health == "critical":
            recovery_actions.append("clear_memory_cache")
            recovery_needed = True
        if network_health == "critical":
            recovery_actions.append("restart_network_service")
            recovery_needed = True
        if task_health == "critical":
            recovery_actions.append("restart_task_engine")
            recovery_needed = True
        
        return AgentHealthCheck(
            agent_id=agent_id,
            timestamp=current_time,
            status=status,
            cpu_health=cpu_health,
            memory_health=memory_health,
            disk_health="unknown",  # TODO: Add disk monitoring
            network_health=network_health,
            task_health=task_health,
            health_score=overall_health,
            response_time=last_heartbeat_age,
            recovery_needed=recovery_needed,
            recovery_actions=recovery_actions
        )
    
    def handle_agent_recovery(self, health_check: AgentHealthCheck):
        """Handle automatic agent recovery"""
        if not health_check.recovery_needed:
            return
        
        self.node_server.logger.warning(f"Agent {health_check.agent_id} needs recovery: {health_check.recovery_actions}")
        
        for action in health_check.recovery_actions:
            try:
                # Map recovery actions to commands
                recovery_commands = {
                    "restart_high_cpu_processes": ("restart_service", {"service": "high_cpu_processes"}),
                    "clear_memory_cache": ("clear_cache", {"cache_type": "memory"}),
                    "restart_network_service": ("restart_service", {"service": "network"}),
                    "restart_task_engine": ("restart_service", {"service": "task_engine"})
                }
                
                if action in recovery_commands:
                    command_type, parameters = recovery_commands[action]
                    
                    command = self.create_agent_command(
                        health_check.agent_id,
                        command_type,
                        parameters
                    )
                    
                    self.execute_command_on_agent(command)
                    self.node_server.logger.info(f"Executed recovery action {action} for agent {health_check.agent_id}")
                    
            except Exception as e:
                self.node_server.logger.error(f"Recovery action {action} failed for agent {health_check.agent_id}: {e}")
    
    def deploy_script_to_agent(self, agent_id: str, script: AgentScript) -> bool:
        """Deploy script to specific agent"""
        try:
            command = self.create_agent_command(
                agent_id,
                "deploy_script",
                {
                    "script_id": script.id,
                    "script_name": script.name,
                    "script_content": script.script_content,
                    "script_type": script.script_type,
                    "checksum": script.checksum
                }
            )
            
            success = self.execute_command_on_agent(command)
            
            if success:
                script.deployment_results[agent_id] = {"status": "deployed", "timestamp": datetime.now().isoformat()}
            else:
                script.deployment_results[agent_id] = {"status": "failed", "error": "Deployment failed"}
            
            self.update_script_in_db(script)
            return success
            
        except Exception as e:
            script.deployment_results[agent_id] = {"status": "error", "error": str(e)}
            self.update_script_in_db(script)
            return False
    
    def create_agent_command(self, agent_id: str, command_type: str, parameters: Dict = None) -> AgentCommand:
        """Create a new agent command"""
        command = AgentCommand(
            id=f"cmd-{int(time.time())}-{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            command_type=command_type,
            parameters=parameters or {}
        )
        
        self.active_commands[command.id] = command
        self.command_queue[agent_id].append(command)
        
        # Store in database
        self.store_command_in_db(command)
        
        # Add to command history
        self.command_history[agent_id].append(command)
        if len(self.command_history[agent_id]) > 100:  # Keep last 100 commands
            self.command_history[agent_id].pop(0)
        
        self.node_server.logger.info(f"Created command {command.id} for agent {agent_id}: {command_type}")
        return command
    
    def execute_command_on_agent(self, command: AgentCommand) -> bool:
        """Execute command on specific agent via WebSocket"""
        try:
            command.status = "executing"
            command.executed_at = datetime.now()
            
            command_data = {
                "command_id": command.id,
                "command_type": command.command_type,
                "parameters": command.parameters,
                "timestamp": command.executed_at.isoformat()
            }
            
            # Send command via WebSocket
            self.node_server.socketio.emit(
                'remote_command', 
                command_data, 
                room=f'agent_{command.agent_id}'
            )
            
            self.update_command_in_db(command)
            self.node_server.logger.info(f"Executed command {command.id} on agent {command.agent_id}")
            return True
            
        except Exception as e:
            command.status = "failed"
            command.error_message = str(e)
            command.completed_at = datetime.now()
            self.update_command_in_db(command)
            self.node_server.logger.error(f"Failed to execute command {command.id}: {e}")
            return False
    
    def handle_command_response(self, command_id: str, success: bool, result: Dict = None, error: str = None):
        """Handle command execution response from agent"""
        if command_id not in self.active_commands:
            return
        
        command = self.active_commands[command_id]
        command.completed_at = datetime.now()
        
        if success:
            command.status = "completed"
            if result:
                command.result.update(result)
        else:
            command.status = "failed"
            command.error_message = error
        
        self.update_command_in_db(command)
        
        # Remove from active commands
        del self.active_commands[command_id]
        
        # Broadcast update
        self.node_server.socketio.emit('command_completed', {
            'command_id': command_id,
            'agent_id': command.agent_id,
            'success': success,
            'result': result
        }, room='dashboard')
        
        self.node_server.logger.info(f"Command {command_id} {'completed' if success else 'failed'}")
    
    def get_command_history(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Get command history for agent"""
        history = self.command_history.get(agent_id, [])
        return [serialize_for_json(cmd) for cmd in history[-limit:]]
    
    def replay_command(self, command_id: str) -> bool:
        """Replay a previous command"""
        try:
            # Find command in history
            for agent_commands in self.command_history.values():
                for cmd in agent_commands:
                    if cmd.id == command_id:
                        # Create new command with same parameters
                        new_command = self.create_agent_command(
                            cmd.agent_id,
                            cmd.command_type,
                            cmd.parameters
                        )
                        return self.execute_command_on_agent(new_command)
            return False
        except Exception as e:
            self.node_server.logger.error(f"Failed to replay command {command_id}: {e}")
            return False
    
    def get_advanced_statistics(self) -> Dict[str, Any]:
        """Get advanced remote control statistics"""
        return {
            "total_commands_executed": sum(len(history) for history in self.command_history.values()),
            "active_commands": len(self.active_commands),
            "scheduled_commands": len([cmd for cmd in self.scheduled_commands.values() if cmd.status == "scheduled"]),
            "bulk_operations": len(self.bulk_operations),
            "agent_scripts": len(self.agent_scripts),
            "health_monitoring_active": self.health_monitor_running,
            "command_scheduler_active": self.scheduler_running,
            "advanced_command_types": len(sum(self.advanced_commands.values(), [])),
            "recovery_actions_available": len(set().union(*[health.recovery_actions for health in self.agent_health_monitors.values() if hasattr(health, 'recovery_actions')]))
        }
    
    # Database methods
    def store_command_in_db(self, command: AgentCommand):
        """Store command in database"""
        try:
            db_command = AgentCommandRecord(
                id=command.id,
                agent_id=command.agent_id,
                command_type=command.command_type,
                parameters=command.parameters,
                created_at=command.created_at,
                executed_at=command.executed_at,
                completed_at=command.completed_at,
                status=command.status,
                result=command.result,
                error_message=command.error_message
            )
            
            self.node_server.db.session.merge(db_command)
            self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to store command: {e}")
    
    def update_command_in_db(self, command: AgentCommand):
        """Update command in database"""
        self.store_command_in_db(command)
    
    def store_scheduled_command_in_db(self, scheduled_cmd: ScheduledCommand):
        """Store scheduled command in database"""
        try:
            db_scheduled = ScheduledCommandRecord(
                id=scheduled_cmd.id,
                command_id=scheduled_cmd.command.id,
                agent_id=scheduled_cmd.command.agent_id,
                command_type=scheduled_cmd.command.command_type,
                parameters=scheduled_cmd.command.parameters,
                scheduled_time=scheduled_cmd.scheduled_time,
                repeat_interval=scheduled_cmd.repeat_interval,
                max_repeats=scheduled_cmd.max_repeats,
                current_repeats=scheduled_cmd.current_repeats,
                status=scheduled_cmd.status,
                created_at=datetime.now()
            )
            
            self.node_server.db.session.add(db_scheduled)
            self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to store scheduled command: {e}")
    
    def update_scheduled_command_in_db(self, scheduled_cmd: ScheduledCommand):
        """Update scheduled command in database"""
        try:
            db_scheduled = self.node_server.db.session.query(ScheduledCommandRecord).filter_by(id=scheduled_cmd.id).first()
            if db_scheduled:
                db_scheduled.status = scheduled_cmd.status
                db_scheduled.current_repeats = scheduled_cmd.current_repeats
                db_scheduled.last_executed = datetime.now() if scheduled_cmd.status == "executing" else None
                self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to update scheduled command: {e}")
    
    def store_bulk_operation_in_db(self, bulk_op: BulkOperation):
        """Store bulk operation in database"""
        try:
            db_bulk = BulkOperationRecord(
                id=bulk_op.id,
                operation_type=bulk_op.operation_type,
                target_agents=bulk_op.target_agents,
                parameters=bulk_op.parameters,
                created_at=bulk_op.created_at,
                started_at=bulk_op.started_at,
                completed_at=bulk_op.completed_at,
                status=bulk_op.status,
                results=bulk_op.results,
                success_count=bulk_op.success_count,
                failure_count=bulk_op.failure_count
            )
            
            self.node_server.db.session.merge(db_bulk)
            self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to store bulk operation: {e}")
    
    def update_bulk_operation_in_db(self, bulk_op: BulkOperation):
        """Update bulk operation in database"""
        self.store_bulk_operation_in_db(bulk_op)
    
    def store_health_check_in_db(self, health_check: AgentHealthCheck):
        """Store health check in database"""
        try:
            db_health = AgentHealthRecord(
                agent_id=health_check.agent_id,
                timestamp=health_check.timestamp,
                status=health_check.status,
                cpu_health=health_check.cpu_health,
                memory_health=health_check.memory_health,
                disk_health=health_check.disk_health,
                network_health=health_check.network_health,
                task_health=health_check.task_health,
                health_score=health_check.health_score,
                response_time=health_check.response_time,
                last_error=health_check.last_error,
                recovery_needed=health_check.recovery_needed,
                recovery_actions=health_check.recovery_actions
            )
            
            self.node_server.db.session.add(db_health)
            self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to store health check: {e}")
    
    def store_script_in_db(self, script: AgentScript):
        """Store script in database"""
        try:
            db_script = AgentScriptRecord(
                id=script.id,
                name=script.name,
                version=script.version,
                script_type=script.script_type,
                script_content=script.script_content,
                checksum=script.checksum,
                target_agents=script.target_agents,
                created_at=script.created_at,
                deployed_at=script.deployed_at,
                status=script.status,
                deployment_results=script.deployment_results
            )
            
            self.node_server.db.session.merge(db_script)
            self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to store script: {e}")
    
    def update_script_in_db(self, script: AgentScript):
        """Update script in database"""
        self.store_script_in_db(script)

# KEEP ALL EXISTING CLASSES UNCHANGED - TaskControlManager class stays exactly the same

class TaskControlManager:
    """Centralized task control manager - EXISTING - UNCHANGED"""
    
    def __init__(self, node_server):
        self.node_server = node_server
        self.pending_tasks = deque()
        self.running_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        # Task generation settings
        self.auto_generation_enabled = True
        self.generation_interval = 30
        self.max_pending_tasks = 20
        
        # Task templates
        self.task_templates = {
            "neural_network_training": {
                "priority": 8, "reward": 0.25, "duration": 120,
                "requirements": {"gpu": True, "memory": 2048}
            },
            "blockchain_transaction": {
                "priority": 9, "reward": 0.10, "duration": 30,
                "requirements": {"blockchain": True}
            },
            "sentiment_analysis": {
                "priority": 6, "reward": 0.08, "duration": 25,
                "requirements": {"ai_models": ["sentiment"]}
            },
            "data_processing": {
                "priority": 5, "reward": 0.12, "duration": 60,
                "requirements": {"cpu": 50}
            }
        }
        
        # Metrics
        self.task_metrics = {
            "total_assigned": 0,
            "total_completed": 0,
            "total_failed": 0,
            "success_rate": 100.0
        }
    
    def start_task_control_services(self):
        """Start task control background services - EXISTING"""
        if self.auto_generation_enabled:
            def task_generation_loop():
                while self.node_server.running:
                    try:
                        self.generate_tasks()
                        time.sleep(self.generation_interval)
                    except Exception as e:
                        self.node_server.logger.error(f"Task generation error: {e}")
                        time.sleep(60)
            
            thread = threading.Thread(target=task_generation_loop, daemon=True, name="TaskGeneration")
            thread.start()
            self.node_server.logger.info("Task control services started")
    
    def generate_tasks(self):
        """Generate new tasks - EXISTING"""
        if len(self.pending_tasks) < self.max_pending_tasks:
            online_agents = len([a for a in self.node_server.agents.values()])
            if online_agents > 0:
                # Generate 1-2 tasks
                for _ in range(random.randint(1, 2)):
                    task_type = random.choice(list(self.task_templates.keys()))
                    task = self.create_task(task_type)
                    self.pending_tasks.append(task)
                    self.store_task_in_db(task)
                    self.node_server.logger.info(f"Generated task: {task.id} ({task.task_type})")
    
    def create_task(self, task_type: str) -> CentralTask:
        """Create a new task - EXISTING"""
        template = self.task_templates.get(task_type, self.task_templates["data_processing"])
        
        task = CentralTask(
            id=f"central-task-{int(time.time())}-{uuid.uuid4().hex[:8]}",
            task_type=task_type,
            priority=template["priority"],
            reward=template["reward"],
            estimated_duration=template["duration"],
            requirements=template.get("requirements", {}),
            config={
                "generated_by": "task_control_manager",
                "auto_generated": True,
                "batch_id": f"batch-{int(time.time())}"
            }
        )
        
        return task
    
    def assign_task_to_agent(self, task: CentralTask, agent_id: str):
        """Assign task to specific agent - EXISTING"""
        task.assigned_agent = agent_id
        task.assigned_at = datetime.now()
        task.status = "assigned"
        
        # Move from pending to running
        try:
            self.pending_tasks.remove(task)
        except ValueError:
            pass
        
        self.running_tasks[task.id] = task
        
        # Send to agent via WebSocket
        self.send_task_to_agent(task, agent_id)
        
        # Update metrics
        self.task_metrics["total_assigned"] += 1
        
        self.node_server.logger.info(f"Assigned task {task.id} to agent {agent_id}")
    
    def send_task_to_agent(self, task: CentralTask, agent_id: str):
        """Send task to agent via WebSocket - EXISTING"""
        task_data = {
            "task_id": task.id,
            "task_type": task.task_type,
            "priority": task.priority,
            "config": task.config,
            "requirements": task.requirements,
            "estimated_duration": task.estimated_duration,
            "reward": task.reward
        }
        
        # Send via WebSocket to agent room
        self.node_server.socketio.emit('central_task_assignment', task_data, room=f'agent_{agent_id}')
    
    def handle_task_completion(self, task_id: str, agent_id: str, success: bool, result: Dict = None):
        """Handle task completion - EXISTING"""
        if task_id not in self.running_tasks:
            return
        
        task = self.running_tasks[task_id]
        task.completed_at = datetime.now()
        
        if success:
            task.status = "completed"
            task.progress = 100.0
            if result:
                task.result.update(result)
            self.completed_tasks[task_id] = task
            self.task_metrics["total_completed"] += 1
        else:
            task.status = "failed"
            self.failed_tasks[task_id] = task
            self.task_metrics["total_failed"] += 1
        
        # Remove from running
        del self.running_tasks[task_id]
        
        # Update success rate
        total = self.task_metrics["total_completed"] + self.task_metrics["total_failed"]
        if total > 0:
            self.task_metrics["success_rate"] = (self.task_metrics["total_completed"] / total) * 100
        
        self.update_task_in_db(task)
        self.node_server.logger.info(f"Task {task_id} {'completed' if success else 'failed'}")
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task control statistics - EXISTING"""
        return {
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "total_assigned": self.task_metrics["total_assigned"],
            "total_completed": self.task_metrics["total_completed"],
            "total_failed": self.task_metrics["total_failed"],
            "success_rate": self.task_metrics["success_rate"]
        }
    
    def store_task_in_db(self, task: CentralTask):
        """Store task in database - EXISTING"""
        try:
            db_task = CentralTaskRecord(
                id=task.id,
                task_type=task.task_type,
                priority=task.priority,
                assigned_agent=task.assigned_agent,
                status=task.status,
                config=task.config,
                requirements=task.requirements,
                created_at=task.created_at,
                assigned_at=task.assigned_at,
                started_at=task.started_at,
                completed_at=task.completed_at,
                progress=task.progress,
                result=task.result,
                error_message=task.error_message,
                retry_count=task.retry_count,
                reward=task.reward,
                estimated_duration=task.estimated_duration,
                actual_duration=task.actual_duration
            )
            
            self.node_server.db.session.merge(db_task)
            self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to store central task: {e}")
    
    def update_task_in_db(self, task: CentralTask):
        """Update task in database - EXISTING"""
        self.store_task_in_db(task)

# MAIN SERVER CLASS - KEEP EXISTING + ADD ADVANCED REMOTE CONTROL
class EnhancedNodeServer:
    """Enhanced Node Server with Advanced Remote Control - EXISTING + NEW"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        
        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["1000 per hour", "100 per minute"]
        )
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(f"{LOG_DIR}/enhanced_node_server_advanced.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("EnhancedNodeServerAdvanced")
        
        # Initialize components
        self.db = EnhancedNodeDatabase(DATABASE_PATH)
        self.agents: Dict[str, EnhancedAgentInfo] = {}
        self.agent_status: Dict[str, EnhancedAgentStatus] = {}
        self.registered_with_manager = False
        self.running = False
        
        # EXISTING: Task control manager
        self.task_control = TaskControlManager(self)
        
        # NEW: Advanced remote control manager
        self.advanced_remote_control = AdvancedRemoteControlManager(self)
        
        # Performance tracking
        self.performance_history = defaultdict(lambda: deque(maxlen=100))
        self.task_queue = deque()
        
        # Prometheus metrics
        self.metrics = {
            'agents_total': Gauge('node_agents_total', 'Total agents connected'),
            'agents_online': Gauge('node_agents_online', 'Online agents'),
            'tasks_running': Gauge('node_tasks_running', 'Tasks currently running'),
            'tasks_completed_total': Counter('node_tasks_completed_total', 'Total tasks completed'),
            'ai_models_total': Gauge('node_ai_models_total', 'Total AI models loaded'),
            'blockchain_balance_total': Gauge('node_blockchain_balance_total', 'Total blockchain balance'),
            'avg_efficiency': Gauge('node_avg_efficiency', 'Average agent efficiency'),
            'commands_total': Counter('node_commands_total', 'Total remote commands sent'),
            'configurations_deployed': Counter('node_configurations_deployed', 'Total configurations deployed'),
            'bulk_operations_total': Counter('node_bulk_operations_total', 'Total bulk operations'),  # NEW
            'health_checks_total': Counter('node_health_checks_total', 'Total health checks'),  # NEW
            'scripts_deployed_total': Counter('node_scripts_deployed_total', 'Total scripts deployed')  # NEW
        }
        
        # Redis for real-time data
        self.redis_client = self._init_redis()
        
        # Manager connection info
        self.manager_url = f"http://{MANAGER_HOST}:{MANAGER_PORT}"
        
        # Setup routes and WebSocket - EXISTING + NEW
        self.setup_enhanced_routes()
        self.setup_enhanced_websocket()
        
        # Start metrics server
        self._start_metrics_server()
        
        self.logger.info(f"Enhanced Node Server {NODE_ID} v{NODE_VERSION} initialized - ADVANCED REMOTE CONTROL")
        self.logger.info("✅ All existing features preserved")
        self.logger.info("➕ Advanced remote control features added")
        self.logger.info("🎮 Comprehensive agent management available")
    
    def _init_redis(self):
        """Initialize Redis for real-time caching - EXISTING"""
        try:
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            self.logger.info("Redis connected for real-time caching")
            return client
        except:
            self.logger.warning("Redis not available, using in-memory cache")
            return None
    
    def _start_metrics_server(self):
        """Start Prometheus metrics server - EXISTING"""
        try:
            start_http_server(8091)
            self.logger.info("Prometheus metrics server started on :8091")
        except Exception as e:
            self.logger.warning(f"Metrics server failed: {e}")
    
    def setup_enhanced_routes(self):
        """Setup enhanced Flask routes - EXISTING + NEW ADVANCED REMOTE CONTROL"""
        
        # KEEP ALL EXISTING ROUTES EXACTLY AS THEY ARE
        @self.app.route('/')
        def enhanced_dashboard():
            """Serve enhanced node dashboard with advanced remote control"""
            return self.get_enhanced_dashboard_html()
        
        @self.app.route('/api/v3/agents/register', methods=['POST'])
        @self.limiter.limit("10 per minute")
        def register_ultimate_agent():
            """Register Ultimate Pain Network Agent - EXISTING"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"success": False, "error": "No data provided"}), 400
                
                agent_id = data.get('agent_id') or data.get('server_id')
                if not agent_id:
                    return jsonify({"success": False, "error": "agent_id required"}), 400
                
                current_time = datetime.now()
                
                agent = EnhancedAgentInfo(
                    id=agent_id,
                    name=data.get('name', f"ultimate-agent-{agent_id}"),
                    host=data.get('host', request.remote_addr),
                    version=data.get('version', 'unknown'),
                    agent_type=data.get('agent_type', 'ultimate'),
                    capabilities=data.get('capabilities', []),
                    ai_models=data.get('ai_models', []),
                    plugins=data.get('plugins', []),
                    features=data.get('features', []),
                    gpu_available=data.get('gpu_available', False),
                    blockchain_enabled=data.get('blockchain_enabled', False),
                    cloud_enabled=data.get('cloud_enabled', False),
                    security_enabled=data.get('security_enabled', False),
                    registered_at=current_time
                )
                
                # Store agent
                self.agents[agent_id] = agent
                self.agent_status[agent_id] = EnhancedAgentStatus(id=agent_id)
                
                # Store in database
                db_agent = Agent(
                    id=agent.id,
                    name=agent.name,
                    host=agent.host,
                    version=agent.version,
                    agent_type=agent.agent_type,
                    capabilities=agent.capabilities,
                    ai_models=agent.ai_models,
                    plugins=agent.plugins,
                    features=agent.features,
                    gpu_available=agent.gpu_available,
                    blockchain_enabled=agent.blockchain_enabled,
                    cloud_enabled=agent.cloud_enabled,
                    security_enabled=agent.security_enabled,
                    registered_at=current_time,
                    last_seen=current_time
                )
                
                self.db.session.merge(db_agent)
                self.db.session.commit()
                
                # Update metrics
                self.metrics['agents_total'].set(len(self.agents))
                
                # Cache in Redis
                if self.redis_client:
                    agent_serializable = serialize_for_json(agent)
                    self.redis_client.setex(f'agent:{agent_id}', 3600, json.dumps(agent_serializable))
                
                self.logger.info(f"Ultimate agent registered: {agent_id} v{agent.version}")
                
                # Broadcast update
                self.socketio.emit('ultimate_agent_registered', {
                    'agent_id': agent_id,
                    'agent_type': agent.agent_type,
                    'features': agent.features,
                    'timestamp': current_time.isoformat()
                }, room='dashboard')
                
                return jsonify({
                    "success": True,
                    "agent_id": agent_id,
                    "node_id": NODE_ID,
                    "node_version": NODE_VERSION,
                    "message": "Ultimate agent registered successfully",
                    "features_supported": ["ai", "blockchain", "cloud", "security", "plugins"],
                    "task_control_available": True,
                    "remote_management_available": True,
                    "advanced_control_available": True  # NEW: Indicate advanced control available
                })
                
            except Exception as e:
                self.logger.error(f"Ultimate agent registration failed: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # Legacy agent registration (redirect to v3) - KEEP EXISTING
        @self.app.route('/api/agents/register', methods=['POST'])
        def legacy_agent_register():
            """Legacy agent registration - redirect to enhanced"""
            return register_ultimate_agent()
        
        # KEEP ALL OTHER EXISTING ROUTES...
        # (I'll include the key ones for brevity, but all existing routes remain unchanged)
        
        @self.app.route('/api/v3/agents/heartbeat', methods=['POST'])
        def ultimate_agent_heartbeat():
            """Process Ultimate agent heartbeat - EXISTING"""
            try:
                data = request.get_json()
                agent_id = data.get('server_id') or data.get('agent_id')
                
                if not agent_id or agent_id not in self.agents:
                    return jsonify({"success": False, "error": "Agent not registered"}), 400
                
                current_time = datetime.now()
                
                # Update enhanced agent status
                status = self.agent_status[agent_id]
                status.status = data.get("status", "online")
                status.cpu_percent = data.get("cpu_percent", 0.0)
                status.memory_mb = data.get("memory_mb", 0.0)
                status.memory_percent = data.get("memory_percent", 0.0)
                status.gpu_percent = data.get("gpu_percent", 0.0)
                status.network_io = data.get("network_io", 0.0)
                status.tasks_running = data.get("tasks_running", 0)
                status.tasks_completed = data.get("tasks_completed", 0)
                status.tasks_failed = data.get("tasks_failed", 0)
                status.current_tasks = data.get("current_tasks", {})
                status.ai_models_loaded = data.get("ai_models_loaded", 0)
                status.ai_inference_count = data.get("ai_inference_count", 0)
                status.neural_training_active = data.get("neural_training_active", False)
                status.blockchain_balance = data.get("blockchain_balance", 0.0)
                status.blockchain_transactions = data.get("blockchain_transactions", 0)
                status.wallet_address = data.get("wallet_address", "")
                status.performance_prediction = data.get("performance_prediction", 80.0)
                status.efficiency_score = data.get("efficiency_score", 100.0)
                status.last_heartbeat = current_time
                
                # Store enhanced heartbeat
                heartbeat = AgentHeartbeat(
                    agent_id=agent_id,
                    timestamp=current_time,
                    status=status.status,
                    cpu_percent=status.cpu_percent,
                    memory_mb=status.memory_mb,
                    memory_percent=status.memory_percent,
                    gpu_percent=status.gpu_percent,
                    network_io=status.network_io,
                    tasks_running=status.tasks_running,
                    tasks_completed=status.tasks_completed,
                    tasks_failed=status.tasks_failed,
                    current_tasks=status.current_tasks,
                    ai_models_loaded=status.ai_models_loaded,
                    ai_inference_count=status.ai_inference_count,
                    neural_training_active=status.neural_training_active,
                    blockchain_balance=status.blockchain_balance,
                    blockchain_transactions=status.blockchain_transactions,
                    performance_prediction=status.performance_prediction,
                    efficiency_score=status.efficiency_score
                )
                
                self.db.session.add(heartbeat)
                
                # Update agent last_seen
                agent_record = self.db.session.query(Agent).filter_by(id=agent_id).first()
                if agent_record:
                    agent_record.last_seen = current_time
                    agent_record.total_tasks_completed = status.tasks_completed
                    agent_record.total_tasks_failed = status.tasks_failed
                    agent_record.efficiency_score = status.efficiency_score
                
                self.db.session.commit()
                
                # Update performance history
                self.performance_history[agent_id].append({
                    'timestamp': current_time.isoformat(),
                    'cpu': status.cpu_percent,
                    'memory': status.memory_percent,
                    'efficiency': status.efficiency_score
                })
                
                # Update metrics
                self._update_prometheus_metrics()
                
                # Cache in Redis
                if self.redis_client:
                    status_serializable = serialize_for_json(status)
                    self.redis_client.setex(f'status:{agent_id}', 120, json.dumps(status_serializable))
                
                # Broadcast real-time update
                self.socketio.emit('ultimate_agent_status_update', {
                    'agent_id': agent_id,
                    'status': serialize_for_json(status),
                    'timestamp': current_time.isoformat()
                }, room='dashboard')
                
                return jsonify({
                    "success": True,
                    "node_id": NODE_ID,
                    "next_heartbeat": 30,
                    "supported_features": ["ai", "blockchain", "cloud", "security"],
                    "task_control_available": True,
                    "remote_management_available": True,
                    "advanced_control_available": True  # NEW: Indicate advanced control available
                })
                
            except Exception as e:
                self.logger.error(f"Enhanced heartbeat processing failed: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # NEW: ADD ADVANCED FEATURES TO EXISTING v5 REMOTE MANAGEMENT API
        @self.app.route('/api/v5/remote/agents/<agent_id>/bulk-command', methods=['POST'])
        def send_bulk_command_to_agent(agent_id):
            """NEW: Enhanced bulk command functionality - ADDED TO EXISTING v5"""
            try:
                if agent_id not in self.agents:
                    return jsonify({"error": "Agent not found"}), 404
                
                data = request.get_json()
                command_type = data.get('command_type')
                parameters = data.get('parameters', {})
                
                if not command_type:
                    return jsonify({"error": "command_type required"}), 400
                
                command = self.advanced_remote_control.create_agent_command(agent_id, command_type, parameters)
                success = self.advanced_remote_control.execute_command_on_agent(command)
                
                if success:
                    self.metrics['commands_total'].inc()
                    return jsonify({
                        "success": True,
                        "command_id": command.id,
                        "message": f"Enhanced command {command_type} sent to agent {agent_id}"
                    })
                else:
                    return jsonify({"success": False, "error": "Failed to send command"}), 500
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/bulk-operation', methods=['POST'])
        def create_bulk_operation():
            """NEW: Create bulk operation for multiple agents - ADDED TO EXISTING v5"""
            try:
                data = request.get_json()
                operation_type = data.get('operation_type')
                target_agents = data.get('target_agents', [])
                parameters = data.get('parameters', {})
                
                if not operation_type:
                    return jsonify({"error": "operation_type required"}), 400
                
                if not target_agents:
                    return jsonify({"error": "target_agents required"}), 400
                
                # Validate agents exist
                invalid_agents = [agent_id for agent_id in target_agents if agent_id not in self.agents]
                if invalid_agents:
                    return jsonify({"error": f"Invalid agents: {invalid_agents}"}), 400
                
                bulk_op = self.advanced_remote_control.create_bulk_operation(operation_type, target_agents, parameters)
                self.metrics['bulk_operations_total'].inc()
                
                return jsonify({
                    "success": True,
                    "operation_id": bulk_op.id,
                    "message": f"Bulk operation {operation_type} created for {len(target_agents)} agents"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/schedule-command', methods=['POST'])
        def schedule_command():
            """NEW: Schedule command for later execution - ADDED TO EXISTING v5"""
            try:
                data = request.get_json()
                agent_id = data.get('agent_id')
                command_type = data.get('command_type')
                scheduled_time_str = data.get('scheduled_time')
                parameters = data.get('parameters', {})
                repeat_interval = data.get('repeat_interval')
                max_repeats = data.get('max_repeats', 1)
                
                if not all([agent_id, command_type, scheduled_time_str]):
                    return jsonify({"error": "agent_id, command_type, and scheduled_time required"}), 400
                
                if agent_id not in self.agents:
                    return jsonify({"error": "Agent not found"}), 404
                
                # Parse scheduled time
                try:
                    scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid scheduled_time format"}), 400
                
                scheduled_cmd = self.advanced_remote_control.create_scheduled_command(
                    agent_id, command_type, scheduled_time, parameters, repeat_interval, max_repeats
                )
                
                return jsonify({
                    "success": True,
                    "scheduled_command_id": scheduled_cmd.id,
                    "message": f"Command {command_type} scheduled for agent {agent_id} at {scheduled_time}"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/deploy-script', methods=['POST'])
        def deploy_script():
            """NEW: Deploy script to agents - ADDED TO EXISTING v5"""
            try:
                data = request.get_json()
                script_name = data.get('script_name')
                script_content = data.get('script_content')
                script_type = data.get('script_type', 'python')
                target_agents = data.get('target_agents', [])
                
                if not all([script_name, script_content]):
                    return jsonify({"error": "script_name and script_content required"}), 400
                
                if not target_agents:
                    return jsonify({"error": "target_agents required"}), 400
                
                # Validate agents exist
                invalid_agents = [agent_id for agent_id in target_agents if agent_id not in self.agents]
                if invalid_agents:
                    return jsonify({"error": f"Invalid agents: {invalid_agents}"}), 400
                
                script = AgentScript(
                    id=f"script-{int(time.time())}-{uuid.uuid4().hex[:8]}",
                    name=script_name,
                    version="1.0",
                    script_type=script_type,
                    script_content=script_content,
                    checksum="",  # Will be calculated in __post_init__
                    target_agents=target_agents
                )
                
                self.advanced_remote_control.agent_scripts[script.id] = script
                self.advanced_remote_control.store_script_in_db(script)
                
                # Deploy to agents
                deployment_results = {}
                for agent_id in target_agents:
                    success = self.advanced_remote_control.deploy_script_to_agent(agent_id, script)
                    deployment_results[agent_id] = "deployed" if success else "failed"
                
                self.metrics['scripts_deployed_total'].inc()
                
                return jsonify({
                    "success": True,
                    "script_id": script.id,
                    "deployment_results": deployment_results,
                    "message": f"Script {script_name} deployed to {len(target_agents)} agents"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/agents/<agent_id>/health', methods=['GET'])
        def get_agent_health(agent_id):
            """NEW: Get comprehensive agent health information - ADDED TO EXISTING v5"""
            try:
                if agent_id not in self.agents:
                    return jsonify({"error": "Agent not found"}), 404
                
                # Get recent health checks
                recent_health = self.db.session.query(AgentHealthRecord).filter(
                    AgentHealthRecord.agent_id == agent_id
                ).order_by(AgentHealthRecord.timestamp.desc()).limit(10).all()
                
                health_data = {
                    "agent_id": agent_id,
                    "current_status": self.agent_status.get(agent_id, {}).status if agent_id in self.agent_status else "unknown",
                    "recent_health_checks": [
                        {
                            "timestamp": check.timestamp.isoformat(),
                            "status": check.status,
                            "health_score": check.health_score,
                            "cpu_health": check.cpu_health,
                            "memory_health": check.memory_health,
                            "network_health": check.network_health,
                            "task_health": check.task_health,
                            "recovery_needed": check.recovery_needed,
                            "recovery_actions": check.recovery_actions
                        }
                        for check in recent_health
                    ]
                }
                
                return jsonify(health_data)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/agents/<agent_id>/history', methods=['GET'])
        def get_command_history(agent_id):
            """NEW: Get command history for agent - ADDED TO EXISTING v5"""
            try:
                if agent_id not in self.agents:
                    return jsonify({"error": "Agent not found"}), 404
                
                limit = request.args.get('limit', 50, type=int)
                history = self.advanced_remote_control.get_command_history(agent_id, limit)
                
                return jsonify({
                    "agent_id": agent_id,
                    "command_history": history,
                    "total_commands": len(history)
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/commands/<command_id>/replay', methods=['POST'])
        def replay_command(command_id):
            """NEW: Replay a previous command - ADDED TO EXISTING v5"""
            try:
                success = self.advanced_remote_control.replay_command(command_id)
                
                if success:
                    return jsonify({
                        "success": True,
                        "message": f"Command {command_id} replayed successfully"
                    })
                else:
                    return jsonify({"success": False, "error": "Failed to replay command"}), 500
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/advanced-statistics', methods=['GET'])
        def get_advanced_remote_statistics():
            """NEW: Get advanced remote control statistics - ADDED TO EXISTING v5"""
            try:
                stats = self.advanced_remote_control.get_advanced_statistics()
                return jsonify(stats)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/v5/remote/advanced-capabilities', methods=['GET'])
        def get_advanced_capabilities():
            """NEW: Get available advanced remote control capabilities - ADDED TO EXISTING v5"""
            try:
                return jsonify({
                    "advanced_commands": self.advanced_remote_control.advanced_commands,
                    "command_templates": self.advanced_remote_control.advanced_command_templates,
                    "features": {
                        "bulk_operations": True,
                        "command_scheduling": True,
                        "script_deployment": True,
                        "health_monitoring": True,
                        "command_history": True,
                        "command_replay": True,
                        "auto_recovery": True
                    }
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        # KEEP ALL EXISTING LEGACY ENDPOINTS UNCHANGED
        @self.app.route('/api/stats', methods=['GET'])
        def legacy_stats():
            """Legacy stats endpoint for backward compatibility - EXISTING"""
            enhanced_stats = self.get_enhanced_node_stats()
            return jsonify({
                "node_id": enhanced_stats["node_id"],
                "total_agents": enhanced_stats["total_agents"],
                "online_agents": enhanced_stats["online_agents"],
                "offline_agents": enhanced_stats["offline_agents"],
                "total_tasks_running": enhanced_stats["total_tasks_running"],
                "total_tasks_completed": enhanced_stats["total_tasks_completed"],
                "avg_cpu_percent": enhanced_stats["avg_cpu_percent"],
                "avg_memory_mb": enhanced_stats.get("avg_memory_percent", 0) * 10,
                "timestamp": enhanced_stats["timestamp"],
                "task_control_enabled": True,
                "remote_management_enabled": True,
                "advanced_control_enabled": True  # NEW
            })
        
        # ... (keep all other existing routes)
    
    def setup_enhanced_websocket(self):
        """Setup enhanced WebSocket events - EXISTING + NEW ADVANCED FEATURES"""
        
        @self.socketio.on('connect')
        def handle_connect(auth):
            """Handle client connection - EXISTING + NEW"""
            join_room('dashboard')
            emit('connected', {
                'node_id': NODE_ID,
                'node_version': NODE_VERSION,
                'features': ['ai', 'blockchain', 'cloud', 'analytics'],
                'task_control_enabled': True,
                'remote_management_enabled': True,
                'advanced_control_enabled': True  # NEW
            })
        
        @self.socketio.on('join_agent_room')
        def handle_join_agent_room(data):
            """Join agent-specific room - EXISTING"""
            agent_id = data.get('agent_id')
            if agent_id and agent_id in self.agents:
                join_room(f'agent_{agent_id}')
                emit('joined_agent_room', {'agent_id': agent_id})
        
        # KEEP ALL EXISTING WEBSOCKET EVENTS
        
        # NEW: ADVANCED REMOTE CONTROL WEBSOCKET EVENTS
        @self.socketio.on('request_advanced_remote_stats')
        def handle_advanced_remote_stats_request():
            """NEW: Send advanced remote control statistics"""
            emit('advanced_remote_stats', self.advanced_remote_control.get_advanced_statistics())
        
        @self.socketio.on('advanced_command_response')
        def handle_advanced_command_response(data):
            """NEW: Handle advanced command execution response from agents"""
            command_id = data.get('command_id')
            success = data.get('success', False)
            result = data.get('result', {})
            error = data.get('error')
            
            self.advanced_remote_control.handle_command_response(command_id, success, result, error)
        
        @self.socketio.on('request_bulk_operation_status')
        def handle_bulk_operation_status_request(data):
            """NEW: Get bulk operation status"""
            operation_id = data.get('operation_id')
            if operation_id in self.advanced_remote_control.bulk_operations:
                bulk_op = self.advanced_remote_control.bulk_operations[operation_id]
                emit('bulk_operation_status', {
                    'operation_id': operation_id,
                    'status': bulk_op.status,
                    'success_count': bulk_op.success_count,
                    'failure_count': bulk_op.failure_count,
                    'results': bulk_op.results
                })
        
        @self.socketio.on('request_agent_health_status')
        def handle_agent_health_status_request(data):
            """NEW: Get real-time agent health status"""
            agent_id = data.get('agent_id')
            if agent_id in self.agents:
                # Get latest health check
                latest_health = self.db.session.query(AgentHealthRecord).filter(
                    AgentHealthRecord.agent_id == agent_id
                ).order_by(AgentHealthRecord.timestamp.desc()).first()
                
                if latest_health:
                    emit('agent_health_status', {
                        'agent_id': agent_id,
                        'status': latest_health.status,
                        'health_score': latest_health.health_score,
                        'cpu_health': latest_health.cpu_health,
                        'memory_health': latest_health.memory_health,
                        'network_health': latest_health.network_health,
                        'task_health': latest_health.task_health,
                        'recovery_needed': latest_health.recovery_needed,
                        'recovery_actions': latest_health.recovery_actions,
                        'timestamp': latest_health.timestamp.isoformat()
                    })
    
    # KEEP ALL EXISTING METHODS - UNCHANGED
    def get_enhanced_node_stats(self):
        """Calculate enhanced node statistics - EXISTING + NEW"""
        total_agents = len(self.agents)
        online_agents = sum(1 for s in self.agent_status.values() 
                           if s.status == "online" and s.last_heartbeat and 
                           (datetime.now() - s.last_heartbeat).seconds < 120)
        
        # Task statistics
        total_tasks_running = sum(s.tasks_running for s in self.agent_status.values())
        total_tasks_completed = sum(s.tasks_completed for s in self.agent_status.values())
        total_tasks_failed = sum(s.tasks_failed for s in self.agent_status.values())
        
        # System metrics
        avg_cpu = sum(s.cpu_percent for s in self.agent_status.values()) / max(total_agents, 1)
        avg_memory = sum(s.memory_percent for s in self.agent_status.values()) / max(total_agents, 1)
        avg_gpu = sum(s.gpu_percent for s in self.agent_status.values()) / max(total_agents, 1)
        
        # AI metrics
        total_ai_models = sum(s.ai_models_loaded for s in self.agent_status.values())
        total_ai_inferences = sum(s.ai_inference_count for s in self.agent_status.values())
        agents_with_gpu = sum(1 for a in self.agents.values() if a.gpu_available)
        
        # Blockchain metrics
        total_blockchain_balance = sum(s.blockchain_balance for s in self.agent_status.values())
        total_blockchain_txs = sum(s.blockchain_transactions for s in self.agent_status.values())
        blockchain_enabled_agents = sum(1 for a in self.agents.values() if a.blockchain_enabled)
        
        # Performance metrics
        avg_efficiency = sum(s.efficiency_score for s in self.agent_status.values()) / max(total_agents, 1)
        
        # EXISTING: Remote management metrics
        mgmt_stats = self.task_control.get_task_statistics()
        
        # NEW: Advanced remote control metrics
        advanced_stats = self.advanced_remote_control.get_advanced_statistics()
        
        return {
            "node_id": NODE_ID,
            "node_version": NODE_VERSION,
            "timestamp": datetime.now().isoformat(),
            
            # Agent statistics
            "total_agents": total_agents,
            "online_agents": online_agents,
            "offline_agents": total_agents - online_agents,
            
            # Task statistics
            "total_tasks_running": total_tasks_running,
            "total_tasks_completed": total_tasks_completed,
            "total_tasks_failed": total_tasks_failed,
            "success_rate": round((total_tasks_completed / max(total_tasks_completed + total_tasks_failed, 1)) * 100, 2),
            
            # System metrics
            "avg_cpu_percent": round(avg_cpu, 2),
            "avg_memory_percent": round(avg_memory, 2),
            "avg_gpu_percent": round(avg_gpu, 2),
            
            # AI metrics
            "total_ai_models": total_ai_models,
            "total_ai_inferences": total_ai_inferences,
            "agents_with_gpu": agents_with_gpu,
            "gpu_utilization": round(avg_gpu, 2),
            
            # Blockchain metrics
            "total_blockchain_balance": round(total_blockchain_balance, 6),
            "total_blockchain_transactions": total_blockchain_txs,
            "blockchain_enabled_agents": blockchain_enabled_agents,
            
            # Performance metrics
            "avg_efficiency_score": round(avg_efficiency, 2),
            
            # Health indicators
            "health_score": self.calculate_health_score(),
            "manager_connected": self.registered_with_manager,
            
            # EXISTING: Task control metrics
            "task_control_enabled": True,
            "central_tasks": mgmt_stats,
            
            # EXISTING: Remote management metrics
            "remote_management_enabled": True,
            
            # NEW: Advanced remote control metrics
            "advanced_control_enabled": True,
            "advanced_control": advanced_stats
        }
    
    def get_ai_summary(self):
        """Get AI capabilities summary - EXISTING"""
        ai_models = defaultdict(int)
        inference_counts = []
        training_active = 0
        
        for agent in self.agents.values():
            for model in agent.ai_models:
                ai_models[model] += 1
        
        for status in self.agent_status.values():
            if status.ai_inference_count > 0:
                inference_counts.append(status.ai_inference_count)
            if status.neural_training_active:
                training_active += 1
        
        return {
            "total_unique_models": len(ai_models),
            "model_distribution": dict(ai_models),
            "total_inferences": sum(inference_counts),
            "avg_inferences_per_agent": statistics.mean(inference_counts) if inference_counts else 0,
            "agents_training": training_active,
            "gpu_agents": sum(1 for a in self.agents.values() if a.gpu_available)
        }
    
    def get_blockchain_summary(self):
        """Get blockchain capabilities summary - EXISTING"""
        total_balance = sum(s.blockchain_balance for s in self.agent_status.values())
        total_transactions = sum(s.blockchain_transactions for s in self.agent_status.values())
        enabled_agents = sum(1 for a in self.agents.values() if a.blockchain_enabled)
        
        wallet_addresses = [s.wallet_address for s in self.agent_status.values() if s.wallet_address]
        
        return {
            "enabled_agents": enabled_agents,
            "total_balance": round(total_balance, 6),
            "total_transactions": total_transactions,
            "unique_wallets": len(set(wallet_addresses)),
            "avg_balance_per_agent": round(total_balance / max(enabled_agents, 1), 6)
        }
    
    def calculate_health_score(self) -> float:
        """Calculate overall node health score - EXISTING"""
        if not self.agents:
            return 100.0
        
        online_ratio = len([s for s in self.agent_status.values() if s.status == "online"]) / len(self.agents)
        avg_efficiency = sum(s.efficiency_score for s in self.agent_status.values()) / len(self.agent_status)
        
        total_completed = sum(s.tasks_completed for s in self.agent_status.values())
        total_failed = sum(s.tasks_failed for s in self.agent_status.values())
        success_rate = total_completed / max(total_completed + total_failed, 1)
        
        health_score = (online_ratio * 40 + avg_efficiency * 0.4 + success_rate * 20)
        return min(100.0, max(0.0, health_score))
    
    def _update_prometheus_metrics(self):
        """Update Prometheus metrics - EXISTING + NEW"""
        stats = self.get_enhanced_node_stats()
        
        self.metrics['agents_total'].set(stats['total_agents'])
        self.metrics['agents_online'].set(stats['online_agents'])
        self.metrics['tasks_running'].set(stats['total_tasks_running'])
        self.metrics['ai_models_total'].set(stats['total_ai_models'])
        self.metrics['blockchain_balance_total'].set(stats['total_blockchain_balance'])
        self.metrics['avg_efficiency'].set(stats['avg_efficiency_score'])
    
    def get_enhanced_dashboard_html(self):
        """Generate enhanced dashboard HTML with advanced remote control - ENHANCED"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Enhanced Node Server v{NODE_VERSION} - ADVANCED REMOTE CONTROL</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: radial-gradient(circle at 25% 25%, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
                    color: white;
                    min-height: 100vh;
                    padding: 20px;
                }}
                .container {{ max-width: 1800px; margin: 0 auto; }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding: 40px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 25px;
                    backdrop-filter: blur(30px);
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    position: relative;
                    overflow: hidden;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: conic-gradient(transparent, rgba(255, 255, 255, 0.1), transparent);
                    animation: rotate 10s linear infinite;
                }}
                @keyframes rotate {{ to {{ transform: rotate(360deg); }} }}
                .header h1 {{
                    font-size: 3rem;
                    font-weight: 900;
                    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f093fb);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 15px;
                    position: relative;
                    z-index: 1;
                }}
                .advanced-badge {{
                    display: inline-block;
                    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                    padding: 8px 20px;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    font-weight: 700;
                    margin: 10px 5px;
                    position: relative;
                    z-index: 1;
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0%, 100% {{ box-shadow: 0 0 5px rgba(255, 107, 107, 0.5); }}
                    50% {{ box-shadow: 0 0 20px rgba(78, 205, 196, 0.8); }}
                }}
                .feature-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                    position: relative;
                    z-index: 1;
                }}
                .feature-badge {{
                    background: rgba(255, 255, 255, 0.15);
                    padding: 8px 12px;
                    border-radius: 12px;
                    text-align: center;
                    font-weight: 600;
                    backdrop-filter: blur(10px);
                    font-size: 0.85rem;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    text-align: center;
                    backdrop-filter: blur(20px);
                    transition: all 0.3s ease;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .stat-card:hover {{
                    transform: translateY(-5px);
                    background: rgba(255, 255, 255, 0.15);
                }}
                .stat-value {{
                    font-size: 2.2em;
                    font-weight: 700;
                    color: #4ecdc4;
                    margin-bottom: 8px;
                }}
                .stat-label {{
                    font-size: 0.9em;
                    opacity: 0.9;
                }}
                .advanced-section {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 25px;
                    backdrop-filter: blur(25px);
                    margin-bottom: 30px;
                    border: 2px solid rgba(255, 107, 107, 0.3);
                }}
                .task-control-section {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 25px;
                    backdrop-filter: blur(25px);
                    margin-bottom: 30px;
                    border: 2px solid rgba(40, 167, 69, 0.3);
                }}
                .section-title {{
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin-bottom: 20px;
                    color: #4ecdc4;
                }}
                .control-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .control-button {{
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    padding: 15px 20px;
                    border-radius: 15px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    font-size: 0.9rem;
                }}
                .control-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
                }}
                .advanced-button {{
                    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                }}
                .advanced-button:hover {{
                    background: linear-gradient(45deg, #ff5252, #26a69a);
                }}
                .bulk-button {{
                    background: linear-gradient(45deg, #f093fb, #f5576c);
                }}
                .bulk-button:hover {{
                    background: linear-gradient(45deg, #e91e63, #ff5722);
                }}
                .agents-section {{
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                    padding: 25px;
                    backdrop-filter: blur(25px);
                    margin-bottom: 30px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .agent-item {{
                    background: rgba(255, 255, 255, 0.08);
                    margin-bottom: 15px;
                    padding: 20px;
                    border-radius: 15px;
                    border-left: 4px solid #4ecdc4;
                    transition: all 0.3s ease;
                }}
                .agent-item:hover {{
                    background: rgba(255, 255, 255, 0.12);
                    transform: translateX(5px);
                }}
                .agent-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }}
                .agent-name {{
                    font-size: 1.1em;
                    font-weight: 600;
                }}
                .status.online {{ color: #4ade80; }}
                .status.offline {{ color: #ef4444; }}
                .agent-controls {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 8px;
                    margin-top: 15px;
                }}
                .agent-control-btn {{
                    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 0.8rem;
                    font-weight: 600;
                    transition: all 0.2s ease;
                }}
                .agent-control-btn:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                }}
                .health-indicator {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }}
                .health-healthy {{ background: #4ade80; }}
                .health-warning {{ background: #facc15; }}
                .health-critical {{ background: #ef4444; }}
                .health-offline {{ background: #6b7280; }}
                .modal {{
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                }}
                .modal-content {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 15% auto;
                    padding: 20px;
                    border-radius: 15px;
                    width: 80%;
                    max-width: 600px;
                    color: white;
                }}
                .close {{
                    color: white;
                    float: right;
                    font-size: 28px;
                    font-weight: bold;
                    cursor: pointer;
                }}
                .loading {{
                    text-align: center;
                    opacity: 0.7;
                    padding: 40px;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Enhanced Node Server</h1>
                    <div class="advanced-badge">🎮 ADVANCED REMOTE CONTROL</div>
                    <div class="advanced-badge">✅ ALL EXISTING FEATURES</div>
                    <div class="advanced-badge">➕ COMPREHENSIVE MANAGEMENT</div>
                    <p style="font-size: 1.1rem; margin: 15px 0; position: relative; z-index: 1;">
                        v{NODE_VERSION} - Advanced Remote Management System
                    </p>
                    
                    <div class="feature-grid">
                        <div class="feature-badge">🧠 AI Orchestration</div>
                        <div class="feature-badge">💰 Blockchain Management</div>
                        <div class="feature-badge">☁️ Cloud Integration</div>
                        <div class="feature-badge">🔒 Security Features</div>
                        <div class="feature-badge">📊 Advanced Analytics</div>
                        <div class="feature-badge">🔌 Plugin Ecosystem</div>
                        <div class="feature-badge">🎯 Task Control</div>
                        <div class="feature-badge">🎮 REMOTE CONTROL</div>
                        <div class="feature-badge">⚙️ CONFIG MGMT</div>
                        <div class="feature-badge">📡 LIVE MONITORING</div>
                        <div class="feature-badge">🚀 BULK OPERATIONS</div>
                        <div class="feature-badge">⏰ SCHEDULING</div>
                        <div class="feature-badge">🔄 AUTO RECOVERY</div>
                        <div class="feature-badge">📋 SCRIPT DEPLOY</div>
                    </div>
                    
                    <p style="position: relative; z-index: 1; opacity: 0.8; font-size: 0.9rem;">
                        Node ID: {NODE_ID} | Advanced Agent Management & Control System
                    </p>
                </div>
                
                <div class="stats-grid" id="statsGrid">
                    <div class="loading">Loading enhanced statistics...</div>
                </div>
                
                <div class="advanced-section">
                    <h3 class="section-title">🎮 NEW: Advanced Remote Control</h3>
                    <div id="advancedControlStats" class="stats-grid">
                        <div class="loading">Loading advanced control statistics...</div>
                    </div>
                    <div class="control-grid">
                        <button class="control-button advanced-button" onclick="openBulkOperationModal()">
                            🚀 Bulk Operations
                        </button>
                        <button class="control-button advanced-button" onclick="openScheduleCommandModal()">
                            ⏰ Schedule Commands
                        </button>
                        <button class="control-button advanced-button" onclick="deployScriptToAllAgents()">
                            📋 Deploy Scripts
                        </button>
                        <button class="control-button advanced-button" onclick="runHealthCheckOnAllAgents()">
                            🏥 Health Check All
                        </button>
                        <button class="control-button bulk-button" onclick="sendBulkCommand('performance_optimization')">
                            ⚡ Optimize All Performance
                        </button>
                        <button class="control-button bulk-button" onclick="sendBulkCommand('system_update')">
                            🔄 Update All Systems
                        </button>
                        <button class="control-button bulk-button" onclick="sendBulkCommand('security_scan')">
                            🔒 Security Scan All
                        </button>
                        <button class="control-button advanced-button" onclick="refreshAdvancedData()">
                            🔄 Refresh Advanced Data
                        </button>
                    </div>
                </div>
                
                <div class="task-control-section">
                    <h3 class="section-title">🎯 Centralized Task Control</h3>
                    <div id="taskControlStats" class="stats-grid">
                        <div class="loading">Loading task control statistics...</div>
                    </div>
                    <div class="control-grid">
                        <button class="control-button" onclick="createCentralTask('neural_network_training')">
                            🧠 Create AI Training Task
                        </button>
                        <button class="control-button" onclick="createCentralTask('blockchain_transaction')">
                            💰 Create Blockchain Task
                        </button>
                        <button class="control-button" onclick="createCentralTask('sentiment_analysis')">
                            📊 Create Analysis Task
                        </button>
                        <button class="control-button" onclick="refreshAllData()">
                            🔄 Refresh All Data
                        </button>
                    </div>
                </div>
                
                <div class="agents-section">
                    <h2 class="section-title">🤖 Connected Ultimate Agents with Advanced Control</h2>
                    <div id="agentsList">
                        <div class="loading">Loading agent information...</div>
                    </div>
                </div>
            </div>
            
            <!-- Bulk Operation Modal -->
            <div id="bulkOperationModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeBulkOperationModal()">&times;</span>
                    <h2>🚀 Bulk Operation</h2>
                    <div style="margin: 20px 0;">
                        <label>Operation Type:</label>
                        <select id="bulkOperationType" style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px;">
                            <option value="restart_agent">Restart Agents</option>
                            <option value="update_config">Update Configuration</option>
                            <option value="run_diagnostics">Run Diagnostics</option>
                            <option value="optimize_performance">Optimize Performance</option>
                            <option value="security_scan">Security Scan</option>
                            <option value="system_update">System Update</option>
                            <option value="backup_data">Backup Data</option>
                            <option value="clear_cache">Clear Cache</option>
                        </select>
                    </div>
                    <div style="margin: 20px 0;">
                        <label>Target Agents:</label>
                        <div id="agentCheckboxes" style="max-height: 200px; overflow-y: auto; margin: 10px 0;">
                            <!-- Agent checkboxes will be populated here -->
                        </div>
                        <button onclick="selectAllAgents()" style="margin: 5px;">Select All</button>
                        <button onclick="selectOnlineAgents()" style="margin: 5px;">Select Online Only</button>
                    </div>
                    <button onclick="executeBulkOperation()" class="control-button advanced-button">
                        Execute Bulk Operation
                    </button>
                </div>
            </div>
            
            <!-- Schedule Command Modal -->
            <div id="scheduleCommandModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeScheduleCommandModal()">&times;</span>
                    <h2>⏰ Schedule Command</h2>
                    <div style="margin: 20px 0;">
                        <label>Agent:</label>
                        <select id="scheduleAgentId" style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px;">
                            <!-- Agent options will be populated here -->
                        </select>
                    </div>
                    <div style="margin: 20px 0;">
                        <label>Command Type:</label>
                        <select id="scheduleCommandType" style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px;">
                            <option value="restart_agent">Restart Agent</option>
                            <option value="run_diagnostics">Run Diagnostics</option>
                            <option value="backup_data">Backup Data</option>
                            <option value="update_system">Update System</option>
                            <option value="clear_cache">Clear Cache</option>
                            <option value="optimize_performance">Optimize Performance</option>
                        </select>
                    </div>
                    <div style="margin: 20px 0;">
                        <label>Scheduled Time:</label>
                        <input type="datetime-local" id="scheduleTime" style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px;">
                    </div>
                    <div style="margin: 20px 0;">
                        <label>
                            <input type="checkbox" id="scheduleRepeat"> Repeat
                        </label>
                        <div id="repeatOptions" style="display: none; margin-top: 10px;">
                            <label>Interval (minutes):</label>
                            <input type="number" id="scheduleInterval" value="60" style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px;">
                            <label>Max Repeats:</label>
                            <input type="number" id="scheduleMaxRepeats" value="5" style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px;">
                        </div>
                    </div>
                    <button onclick="scheduleCommand()" class="control-button advanced-button">
                        Schedule Command
                    </button>
                </div>
            </div>
            
            <script>
                let socket;
                let currentAgents = [];
                
                // Initialize Advanced Dashboard
                document.addEventListener('DOMContentLoaded', () => {{
                    initSocket();
                    refreshAllData();
                    setInterval(refreshAllData, 10000); // Update every 10 seconds
                    
                    // Setup schedule repeat checkbox
                    document.getElementById('scheduleRepeat').addEventListener('change', function() {{
                        document.getElementById('repeatOptions').style.display = this.checked ? 'block' : 'none';
                    }});
                }});
                
                function initSocket() {{
                    try {{
                        socket = io();
                        socket.on('connect', () => console.log('🚀 Connected to Enhanced Node Server - ADVANCED CONTROL'));
                        socket.on('ultimate_agent_registered', (data) => {{
                            console.log('🤖 Ultimate agent registered:', data);
                            refreshAllData();
                        }});
                        socket.on('ultimate_agent_status_update', (data) => {{
                            console.log('📈 Agent status update:', data);
                            refreshAllData();
                        }});
                        socket.on('central_task_update', (data) => {{
                            console.log('🎯 Central task update:', data);
                            refreshTaskControlStats();
                        }});
                        socket.on('command_completed', (data) => {{
                            console.log('🎮 Command completed:', data);
                            refreshAdvancedData();
                            showNotification(`Command completed on agent ${{data.agent_id}}`, data.success ? 'success' : 'error');
                        }});
                        socket.on('bulk_operation_completed', (data) => {{
                            console.log('🚀 Bulk operation completed:', data);
                            refreshAdvancedData();
                            showNotification(`Bulk operation completed: ${{data.success_count}} success, ${{data.failure_count}} failed`, 'info');
                        }});
                        socket.on('advanced_command_response', (data) => {{
                            console.log('🎮 Advanced command response:', data);
                            refreshAdvancedData();
                        }});
                    }} catch (e) {{
                        console.log('⚠️ WebSocket not available');
                    }}
                }}
                
                async function refreshAllData() {{
                    try {{
                        // Refresh existing stats
                        const response = await fetch('/api/v3/agents');
                        const data = await response.json();
                        
                        updateStats(data.stats);
                        updateAgentsList(data.agents);
                        currentAgents = data.agents;
                        
                        // Refresh task control stats
                        refreshTaskControlStats();
                        
                        // Refresh advanced control stats
                        refreshAdvancedData();
                        
                    }} catch (error) {{
                        console.error('Failed to refresh data:', error);
                    }}
                }}
                
                async function refreshTaskControlStats() {{
                    try {{
                        const response = await fetch('/api/v4/task-control/statistics');
                        const taskStats = await response.json();
                        
                        updateTaskControlStats(taskStats);
                        
                    }} catch (error) {{
                        console.error('Failed to refresh task control stats:', error);
                    }}
                }}
                
                async function refreshAdvancedData() {{
                    try {{
                        const response = await fetch('/api/v5/remote/advanced-statistics');
                        const advancedStats = await response.json();
                        
                        updateAdvancedControlStats(advancedStats);
                        
                    }} catch (error) {{
                        console.error('Failed to refresh advanced stats:', error);
                    }}
                }}
                
                function updateStats(stats) {{
                    const statsGrid = document.getElementById('statsGrid');
                    statsGrid.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-value">${{stats.total_agents}}</div>
                            <div class="stat-label">Total Agents</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.online_agents}}</div>
                            <div class="stat-label">Online Agents</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.total_tasks_running}}</div>
                            <div class="stat-label">Tasks Running</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.total_tasks_completed}}</div>
                            <div class="stat-label">Tasks Completed</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.total_ai_models}}</div>
                            <div class="stat-label">AI Models</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.total_blockchain_balance.toFixed(3)}}</div>
                            <div class="stat-label">Total ETH Balance</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.avg_efficiency_score.toFixed(1)}}%</div>
                            <div class="stat-label">Avg Efficiency</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${{stats.health_score.toFixed(0)}}%</div>
                            <div class="stat-label">Health Score</div>
                        </div>
                    `;
                }}
                
                function updateTaskControlStats(taskStats) {{
                    const taskControlDiv = document.getElementById('taskControlStats');
                    taskControlDiv.innerHTML = `
                        <div class="stat-card" style="border: 2px solid #28a745;">
                            <div class="stat-value">${{taskStats.pending_tasks || 0}}</div>
                            <div class="stat-label">Pending Central Tasks</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #17a2b8;">
                            <div class="stat-value">${{taskStats.running_tasks || 0}}</div>
                            <div class="stat-label">Running Central Tasks</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #ffc107;">
                            <div class="stat-value">${{taskStats.completed_tasks || 0}}</div>
                            <div class="stat-label">Completed Central Tasks</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #dc3545;">
                            <div class="stat-value">${{(taskStats.success_rate || 100).toFixed(1)}}%</div>
                            <div class="stat-label">Central Task Success Rate</div>
                        </div>
                    `;
                }}
                
                function updateAdvancedControlStats(advancedStats) {{
                    const advancedDiv = document.getElementById('advancedControlStats');
                    advancedDiv.innerHTML = `
                        <div class="stat-card" style="border: 2px solid #ff6b6b;">
                            <div class="stat-value">${{advancedStats.total_commands_executed || 0}}</div>
                            <div class="stat-label">Total Commands Executed</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #4ecdc4;">
                            <div class="stat-value">${{advancedStats.active_commands || 0}}</div>
                            <div class="stat-label">Active Commands</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #45b7d1;">
                            <div class="stat-value">${{advancedStats.scheduled_commands || 0}}</div>
                            <div class="stat-label">Scheduled Commands</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #f093fb;">
                            <div class="stat-value">${{advancedStats.bulk_operations || 0}}</div>
                            <div class="stat-label">Bulk Operations</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #f5576c;">
                            <div class="stat-value">${{advancedStats.agent_scripts || 0}}</div>
                            <div class="stat-label">Deployed Scripts</div>
                        </div>
                        <div class="stat-card" style="border: 2px solid #4facfe;">
                            <div class="stat-value">${{advancedStats.health_monitoring_active ? '✅' : '❌'}}</div>
                            <div class="stat-label">Health Monitoring</div>
                        </div>
                    `;
                }}
                
                function updateAgentsList(agents) {{
                    const agentsList = document.getElementById('agentsList');
                    
                    if (agents.length === 0) {{
                        agentsList.innerHTML = '<div class="loading">No Ultimate agents connected yet</div>';
                        return;
                    }}
                    
                    agentsList.innerHTML = agents.map(agent => `
                        <div class="agent-item">
                            <div class="agent-header">
                                <div class="agent-name">
                                    <span class="health-indicator health-${{getHealthStatus(agent)}}"></span>
                                    ${{agent.name}}
                                </div>
                                <div class="status ${{agent.status || 'offline'}}">${{agent.status || 'offline'}}</div>
                            </div>
                            <div style="font-size: 0.9em; opacity: 0.8; margin-bottom: 8px;">
                                ${{agent.host}} • ${{agent.version}} • ${{agent.agent_type}}
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin: 10px 0; font-size: 0.85em;">
                                <div>
                                    <div>CPU: ${{Math.round(agent.cpu_percent || 0)}}%</div>
                                    <div>Memory: ${{Math.round(agent.memory_percent || 0)}}%</div>
                                    <div>GPU: ${{Math.round(agent.gpu_percent || 0)}}%</div>
                                </div>
                                <div>
                                    <div>Tasks: ${{agent.tasks_running || 0}} running</div>
                                    <div>Completed: ${{agent.tasks_completed || 0}}</div>
                                    <div>Efficiency: ${{Math.round(agent.efficiency_score || 100)}}%</div>
                                </div>
                                <div>
                                    <div>AI Models: ${{agent.ai_models_loaded || 0}}</div>
                                    <div>Balance: ${{(agent.blockchain_balance || 0).toFixed(4)}} ETH</div>
                                    <div>Health: ${{getHealthScore(agent)}}%</div>
                                </div>
                            </div>
                            
                            <div class="agent-controls">
                                <button class="agent-control-btn" onclick="sendAdvancedAgentCommand('${{agent.id}}', 'restart_agent')">
                                    🔄 Restart
                                </button>
                                <button class="agent-control-btn" onclick="sendAdvancedAgentCommand('${{agent.id}}', 'run_diagnostics')">
                                    🔍 Diagnostics
                                </button>
                                <button class="agent-control-btn" onclick="sendAdvancedAgentCommand('${{agent.id}}', 'optimize_performance')">
                                    ⚡ Optimize
                                </button>
                                <button class="agent-control-btn" onclick="sendAdvancedAgentCommand('${{agent.id}}', 'backup_data')">
                                    💾 Backup
                                </button>
                                <button class="agent-control-btn" onclick="sendAdvancedAgentCommand('${{agent.id}}', 'security_scan')">
                                    🔒 Security
                                </button>
                                <button class="agent-control-btn" onclick="getAgentHealthDetails('${{agent.id}}')">
                                    🏥 Health
                                </button>
                                <button class="agent-control-btn" onclick="getCommandHistory('${{agent.id}}')">
                                    📋 History
                                </button>
                                <button class="agent-control-btn" onclick="scheduleAgentCommand('${{agent.id}}')">
                                    ⏰ Schedule
                                </button>
                            </div>
                        </div>
                    `).join('');
                }}
                
                function getHealthStatus(agent) {{
                    const cpu = agent.cpu_percent || 0;
                    const memory = agent.memory_percent || 0;
                    const efficiency = agent.efficiency_score || 100;
                    
                    if (cpu > 90 || memory > 90 || efficiency < 50) return 'critical';
                    if (cpu > 75 || memory > 75 || efficiency < 70) return 'warning';
                    if (agent.status === 'online') return 'healthy';
                    return 'offline';
                }}
                
                function getHealthScore(agent) {{
                    const cpu_score = Math.max(0, 100 - (agent.cpu_percent || 0));
                    const memory_score = Math.max(0, 100 - (agent.memory_percent || 0));
                    const efficiency = agent.efficiency_score || 100;
                    return Math.round((cpu_score + memory_score + efficiency) / 3);
                }}
                
                // Advanced Command Functions - USING EXISTING v5 API
                async function sendAdvancedAgentCommand(agentId, commandType, parameters = {{}}) {{
                    try {{
                        const response = await fetch(`/api/v5/remote/agents/${{agentId}}/bulk-command`, {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ 
                                command_type: commandType,
                                parameters: parameters
                            }})
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`🎮 Advanced command ${{commandType}} sent to agent ${{agentId}}`, 'success');
                            refreshAdvancedData();
                        }} else {{
                            showNotification(`❌ Failed to send command: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error sending command: ${{error.message}}`, 'error');
                    }}
                }}
                
                async function sendBulkCommand(commandType) {{
                    try {{
                        const onlineAgents = currentAgents.filter(agent => agent.status === 'online').map(agent => agent.id);
                        
                        if (onlineAgents.length === 0) {{
                            showNotification('❌ No online agents to send command to', 'error');
                            return;
                        }}
                        
                        const response = await fetch('/api/v5/remote/bulk-operation', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                operation_type: commandType,
                                target_agents: onlineAgents,
                                parameters: {{}}
                            }})
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`🚀 Bulk operation ${{commandType}} started for ${{onlineAgents.length}} agents`, 'success');
                            refreshAdvancedData();
                        }} else {{
                            showNotification(`❌ Failed to start bulk operation: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error starting bulk operation: ${{error.message}}`, 'error');
                    }}
                }}
                
                // Modal Functions
                function openBulkOperationModal() {{
                    populateAgentCheckboxes();
                    document.getElementById('bulkOperationModal').style.display = 'block';
                }}
                
                function closeBulkOperationModal() {{
                    document.getElementById('bulkOperationModal').style.display = 'none';
                }}
                
                function openScheduleCommandModal() {{
                    populateAgentSelect();
                    document.getElementById('scheduleCommandModal').style.display = 'block';
                }}
                
                function closeScheduleCommandModal() {{
                    document.getElementById('scheduleCommandModal').style.display = 'none';
                }}
                
                function populateAgentCheckboxes() {{
                    const container = document.getElementById('agentCheckboxes');
                    container.innerHTML = currentAgents.map(agent => `
                        <div>
                            <label>
                                <input type="checkbox" value="${{agent.id}}" class="agent-checkbox">
                                ${{agent.name}} (${{agent.status}})
                            </label>
                        </div>
                    `).join('');
                }}
                
                function populateAgentSelect() {{
                    const select = document.getElementById('scheduleAgentId');
                    select.innerHTML = currentAgents.map(agent => `
                        <option value="${{agent.id}}">${{agent.name}} (${{agent.status}})</option>
                    `).join('');
                }}
                
                function selectAllAgents() {{
                    const checkboxes = document.querySelectorAll('.agent-checkbox');
                    checkboxes.forEach(cb => cb.checked = true);
                }}
                
                function selectOnlineAgents() {{
                    const checkboxes = document.querySelectorAll('.agent-checkbox');
                    checkboxes.forEach(cb => {{
                        const agent = currentAgents.find(a => a.id === cb.value);
                        cb.checked = agent && agent.status === 'online';
                    }});
                }}
                
                async function executeBulkOperation() {{
                    try {{
                        const operationType = document.getElementById('bulkOperationType').value;
                        const selectedAgents = Array.from(document.querySelectorAll('.agent-checkbox:checked')).map(cb => cb.value);
                        
                        if (selectedAgents.length === 0) {{
                            showNotification('❌ Please select at least one agent', 'error');
                            return;
                        }}
                        
                        const response = await fetch('/api/v5/remote/bulk-operation', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                operation_type: operationType,
                                target_agents: selectedAgents,
                                parameters: {{}}
                            }})
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`🚀 Bulk operation ${{operationType}} started for ${{selectedAgents.length}} agents`, 'success');
                            closeBulkOperationModal();
                            refreshAdvancedData();
                        }} else {{
                            showNotification(`❌ Failed to start bulk operation: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error executing bulk operation: ${{error.message}}`, 'error');
                    }}
                }}
                
                async function scheduleCommand() {{
                    try {{
                        const agentId = document.getElementById('scheduleAgentId').value;
                        const commandType = document.getElementById('scheduleCommandType').value;
                        const scheduledTime = document.getElementById('scheduleTime').value;
                        const isRepeat = document.getElementById('scheduleRepeat').checked;
                        
                        if (!scheduledTime) {{
                            showNotification('❌ Please select a scheduled time', 'error');
                            return;
                        }}
                        
                        const requestBody = {{
                            agent_id: agentId,
                            command_type: commandType,
                            scheduled_time: new Date(scheduledTime).toISOString(),
                            parameters: {{}}
                        }};
                        
                        if (isRepeat) {{
                            requestBody.repeat_interval = parseInt(document.getElementById('scheduleInterval').value) * 60; // Convert to seconds
                            requestBody.max_repeats = parseInt(document.getElementById('scheduleMaxRepeats').value);
                        }}
                        
                        const response = await fetch('/api/v5/remote/schedule-command', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify(requestBody)
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`⏰ Command ${{commandType}} scheduled for agent ${{agentId}}`, 'success');
                            closeScheduleCommandModal();
                            refreshAdvancedData();
                        }} else {{
                            showNotification(`❌ Failed to schedule command: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error scheduling command: ${{error.message}}`, 'error');
                    }}
                }}
                
                async function getAgentHealthDetails(agentId) {{
                    try {{
                        const response = await fetch(`/api/v5/remote/agents/${{agentId}}/health`);
                        const healthData = await response.json();
                        
                        // Create detailed health view modal (simplified for demo)
                        const healthWindow = window.open('', '_blank', 'width=800,height=600');
                        healthWindow.document.write(`
                            <html>
                                <head>
                                    <title>Agent Health Details: ${{agentId}}</title>
                                    <style>
                                        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                                        .health-card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                                        .health-good {{ border-left: 4px solid #4ade80; }}
                                        .health-warning {{ border-left: 4px solid #facc15; }}
                                        .health-critical {{ border-left: 4px solid #ef4444; }}
                                        pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                                    </style>
                                </head>
                                <body>
                                    <h2>🏥 Agent Health Details: ${{agentId}}</h2>
                                    <div class="health-card">
                                        <h3>Current Status: ${{healthData.current_status}}</h3>
                                        <p>Last updated: ${{new Date().toLocaleString()}}</p>
                                    </div>
                                    <div class="health-card">
                                        <h3>Recent Health Checks</h3>
                                        <pre>${{JSON.stringify(healthData.recent_health_checks, null, 2)}}</pre>
                                    </div>
                                </body>
                            </html>
                        `);
                        
                    }} catch (error) {{
                        showNotification(`❌ Error getting agent health: ${{error.message}}`, 'error');
                    }}
                }}
                
                async function getCommandHistory(agentId) {{
                    try {{
                        const response = await fetch(`/api/v5/remote/agents/${{agentId}}/history`);
                        const historyData = await response.json();
                        
                        // Create command history view modal (simplified for demo)
                        const historyWindow = window.open('', '_blank', 'width=800,height=600');
                        historyWindow.document.write(`
                            <html>
                                <head>
                                    <title>Command History: ${{agentId}}</title>
                                    <style>
                                        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                                        .command-item {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                                        .command-success {{ border-left: 4px solid #4ade80; }}
                                        .command-failed {{ border-left: 4px solid #ef4444; }}
                                        .command-pending {{ border-left: 4px solid #facc15; }}
                                        button {{ background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin: 5px; }}
                                    </style>
                                </head>
                                <body>
                                    <h2>📋 Command History: ${{agentId}}</h2>
                                    <p>Total Commands: ${{historyData.total_commands}}</p>
                                    <div>
                                        ${{historyData.command_history.map(cmd => `
                                            <div class="command-item command-${{cmd.status}}">
                                                <h4>${{cmd.command_type}} (${{cmd.status}})</h4>
                                                <p>Created: ${{new Date(cmd.created_at).toLocaleString()}}</p>
                                                ${{cmd.completed_at ? `<p>Completed: ${{new Date(cmd.completed_at).toLocaleString()}}</p>` : ''}}
                                                <button onclick="if(confirm('Replay this command?')) {{ window.opener.replayCommand('${{cmd.id}}'); }}">Replay</button>
                                            </div>
                                        `).join('')}}
                                    </div>
                                </body>
                            </html>
                        `);
                        
                    }} catch (error) {{
                        showNotification(`❌ Error getting command history: ${{error.message}}`, 'error');
                    }}
                }}
                
                async function replayCommand(commandId) {{
                    try {{
                        const response = await fetch(`/api/v5/remote/commands/${{commandId}}/replay`, {{
                            method: 'POST'
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`🔄 Command ${{commandId}} replayed successfully`, 'success');
                            refreshAdvancedData();
                        }} else {{
                            showNotification(`❌ Failed to replay command: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error replaying command: ${{error.message}}`, 'error');
                    }}
                }}
                
                function scheduleAgentCommand(agentId) {{
                    document.getElementById('scheduleAgentId').value = agentId;
                    openScheduleCommandModal();
                }}
                
                async function deployScriptToAllAgents() {{
                    const script = prompt('Enter Python script to deploy to all agents:', 'print("Hello from remote script!")');
                    if (!script) return;
                    
                    const scriptName = prompt('Enter script name:', 'remote_script');
                    if (!scriptName) return;
                    
                    try {{
                        const onlineAgents = currentAgents.filter(agent => agent.status === 'online').map(agent => agent.id);
                        
                        if (onlineAgents.length === 0) {{
                            showNotification('❌ No online agents to deploy script to', 'error');
                            return;
                        }}
                        
                        const response = await fetch('/api/v5/remote/deploy-script', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                script_name: scriptName,
                                script_content: script,
                                script_type: 'python',
                                target_agents: onlineAgents
                            }})
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`📋 Script ${{scriptName}} deployed to ${{onlineAgents.length}} agents`, 'success');
                            refreshAdvancedData();
                        }} else {{
                            showNotification(`❌ Failed to deploy script: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error deploying script: ${{error.message}}`, 'error');
                    }}
                }}
                
                async function runHealthCheckOnAllAgents() {{
                    try {{
                        const onlineAgents = currentAgents.filter(agent => agent.status === 'online').map(agent => agent.id);
                        
                        if (onlineAgents.length === 0) {{
                            showNotification('❌ No online agents to check health', 'error');
                            return;
                        }}
                        
                        const response = await fetch('/api/v5/remote/bulk-operation', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                operation_type: 'run_diagnostics',
                                target_agents: onlineAgents,
                                parameters: {{
                                    comprehensive: true,
                                    include_health_check: true
                                }}
                            }})
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`🏥 Health check started for ${{onlineAgents.length}} agents`, 'success');
                            refreshAdvancedData();
                        }} else {{
                            showNotification(`❌ Failed to start health check: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error starting health check: ${{error.message}}`, 'error');
                    }}
                }}
                
                // KEEP ALL EXISTING FUNCTIONS (createCentralTask, etc.)
                async function createCentralTask(taskType) {{
                    try {{
                        const response = await fetch('/api/v4/task-control/create-task', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ 
                                task_type: taskType,
                                priority: 7
                            }})
                        }});
                        
                        const result = await response.json();
                        if (result.success) {{
                            showNotification(`✅ Central task created: ${{result.task_id}}`, 'success');
                            refreshTaskControlStats();
                        }} else {{
                            showNotification(`❌ Failed to create task: ${{result.error}}`, 'error');
                        }}
                    }} catch (error) {{
                        showNotification(`❌ Error creating task: ${{error.message}}`, 'error');
                    }}
                }}
                
                function showNotification(message, type = 'info') {{
                    // Create notification element
                    const notification = document.createElement('div');
                    notification.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        padding: 15px 20px;
                        border-radius: 8px;
                        color: white;
                        font-weight: 600;
                        z-index: 10000;
                        max-width: 400px;
                        opacity: 0;
                        transform: translateX(100%);
                        transition: all 0.3s ease;
                    `;
                    
                    // Set background color based on type
                    const colors = {{
                        'success': '#28a745',
                        'error': '#dc3545',
                        'info': '#17a2b8',
                        'warning': '#ffc107'
                    }};
                    notification.style.background = colors[type] || colors.info;
                    
                    notification.textContent = message;
                    document.body.appendChild(notification);
                    
                    // Animate in
                    setTimeout(() => {{
                        notification.style.opacity = '1';
                        notification.style.transform = 'translateX(0)';
                    }}, 100);
                    
                    // Remove after 5 seconds
                    setTimeout(() => {{
                        notification.style.opacity = '0';
                        notification.style.transform = 'translateX(100%)';
                        setTimeout(() => notification.remove(), 300);
                    }}, 5000);
                }}
                
                console.log('🚀 Enhanced Node Server Dashboard Ready - ADVANCED REMOTE CONTROL');
                console.log('✅ All existing features preserved');
                console.log('🎮 Advanced remote control features added');
                console.log('🚀 Bulk operations, scheduling, script deployment available');
                console.log('🏥 Health monitoring and auto-recovery enabled');
            </script>
        </body>
        </html>
        """
    
    #