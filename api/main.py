from fastapi import FastAPI

from api.routers.journal_router import router as journal_router

# TODO (Task 1): Configure logging here.
# Reference: https://docs.python.org/3/howto/logging.html
# Steps:
#   1. ``import logging`` at the top of this file.
#   2. Call ``logging.basicConfig(level=logging.INFO, format="...")``.
#   3. Log an INFO message on startup (e.g. "Journal API starting up").

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)
