import asyncio
from ultimate_agent.config.settings import settings
from ultimate_agent.core.container import Container
from ultimate_agent.tasks.execution.scheduler import TaskScheduler

class UltimateAgent:
    def __init__(self):
        self.container = Container()
        self.config = settings
        self.scheduler = TaskScheduler()
        print(f"✅ UltimateAgent initialized in {self.config.ENV} mode")

    def run(self):
        print("🚀 Running UltimateAgent with async scheduler...")
        asyncio.run(self.scheduler.run_loop())
