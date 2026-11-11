FROM python:3.14-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# Expose application port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]