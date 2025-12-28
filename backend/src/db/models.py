"""SQLModel database models for Strudel Agent."""

from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB

# ============================================================================
# Sessions
# ============================================================================

class SessionBase(SQLModel):
    """Base session fields (shared between table and API models)."""
    agent_name: str = Field(default="strudel")
    model_name: str = Field(default="x-ai/grok-beta")
    provider: Optional[str] = Field(default="openrouter")
    
    # Strudel-specific fields (optional for general chat sessions)
    session_type: str = Field(default="chat", description="chat or other session types")
    item_id: Optional[str] = Field(default=None, description="Optional item ID")
    project_id: Optional[str] = Field(default=None, description="Optional project ID")

class Session(SessionBase, table=True):
    """Session table model."""
    __tablename__ = "sessions"
    
    session_id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="active")  # active, idle, terminated
    metadata_: Optional[dict] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, name="metadata", nullable=True)
    )

class SessionCreate(SessionBase):
    """Session creation input (API)."""
    session_id: Optional[UUID] = Field(None, description="Optional client-provided session ID")
    session_name: Optional[str] = Field(None, description="Custom session name")

class SessionRead(SessionBase):
    """Session read output (API)."""
    session_id: UUID
    created_at: datetime
    last_activity: datetime
    status: str
    message_count: int = 0
    session_name: Optional[str] = Field(None, description="Custom session name from metadata")

class SessionNameUpdate(SQLModel):
    """Update session name."""
    name: Optional[str] = Field(None, description="New name (null to clear)")

# ============================================================================
# Messages
# ============================================================================

class MessageBase(SQLModel):
    """Base message fields."""
    session_id: UUID = Field(foreign_key="sessions.session_id")
    message_index: int
    message_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))

class Message(MessageBase, table=True):
    """Message table model."""
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

class MessageCreate(MessageBase):
    """Message creation input."""
    pass

# ============================================================================
# Memory Files
# ============================================================================

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
