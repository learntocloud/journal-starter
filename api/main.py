from fastapi import FastAPI
from dotenv import load_dotenv
from api.controllers import journal_router

load_dotenv()

# TODO: Setup basic console logging
# Hint: Use logging.basicConfig() with level=logging.INFO

app = FastAPI()
app.include_router(journal_router)