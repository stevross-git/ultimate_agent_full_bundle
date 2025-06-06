import time
from typing import Dict, Any


class RemoteCommandHandler:
    """Simple remote command handler."""

    def __init__(self, agent: Any):
        self.agent = agent
        self.command_handlers = {
            'restart_agent': self.restart_agent,
            'shutdown_agent': self.shutdown_agent,
            'get_status': self.get_status,
            'start_task': self.start_task,
            'cancel_task': self.cancel_task,
            'update_config': self.update_config,
            'reload_config': self.reload_config,
        }

    def handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        cmd_type = command.get('command_type')
        params = command.get('parameters', {})
        handler = self.command_handlers.get(cmd_type)
        if not handler:
            return {'success': False, 'error': 'unknown_command'}
        try:
            result = handler(params)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def restart_agent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        delay = int(params.get('delay', 1))
        self.agent.stop()
        time.sleep(delay)
        # in modular repo restarting would require external supervisor
        return {'action': 'restart_scheduled', 'delay': delay}

    def shutdown_agent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self.agent.stop()
        return {'action': 'shutdown'}

    def get_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.agent.get_status()

    def start_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a task via the agent's scheduler"""
        task_type = params.get('task_type', 'data_processing')
        task_config = params.get('task_config', {})
        task_id = self.agent.start_task(task_type, task_config)
        return {'task_id': task_id, 'task_type': task_type}

    def cancel_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a running or queued task"""
        task_id = params.get('task_id')
        if not task_id:
            raise ValueError('task_id required')
        success = False
        if hasattr(self.agent, 'task_scheduler'):
            success = self.agent.task_scheduler.cancel_task(task_id)
        elif task_id in getattr(self.agent, 'current_tasks', {}):
            del self.agent.current_tasks[task_id]
            success = True
        return {'task_id': task_id, 'cancelled': success}

    def update_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration section with provided key/value pairs"""
        section = params.get('section')
        updates = params.get('updates', {})
        if not section or not isinstance(updates, dict):
            raise ValueError('invalid parameters')
        for key, value in updates.items():
            self.agent.config_manager.set(section, key, str(value))
        return {'section': section, 'updated_keys': list(updates.keys())}

    def reload_config(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reload configuration from disk"""
        self.agent.config_manager.reload()
        return {'reloaded': True}
