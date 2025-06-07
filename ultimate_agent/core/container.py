try:
    from dependency_injector import containers, providers
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    class containers:
        class DeclarativeContainer:
            pass

    class providers:
        class Configuration(dict):
            def override(self, value):
                self.update(value)

        class Singleton:
            def __init__(self, cls, *args, **kwargs):
                self.cls = cls
                self.args = args
                self.kwargs = kwargs
                self._instance = None

            def __call__(self):
                if self._instance is None:
                    self._instance = self.cls(*self.args, **self.kwargs)
                return self._instance

try:
    from ..config.settings import settings
except ImportError:  # pragma: no cover - allow running module standalone
    from ultimate_agent.config.settings import settings  # type: ignore

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.override(settings.dict())

    # Example: Register components here
    # logger = providers.Singleton(YourLoggerClass)
    # wallet_manager = providers.Singleton(WalletManager, encryption_key=config.WALLET_ENCRYPTION_KEY)
