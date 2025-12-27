#!/bin/bash

# Strudel Agent Server Startup Script

cd "$(dirname "$0")"

echo "=== Strudel Agent Server ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and set:"
    echo "  - STRUDEL_DB_URL (PostgreSQL connection string)"
    echo "  - OPENROUTER_API_KEY (your OpenRouter API key)"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    echo ""
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dependencies not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "Starting server..."
echo "Server will be available at: http://0.0.0.0:8034"
echo "WebSocket endpoint: ws://0.0.0.0:8034/ws"
echo ""

# Run server from backend directory
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8034
