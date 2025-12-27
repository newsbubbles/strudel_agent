"""FastAPI server for Strudel Agent."""

# Load environment variables FIRST before any other imports
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory
backend_dir = Path(__file__).parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage

from src.db import (
    init_db, close_db, get_session as get_db_session, async_session,
    SessionCreate, SessionRead, SessionNameUpdate,
    ClipCreate, ClipUpdate, ClipRead,
    SongCreate, SongUpdate, SongRead,
    PlaylistCreate, PlaylistUpdate, PlaylistRead,
    create_session as db_create_session,
    get_session_by_id as db_get_session,
    list_sessions as db_list_sessions,
    delete_session as db_delete_session,
    update_session_name as db_update_session_name,
    load_messages_paginated,
    get_message_count,
)
from src.services.filesystem import FilesystemService
from src.models import (
    Handshake, UserMessage,
    ToolResponse,
)
from src.core import (
    manager, session_manager,
    SessionState,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Strudel Agent backend...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Strudel Agent backend...")
    await close_db()
    logger.info("Database connections closed")

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Strudel Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    session_id: str | None = None
    connection_id: str | None = None
    connection_type: str = 'pwa'
    
    try:
        await websocket.accept()
        logger.info("WebSocket connection accepted")
        
        # Wait for handshake
        handshake_data = await websocket.receive_json()
        handshake = Handshake(**handshake_data)
        session_id = handshake.session_id
        connection_type = handshake.client_type or 'pwa'
        
        logger.info(f"Handshake received: session={session_id}, type={connection_type}")
        
        # Register connection
        context, connection_id = await manager.connect(
            websocket, session_id, connection_type
        )
        
        # Get or restore session
        session_state = await session_manager.get_session(UUID(session_id))
        is_reconnect = session_state is not None
        
        if not session_state:
            logger.info(f"Restoring session {session_id} from database")
            session_state = await session_manager.restore_session(UUID(session_id))
        
        # Send handshake ack
        await manager.send_handshake_ack(
            session_id=session_id,
            connection_id=connection_id,
            is_reconnect=is_reconnect,
            connection_type=connection_type,
            session_info=session_state.to_dict()
        )
        
        logger.info(f"Connection {connection_id} established for session {session_id}")
        
        # MCP temporarily disabled - handle all connections the same way
        await handle_websocket_messages(
            websocket, session_id, connection_type, session_state
        )
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}/{connection_id}")
        if session_id and connection_id:
            manager.disconnect(session_id, connection_id)
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}", exc_info=True)
        if session_id and connection_id:
            manager.disconnect(session_id, connection_id)

async def handle_websocket_messages(
    websocket: WebSocket,
    session_id: str,
    connection_type: str,
    session_state: SessionState
):
    """Handle incoming WebSocket messages.
    
    Args:
        websocket: WebSocket connection
        session_id: Session ID
        connection_type: Connection type (pwa or mcp)
        session_state: Session state
    """
    while True:
        data = await websocket.receive_json()
        msg_type = data.get("type")
        
        logger.debug(f"Received message: type={msg_type}")
        
        if msg_type == "user_message":
            # User message to agent
            asyncio.create_task(
                handle_user_message(session_id, data, session_state)
            )
        elif msg_type == "tool_response":
            # PWA response to tool request
            await manager.handle_tool_response(session_id, data)
        else:
            logger.warning(f"Unknown message type: {msg_type}")

async def handle_user_message(
    session_id: str,
    data: dict,
    session_state: SessionState
):
    """Handle user message to agent.
    
    Args:
        session_id: Session ID
        data: Message data
        session_state: Session state
    """
    try:
        message = UserMessage(**data)
        
        # Send typing indicator
        await manager.send_message(session_id, {
            "type": "typing_indicator",
            "is_typing": True,
        }, target='pwa')
        
        # Build context from session
        context_str = f"""
Current context:
- Item type: {session_state.session_type}
- Item ID: {session_state.item_id}
- Project ID: {session_state.project_id}
"""
        
        if message.context:
            context_str += f"\nAdditional context: {message.context}"
        
        full_message = f"{context_str}\n\nUser message: {message.message}"
        
        # Event stream handler for tool calls
        async def event_stream_handler(ctx, stream):
            from pydantic_ai.messages import PartStartEvent, FunctionToolResultEvent
            from pydantic_ai.messages import ToolCallPart
            
            async for event in stream:
                if isinstance(event, PartStartEvent):
                    if isinstance(event.part, ToolCallPart):
                        await manager.send_message(session_id, {
                            "type": "tool_report",
                            "tool_name": event.part.tool_name,
                            "tool_call_id": event.part.tool_call_id,
                        }, target='pwa')
                
                elif isinstance(event, FunctionToolResultEvent):
                    await manager.send_message(session_id, {
                        "type": "tool_result",
                        "tool_name": event.result.tool_name,
                        "content": event.result.content,
                    }, target='pwa')
        
        # Run agent
        response = await session_state.agent.run(
            full_message,
            message_history=session_state.conversation_history,
            event_stream_handler=event_stream_handler
        )
        
        # Send response
        await manager.send_message(session_id, {
            "type": "agent_response",
            "content": response.output,
            "is_final": True,
        }, target='pwa')
        
        # Stop typing indicator
        await manager.send_message(session_id, {
            "type": "typing_indicator",
            "is_typing": False,
        }, target='pwa')
        
        # Update history
        await session_state.add_messages(response.new_messages())
        
        logger.info(f"Agent response sent for session {session_id}")
    
    except Exception as e:
        logger.error(f"Error handling user message: {e}", exc_info=True)
        await manager.send_message(session_id, {
            "type": "agent_response",
            "content": f"Error: {str(e)}",
            "is_final": True,
        }, target='pwa')

