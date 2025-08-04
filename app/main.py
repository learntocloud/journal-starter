from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os

from app.routers.journal_router import router as journal_router  # adjusted for correct import

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting Journal API...")

# Initialize FastAPI app
app = FastAPI(title="Journal API")

# CORS settings
origins = [
    "http://localhost:3000",  # React dev server or similar
    "http://127.0.0.1:3000",
    # Add your deployed frontend URL here when applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # you can also use ["*"] for open access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routers
app.include_router(journal_router)

# Healthcheck route
@app.get("/healthz", tags=["Health"])
async def healthcheck():
    return {"status": "ok"}
