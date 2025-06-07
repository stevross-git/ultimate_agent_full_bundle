import time

try:
    from ...core.events import event_bus
    from ...config.settings import settings
except ImportError:  # pragma: no cover - allow running module standalone
    from ultimate_agent.core.events import event_bus  # type: ignore
    from ultimate_agent.config.settings import settings  # type: ignore

class TaskExecutor:
    def __init__(self):
        self.batch_size = settings.TASK_FETCH_BATCH

    def execute(self, task: dict):
        task_id = task.get("task_id", "unknown")
        print(f"🛠️ Executing task: {task_id}")
        time.sleep(1)  # Simulate workload
        result = {"task_id": task_id, "status": "success"}
        print(f"✅ Completed task: {task_id}")
        event_bus.publish("task.completed", result)
        return result
