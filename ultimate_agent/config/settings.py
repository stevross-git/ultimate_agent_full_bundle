from pydantic import BaseSettings, Field
from typing import Literal

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
