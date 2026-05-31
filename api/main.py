import logging
from dotenv import load_dotenv

# 1. Load env vars and configure logging BEFORE other imports
# so that telemetry and database initialization can see the environment.
load_dotenv(override=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
    force=True,  # Ensures configuration is applied even if handlers already exist (required for pytest)
)
logging.getLogger().setLevel(logging.INFO)

logging.info("Journal API started.")

# noqa: E402 is used because environment loading must occur before these modules are imported.
from fastapi import FastAPI  # noqa: E402
from api.routers.journal_router import router as journal_router  # noqa: E402
from api.telemetry import instrument_app  # noqa: E402

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
