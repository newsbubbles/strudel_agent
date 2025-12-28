"""Database CRUD operations."""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import (
    Session, SessionCreate, SessionNameUpdate,
    Message, MessageCreate,
    MemoryFile, MemoryFileCreate,
)

# ============================================================================
# Sessions
# ============================================================================

async def create_session(
    db: AsyncSession,
    session_data: SessionCreate
) -> Session:
    """Create a new session."""
    # Create session from base fields
    session_dict = session_data.model_dump(exclude={'session_id', 'session_name'})
    db_session = Session(**session_dict)
    
    # Use client-provided session_id if available
    if session_data.session_id:
        db_session.session_id = session_data.session_id
    
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

async def get_session(
    db: AsyncSession,
    session_id: UUID
) -> Optional[Session]:
    """Get session by ID."""
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    return result.scalar_one_or_none()

async def list_sessions(
    db: AsyncSession,
    status: Optional[str] = None,
    project_id: Optional[str] = None
) -> List[Session]:
    """List sessions with optional filtering."""
    query = select(Session)
    
    if status:
        query = query.where(Session.status == status)
    
    if project_id:
        query = query.where(Session.project_id == project_id)
    
    query = query.order_by(Session.last_activity.desc())
    result = await db.execute(query)
    return result.scalars().all()

async def update_session_activity(
    db: AsyncSession,
    session_id: UUID
) -> Optional[Session]:
    """Update session last_activity timestamp."""
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    db_session = result.scalar_one_or_none()
    
    if db_session:
        db_session.last_activity = datetime.now()
        await db.commit()
        await db.refresh(db_session)
    
    return db_session

async def update_session_status(
    db: AsyncSession,
    session_id: UUID,
    status: str
) -> Optional[Session]:
    """Update session status."""
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    db_session = result.scalar_one_or_none()
    
    if db_session:
        db_session.status = status
        await db.commit()
        await db.refresh(db_session)
    
    return db_session

async def update_session_name(
    db: AsyncSession,
    session_id: UUID,
    name_update: SessionNameUpdate
) -> Optional[Session]:
    """Update session name."""
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    db_session = result.scalar_one_or_none()
    
    if db_session:
        metadata = db_session.metadata_ or {}
        
        if name_update.name is not None:
            metadata["name"] = name_update.name
            metadata["created_by_user"] = True
        else:
            metadata.pop("name", None)
            metadata.pop("created_by_user", None)
        
        db_session.metadata_ = metadata
        await db.commit()
        await db.refresh(db_session)
    
    return db_session

async def delete_session(
    db: AsyncSession,
    session_id: UUID
) -> bool:
    """Delete a session."""
    result = await db.execute(
        delete(Session).where(Session.session_id == session_id)
    )
    await db.commit()
    return result.rowcount > 0

# ============================================================================
# Messages
# ============================================================================

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
            message_data=msg_data
        )
        db.add(db_message)
    
    await db.commit()

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

async def get_message_count(
    db: AsyncSession,
    session_id: UUID
) -> int:
    """Get message count for a session."""
    result = await db.execute(
        select(Message).where(Message.session_id == session_id)
    )
    return len(result.scalars().all())

# ============================================================================
# Memory Files
# ============================================================================

async def create_memory_file(
    db: AsyncSession,
    memory_data: MemoryFileCreate
) -> MemoryFile:
    """Create a memory file record."""
    db_memory = MemoryFile.model_validate(memory_data)
    db.add(db_memory)
    await db.commit()
    await db.refresh(db_memory)
    return db_memory

async def get_session_memory_files(
    db: AsyncSession,
    session_id: UUID
) -> List[MemoryFile]:
    """Get all memory files for a session."""
    result = await db.execute(
        select(MemoryFile).where(MemoryFile.session_id == session_id)
    )
    return result.scalars().all()

async def get_primary_memory_file(
    db: AsyncSession,
    session_id: UUID
) -> Optional[MemoryFile]:
    """Get primary memory file for a session."""
    result = await db.execute(
        select(MemoryFile)
        .where(MemoryFile.session_id == session_id)
        .where(MemoryFile.is_primary == True)
    )
    return result.scalar_one_or_none()
