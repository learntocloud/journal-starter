import logging
import os

from dotenv import load_dotenv

# 1. Load env vars and configure logging BEFORE any other imports
load_dotenv(override=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logging.getLogger().setLevel(logging.INFO)

from fastapi import FastAPI

from api.routers.journal_router import router as journal_router
from api.telemetry import instrument_app

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)
app.include_router(journal_router)

instrument_app(app)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}
