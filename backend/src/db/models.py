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
    
    # Strudel-specific fields
    session_type: str = Field(description="clip, song, playlist, or pack")
    item_id: str = Field(description="ID of the clip/song/playlist/pack")
    project_id: str = Field(description="Strudel project ID")

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
    message_data: dict = Field(sa_column=Column(JSONB))

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

# ============================================================================
# Clips
# ============================================================================

class ClipBase(SQLModel):
    """Base clip fields."""
    clip_id: str = Field(description="Unique clip identifier")
    project_id: str = Field(description="Project this clip belongs to")
    name: str = Field(description="Clip name")
    code: str = Field(description="Strudel code")

class Clip(ClipBase, table=True):
    """Clip table model."""
    __tablename__ = "clips"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata_: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, name="metadata")
    )

class ClipCreate(ClipBase):
    """Clip creation input."""
    metadata: Optional[dict] = None

class ClipUpdate(SQLModel):
    """Clip update input."""
    name: Optional[str] = None
    code: Optional[str] = None
    metadata: Optional[dict] = None

class ClipRead(ClipBase):
    """Clip read output."""
    id: int
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(default_factory=dict)

# ============================================================================
# Songs
# ============================================================================

class SongBase(SQLModel):
    """Base song fields."""
    song_id: str = Field(description="Unique song identifier")
    project_id: str = Field(description="Project this song belongs to")
    name: str = Field(description="Song name")

class Song(SongBase, table=True):
    """Song table model."""
    __tablename__ = "songs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    clip_ids: list = Field(
        default_factory=list,
        sa_column=Column(JSONB, name="clip_ids")
    )
    metadata_: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, name="metadata")
    )

class SongCreate(SongBase):
    """Song creation input."""
    clip_ids: Optional[list] = None
    metadata: Optional[dict] = None

class SongUpdate(SQLModel):
    """Song update input."""
    name: Optional[str] = None
    clip_ids: Optional[list] = None
    metadata: Optional[dict] = None

class SongRead(SongBase):
    """Song read output."""
    id: int
    created_at: datetime
    updated_at: datetime
    clip_ids: list = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

# ============================================================================
# Playlists
# ============================================================================

class PlaylistBase(SQLModel):
    """Base playlist fields."""
    playlist_id: str = Field(description="Unique playlist identifier")
    project_id: str = Field(description="Project this playlist belongs to")
    name: str = Field(description="Playlist name")

class Playlist(PlaylistBase, table=True):
    """Playlist table model."""
    __tablename__ = "playlists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    song_ids: list = Field(
        default_factory=list,
        sa_column=Column(JSONB, name="song_ids")
    )
    metadata_: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB, name="metadata")
    )

class PlaylistCreate(PlaylistBase):
    """Playlist creation input."""
    song_ids: Optional[list] = None
    metadata: Optional[dict] = None

class PlaylistUpdate(SQLModel):
    """Playlist update input."""
    name: Optional[str] = None
    song_ids: Optional[list] = None
    metadata: Optional[dict] = None

class PlaylistRead(PlaylistBase):
    """Playlist read output."""
    id: int
    created_at: datetime
    updated_at: datetime
    song_ids: list = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
