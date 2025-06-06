import os,sys,importlib.util,pathlib
MODULE_PATH = pathlib.Path(__file__).resolve().parents[1]/"ultimate_agent"/"remote"/"command_handler.py"
spec = importlib.util.spec_from_file_location("remote.command_handler", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RemoteCommandHandler = module.RemoteCommandHandler
import pytest

class DummyConfig:
    def __init__(self):
        self.set_calls = []
        self.reloaded = False
    def set(self, section, key, value):
        self.set_calls.append((section, key, value))
    def reload(self):
        self.reloaded = True

class DummyAgent:
    def __init__(self):
        self.config_manager = DummyConfig()
        self.current_tasks = {}
        self.stopped = False
    def start_task(self, task_type, task_config=None):
        task_id = f"{task_type}-1"
        self.current_tasks[task_id] = {"status": "running"}
        return task_id
    def get_status(self):
        return {"status": "ok"}
    def stop(self):
        self.stopped = True


def test_start_task_command():
    agent = DummyAgent()
    handler = RemoteCommandHandler(agent)
    cmd = {
        "command_id": "c1",
        "command_type": "start_task",
        "parameters": {"task_type": "demo"}
    }
    result = handler.handle_command(cmd)
    assert result["success"] is True
    assert result["command_id"] == "c1"
    assert result["result"]["task_id"] == "demo-1"
    assert "demo-1" in agent.current_tasks


def test_update_and_reload_config():
    agent = DummyAgent()
    handler = RemoteCommandHandler(agent)
    update_cmd = {
        "command_id": "c2",
        "command_type": "update_config",
        "parameters": {"section": "DEFAULT", "updates": {"foo": "bar"}}
    }
    result = handler.handle_command(update_cmd)
    assert result["success"] is True
    assert ("DEFAULT", "foo", "bar") in agent.config_manager.set_calls

    reload_cmd = {
        "command_id": "c3",
        "command_type": "reload_config",
        "parameters": {}
    }
    result = handler.handle_command(reload_cmd)
    assert result["success"] is True
    assert agent.config_manager.reloaded


def test_unknown_command():
    agent = DummyAgent()
    handler = RemoteCommandHandler(agent)
    cmd = {"command_id": "c4", "command_type": "nonexistent"}
    result = handler.handle_command(cmd)
    assert result["success"] is False
    assert result["command_id"] == "c4"
