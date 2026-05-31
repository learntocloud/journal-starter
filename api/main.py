import logging
import os
from urllib.parse import urlparse

from dotenv import load_dotenv

# 1. Load env vars and configure logging BEFORE other imports
# so that telemetry and database initialization can see the environment.
load_dotenv(override=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logging.getLogger().setLevel(logging.INFO)

# Log the database target to debug DNS resolution issues
db_url = os.getenv("DATABASE_URL")
if db_url:
    try:
        parsed = urlparse(db_url)
        logging.info(
            f"Database connection attempt targeting host: {parsed.hostname} on port: {parsed.port}"
        )
    except Exception as e:
        logging.error(f"Failed to parse DATABASE_URL for logging: {e}")
else:
    logging.warning("DATABASE_URL environment variable is not set.")

from fastapi import FastAPI  # noqa: E402

# Environment loading must occur before local modules are imported.
from api.routers.journal_router import router as journal_router  # noqa: E402
from api.telemetry import instrument_app  # noqa: E402

logging.getLogger("journal-api").info("Journal API started.")

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
