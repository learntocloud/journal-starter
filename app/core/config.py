from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import ConfigDict  # ✅ For Pydantic v2 compatibility

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: str = "5433"
    db_name: str = "journal"
    db_user: str = "postgres"
    db_password: str = "postgres"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = ConfigDict(env_file=".env")  # ✅ Replaces deprecated `class Config`

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
