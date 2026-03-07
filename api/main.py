import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routers.journal_router import router as journal_router

logger = logging.getLogger(__name__)

load_dotenv(override=True)


logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)

logger.info("Journal API application has started")
