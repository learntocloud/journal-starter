# migrations/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Make the app importable when Alembic runs from the repo root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.db.base import Base
from app.models import entry  # ensure models are imported so metadata is populated

# Alembic Config object
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------
# Build a **sync** SQLAlchemy URL
# -------------------------------
# 1) Prefer DATABASE_URL from the environment (CI sets this)
env_database_url = os.getenv("DATABASE_URL")

if env_database_url:
    raw_url = env_database_url
else:
    # 2) Else build from DB_* envs with sane defaults (5432),
    #    falling back to values from settings for name/user/password.
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")  # <- keep default 5432
    name = os.getenv("DB_NAME", settings.db_name)
    user = os.getenv("DB_USER", settings.db_user)
    password = os.getenv("DB_PASSWORD", settings.db_password)
    raw_url = f"postgresql://{user}:{password}@{host}:{port}/{name}"

# Alembic must use a sync driver; strip +asyncpg if present
sync_url = raw_url.replace("+asyncpg", "")

print(f"[alembic] Using SQLAlchemy URL: {sync_url}")
config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
