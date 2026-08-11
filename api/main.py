from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app

from api.request_logging import log_http_request
from api.routers.journal_router import router as journal_router
from api.telemetry import logger

app = FastAPI(
    title="Journal API",
    description="A simple journal API for tracking daily work, struggles, and intentions",
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(journal_router)

FastAPIInstrumentor.instrument_app(app)

logger.info(
    "Journal API started",
    extra={
        "service.name": "journal-api",
        "event.name": "application.started",
    },
)


@app.middleware("http")
async def request_logging_middleware(request, call_next):
    return await log_http_request(request, call_next)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
