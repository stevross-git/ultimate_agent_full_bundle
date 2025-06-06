from dependency_injector import containers, providers
from ultimate_agent.config.settings import settings

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.override(settings.dict())

    # Example: Register components here
    # logger = providers.Singleton(YourLoggerClass)
    # wallet_manager = providers.Singleton(WalletManager, encryption_key=config.WALLET_ENCRYPTION_KEY)
