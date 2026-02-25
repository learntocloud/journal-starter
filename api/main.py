
import logging
from api.routers.journal_router import router as journal_router
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv(override=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.info(" ********* Journal API is launching... ********* ")

app = FastAPI(title="Journal API",
              description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)
