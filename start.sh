#!/bin/bash

# Journal API Startup Script (Local Setup)
echo "🚀 Starting Journal API (Local Setup)..."

# Ensure we're in the root directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r api/requirements.txt

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Make sure DATABASE_URL is set"
fi

# Run the app locally
echo "🎉 Starting FastAPI server (local)..."
echo "📖 API docs available at: http://localhost:8000/docs"
cd api && uvicorn main:app --reload --host 127.0.0.1 --port 8000
