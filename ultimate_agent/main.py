from ultimate_agent.core.agent import UltimateAgent
from ultimate_agent.core.events import event_bus

def on_startup():
    print("📡 Event: Startup triggered")

event_bus.subscribe("startup", on_startup)

if __name__ == "__main__":
    event_bus.publish("startup")
    agent = UltimateAgent()
    agent.run()
