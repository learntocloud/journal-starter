import logging  # noqa: F401

from dotenv import load_dotenv

# Load .env BEFORE importing anything that reads env vars at import time
# (e.g. api.repositories.postgres_repository reads DATABASE_URL).
load_dotenv(override=True)

# TODO (Task 1): Configure logging here.
# Reference: https://docs.python.org/3/howto/logging.html
# Steps:
#   1. Call logging.basicConfig(level=logging.INFO, format="...")
#   2. Log an INFO message on startup (e.g. "Journal API starting up")

from fastapi import FastAPI  # noqa: E402

from api.routers.journal_router import router as journal_router  # noqa: E402

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)
