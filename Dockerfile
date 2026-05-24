FROM python:3.14-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY api ./api
COPY scripts ./scripts

EXPOSE 80

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
