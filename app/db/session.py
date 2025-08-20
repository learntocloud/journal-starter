from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Import settings from your actual location
from app.core.config import settings


# Use NullPool so connections are not reused across different event loops
# during tests (prevents "future attached to a different loop" / asyncpg
# "another operation is in progress" errors).
engine = create_async_engine(
    settings.database_url,        # must be postgresql+asyncpg per project rules
    echo=False,
    future=True,
    poolclass=NullPool,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """FastAPI dependency that yields an AsyncSession."""
    async with SessionLocal() as session:
        yield session

# --- compatibility alias for existing imports ---
get_db = get_session
