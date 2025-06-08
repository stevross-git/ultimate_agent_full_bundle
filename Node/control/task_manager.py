import time
import threading
import random
from collections import deque
from datetime import datetime
from typing import Dict, Any

from models.tasks import CentralTask
from core.database import CentralTaskRecord


class TaskControlManager:
    def __init__(self, node_server):
        self.node_server = node_server
        self.pending_tasks = deque()
        self.running_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}

        self.auto_generation_enabled = True
        self.generation_interval = 30
        self.max_pending_tasks = 20

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

        self.task_metrics = {
            "total_assigned": 0,
            "total_completed": 0,
            "total_failed": 0,
            "success_rate": 100.0
        }

    def start_task_control_services(self):
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
        if len(self.pending_tasks) < self.max_pending_tasks:
            online_agents = len([a for a in self.node_server.agents.values()])
            if online_agents > 0:
                for _ in range(random.randint(1, 2)):
                    task_type = random.choice(list(self.task_templates.keys()))
                    task = self.create_task(task_type)
                    self.pending_tasks.append(task)
                    self.store_task_in_db(task)
                    self.node_server.logger.info(f"Generated task: {task.id} ({task.task_type})")

    def create_task(self, task_type: str) -> CentralTask:
        template = self.task_templates.get(task_type, self.task_templates["data_processing"])
        task = CentralTask(
            id=f"central-task-{int(time.time())}-{random.randint(1000,9999)}",
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
        task.assigned_agent = agent_id
        task.assigned_at = datetime.now()
        task.status = "assigned"

        try:
            self.pending_tasks.remove(task)
        except ValueError:
            pass

        self.running_tasks[task.id] = task
        self.send_task_to_agent(task, agent_id)
        self.task_metrics["total_assigned"] += 1
        self.node_server.logger.info(f"Assigned task {task.id} to agent {agent_id}")

    def send_task_to_agent(self, task: CentralTask, agent_id: str):
        task_data = {
            "task_id": task.id,
            "task_type": task.task_type,
            "priority": task.priority,
            "config": task.config,
            "requirements": task.requirements,
            "estimated_duration": task.estimated_duration,
            "reward": task.reward
        }
        self.node_server.socketio.emit('central_task_assignment', task_data, room=f'agent_{agent_id}')

    def handle_task_completion(self, task_id: str, agent_id: str, success: bool, result: Dict = None):
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

        del self.running_tasks[task_id]

        total = self.task_metrics["total_completed"] + self.task_metrics["total_failed"]
        if total > 0:
            self.task_metrics["success_rate"] = (self.task_metrics["total_completed"] / total) * 100

        self.update_task_in_db(task)
        self.node_server.logger.info(f"Task {task_id} {'completed' if success else 'failed'}")

    def get_task_statistics(self) -> Dict[str, Any]:
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
        self.store_task_in_db(task)
