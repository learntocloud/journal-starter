FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock .

RUN uv sync --frozen --no-dev

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD [".venv/bin/python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
