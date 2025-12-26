# Quick Start Fix Guide

**Your Issues**:
1. ❌ PostgreSQL role doesn't exist
2. ❌ Server can't find module

**Solution**: Use the automated fix scripts!

---

## Fastest Fix (Recommended)

```bash
# 1. Go to backend directory
cd backend

# 2. Make scripts executable
chmod +x quick_fix.sh run_server.sh setup_db.sh

# 3. Run the quick fix (sets up Docker PostgreSQL + Python env)
./quick_fix.sh

# 4. Edit .env and add your OpenRouter API key
nano .env
# Change: OPENROUTER_API_KEY=sk-or-v1-your-actual-key

# 5. Start the server
./run_server.sh
```

**That's it!** Server should start on `http://0.0.0.0:8000`

---

## What the Scripts Do

### `quick_fix.sh`
- Starts PostgreSQL in Docker (no manual setup needed)
- Creates Python virtual environment
- Installs all dependencies
- Creates `.env` file with correct settings

### `run_server.sh`
- Activates virtual environment
- Checks dependencies
- Starts FastAPI server from correct directory

---

## Manual Fix (If Scripts Don't Work)

### Fix 1: PostgreSQL

**Option A - Docker** (Easiest):
```bash
docker run --name strudel-postgres \
  -e POSTGRES_USER=osiris \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=strudel_agent \
  -p 5432:5432 \
  -d postgres:16
```

**Option B - Create PostgreSQL User**:
```bash
sudo -u postgres createuser -s osiris
createdb strudel_agent
```

### Fix 2: Server Module

```bash
# Must be IN the backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run from backend directory
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

---

## Verify It Works

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy"}
```

---

## Common Issues

### "Docker not found"
**Solution**: Install Docker or use manual PostgreSQL setup (see TROUBLESHOOTING.md)

### "Port 8000 already in use"
**Solution**: 
```bash
# Find what's using it
lsof -i :8000

# Kill it or use different port
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### "Module not found" errors
**Solution**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## Your Specific Errors Explained

### Error 1: `role "osiris" does not exist`

**What happened**: PostgreSQL doesn't have a user called "osiris"

**Why**: When you run `createdb`, it tries to connect as your system user (osiris), but PostgreSQL doesn't have that user.

**Fix**: Either create the user OR use Docker (which creates it automatically)

### Error 2: `Could not import module "server"`

**What happened**: You ran `uvicorn server:app` from the project root, not the backend directory

**Why**: The import path `server` only works when you're IN the backend directory

**Fix**: Run from backend directory OR use the startup script

---

## Next Steps After Fix

1. ✅ Server running on http://localhost:8000
2. ✅ Database connected
3. ✅ Ready to test API

**Test it**:
```bash
# Create a session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "strudel",
    "session_type": "clip",
    "item_id": "kick",
    "project_id": "test_project"
  }'
```

---

## TL;DR

```bash
cd backend
chmod +x *.sh
./quick_fix.sh
# Edit .env with your API key
./run_server.sh
```

Done! 🎉
