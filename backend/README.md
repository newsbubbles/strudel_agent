# Strudel Agent Backend

**FastAPI backend for Strudel Agent** - An AI assistant for live coding music with Strudel.

---

## Features

- ✅ **FastAPI** with WebSocket support
- ✅ **PostgreSQL** database (SQLModel + asyncpg)
- ✅ **Pydantic-AI** agent with OpenRouter
- ✅ **Session management** (clip/song/playlist/pack)
- ✅ **Message history** with pagination
- ✅ **Real-time updates** via WebSocket
- ✅ **MCP tools** for Strudel operations
- ✅ **Hypergraph memory** integration

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Create PostgreSQL database
createdb strudel_agent

# Or use Docker
docker run --name strudel-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=strudel_agent \
  -p 5432:5432 \
  -d postgres:16
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
STRUDEL_DB_URL=postgresql+asyncpg://user:password@localhost:5432/strudel_agent
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 4. Run Server

```bash
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Server running at: `http://localhost:8000`

### 5. Test

```bash
# Health check
curl http://localhost:8000/health

# Create session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "strudel",
    "session_type": "clip",
    "item_id": "kick",
    "project_id": "test"
  }'
```

---

## Project Structure

```
backend/
├── server.py                 # FastAPI app + WebSocket endpoint
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── src/
    ├── db/                   # Database layer
    │   ├── models.py         # SQLModel definitions
    │   ├── connection.py     # Database connection
    │   └── crud.py           # CRUD operations
    ├── models/               # Pydantic models
    │   └── messages.py       # WebSocket message models
    ├── core/                 # Core backend logic
    │   ├── manager.py        # WebSocket connection manager
    │   ├── session_manager.py # Session lifecycle
    │   └── agent_factory.py  # Agent creation
    └── mcp/                  # MCP servers
        └── strudel_server.py # Strudel-specific tools
```

---

## API Documentation

See **[notes/interface/integration.md](../notes/interface/integration.md)** for complete API specification.

### Quick Reference

**Sessions**:
- `POST /api/sessions` - Create session
- `GET /api/sessions` - List sessions
- `DELETE /api/sessions/{id}` - Delete session

**Messages**:
- `GET /api/messages/{session_id}` - Get paginated messages

**Clips**:
- `POST /api/clips` - Create clip
- `GET /api/clips/{project_id}` - List clips
- `GET /api/clips/{project_id}/{clip_id}` - Get clip
- `PUT /api/clips/{project_id}/{clip_id}` - Update clip
- `DELETE /api/clips/{project_id}/{clip_id}` - Delete clip

**Songs**: Same pattern as clips
**Playlists**: Same pattern as clips

**WebSocket**: `ws://localhost:8000/ws`

---

## Development

### Database Migrations

**Pre-production**: Just recreate tables

```python
# In src/db/connection.py, init_db()
# Uncomment to drop/recreate:
await conn.run_sync(SQLModel.metadata.drop_all)
await conn.run_sync(SQLModel.metadata.create_all)
```

**Production**: Use Alembic (not needed yet)

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (TODO: add tests)
pytest
```

### Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `STRUDEL_DB_URL` | Yes | PostgreSQL connection string |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 8000) |

---

## Architecture

### Session Flow

1. **Frontend creates session** via `POST /api/sessions`
2. **Backend creates**:
   - Database record (sessions table)
   - Memory files (pickle + hypergraph)
   - Agent instance (Pydantic-AI + MCP servers)
3. **Frontend connects** via WebSocket
4. **Handshake** establishes connection
5. **Messages flow** bidirectionally
6. **Agent processes** with tools
7. **Updates sent** to frontend

### Database Schema

**sessions**: Session metadata
**messages**: Simplified message history (for frontend)
**memory_files**: Hypergraph memory file tracking
**clips**: Strudel code clips
**songs**: Song compositions (clip IDs)
**playlists**: Playlist compositions (song IDs)

### WebSocket Protocol

1. **Handshake**: Client sends session_id
2. **Handshake Ack**: Server confirms connection
3. **User Message**: Client sends message
4. **Typing Indicator**: Server shows agent is working
5. **Tool Report**: Agent starts using tool
6. **Tool Result**: Tool execution complete
7. **Agent Response**: Final reply
8. **Update Events**: clip_updated, song_updated, etc.

---

## Troubleshooting

### Database Connection Error

```
ValueError: STRUDEL_DB_URL environment variable is required
```

**Fix**: Set `STRUDEL_DB_URL` in `.env` file

### OpenRouter API Error

```
OpenAI API error: 401 Unauthorized
```

**Fix**: Check `OPENROUTER_API_KEY` in `.env` file

### WebSocket Connection Failed

```
WebSocket connection to 'ws://localhost:8000/ws' failed
```

**Fix**: 
- Ensure server is running
- Check CORS configuration
- Verify session_id exists

### Agent Not Responding

**Check**:
- MCP servers started (logs should show "MCP server started")
- Hypergraph memory file exists
- Database connection working

---

## Production Deployment

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn backend.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment

- Update CORS origins in `server.py`
- Use production database
- Set secure environment variables
- Enable HTTPS

---

## Contributing

This is the backend for Strudel Agent. The frontend is built with Svelte + shadcn-svelte.

**Key files to modify**:
- `server.py` - Add new endpoints
- `src/db/models.py` - Add new database models
- `src/db/crud.py` - Add new CRUD operations
- `src/mcp/strudel_server.py` - Add new MCP tools
- `agents/strudel.md` - Update agent prompt

---

## License

MIT
