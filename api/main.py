from dotenv import load_dotenv

load_dotenv(override=True)

from fastapi import FastAPI

from api.routers.journal_router import router as journal_router

import logging

# Logging konfigurieren (TODO erledigt)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logging.info("Journal API starting up...")

app = FastAPI(title="Journal API", description="A simple journal API for tracking daily work, struggles, and intentions")
app.include_router(journal_router)
# Logging configured Sun Mar 22 00:07:57 UTC 2026
