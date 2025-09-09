from fastapi import FastAPI
from dotenv import load_dotenv
from routers.journal_router import router as journal_router
import logging
import sys

load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("journal_api")

app = FastAPI(title="Journal API", description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)

@app.on_event("startup")
async def on_startup():
    logger.info("Starting Journal API...")