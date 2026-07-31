FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock .

RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD [".venv/bin/python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
