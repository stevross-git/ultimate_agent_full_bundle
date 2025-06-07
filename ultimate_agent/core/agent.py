import asyncio

try:
    from ..config.settings import settings
    from .container import Container
    from ..tasks.execution.scheduler import TaskScheduler
    from ..remote.handler import RemoteCommandHandler  # ✅ use the actual file
except ImportError:  # pragma: no cover - allow running module standalone
    from ultimate_agent.config.settings import settings  # type: ignore
    from ultimate_agent.core.container import Container  # type: ignore
    from ultimate_agent.tasks.execution.scheduler import TaskScheduler  # type: ignore
    from ultimate_agent.remote.handler import RemoteCommandHandler  # type: ignore

from ultimate_agent_full_bundle.ultimate_agent.core.events import event_bus

class UltimateAgent:
    def __init__(self):
        self.container = Container()
        self.config = settings
        self.scheduler = TaskScheduler()

        self.remote_commands = RemoteCommandHandler()
        self.remote_commands.set_shutdown_callback(self.scheduler.shutdown_event.set)
        event_bus.subscribe("remote.command.result", self._on_command_result)

        print(f"✅ UltimateAgent initialized in {self.config.ENV} mode")

    def _on_command_result(self, result):
        print(f"🎮 Command result: {result}")

    def run(self):
        print("🚀 Running UltimateAgent with async scheduler...")
        asyncio.run(self.scheduler.run_loop())

    def handle_command(self, command: str, **kwargs):
        """Execute a remote command via the command handler."""
        result = self.remote_commands.execute(command, **kwargs)
        if command == "ping" and "status" in result:
            return {"message": result["status"]}
        return result
