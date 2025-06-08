import time
import threading
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any

<<<<<<< HEAD
from models.commands import AgentCommand, AgentConfiguration
from models.scripts import ScheduledCommand, BulkOperation, AgentHealthCheck, AgentScript
from models.agents import EnhancedAgentStatus
from core.database import (
    AgentCommandRecord, ScheduledCommandRecord, BulkOperationRecord,
    AgentHealthRecord, AgentScriptRecord
)
from utils.serialization import serialize_for_json
from utils.logger import get_remote_logger
=======
from ..models.commands import AgentCommand, AgentConfiguration
from ..models.scripts import ScheduledCommand, BulkOperation, AgentHealthCheck, AgentScript
from ..models.agents import EnhancedAgentStatus
from ..core.database import (
    AgentCommandRecord, ScheduledCommandRecord, BulkOperationRecord,
    AgentHealthRecord, AgentScriptRecord
)
from ..utils.serialization import serialize_for_json
from ..utils.logger import get_remote_logger
>>>>>>> 1eee087fad254c0d8449abb55113bbe3bc442923


class AdvancedRemoteControlManager:
    """Advanced remote control capabilities"""
    
    def __init__(self, node_server):
        self.node_server = node_server
        self.logger = get_remote_logger()
        
        # EXISTING features
        self.active_commands = {}
        self.agent_configurations = {}
        self.command_queue = defaultdict(deque)
        
        # NEW: Advanced features
        self.scheduled_commands = {}
        self.bulk_operations = {}
        self.agent_health_monitors = {}
        self.agent_scripts = {}
        self.command_history = defaultdict(list)
        
        # NEW: Service control
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
        self.logger.info("Advanced remote control services started")
    
    def start_command_scheduler(self):
        """Start command scheduler service"""
        def scheduler_loop():
            self.scheduler_running = True
            while self.scheduler_running:
                try:
                    self.process_scheduled_commands()
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    self.logger.error(f"Command scheduler error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=scheduler_loop, daemon=True, name="CommandScheduler")
        thread.start()
        self.logger.info("Command scheduler started")
    
    def start_health_monitor(self):
        """Start agent health monitoring service"""
        def health_monitor_loop():
            self.health_monitor_running = True
            while self.health_monitor_running:
                try:
                    self.monitor_agent_health()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    self.logger.error(f"Health monitor error: {e}")
                    time.sleep(120)
        
        thread = threading.Thread(target=health_monitor_loop, daemon=True, name="HealthMonitor")
        thread.start()
        self.logger.info("Agent health monitor started")
    
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
        
        self.logger.info(f"Scheduled command {scheduled_cmd.id} for agent {agent_id} at {scheduled_time}")
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
                    self.logger.error(f"Scheduled command {scheduled_cmd.id} failed: {e}")
    
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
                self.logger.error(f"Bulk operation {bulk_op.id} failed: {e}")
        
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
                self.logger.error(f"Health check failed for agent {agent_id}: {e}")
    
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
        
        self.logger.warning(f"Agent {health_check.agent_id} needs recovery: {health_check.recovery_actions}")
        
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
                    self.logger.info(f"Executed recovery action {action} for agent {health_check.agent_id}")
                    
            except Exception as e:
                self.logger.error(f"Recovery action {action} failed for agent {health_check.agent_id}: {e}")
    
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
        
        self.logger.info(f"Created command {command.id} for agent {agent_id}: {command_type}")
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
            self.logger.info(f"Executed command {command.id} on agent {command.agent_id}")
            return True
            
        except Exception as e:
            command.status = "failed"
            command.error_message = str(e)
            command.completed_at = datetime.now()
            self.update_command_in_db(command)
            self.logger.error(f"Failed to execute command {command.id}: {e}")
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
        
        self.logger.info(f"Command {command_id} {'completed' if success else 'failed'}")
    
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
            self.logger.error(f"Failed to replay command {command_id}: {e}")
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
            self.logger.error(f"Failed to store command: {e}")
    
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
            self.logger.error(f"Failed to store scheduled command: {e}")
    
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
            self.logger.error(f"Failed to update scheduled command: {e}")
    
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
            self.logger.error(f"Failed to store bulk operation: {e}")
    
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
            self.logger.error(f"Failed to store health check: {e}")
    
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
            self.logger.error(f"Failed to store script: {e}")
    
    def update_script_in_db(self, script: AgentScript):
        """Update script in database"""
<<<<<<< HEAD
        self.store_script_in_db(script)
=======
        self.store_script_in_db(script)
>>>>>>> 1eee087fad254c0d8449abb55113bbe3bc442923
