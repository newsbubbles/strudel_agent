# Database Architecture - Tooler Example Analysis

**Date**: 2025-12-25  
**Purpose**: Document database schema, models, and CRUD operations from tooler_example  
**For**: Backend implementation reference  
**Source**: `tooler_example_for_answers/src/db/`

---

## Overview

Tooler uses **PostgreSQL** with **SQLModel** (SQLAlchemy + Pydantic) for database operations.

**Key features**:
- Async database operations (asyncio + asyncpg)
- JSONB columns for flexible metadata storage
- Foreign key cascades for data integrity
- Session-based message history
- Memory file tracking

---

## Database Technology Stack

```python
# Core libraries
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.dialects.postgresql import JSONB
```

**Why SQLModel?**
- Combines SQLAlchemy (ORM) + Pydantic (validation)
- Single model definition for database AND API
- Type safety with Python type hints
- Async support out of the box

**Why PostgreSQL?**
- JSONB support for flexible metadata
- Robust async driver (asyncpg)
- Production-ready with good performance

---

## Schema Overview

### Tables

1. **`sessions`** - Session metadata and configuration
2. **`messages`** - Message history (simplified for frontend)
3. **`memory_files`** - Hypergraph memory file tracking

### Relationships

```
sessions (1) ----< (N) messages
    |                   |
    |                   └─ ON DELETE CASCADE
    |
    └----< (N) memory_files
                    |
                    └─ ON DELETE CASCADE
```

---

## 1. Sessions Table

### Schema (`schema.sql`)

```sql
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50),
    use_claude_code BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    current_project VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT valid_status CHECK (status IN ('active', 'idle', 'terminated'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_sessions_agent_name ON sessions(agent_name);
```

### SQLModel Definition (`models.py`)

```python
class SessionBase(SQLModel):
    """Base session fields (shared between table and API models)."""
    agent_name: str
    model_name: Optional[str] = None
    provider: Optional[str] = None
    use_claude_code: bool = False
    current_project: Optional[str] = None

class Session(SessionBase, table=True):
    """Session table model."""
    __tablename__ = "sessions"
    
    session_id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active")  # active, idle, terminated
    metadata_: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, name="metadata")
    )

class SessionCreate(SessionBase):
    """Session creation input (API)."""
    session_name: Optional[str] = Field(None, description="Custom session name")

class SessionRead(SessionBase):
    """Session read output (API)."""
    session_id: UUID
    created_at: datetime
    last_activity: datetime
    status: str
    message_count: int = 0
    session_name: Optional[str] = Field(None, description="Custom session name from metadata")
    display_name: Optional[str] = Field(None, description="Computed display name")
```

### Fields Explained

| Field | Type | Purpose |
|-------|------|----------|
| `session_id` | UUID | Primary key, auto-generated |
| `agent_name` | VARCHAR(50) | Agent type (tooler, devmate, etc.) |
| `model_name` | VARCHAR(100) | LLM model (grok-4-fast, etc.) |
| `provider` | VARCHAR(50) | Provider (openrouter, anthropic) |
| `use_claude_code` | BOOLEAN | Use Claude Code model (skip for Strudel) |
| `created_at` | TIMESTAMP | Session creation time |
| `last_activity` | TIMESTAMP | Last message/activity time |
| `status` | VARCHAR(20) | active, idle, terminated |
| `current_project` | VARCHAR(255) | Current working project |
| `metadata` | JSONB | **Flexible metadata storage** |

### Metadata Field Usage

**Purpose**: Store arbitrary session data without schema changes

**Example metadata**:
```json
{
  "name": "Debug Auth Flow",
  "created_by_user": true,
  "tags": ["authentication", "debugging"],
  "custom_settings": {
    "temperature": 0.7,
    "max_tokens": 4000
  }
}
```

**For Strudel Agent**:
```json
{
  "item_type": "clip",
  "item_id": "kick",
  "project_id": "house_project",
  "bpm": 120,
  "scale": "C minor"
}
```

### Session Status Values

- **`active`**: Session currently in use (WebSocket connected)
- **`idle`**: Session inactive but not terminated (can reconnect)
- **`terminated`**: Session ended (cleanup candidate)

### CRUD Operations (`crud.py`)

#### Create Session

```python
async def create_session(
    db: AsyncSession,
    session_data: SessionCreate
) -> Session:
    db_session = Session.model_validate(session_data)
    
    # Store session name in metadata if provided
    if session_data.session_name:
        db_session.metadata_ = {
            **db_session.metadata_,
            "name": session_data.session_name,
            "created_by_user": True
        }
    
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session
```

#### Get Session

