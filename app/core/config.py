# app/core/config.py
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict  # Pydantic v2 settings
from pydantic import Field


class Settings(BaseSettings):
    # Piecewise DB settings (used if no full DATABASE_URL is provided)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "journal"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # Optional full DSN override from env (CI/production-friendly)
    # We look for BOTH DATABASE_URL and database_url in env.
    # Using Field with validation alias keeps mypy happy, but we’ll still
    # double-check os.environ below for extra safety.
    DATABASE_URL: str | None = Field(default=None, validation_alias="DATABASE_URL")

    # Pydantic v2 settings config:
    # - env_file: load .env
    # - extra='ignore': tolerate unrelated keys in .env (prevents alembic crashes)
    # - no env prefix (read variables as-is)
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_prefix="",
    )

    @property
    def database_url(self) -> str:
        """
        Single source of truth for the app’s async DB URL.
        Precedence:
          1) env var DATABASE_URL
          2) env var database_url (lowercase; tolerated)
          3) piecewise settings (db_user/password/host/port/name)
        Normalizes to 'postgresql+asyncpg://...' for the async engine.
        """
        url = (
            os.getenv("DATABASE_URL")
            or os.getenv("database_url")
            or self.DATABASE_URL
        )
        if url:
            # Normalize to async driver
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        # Fallback from parts (async driver)
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sync_database_url(self) -> str:
        """
        Convenience for Alembic or other sync-only tools.
        Converts '+asyncpg' to sync psycopg/psycopg2-style URL.
        """
        url = self.database_url
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
