import asyncio
from ultimate_agent.config.settings import settings
from ultimate_agent.core.container import Container
from ultimate_agent.tasks.execution.scheduler import TaskScheduler
from ultimate_agent.remote import RemoteCommandHandler

class UltimateAgent:
    def __init__(self):
        self.container = Container()
        self.config = settings
        self.scheduler = TaskScheduler()
        self.command_handler = RemoteCommandHandler()
        print(f"✅ UltimateAgent initialized in {self.config.ENV} mode")

    def run(self):
        print("🚀 Running UltimateAgent with async scheduler...")
        asyncio.run(self.scheduler.run_loop())

    def handle_command(self, command: str, **kwargs):
        """Execute a remote command via the command handler."""
        return self.command_handler.execute(command, **kwargs)
