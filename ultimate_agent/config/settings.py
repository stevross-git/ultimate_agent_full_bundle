from typing import Literal

try:
    from pydantic import BaseSettings, Field
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    class BaseSettings:
        """Basic stub of pydantic.BaseSettings for test environments."""

        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

        def dict(self):
            return self.__dict__

    def Field(default=None, *, description: str | None = None, default_factory=None):
        """Simple replacement for pydantic.Field."""
        if default_factory is not None:
            return default_factory()
        return default

class Settings(BaseSettings):
    ENV: Literal['dev', 'staging', 'prod'] = 'dev'
    NODE_URL: str = Field(..., description='URL of the Enhanced Node')
    REDIS_URL: str = 'redis://localhost:6379'
    DATABASE_URL: str = 'postgresql://user:pass@localhost:5432/ai_net'
    WALLET_ENCRYPTION_KEY: str = Field(..., description='Fernet encryption key for wallet')
    TASK_FETCH_BATCH: int = 4

    class Config:
        env_file = '.env'
        case_sensitive = True

settings = Settings()
