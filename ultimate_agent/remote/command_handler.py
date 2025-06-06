class RemoteCommandHandler:
    """Simple remote command handler."""

    def __init__(self):
        self.commands = {
            "ping": self.ping,
        }

    def execute(self, command: str, **kwargs):
        func = self.commands.get(command)
        if not func:
            raise ValueError(f"Unknown command: {command}")
        return func(**kwargs)

    def ping(self):
        return {"status": "ok", "message": "pong"}
