#!/bin/bash

# Quick Fix Script for Strudel Agent Backend

echo "=== Strudel Agent Quick Fix ==="
echo ""

cd "$(dirname "$0")"

echo "Step 1: Setting up PostgreSQL with Docker..."
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker or setup PostgreSQL manually."
    echo "See TROUBLESHOOTING.md for manual setup instructions."
    exit 1
fi

# Stop and remove existing container if it exists
docker stop strudel-postgres 2>/dev/null
docker rm strudel-postgres 2>/dev/null

echo "Starting PostgreSQL in Docker..."
docker run --name strudel-postgres \
  -e POSTGRES_USER=$(whoami) \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=strudel_agent \
  -p 5432:5432 \
  -d postgres:16

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL started successfully!"
else
    echo "❌ Failed to start PostgreSQL"
    exit 1
fi

echo ""
echo "Step 2: Waiting for PostgreSQL to be ready..."
sleep 3

echo ""
echo "Step 3: Setting up Python environment..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Step 4: Configuring environment..."

if [ ! -f .env ]; then
    cp .env.example .env
fi

# Update .env with correct database URL
cat > .env << EOF
STRUDEL_DB_URL=postgresql+asyncpg://$(whoami):password@localhost:5432/strudel_agent
OPENROUTER_API_KEY=sk-or-v1-your-key-here
HOST=0.0.0.0
PORT=8034
EOF

echo "✅ Environment configured!"
echo ""
echo "⚠️  IMPORTANT: Edit .env and set your OPENROUTER_API_KEY"
echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenRouter API key"
echo "2. Run: ./run_server.sh"
echo ""
echo "Database: postgresql://$(whoami):password@localhost:5432/strudel_agent"
echo "Server will run on: http://0.0.0.0:8034"
echo ""
