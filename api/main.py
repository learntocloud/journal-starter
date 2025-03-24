from fastapi import FastAPI
from dotenv import load_dotenv
from api.controllers import journal_router
import logging

load_dotenv()

# TODO: Setup basic console logging
# Hint: Use logging.basicConfig() with level=logging.INFO

# Configure logging to print logs to the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(journal_router, prefix="/api/v1")

logger.info("FastAPI application started successfully")