```python
async def get_session(
    db: AsyncSession,
    session_id: UUID
) -> Optional[Session]:
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    return result.scalar_one_or_none()
```

#### List Sessions

```python
async def list_sessions(
    db: AsyncSession,
    status: Optional[str] = None
) -> List[Session]:
    query = select(Session)
    
    if status:
        query = query.where(Session.status == status)
    
    query = query.order_by(Session.last_activity.desc())
    result = await db.execute(query)
    return result.scalars().all()
```

#### Update Session Activity

```python
async def update_session_activity(
    db: AsyncSession,
    session_id: UUID
) -> Optional[Session]:
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    db_session = result.scalar_one_or_none()
    
    if db_session:
        db_session.last_activity = datetime.now()
        await db.commit()
        await db.refresh(db_session)
    
    return db_session
```

#### Update Session Status

```python
async def update_session_status(
    db: AsyncSession,
    session_id: UUID,
    status: str
) -> Optional[Session]:
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    db_session = result.scalar_one_or_none()
    
    if db_session:
        db_session.status = status
        await db.commit()
        await db.refresh(db_session)
    
    return db_session
```

#### Update Session Name

```python
async def update_session_name(
    db: AsyncSession,
    session_id: UUID,
    name_update: SessionNameUpdate
) -> Optional[Session]:
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    db_session = result.scalar_one_or_none()
    
    if db_session:
        metadata = db_session.metadata_ or {}
        
        if name_update.name is not None:
            # Set or update name
            metadata["name"] = name_update.name
            metadata["created_by_user"] = True
        else:
            # Clear name (remove from metadata)
            metadata.pop("name", None)
            metadata.pop("created_by_user", None)
        
        db_session.metadata_ = metadata
        await db.commit()
        await db.refresh(db_session)
    
    return db_session
```

---

## 2. Messages Table

### Schema (`schema.sql`)

```sql
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    message_index INTEGER NOT NULL,
    message_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_session_message UNIQUE (session_id, message_index)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_index ON messages(session_id, message_index);
```

### SQLModel Definition (`models.py`)

```python
class MessageBase(SQLModel):
    """Base message fields."""
    session_id: UUID = Field(foreign_key="sessions.session_id")
    message_index: int
    message_data: dict = Field(sa_column=Column(JSONB))

class Message(MessageBase, table=True):
    """Message table model."""
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

class MessageCreate(MessageBase):
    """Message creation input."""
    pass
```

### Fields Explained

| Field | Type | Purpose |
|-------|------|----------|
| `id` | BIGSERIAL | Auto-increment primary key |
| `session_id` | UUID | Foreign key to sessions |
| `message_index` | INTEGER | Sequential index within session |
| `message_data` | JSONB | **Message content (simplified)** |
| `created_at` | TIMESTAMP | Message creation time |

### Message Data Format

**Simplified for frontend display**:
```json
{
  "role": "user",
  "content": "How do I fix this bug?",
  "timestamp": "2025-12-25T01:35:06Z"
}
```

```json
{
  "role": "assistant",
  "content": "Let me help you debug this...",
  "timestamp": "2025-12-25T01:35:12Z"
}
```

**NOT stored in database**:
- Tool calls
- Thinking parts
- Internal agent state
- Model metadata

**Why simplified?**
- Frontend only needs role + content for display
- Full history stored in pickle files
- Reduces database size
- Faster pagination queries

### Message Index

**Purpose**: Sequential ordering within session

**Example**:
```
session_id: abc-123
  message_index: 0 -> "Hello"
  message_index: 1 -> "Hi! How can I help?"
  message_index: 2 -> "I need help with..."
  message_index: 3 -> "Sure, let me..."
```

**Unique constraint**: `(session_id, message_index)` must be unique

### CRUD Operations (`crud.py`)

#### Save Display Messages (Append)

```python
async def save_display_messages(
    db: AsyncSession,
    session_id: UUID,
    messages: List[dict]
) -> None:
    """Save simplified display messages for frontend.
    
    Args:
        session_id: Session UUID
        messages: List of {"role": str, "content": str, "timestamp": str}
    """
    # Get current message count to determine starting index
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.message_index.desc())
        .limit(1)
    )
    last_message = result.scalar_one_or_none()
    next_index = (last_message.message_index + 1) if last_message else 0
    
    # Insert simplified messages
    for idx, msg_data in enumerate(messages):
        db_message = Message(
            session_id=session_id,
            message_index=next_index + idx,
            message_data=msg_data  # Simplified: {role, content, timestamp}
        )
        db.add(db_message)
    
    await db.commit()
```

