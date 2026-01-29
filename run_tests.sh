#!/bin/bash

# Test runner script for Journal API
# This script sets up the environment and runs the test suite

set -e  # Exit on error

echo "🧪 Journal API Test Runner"
echo "=========================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating default .env file..."
    echo "DATABASE_URL=postgresql://postgres:postgres@postgres:5432/career_journal" > .env
fi

# Check if dependencies are installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "📦 Installing test dependencies..."
    pip install -e ".[dev]"
    echo ""
fi

# Run tests
echo "🏃 Running tests..."
echo ""

pytest -v "$@"

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. See output above for details."
fi

exit $TEST_EXIT_CODE