# ============================================================================
# Session Endpoints
# ============================================================================

@app.post("/api/sessions", response_model=SessionRead)
async def create_session(session_data: SessionCreate):
    """Create a new session."""
    session_state = await session_manager.create_session(session_data)
    
    async with async_session() as db:
        db_session = await db_get_session(db, session_state.session_id)
        message_count = await get_message_count(db, session_state.session_id)
    
    return SessionRead(
        session_id=db_session.session_id,
        agent_name=db_session.agent_name,
        model_name=db_session.model_name,
        provider=db_session.provider,
        session_type=db_session.session_type,
        item_id=db_session.item_id,
        project_id=db_session.project_id,
        created_at=db_session.created_at,
        last_activity=db_session.last_activity,
        status=db_session.status,
        message_count=message_count,
    )

@app.get("/api/sessions", response_model=list[SessionRead])
async def list_sessions(status: Optional[str] = None, project_id: Optional[str] = None):
    """List all sessions."""
    async with async_session() as db:
        sessions = await db_list_sessions(db, status=status, project_id=project_id)
        
        result = []
        for session in sessions:
            message_count = await get_message_count(db, session.session_id)
            result.append(SessionRead(
                session_id=session.session_id,
                agent_name=session.agent_name,
                model_name=session.model_name,
                provider=session.provider,
                session_type=session.session_type,
                item_id=session.item_id,
                project_id=session.project_id,
                created_at=session.created_at,
                last_activity=session.last_activity,
                status=session.status,
                message_count=message_count,
            ))
        
        return result

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: UUID):
    """Delete a session."""
    await session_manager.terminate_session(session_id)
    
    async with async_session() as db:
        success = await db_delete_session(db, session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True}

@app.patch("/api/sessions/{session_id}/name")
async def update_session_name(session_id: UUID, name_update: SessionNameUpdate):
    """Update session name."""
    async with async_session() as db:
        session = await db_update_session_name(db, session_id, name_update)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True}

# ============================================================================
# Message Endpoints
# ============================================================================

@app.get("/api/messages/{session_id}")
async def get_messages(
    session_id: UUID,
    page_size: int = 50,
    before_index: Optional[int] = None
):
    """Get paginated messages for a session."""
    async with async_session() as db:
        messages = await load_messages_paginated(
            db, session_id, page_size, before_index
        )
    
    return {"messages": messages}

# ============================================================================
# Project Endpoints (NEW - Filesystem-based)
# ============================================================================

class ProjectCreate(BaseModel):
    """Project creation input."""
    project_id: str
    name: str
    description: Optional[str] = ""

class ProjectUpdate(BaseModel):
    """Project update input."""
    name: Optional[str] = None
    description: Optional[str] = None

