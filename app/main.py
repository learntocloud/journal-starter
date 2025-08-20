# app/main.py
from __future__ import annotations

import logging

from fastapi import FastAPI

from app.core.config import settings
from app.routers.journal_router import router as journal_router

# Ensure we at least have INFO logs if nothing else configures logging.
# (Uvicorn will still manage its own loggers; this is a safe fallback.)
root_logger = logging.getLogger()
if not root_logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Journal API", version="0.1.0")


@app.on_event("startup")
async def on_startup() -> None:
    """
    Small robustness/observability tweak:
    Log the DSNs we resolved so drift (e.g., localhost vs db) is obvious.
    """
    logger = logging.getLogger("uvicorn")
    logger.info("DB URL in use (async): %s", settings.database_url)
    # Handy if Alembic or anything else ever uses the sync DSN
    if hasattr(settings, "sync_database_url"):
        logger.info("DB URL in use (sync): %s", settings.sync_database_url)


# Health endpoint
@app.get("/healthz", tags=["Health"], summary="Healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


# API routes
app.include_router(journal_router)


if __name__ == "__main__":
    import uvicorn

    # Run a dev server if launched directly
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
