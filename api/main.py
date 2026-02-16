import logging

from dotenv import load_dotenv

load_dotenv(override=True)

from fastapi import FastAPI  # noqa: E402

from api.routers.journal_router import router as journal_router  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Journal API", description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)

logger.info("Journal API started successfully")