@app.get("/api/projects")
async def list_projects(query: Optional[str] = None):
    """List all projects."""
    return FilesystemService.list_projects(query)

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get a project."""
    project = FilesystemService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/projects")
async def create_project(project_data: ProjectCreate):
    """Create a new project."""
    result = FilesystemService.create_project(
        project_data.project_id,
        project_data.name,
        project_data.description or ""
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@app.put("/api/projects/{project_id}")
async def update_project(project_id: str, project_update: ProjectUpdate):
    """Update a project."""
    result = FilesystemService.update_project(
        project_id,
        project_update.name,
        project_update.description
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result

# ============================================================================
# Clip Endpoints (Filesystem-based)
# ============================================================================

@app.post("/api/clips")
async def create_clip(clip_data: ClipCreate):
    """Create a new clip."""
    result = FilesystemService.create_clip(
        clip_data.project_id,
        clip_data.clip_id,
        clip_data.name,
        clip_data.code,
        clip_data.metadata
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    # Return the created clip
    clip = FilesystemService.get_clip(clip_data.project_id, clip_data.clip_id)
    return clip

@app.get("/api/clips/{project_id}/{clip_id}")
async def get_clip(project_id: str, clip_id: str):
    """Get a clip."""
    clip = FilesystemService.get_clip(project_id, clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return clip

@app.get("/api/clips/{project_id}")
async def list_clips(project_id: str, query: Optional[str] = None):
    """List all clips for a project."""
    clips = FilesystemService.list_clips(project_id, query)
    return {"clips": clips, "total": len(clips), "project_id": project_id}

@app.put("/api/clips/{project_id}/{clip_id}")
async def update_clip(project_id: str, clip_id: str, clip_update: ClipUpdate):
    """Update a clip."""
    result = FilesystemService.update_clip(
        project_id,
        clip_id,
        clip_update.name,
        clip_update.code,
        clip_update.metadata
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    # Return the updated clip
    clip = FilesystemService.get_clip(project_id, clip_id)
    return clip

@app.delete("/api/clips/{project_id}/{clip_id}")
async def delete_clip(project_id: str, clip_id: str):
    """Delete a clip."""
    result = FilesystemService.delete_clip(project_id, clip_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return {"success": True}

# ============================================================================
# Song Endpoints (Filesystem-based)
# ============================================================================

@app.post("/api/songs")
async def create_song(song_data: SongCreate):
    """Create a new song."""
    result = FilesystemService.create_song(
        song_data.project_id,
        song_data.song_id,
        song_data.name,
        song_data.clip_ids,
        song_data.metadata
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    # Return the created song
    song = FilesystemService.get_song(song_data.project_id, song_data.song_id)
    return song

@app.get("/api/songs/{project_id}/{song_id}")
async def get_song(project_id: str, song_id: str):
    """Get a song."""
    song = FilesystemService.get_song(project_id, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@app.get("/api/songs/{project_id}")
async def list_songs(project_id: str, query: Optional[str] = None):
    """List all songs for a project."""
    songs = FilesystemService.list_songs(project_id, query)
    return {"songs": songs, "total": len(songs), "project_id": project_id}

@app.put("/api/songs/{project_id}/{song_id}")
async def update_song(project_id: str, song_id: str, song_update: SongUpdate):
    """Update a song."""
    result = FilesystemService.update_song(
        project_id,
        song_id,
        song_update.name,
        song_update.clip_ids,
        song_update.metadata
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    # Return the updated song
    song = FilesystemService.get_song(project_id, song_id)
    return song

@app.delete("/api/songs/{project_id}/{song_id}")
async def delete_song(project_id: str, song_id: str):
    """Delete a song."""
    result = FilesystemService.delete_song(project_id, song_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return {"success": True}

# ============================================================================
# Playlist Endpoints (Filesystem-based)
# ============================================================================

@app.post("/api/playlists")
async def create_playlist(playlist_data: PlaylistCreate):
    """Create a new playlist."""
    result = FilesystemService.create_playlist(
        playlist_data.project_id,
        playlist_data.playlist_id,
        playlist_data.name,
        playlist_data.song_ids,
        playlist_data.metadata
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    # Return the created playlist
    playlist = FilesystemService.get_playlist(playlist_data.project_id, playlist_data.playlist_id)
    return playlist

@app.get("/api/playlists/{project_id}/{playlist_id}")
async def get_playlist(project_id: str, playlist_id: str):
    """Get a playlist."""
    playlist = FilesystemService.get_playlist(project_id, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist

@app.get("/api/playlists/{project_id}")
async def list_playlists(project_id: str, query: Optional[str] = None):
    """List all playlists for a project."""
    playlists = FilesystemService.list_playlists(project_id, query)
    return {"playlists": playlists, "total": len(playlists), "project_id": project_id}

@app.put("/api/playlists/{project_id}/{playlist_id}")
async def update_playlist(project_id: str, playlist_id: str, playlist_update: PlaylistUpdate):
    """Update a playlist."""
    result = FilesystemService.update_playlist(
        project_id,
        playlist_id,
        playlist_update.name,
        playlist_update.song_ids,
        playlist_update.metadata
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    # Return the updated playlist
    playlist = FilesystemService.get_playlist(project_id, playlist_id)
    return playlist

@app.delete("/api/playlists/{project_id}/{playlist_id}")
async def delete_playlist(project_id: str, playlist_id: str):
    """Delete a playlist."""
    result = FilesystemService.delete_playlist(project_id, playlist_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return {"success": True}

# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8034,
        reload=True,
        reload_dirs=[str(backend_dir)]
    )
