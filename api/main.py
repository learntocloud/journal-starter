from fastapi import FastAPI
from dotenv import load_dotenv
from routers.journal_router import router as journal_router
import logging

load_dotenv()

# DONE
# TODO: Setup basic console logging
# Hint: Use logging.basicConfig() with level=logging.INFO
# Steps:
# 1. Configure logging with basicConfig()
# 2. Set level to logging.INFO
# 3. Add console handler
# 4. Test by adding a log message when the app starts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Journal API",
              description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Journal API has started successfully!")
