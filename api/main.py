import logging
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

# 1. Load env vars and configure logging BEFORE other imports
# so that telemetry and database initialization can see the environment.
load_dotenv(override=False)  # Don't override existing env vars, especially in production
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logging.getLogger().setLevel(logging.INFO)
logging.captureWarnings(True)

# Log the database target to debug DNS resolution issues
db_url = os.getenv("DATABASE_URL")
if db_url:
    try:
        parsed = urlparse(db_url)
        msg = f"STARTUP_DEBUG: DB Host: {parsed.hostname} Port: {parsed.port}"
        print(msg, file=sys.stderr, flush=True)
        logging.info(msg)
    except Exception as e:
        print(f"STARTUP_DEBUG: Parse Error: {e}", file=sys.stderr, flush=True)
else:
    print("STARTUP_DEBUG: DATABASE_URL IS MISSING", file=sys.stderr, flush=True)

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
