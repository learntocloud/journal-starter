FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 / asyncpg
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

