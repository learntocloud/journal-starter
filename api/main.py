
from dotenv import load_dotenv
import logging
load_dotenv(override=True)

from fastapi import FastAPI

from api.routers.journal_router import router as journal_router


# TODO: Setup basic console logging
# Hint: Use logging.basicConfig() with level=logging.INFO
# Steps:
# 1. Configure logging with basicConfig()
# 2. Set level to logging.INFO
# 3. Add console handler
# 4. Test by adding a log message when the app starts

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.info("Starting Journal API")

app = FastAPI(title="Journal API", description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)
