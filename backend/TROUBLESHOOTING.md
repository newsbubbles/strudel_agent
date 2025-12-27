# Strudel Agent Backend Troubleshooting

## Quick Fixes

### Issue 1: PostgreSQL Role Does Not Exist

```
createdb: error: FATAL: role "osiris" does not exist
```

**Cause**: PostgreSQL doesn't have a user matching your system username.

**Solution A - Create PostgreSQL User** (Recommended):

```bash
# Create PostgreSQL user matching your system user
sudo -u postgres createuser -s $(whoami)

# Now create the database
createdb strudel_agent

# Update .env
STRUDEL_DB_URL=postgresql+asyncpg://$(whoami)@localhost:5432/strudel_agent
```

**Solution B - Use Docker** (Easiest):

```bash
# Start PostgreSQL in Docker
docker run --name strudel-postgres \
  -e POSTGRES_USER=osiris \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=strudel_agent \
  -p 5432:5432 \
  -d postgres:16

# Update .env
STRUDEL_DB_URL=postgresql+asyncpg://osiris:password@localhost:5432/strudel_agent
```

**Solution C - Use postgres User**:

```bash
# Create database as postgres user
sudo -u postgres createdb strudel_agent

# Set password for postgres user
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"

# Update .env
STRUDEL_DB_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/strudel_agent
```

---

### Issue 2: Could Not Import Module "server"

```
ERROR: Error loading ASGI app. Could not import module "server".
```

**Cause**: Running uvicorn from wrong directory or missing dependencies.

**Solution A - Use Startup Script**:

```bash
cd backend
chmod +x run_server.sh
./run_server.sh
```

**Solution B - Run from Backend Directory**:

```bash
# Make sure you're IN the backend directory
cd backend

# Run uvicorn
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8034
```

**Solution C - Check Dependencies**:

```bash
cd backend
pip install -r requirements.txt
```

---

### Issue 3: Port Already in Use

```
ERROR: [Errno 98] Address already in use
```

**Solution**:

```bash
# Find process using port 8034
lsof -i :8034

# Kill the process
kill -9 <PID>
```

---

### Issue 4: OPENROUTER_API_KEY Not Set

```
ValueError: OPENROUTER_API_KEY environment variable is required
```

**Solution**:

```bash
# Edit .env file
cd backend
nano .env

# Add your API key
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

---

### Issue 5: Database Connection Failed

```
AsyncConnectionPool.connect() failed: could not connect to server
```

**Check**:

1. PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Database exists:
   ```bash
   psql -l | grep strudel_agent
   ```

3. Connection string is correct in `.env`:
   ```
   STRUDEL_DB_URL=postgresql+asyncpg://user:password@localhost:5432/strudel_agent
   ```

4. Port is correct (default: 5432):
   ```bash
   # Check PostgreSQL port
   sudo -u postgres psql -c "SHOW port;"
   ```

---

## Complete Setup (Fresh Start)

### Option 1: Local PostgreSQL

```bash
# 1. Create PostgreSQL user
sudo -u postgres createuser -s $(whoami)

# 2. Create database
createdb strudel_agent

# 3. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# 5. Run server
chmod +x run_server.sh
./run_server.sh
```

### Option 2: Docker PostgreSQL

```bash
# 1. Start PostgreSQL
docker run --name strudel-postgres \
  -e POSTGRES_USER=$(whoami) \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=strudel_agent \
  -p 5432:5432 \
  -d postgres:16

# 2. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
echo "STRUDEL_DB_URL=postgresql+asyncpg://$(whoami):password@localhost:5432/strudel_agent" >> .env
echo "OPENROUTER_API_KEY=sk-or-v1-your-key" >> .env

# 4. Run server
./run_server.sh
```

---

## Verification

### Test Database Connection

```bash
# Connect to database
psql strudel_agent

# List tables (should be empty initially)
\dt

# Exit
\q
```

### Test Server

```bash
# Health check
curl http://localhost:8034/health

# Should return:
# {"status":"healthy"}
```

### Test API

```bash
# Create a session
curl -X POST http://localhost:8034/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "strudel",
    "session_type": "clip",
    "item_id": "test",
    "project_id": "test"
  }'
```

---

## Common Environment Issues

### Python Version

Requires Python 3.11+

```bash
python --version
# Should be 3.11 or higher
```

### Virtual Environment

Always activate before running:

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Dependencies

If you get import errors:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## Logs

### Enable Debug Logging

Edit `backend/server.py` and add at the top:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check PostgreSQL Logs

```bash
# Ubuntu/Debian
sudo tail -f /var/log/postgresql/postgresql-*.log

# Or check with journalctl
sudo journalctl -u postgresql -f
```

---

## Still Having Issues?

1. Check all environment variables are set in `.env`
2. Verify PostgreSQL is running: `sudo systemctl status postgresql`
3. Check port conflicts: `lsof -i :8034`
4. Verify Python version: `python --version` (need 3.11+)
5. Check logs for specific errors

---

## Quick Reference

### Start Everything

```bash
# Start PostgreSQL (if using Docker)
docker start strudel-postgres

# Start backend server
cd backend
source venv/bin/activate
./run_server.sh
```

### Stop Everything

```bash
# Stop server: CTRL+C

# Stop PostgreSQL (if using Docker)
docker stop strudel-postgres
```

### Reset Database

```bash
# Drop and recreate
dropdb strudel_agent
createdb strudel_agent

# Or with Docker
docker stop strudel-postgres
docker rm strudel-postgres
# Then run docker run command again
```
