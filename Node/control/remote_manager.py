import time
import threading
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any

from models.commands import AgentCommand, AgentConfiguration
from models.scripts import ScheduledCommand, BulkOperation, AgentHealthCheck, AgentScript
from models.agents import EnhancedAgentStatus
from core.database import (
    AgentCommandRecord, ScheduledCommandRecord, BulkOperationRecord,
    AgentHealthRecord, AgentScriptRecord
)
from utils.serialization import serialize_for_json

class AdvancedRemoteControlManager:
    def __init__(self, node_server):
        self.node_server = node_server
        self.active_commands = {}
        self.agent_configurations = {}
        self.command_queue = defaultdict(deque)
        self.scheduled_commands = {}
        self.bulk_operations = {}
        self.agent_health_monitors = {}
        self.agent_scripts = {}
        self.command_history = defaultdict(list)
        self.scheduler_running = False
        self.health_monitor_running = False

    def start_advanced_services(self):
        self.start_command_scheduler()
        self.start_health_monitor()
        self.node_server.logger.info("Advanced remote control services started")

    def start_command_scheduler(self):
        def scheduler_loop():
            self.scheduler_running = True
            while self.scheduler_running:
                try:
                    self.process_scheduled_commands()
                    time.sleep(10)
                except Exception as e:
                    self.node_server.logger.error(f"Command scheduler error: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=scheduler_loop, daemon=True, name="CommandScheduler")
        thread.start()
        self.node_server.logger.info("Command scheduler started")

    def start_health_monitor(self):
        def health_monitor_loop():
            self.health_monitor_running = True
            while self.health_monitor_running:
                try:
                    self.monitor_agent_health()
                    time.sleep(30)
                except Exception as e:
                    self.node_server.logger.error(f"Health monitor error: {e}")
                    time.sleep(120)

        thread = threading.Thread(target=health_monitor_loop, daemon=True, name="HealthMonitor")
        thread.start()
        self.node_server.logger.info("Agent health monitor started")

    def monitor_agent_health(self):
        for agent_id, status in self.node_server.agent_status.items():
            try:
                health_check = self.perform_health_check(agent_id, status)
                self.store_health_check_in_db(health_check)
            except Exception as e:
                self.node_server.logger.error(f"Health check failed for agent {agent_id}: {e}")

    def perform_health_check(self, agent_id: str, status: EnhancedAgentStatus) -> AgentHealthCheck:
        current_time = datetime.now()
        cpu_health = "healthy" if status.cpu_percent < 80 else "warning" if status.cpu_percent < 95 else "critical"
        memory_health = "healthy" if status.memory_percent < 80 else "warning" if status.memory_percent < 95 else "critical"
        last_heartbeat_age = (current_time - status.last_heartbeat).total_seconds() if status.last_heartbeat else float('inf')
        network_health = "healthy" if last_heartbeat_age < 60 else "warning" if last_heartbeat_age < 120 else "critical"
        total_tasks = status.tasks_completed + status.tasks_failed
        task_success_rate = status.tasks_completed / max(total_tasks, 1)
        task_health = "healthy" if task_success_rate > 0.9 else "warning" if task_success_rate > 0.7 else "critical"

        health_scores = {"healthy": 100, "warning": 70, "critical": 30, "offline": 0}
        overall_health = min(
            health_scores[cpu_health],
            health_scores[memory_health],
            health_scores[network_health],
            health_scores[task_health]
        )
        status_text = "healthy" if overall_health >= 90 else "warning" if overall_health >= 70 else "critical" if overall_health >= 30 else "offline"

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
            status=status_text,
            cpu_health=cpu_health,
            memory_health=memory_health,
            disk_health="unknown",
            network_health=network_health,
            task_health=task_health,
            health_score=overall_health,
            response_time=last_heartbeat_age,
            recovery_needed=recovery_needed,
            recovery_actions=recovery_actions
        )

    def store_health_check_in_db(self, check: AgentHealthCheck):
        try:
            record = AgentHealthRecord(
                agent_id=check.agent_id,
                timestamp=check.timestamp,
                status=check.status,
                cpu_health=check.cpu_health,
                memory_health=check.memory_health,
                disk_health=check.disk_health,
                network_health=check.network_health,
                task_health=check.task_health,
                health_score=check.health_score,
                response_time=check.response_time,
                last_error=check.last_error,
                recovery_needed=check.recovery_needed,
                recovery_actions=check.recovery_actions
            )
            self.node_server.db.session.add(record)
            self.node_server.db.session.commit()
        except Exception as e:
            self.node_server.logger.error(f"Failed to store health check: {e}")