**Key points**:
- **Appends** messages (doesn't delete existing)
- Calculates next index from last message
- Only stores simplified display format

#### Load Messages (Paginated)

```python
async def load_messages_paginated(
    db: AsyncSession,
    session_id: UUID,
    page_size: int = 50,
    before_index: Optional[int] = None
) -> List[dict]:
    """Load paginated messages in chronological order.
    
    Args:
        db: Database session
        session_id: Session UUID
        page_size: Number of messages to load (default: 50)
        before_index: Load messages before this index (for pagination)
    
    Returns:
        List of message dicts (message_data + message_index) in chronological order
    """
    query = select(Message).where(Message.session_id == session_id)
    
    if before_index is not None:
        query = query.where(Message.message_index < before_index)
    
    # Get last N messages (newest first)
    query = query.order_by(Message.message_index.desc()).limit(page_size)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Reverse to chronological order and merge message_index into dict
    return [
        {**msg.message_data, "message_index": msg.message_index}
        for msg in reversed(messages)
    ]
```

**Pagination flow**:
1. Initial load: `page_size=50, before_index=None` → Last 50 messages
2. Load more: `page_size=50, before_index=oldest_loaded_index` → Previous 50 messages

**Example**:
```python
# Initial load (most recent 50)
result = await load_messages_paginated(db, session_id, page_size=50)
# Returns: messages with index 150-199 (if total is 200)

# Load more (scroll up)
result = await load_messages_paginated(db, session_id, page_size=50, before_index=150)
# Returns: messages with index 100-149
```

#### Get Message Count

```python
async def get_message_count(
    db: AsyncSession,
    session_id: UUID
) -> int:
    result = await db.execute(
        select(Message).where(Message.session_id == session_id)
    )
    return len(result.scalars().all())
```

---

## 3. Memory Files Table

### Schema (`schema.sql`)

```sql
CREATE TABLE IF NOT EXISTS memory_files (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    loaded BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_session_file UNIQUE (session_id, file_path)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_memory_session_id ON memory_files(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_file_path ON memory_files(file_path);
```

### SQLModel Definition (`models.py`)

```python
class MemoryFileBase(SQLModel):
    """Base memory file fields."""
    session_id: UUID = Field(foreign_key="sessions.session_id")
    file_path: str
    is_primary: bool = False
    loaded: bool = True

class MemoryFile(MemoryFileBase, table=True):
    """Memory file table model."""
    __tablename__ = "memory_files"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MemoryFileCreate(MemoryFileBase):
    """Memory file creation input."""
    pass
```

### Fields Explained

| Field | Type | Purpose |
|-------|------|----------|
| `id` | SERIAL | Auto-increment primary key |
| `session_id` | UUID | Foreign key to sessions |
| `file_path` | VARCHAR(500) | Path to hypergraph JSON file |
| `is_primary` | BOOLEAN | Is this the main memory file? |
| `loaded` | BOOLEAN | Is this file currently loaded? |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

### Purpose

**Tracks hypergraph memory files** used by session:
- Primary memory file (session-scoped)
- Linked memory files (loaded via hyperlinks)
- Load status tracking

**Example**:
```
session_id: abc-123
  file_path: memory/sessions/abc-123/memory.json
  is_primary: true
  loaded: true
  
  file_path: memory/knowledge/strudel_patterns.json
  is_primary: false
  loaded: true
```

### CRUD Operations (`crud.py`)

#### Create Memory File

```python
async def create_memory_file(
    db: AsyncSession,
    memory_data: MemoryFileCreate
) -> MemoryFile:
    db_memory = MemoryFile.model_validate(memory_data)
    db.add(db_memory)
    await db.commit()
    await db.refresh(db_memory)
    return db_memory
```

#### Get Session Memory Files

```python
async def get_session_memory_files(
    db: AsyncSession,
    session_id: UUID
) -> List[MemoryFile]:
    result = await db.execute(
        select(MemoryFile).where(MemoryFile.session_id == session_id)
    )
    return result.scalars().all()
```

#### Get Primary Memory File

```python
async def get_primary_memory_file(
    db: AsyncSession,
    session_id: UUID
) -> Optional[MemoryFile]:
    result = await db.execute(
        select(MemoryFile)
        .where(MemoryFile.session_id == session_id)
        .where(MemoryFile.is_primary == True)
    )
    return result.scalar_one_or_none()
```

---

## 4. Database Connection (`connection.py`)

### Configuration

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = os.getenv('TOOLER_DB_URL')
# Example: postgresql+asyncpg://user:pass@localhost/tooler

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Check connection health
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args={
        "command_timeout": 30,
        "statement_cache_size": 512,
    }
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL for async
)
```

### Connection Pool Settings

| Setting | Value | Purpose |
|---------|-------|----------|
| `pool_size` | 10 | Base connection pool size |
| `max_overflow` | 20 | Additional connections when busy |
| `pool_pre_ping` | True | Verify connection before use |
| `pool_recycle` | 3600 | Recycle after 1 hour |
| `command_timeout` | 30 | Query timeout (seconds) |
| `expire_on_commit` | False | **Required for async** |

### Initialization

```python
async def init_db():
    """Initialize database tables."""
    # Import all models to register them
    from .models import Session, Message, MemoryFile
    
    async with engine.begin() as conn:
        # Use run_sync for non-async metadata operations
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("Database tables initialized")
```

**Called on app startup** (see `server.py` lifespan):
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()
```

