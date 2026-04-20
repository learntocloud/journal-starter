import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor

if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(logger_name="journal")

from fastapi import FastAPI

from api.routers.journal_router import router as journal_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("journal")
logger.info("Journal API starting up")

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)
