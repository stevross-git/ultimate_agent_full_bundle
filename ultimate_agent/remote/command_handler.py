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
