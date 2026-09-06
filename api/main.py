from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.config import get_settings
from api.repositories.postgres_repository import PostgresDB
from api.routers.journal_router import router as journal_router

# TODO (Task 1): Configure logging here.
# Reference: https://docs.python.org/3/howto/logging.html
# Steps:
#   1. ``import logging`` at the top of this file.
#   2. Call ``logging.basicConfig(level=logging.INFO, format="...")``.
#   3. Log an INFO message on startup (e.g. "Journal API starting up").


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    async with PostgresDB(settings.database_url) as database:
        app.state.database = database
        try:
            yield
        finally:
            del app.state.database


app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
    lifespan=lifespan,
)
app.include_router(journal_router)