### FastAPI Dependency

```python
async def get_session() -> AsyncSession:
    """Get database session (FastAPI dependency)."""
    async with async_session() as session:
        yield session
```

**Usage in routes**:
```python
@app.get("/api/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_session)
):
    sessions = await db_list_sessions(db)
    return sessions
```

### Cleanup

```python
async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
```

---

## 5. Database Patterns for Strudel Agent

### Adapted Sessions Table

**Add item metadata to sessions**:

```sql
-- Same base structure
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL DEFAULT 'strudel',
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    
    -- Strudel-specific fields
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT valid_status CHECK (status IN ('active', 'idle', 'terminated'))
);
```

**Metadata for Strudel sessions**:
```json
{
  "item_type": "clip",
  "item_id": "kick",
  "project_id": "house_project",
  "bpm": 120,
  "scale": "C minor",
  "loaded_in_carousel": true,
  "panel_index": 0
}
```

### Additional Tables for Strudel

#### Clips Table

```sql
CREATE TABLE IF NOT EXISTS clips (
    clip_id VARCHAR(100) PRIMARY KEY,
    project_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    code TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_clips_project ON clips(project_id);
```

**Metadata example**:
```json
{
  "bpm": 120,
  "scale": "C minor",
  "tags": ["drums", "kick"],
  "color": "#FF5733"
}
```

#### Songs Table

```sql
CREATE TABLE IF NOT EXISTS songs (
    song_id VARCHAR(100) PRIMARY KEY,
    project_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    clip_ids JSONB DEFAULT '[]'::jsonb,  -- Array of clip IDs
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_songs_project ON songs(project_id);
```

**clip_ids format**:
```json
["kick", "bass", "hats", "melody"]
```

#### Playlists Table

```sql
CREATE TABLE IF NOT EXISTS playlists (
    playlist_id VARCHAR(100) PRIMARY KEY,
    project_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    song_ids JSONB DEFAULT '[]'::jsonb,  -- Array of song IDs
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_playlists_project ON playlists(project_id);
```

### Message Data for Strudel

**Include context in message_data**:
```json
{
  "role": "user",
  "content": "Make the kick punchier",
  "timestamp": "2025-12-25T01:35:06Z",
  "context": {
    "item_type": "clip",
    "item_id": "kick",
    "code_snapshot": "sound('bd').gain(0.8)"
  }
}
```

```json
{
  "role": "assistant",
  "content": "I'll increase the gain and add some distortion",
  "timestamp": "2025-12-25T01:35:12Z",
  "code_changes": {
    "before": "sound('bd').gain(0.8)",
    "after": "sound('bd').gain(1.2).distort(0.3)"
  }
}
```

---

## 6. Environment Variables

### Required

```bash
# Database connection
TOOLER_DB_URL=postgresql+asyncpg://user:password@localhost:5432/strudel_agent

# API keys
OPENROUTER_API_KEY=sk-or-v1-...
```

### Optional

```bash
# Database pool settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600

# Logging
DB_ECHO=false  # Set to true for SQL query logging
```

---

## 7. Migration Strategy

### Development (Pre-production)

**Simple approach** (no migrations needed):
1. Drop all tables
2. Recreate from SQLModel
3. Restart app

```python
# In init_db()
async with engine.begin() as conn:
    # Drop all tables (DEVELOPMENT ONLY)
    await conn.run_sync(SQLModel.metadata.drop_all)
    # Recreate
    await conn.run_sync(SQLModel.metadata.create_all)
```

### Production (Future)

**Use Alembic** for migrations:
```bash
alembic init alembic
alembic revision --autogenerate -m "Add clips table"
alembic upgrade head
```

**But for now**: Pre-production = just recreate tables

---

## 8. Database Best Practices

### Async Patterns

