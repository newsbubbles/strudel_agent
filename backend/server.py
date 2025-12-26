"""FastAPI server for Strudel Agent."""

import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic_ai.messages import ModelMessage

from backend.src.db import (
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
    create_clip as db_create_clip,
    get_clip as db_get_clip,
    list_clips as db_list_clips,
    update_clip as db_update_clip,
    delete_clip as db_delete_clip,
    create_song as db_create_song,
    get_song as db_get_song,
    list_songs as db_list_songs,
    update_song as db_update_song,
    delete_song as db_delete_song,
    create_playlist as db_create_playlist,
    get_playlist as db_get_playlist,
    list_playlists as db_list_playlists,
    update_playlist as db_update_playlist,
    delete_playlist as db_delete_playlist,
)
from backend.src.models import (
    Handshake, UserMessage,
    ToolResponse,
)
from backend.src.core import (
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
        
        # Start MCP servers for PWA connections
        if connection_type == 'pwa':
            async with session_state.agent.run_mcp_servers():
                await handle_websocket_messages(
                    websocket, session_id, connection_type, session_state
                )
        else:
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
# Clip Endpoints
# ============================================================================

@app.post("/api/clips", response_model=ClipRead)
async def create_clip(clip_data: ClipCreate):
    """Create a new clip."""
    async with async_session() as db:
        clip = await db_create_clip(db, clip_data)
        return ClipRead(
            id=clip.id,
            clip_id=clip.clip_id,
            project_id=clip.project_id,
            name=clip.name,
            code=clip.code,
            created_at=clip.created_at,
            updated_at=clip.updated_at,
            metadata=clip.metadata_ or {}
        )

@app.get("/api/clips/{project_id}/{clip_id}", response_model=ClipRead)
async def get_clip(project_id: str, clip_id: str):
    """Get a clip."""
    async with async_session() as db:
        clip = await db_get_clip(db, clip_id, project_id)
        
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        return ClipRead(
            id=clip.id,
            clip_id=clip.clip_id,
            project_id=clip.project_id,
            name=clip.name,
            code=clip.code,
            created_at=clip.created_at,
            updated_at=clip.updated_at,
            metadata=clip.metadata_ or {}
        )

@app.get("/api/clips/{project_id}", response_model=list[ClipRead])
async def list_clips(project_id: str):
    """List all clips for a project."""
    async with async_session() as db:
        clips = await db_list_clips(db, project_id)
        return [
            ClipRead(
                id=clip.id,
                clip_id=clip.clip_id,
                project_id=clip.project_id,
                name=clip.name,
                code=clip.code,
                created_at=clip.created_at,
                updated_at=clip.updated_at,
                metadata=clip.metadata_ or {}
            )
            for clip in clips
        ]

@app.put("/api/clips/{project_id}/{clip_id}", response_model=ClipRead)
async def update_clip(project_id: str, clip_id: str, clip_update: ClipUpdate):
    """Update a clip."""
    async with async_session() as db:
        clip = await db_update_clip(db, clip_id, project_id, clip_update)
        
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        return ClipRead(
            id=clip.id,
            clip_id=clip.clip_id,
            project_id=clip.project_id,
            name=clip.name,
            code=clip.code,
            created_at=clip.created_at,
            updated_at=clip.updated_at,
            metadata=clip.metadata_ or {}
        )

@app.delete("/api/clips/{project_id}/{clip_id}")
async def delete_clip(project_id: str, clip_id: str):
    """Delete a clip."""
    async with async_session() as db:
        success = await db_delete_clip(db, clip_id, project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    return {"success": True}

# ============================================================================
# Song Endpoints
# ============================================================================

@app.post("/api/songs", response_model=SongRead)
async def create_song(song_data: SongCreate):
    """Create a new song."""
    async with async_session() as db:
        song = await db_create_song(db, song_data)
        return SongRead(
            id=song.id,
            song_id=song.song_id,
            project_id=song.project_id,
            name=song.name,
            created_at=song.created_at,
            updated_at=song.updated_at,
            clip_ids=song.clip_ids or [],
            metadata=song.metadata_ or {}
        )

@app.get("/api/songs/{project_id}/{song_id}", response_model=SongRead)
async def get_song(project_id: str, song_id: str):
    """Get a song."""
    async with async_session() as db:
        song = await db_get_song(db, song_id, project_id)
        
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        return SongRead(
            id=song.id,
            song_id=song.song_id,
            project_id=song.project_id,
            name=song.name,
            created_at=song.created_at,
            updated_at=song.updated_at,
            clip_ids=song.clip_ids or [],
            metadata=song.metadata_ or {}
        )

@app.get("/api/songs/{project_id}", response_model=list[SongRead])
async def list_songs(project_id: str):
    """List all songs for a project."""
    async with async_session() as db:
        songs = await db_list_songs(db, project_id)
        return [
            SongRead(
                id=song.id,
                song_id=song.song_id,
                project_id=song.project_id,
                name=song.name,
                created_at=song.created_at,
                updated_at=song.updated_at,
                clip_ids=song.clip_ids or [],
                metadata=song.metadata_ or {}
            )
            for song in songs
        ]

@app.put("/api/songs/{project_id}/{song_id}", response_model=SongRead)
async def update_song(project_id: str, song_id: str, song_update: SongUpdate):
    """Update a song."""
    async with async_session() as db:
        song = await db_update_song(db, song_id, project_id, song_update)
        
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        return SongRead(
            id=song.id,
            song_id=song.song_id,
            project_id=song.project_id,
            name=song.name,
            created_at=song.created_at,
            updated_at=song.updated_at,
            clip_ids=song.clip_ids or [],
            metadata=song.metadata_ or {}
        )

@app.delete("/api/songs/{project_id}/{song_id}")
async def delete_song(project_id: str, song_id: str):
    """Delete a song."""
    async with async_session() as db:
        success = await db_delete_song(db, song_id, project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Song not found")
    
    return {"success": True}

# ============================================================================
# Playlist Endpoints
# ============================================================================

@app.post("/api/playlists", response_model=PlaylistRead)
async def create_playlist(playlist_data: PlaylistCreate):
    """Create a new playlist."""
    async with async_session() as db:
        playlist = await db_create_playlist(db, playlist_data)
        return PlaylistRead(
            id=playlist.id,
            playlist_id=playlist.playlist_id,
            project_id=playlist.project_id,
            name=playlist.name,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at,
            song_ids=playlist.song_ids or [],
            metadata=playlist.metadata_ or {}
        )

@app.get("/api/playlists/{project_id}/{playlist_id}", response_model=PlaylistRead)
async def get_playlist(project_id: str, playlist_id: str):
    """Get a playlist."""
    async with async_session() as db:
        playlist = await db_get_playlist(db, playlist_id, project_id)
        
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        return PlaylistRead(
            id=playlist.id,
            playlist_id=playlist.playlist_id,
            project_id=playlist.project_id,
            name=playlist.name,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at,
            song_ids=playlist.song_ids or [],
            metadata=playlist.metadata_ or {}
        )

@app.get("/api/playlists/{project_id}", response_model=list[PlaylistRead])
async def list_playlists(project_id: str):
    """List all playlists for a project."""
    async with async_session() as db:
        playlists = await db_list_playlists(db, project_id)
        return [
            PlaylistRead(
                id=playlist.id,
                playlist_id=playlist.playlist_id,
                project_id=playlist.project_id,
                name=playlist.name,
                created_at=playlist.created_at,
                updated_at=playlist.updated_at,
                song_ids=playlist.song_ids or [],
                metadata=playlist.metadata_ or {}
            )
            for playlist in playlists
        ]

@app.put("/api/playlists/{project_id}/{playlist_id}", response_model=PlaylistRead)
async def update_playlist(project_id: str, playlist_id: str, playlist_update: PlaylistUpdate):
    """Update a playlist."""
    async with async_session() as db:
        playlist = await db_update_playlist(db, playlist_id, project_id, playlist_update)
        
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        return PlaylistRead(
            id=playlist.id,
            playlist_id=playlist.playlist_id,
            project_id=playlist.project_id,
            name=playlist.name,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at,
            song_ids=playlist.song_ids or [],
            metadata=playlist.metadata_ or {}
        )

@app.delete("/api/playlists/{project_id}/{playlist_id}")
async def delete_playlist(project_id: str, playlist_id: str):
    """Delete a playlist."""
    async with async_session() as db:
        success = await db_delete_playlist(db, playlist_id, project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
