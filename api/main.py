import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routers.journal_router import router as journal_router
from api.telemetry import instrument_app

load_dotenv(override=True)

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


# Configure logging at INFO level
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", handlers=[logging.StreamHandler()]
)
# Ensure root logger is set to INFO even if basicConfig didn't apply
logging.getLogger().setLevel(logging.INFO)

logging.info("Journal API started.")
