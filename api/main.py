import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.config import get_settings
from api.logging_config import configure_logging
from api.repositories.postgres_repository import PostgresDB
from api.routers.journal_router import router as journal_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    async with PostgresDB(settings.database_url) as database:
        app.state.database = database
        try:
            # TODO (Task 3): Log API readiness at INFO after the database is ready.
            yield
        finally:
            # TODO (Task 3): Log API shutdown at INFO during cleanup.
            del app.state.database


app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
    lifespan=lifespan,
)
app.include_router(journal_router)
