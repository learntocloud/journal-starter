#!/bin/bash

# Journal API Startup Script
echo "🚀 Starting Journal API..."

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Install dependencies
echo "📥 Installing dependencies with uv..."
uv sync

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Make sure to set DATABASE_URL"
fi

# Set PYTHONPATH for absolute imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the API
echo "🎉 Starting FastAPI server..."
echo "📖 API docs will be available at: http://localhost:8000/docs"
uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000