**DO**:
```python
async def get_session(db: AsyncSession, session_id: UUID):
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    return result.scalar_one_or_none()
```

**DON'T**:
```python
# This will fail with async
session = db.query(Session).filter_by(session_id=session_id).first()
```

### Transaction Management

**Automatic commits in FastAPI dependencies**:
```python
@app.post("/api/sessions")
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_session)
):
    # db.commit() called automatically at end of request
    new_session = await db_create_session(db, session_data)
    return new_session
```

**Manual transactions** (for complex operations):
```python
async with async_session() as db:
    async with db.begin():
        # Multiple operations
        session = await create_session(db, session_data)
        await create_memory_file(db, memory_data)
        # Commits automatically at end of block
```

### Error Handling

```python
from sqlalchemy.exc import IntegrityError

try:
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    raise HTTPException(
        status_code=409,
        detail="Session already exists"
    )
```

### JSONB Queries

**Filter by JSONB field**:
```python
from sqlalchemy import cast, String

# Get sessions with specific item_type
result = await db.execute(
    select(Session).where(
        Session.metadata_['item_type'].astext == 'clip'
    )
)
```

**Update JSONB field**:
```python
session.metadata_ = {
    **session.metadata_,
    "new_field": "new_value"
}
await db.commit()
```

---

## 9. Testing Database Operations

### Test Database Setup

```python
import pytest
from sqlmodel import create_engine, Session
from sqlmodel.pool import StaticPool

@pytest.fixture(name="session")
def session_fixture():
    # In-memory SQLite for tests
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

### Example Test

```python
async def test_create_session(session):
    session_data = SessionCreate(
        agent_name="strudel",
        model_name="grok-4-fast",
        session_name="Test Session"
    )
    
    db_session = await create_session(session, session_data)
    
    assert db_session.agent_name == "strudel"
    assert db_session.metadata_["name"] == "Test Session"
```

---

## 10. Implementation Checklist for Strudel Agent

### Database Setup

- [ ] **Install dependencies**
  ```bash
  pip install sqlmodel asyncpg psycopg2-binary
  ```

- [ ] **Create PostgreSQL database**
  ```bash
  createdb strudel_agent
  ```

- [ ] **Set environment variable**
  ```bash
  export TOOLER_DB_URL="postgresql+asyncpg://user:pass@localhost/strudel_agent"
  ```

### Code Structure

- [ ] **Create `src/db/` folder**
  - [ ] `connection.py` - Database engine and session factory
  - [ ] `models.py` - SQLModel definitions
  - [ ] `crud.py` - CRUD operations
  - [ ] `schema.sql` - Reference schema (optional)

- [ ] **Define models**
  - [ ] Session model (with Strudel metadata)
  - [ ] Message model (with context)
  - [ ] Clip model
  - [ ] Song model
  - [ ] Playlist model
  - [ ] MemoryFile model

- [ ] **Implement CRUD operations**
  - [ ] Session CRUD
  - [ ] Message CRUD (with pagination)
  - [ ] Clip CRUD
  - [ ] Song CRUD
  - [ ] Playlist CRUD

- [ ] **Initialize in FastAPI**
  - [ ] Add `init_db()` to lifespan
  - [ ] Add `get_session()` dependency
  - [ ] Add `close_db()` to shutdown

### API Integration

- [ ] **Session endpoints**
  - [ ] `POST /api/sessions` - Create session
  - [ ] `GET /api/sessions` - List sessions
  - [ ] `GET /api/sessions/{id}` - Get session
  - [ ] `DELETE /api/sessions/{id}` - Delete session

- [ ] **Message endpoints**
  - [ ] `GET /api/messages/{session_id}` - Paginated messages

- [ ] **Item endpoints**
  - [ ] `GET /api/clips` - List clips
  - [ ] `POST /api/clips` - Create clip
  - [ ] `GET /api/clips/{id}` - Get clip
  - [ ] `PUT /api/clips/{id}` - Update clip
  - [ ] `DELETE /api/clips/{id}` - Delete clip
  - [ ] (Same for songs, playlists)

---

## Summary

The Tooler database architecture provides:
- ✅ **Async PostgreSQL** with SQLModel
- ✅ **Session management** with flexible metadata
- ✅ **Message history** with pagination
- ✅ **Memory file tracking**
- ✅ **Clean CRUD operations**
- ✅ **Production-ready patterns**

**For Strudel Agent**: Copy the structure, add Clip/Song/Playlist tables, adapt metadata for item context.

**Key takeaway**: The database is simple and focused. Don't overcomplicate it. Use JSONB for flexibility, keep tables normalized, and rely on async patterns.
