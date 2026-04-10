from contextlib import asynccontextmanager
from api.routers.journal_router import router as journal_router
import logging
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv(override=True)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: Setup basic console logging
# Hint: Use logging.basicConfig() with level=logging.INFO
# Steps:
# 1. Configure logging with basicConfig()
# 2. Set level to logging.INFO
# 3. Add console handler
# 4. Test by adding a log message when the app starts


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI application started!")
    yield

app = FastAPI(title="Journal API",
              description="A simple journal API for tracking daily work, struggles, and intentions", lifespan=lifespan)
app.include_router(journal_router)
