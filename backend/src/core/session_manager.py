"""Session lifecycle management for Strudel Agent."""

import logging
import json
import pickle
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart

from backend.src.db import (
    async_session,
    SessionCreate,
    create_session as db_create_session,
    get_session_by_id as db_get_session,
    update_session_activity,
    update_session_status,
    save_display_messages,
    create_memory_file,
)
from backend.src.db.models import MemoryFileCreate
from backend.src.core.agent_factory import create_agent

logger = logging.getLogger(__name__)

class SessionState:
    """Runtime state for an active session."""
    
    def __init__(self, session_id: UUID, config: SessionCreate):
        self.session_id = session_id
        self.config = config
        self.agent: Optional[Agent] = None
        self.conversation_history: list[ModelMessage] = []
        self.last_activity = datetime.now()
        
        # Strudel-specific context
        self.session_type = config.session_type  # clip, song, playlist, pack
        self.item_id = config.item_id
        self.project_id = config.project_id
    
    def to_dict(self):
        return {
            'session_id': str(self.session_id),
            'session_type': self.session_type,
            'item_id': self.item_id,
            'project_id': self.project_id,
            'agent': self.config.agent_name,
            'last_activity': str(self.last_activity),
            'message_count': len(self.conversation_history),
        }
    
    async def initialize_agent(self):
        """Initialize agent instance."""
        self.agent = create_agent(self.session_id, self.config)
        logger.info(f"Agent initialized for session {self.session_id}")
    
    async def add_messages(self, new_messages_obj: List[ModelMessage]):
        """Add new messages to history and persist.
        
        Args:
            new_messages_obj: List of ModelMessage objects from response.new_messages()
        """
        # Append to in-memory history
        self.conversation_history.extend(new_messages_obj)
        
        # Save full history to pickle file
        await self.save_conversation_history_to_file()
        
        # Extract simplified messages for database
        display_messages = self._extract_display_messages_from_objects(new_messages_obj)
        
        # Save to database for frontend
        async with async_session() as db:
            await save_display_messages(db, self.session_id, display_messages)
            await update_session_activity(db, self.session_id)
        
        logger.debug(f"Saved {len(new_messages_obj)} messages (pickle + DB)")
    
    def _extract_display_messages_from_objects(self, messages_obj: List[ModelMessage]) -> List[dict]:
        """Extract simplified messages for frontend display.
        
        Only the LAST ModelResponse is saved as a display message.
        Intermediate ModelResponse objects (tool calls) are filtered out.
        
        Args:
            messages_obj: List of pydantic-ai ModelMessage objects
        
        Returns:
            List of {"role": str, "content": str, "timestamp": str}
        """
        display_messages = []
        now = datetime.now().isoformat()
        
        # Find the index of the LAST ModelResponse
        last_response_index = None
        for i in range(len(messages_obj) - 1, -1, -1):
            if isinstance(messages_obj[i], ModelResponse):
                last_response_index = i
                break
        
        for i, msg in enumerate(messages_obj):
            timestamp = now
            
            # Handle ModelRequest (user messages)
            if isinstance(msg, ModelRequest):
                for part in msg.parts:
                    if isinstance(part, UserPromptPart):
                        display_messages.append({
                            "role": "user",
                            "content": part.content,
                            "timestamp": timestamp
                        })
            
            # Handle ModelResponse (assistant messages)
            # ONLY process the LAST ModelResponse in the list
            elif isinstance(msg, ModelResponse) and i == last_response_index:
                content_parts = []
                for part in msg.parts:
                    if isinstance(part, TextPart):
                        content_parts.append(part.content)
                
                if content_parts:
                    display_messages.append({
                        "role": "assistant",
                        "content": content_parts[-1],  # Use last text part
                        "timestamp": timestamp
                    })
        
        return display_messages
    
    async def save_conversation_history_to_file(self):
        """Persist full conversation history to pickle file."""
        history_file = Path("memory/sessions") / str(self.session_id) / "conversation_history.pkl"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with history_file.open('wb') as f:
                pickle.dump(self.conversation_history, f)
            logger.debug(f"Saved {len(self.conversation_history)} messages to {history_file}")
        except Exception as e:
            logger.error(f"Failed to save conversation history: {e}", exc_info=True)
            raise
    
    async def load_conversation_history_from_file(self):
        """Load full conversation history from pickle file."""
        history_file = Path("memory/sessions") / str(self.session_id) / "conversation_history.pkl"
        
        if not history_file.exists():
            logger.info(f"No conversation history file found for session {self.session_id}")
            return
        
        try:
            with history_file.open('rb') as f:
                self.conversation_history = pickle.load(f)
            logger.info(f"Loaded {len(self.conversation_history)} messages from {history_file}")
        except Exception as e:
            logger.warning(f"Failed to load conversation history: {e}")
            self.conversation_history = []
    
    async def load_history(self):
        """Load conversation history from pickle file."""
        await self.load_conversation_history_from_file()


