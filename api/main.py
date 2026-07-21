import logging

from fastapi import FastAPI

from api.routers.journal_router import router as journal_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.info("Journal API starting up")

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)

app.include_router(journal_router)
