#!/bin/bash

# Strudel Agent Database Setup Script

echo "=== PostgreSQL Setup for Strudel Agent ==="
echo ""

# Check if PostgreSQL is running
echo "1. Checking PostgreSQL status..."
if command -v systemctl &> /dev/null; then
    sudo systemctl status postgresql | grep "Active:"
else
    echo "systemctl not available, skipping status check"
fi

echo ""
echo "2. Checking PostgreSQL connection..."
psql --version

echo ""
echo "3. Current PostgreSQL user:"
whoami

echo ""
echo "4. Attempting to connect to PostgreSQL..."
psql -U postgres -c "SELECT version();" 2>&1 || echo "Failed to connect as 'postgres' user"

echo ""
echo "=== Setup Instructions ==="
echo ""
echo "Option 1: Create PostgreSQL user matching your system user"
echo "  sudo -u postgres createuser -s $(whoami)"
echo "  createdb strudel_agent"
echo ""
echo "Option 2: Use postgres user"
echo "  sudo -u postgres createdb strudel_agent"
echo "  # Then update .env with: postgresql+asyncpg://postgres:password@localhost:5432/strudel_agent"
echo ""
echo "Option 3: Use Docker (recommended for development)"
echo "  docker run --name strudel-postgres \\"
echo "    -e POSTGRES_USER=$(whoami) \\"
echo "    -e POSTGRES_PASSWORD=password \\"
echo "    -e POSTGRES_DB=strudel_agent \\"
echo "    -p 5432:5432 \\"
echo "    -d postgres:16"
echo ""