class SessionManager:
    """Manage session lifecycle."""
    
    def __init__(self):
        self.sessions: Dict[UUID, SessionState] = {}
        logger.info("SessionManager initialized")
    
    async def create_session(self, config: SessionCreate) -> SessionState:
        """Create a new session.
        
        Args:
            config: Session configuration
            
        Returns:
            SessionState instance
        """
        # Create session in database
        async with async_session() as db:
            db_session = await db_create_session(db, config)
            session_id = db_session.session_id
        
        # Initialize memory file structure
        await self._initialize_memory(session_id)
        
        # Create session state
        session_state = SessionState(session_id, config)
        await session_state.initialize_agent()
        
        self.sessions[session_id] = session_state
        
        logger.info(f"Created session {session_id}: {config.session_type}/{config.item_id}")
        return session_state
    
    async def get_session(self, session_id: UUID) -> Optional[SessionState]:
        """Get existing session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            SessionState if exists, None otherwise
        """
        return self.sessions.get(session_id)
    
    async def restore_session(self, session_id: UUID) -> SessionState:
        """Restore session from database.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Restored SessionState
        """
        # Load session from database
        async with async_session() as db:
            db_session = await db_get_session(db, session_id)
        
        if not db_session:
            raise ValueError(f"Session {session_id} not found in database")
        
        # Extract session name from metadata
        session_name = None
        if db_session.metadata_:
            session_name = db_session.metadata_.get('name')
        
        # Create config from database
        config = SessionCreate(
            agent_name=db_session.agent_name,
            model_name=db_session.model_name,
            provider=db_session.provider,
            session_type=db_session.session_type,
            item_id=db_session.item_id,
            project_id=db_session.project_id,
            session_name=session_name,
        )
        
        # Create session state
        session_state = SessionState(session_id, config)
        await session_state.initialize_agent()
        await session_state.load_history()
        
        self.sessions[session_id] = session_state
        
        logger.info(f"Restored session {session_id} with {len(session_state.conversation_history)} messages")
        return session_state
    
    async def terminate_session(self, session_id: UUID):
        """Terminate a session.
        
        Args:
            session_id: Session UUID
        """
        # Remove from memory
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        # Update status in database
        async with async_session() as db:
            await update_session_status(db, session_id, 'terminated')
        
        logger.info(f"Terminated session {session_id}")
    
    async def _initialize_memory(self, session_id: UUID):
        """Initialize memory file structure for session.
        
        Args:
            session_id: Session UUID
        """
        memory_dir = Path("memory/sessions") / str(session_id)  # FIXED: was self.session_id
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Create memory.json (hypergraph memory)
        memory_file = memory_dir / "memory.json"
        memory_file.write_text(json.dumps({
            "summary": f"Session memory for {session_id}",
            "nodes": {},
            "edges": []
        }))
        
        # Create empty conversation_history.pkl
        history_file = memory_dir / "conversation_history.pkl"
        with history_file.open('wb') as f:
            pickle.dump([], f)
        
        # Record files in database
        async with async_session() as db:
            # Memory file (primary)
            await create_memory_file(db, MemoryFileCreate(
                session_id=session_id,
                file_path=str(memory_file.relative_to("memory")),
                is_primary=True
            ))
            
            # Conversation history file (secondary)
            await create_memory_file(db, MemoryFileCreate(
                session_id=session_id,
                file_path=str(history_file.relative_to("memory")),
                is_primary=False
            ))
        
        logger.debug(f"Initialized memory for session {session_id}")


# Global session manager instance
session_manager = SessionManager()
