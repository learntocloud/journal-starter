import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logger = logging.getLogger("journal-api")


async def log_http_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Log every HTTP request, including failed requests."""

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "HTTP request failed with an unhandled exception",
            extra={
                "event.name": "http.request.completed",
                "http.request.method": request.method,
                "url.path": request.url.path,
                "http.response.status_code": 500,
                "http.request.duration_ms": round(duration_ms, 2),
            },
        )

        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    status_code = response.status_code

    log_attributes = {
        "event.name": "http.request.completed",
        "http.request.method": request.method,
        "url.path": request.url.path,
        "http.response.status_code": status_code,
        "http.request.duration_ms": round(duration_ms, 2),
    }

    if status_code >= 500:
        logger.error(
            "HTTP request completed with server error",
            extra=log_attributes,
        )
    elif status_code >= 400:
        logger.warning(
            "HTTP request completed with client error",
            extra=log_attributes,
        )
    else:
        logger.info(
            "HTTP request completed",
            extra=log_attributes,
        )

    return response
