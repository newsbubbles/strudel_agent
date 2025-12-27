"""MCP server for Strudel-specific tools using FastMCP.

This server provides tools for managing Strudel clips, songs, and playlists,
as well as PWA interaction tools for user input and notifications.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

from src.db import (
    async_session,
    get_clip, create_clip, update_clip, delete_clip, list_clips,
    get_song, create_song, update_song, delete_song, list_songs,
    get_playlist, create_playlist, update_playlist, delete_playlist, list_playlists,
    ClipCreate, ClipUpdate,
    SongCreate, SongUpdate,
    PlaylistCreate, PlaylistUpdate,
)
from src.core.manager import manager


# ============================================================================
# Logging Setup
# ============================================================================

def setup_mcp_logging() -> logging.Logger:
    """Standard logging setup for MCP servers."""
    logger_name = os.getenv("LOGGER_NAME", __name__)
    logger_path = os.getenv("LOGGER_PATH")
    
    logger = logging.getLogger(logger_name)
    
    if logger_path and not logger.handlers:
        handler = logging.FileHandler(logger_path, mode='a')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


logger = setup_mcp_logging()


# ============================================================================
# Environment Configuration
# ============================================================================

SESSION_ID = os.getenv('STRUDEL_SESSION_ID')
PROJECT_ID = os.getenv('STRUDEL_PROJECT_ID')
ITEM_TYPE = os.getenv('STRUDEL_ITEM_TYPE')
ITEM_ID = os.getenv('STRUDEL_ITEM_ID')


# ============================================================================
# Request/Response Models
# ============================================================================

# --- Clip Models ---

class StrudelGetClipRequest(BaseModel):
    """Request to get a clip's code."""
    clip_id: str = Field(..., description="Unique identifier for the clip")


class StrudelGetClipResponse(BaseModel):
    """Response containing clip data."""
    clip_id: str = Field(..., description="Clip identifier")
    name: str = Field(..., description="Clip name")
    code: str = Field(..., description="Strudel code for the clip")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional clip metadata")
    error: Optional[str] = Field(None, description="Error message if retrieval failed")


class StrudelUpdateClipRequest(BaseModel):
    """Request to update a clip's code."""
    clip_id: str = Field(..., description="Unique identifier for the clip")
    new_code: str = Field(..., description="New Strudel code for the clip")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata to update")


class StrudelUpdateClipResponse(BaseModel):
    """Response for clip update operation."""
    success: bool = Field(..., description="Whether the update succeeded")
    clip_id: str = Field(..., description="Clip identifier")
    error: Optional[str] = Field(None, description="Error message if update failed")


class StrudelCreateClipRequest(BaseModel):
    """Request to create a new clip."""
    clip_id: str = Field(..., description="Unique identifier for the new clip")
    name: str = Field(..., description="Display name for the clip")
    code: str = Field(..., description="Strudel code for the clip")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class StrudelCreateClipResponse(BaseModel):
    """Response for clip creation operation."""
    success: bool = Field(..., description="Whether the creation succeeded")
    clip_id: str = Field(..., description="Created clip identifier")
    error: Optional[str] = Field(None, description="Error message if creation failed")


class StrudelListClipsResponse(BaseModel):
    """Response containing list of clips."""
    clips: List[StrudelGetClipResponse] = Field(default_factory=list, description="List of clips")


class StrudelDeleteClipRequest(BaseModel):
    """Request to delete a clip."""
    clip_id: str = Field(..., description="Unique identifier for the clip to delete")


class StrudelDeleteClipResponse(BaseModel):
    """Response for clip deletion operation."""
    success: bool = Field(..., description="Whether the deletion succeeded")
    clip_id: str = Field(..., description="Deleted clip identifier")
    error: Optional[str] = Field(None, description="Error message if deletion failed")


# --- Song Models ---

class StrudelGetSongRequest(BaseModel):
    """Request to get a song's composition."""
    song_id: str = Field(..., description="Unique identifier for the song")


class StrudelGetSongResponse(BaseModel):
    """Response containing song data."""
    song_id: str = Field(..., description="Song identifier")
    name: str = Field(..., description="Song name")
    clip_ids: List[str] = Field(default_factory=list, description="List of clip IDs in the song")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional song metadata")
    error: Optional[str] = Field(None, description="Error message if retrieval failed")


class StrudelUpdateSongRequest(BaseModel):
    """Request to update a song's composition."""
    song_id: str = Field(..., description="Unique identifier for the song")
    clip_ids: List[str] = Field(..., description="New list of clip IDs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata to update")


class StrudelUpdateSongResponse(BaseModel):
    """Response for song update operation."""
    success: bool = Field(..., description="Whether the update succeeded")
    song_id: str = Field(..., description="Song identifier")
    error: Optional[str] = Field(None, description="Error message if update failed")


class StrudelCreateSongRequest(BaseModel):
    """Request to create a new song."""
    song_id: str = Field(..., description="Unique identifier for the new song")
    name: str = Field(..., description="Display name for the song")
    clip_ids: Optional[List[str]] = Field(None, description="Initial list of clip IDs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class StrudelCreateSongResponse(BaseModel):
    """Response for song creation operation."""
    success: bool = Field(..., description="Whether the creation succeeded")
    song_id: str = Field(..., description="Created song identifier")
    error: Optional[str] = Field(None, description="Error message if creation failed")


# --- Playlist Models ---

class StrudelGetPlaylistRequest(BaseModel):
    """Request to get a playlist's songs."""
    playlist_id: str = Field(..., description="Unique identifier for the playlist")


class StrudelGetPlaylistResponse(BaseModel):
    """Response containing playlist data."""
    playlist_id: str = Field(..., description="Playlist identifier")
    name: str = Field(..., description="Playlist name")
    song_ids: List[str] = Field(default_factory=list, description="List of song IDs in the playlist")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional playlist metadata")
    error: Optional[str] = Field(None, description="Error message if retrieval failed")


class StrudelUpdatePlaylistRequest(BaseModel):
    """Request to update a playlist's songs."""
    playlist_id: str = Field(..., description="Unique identifier for the playlist")
    song_ids: List[str] = Field(..., description="New list of song IDs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata to update")


class StrudelUpdatePlaylistResponse(BaseModel):
    """Response for playlist update operation."""
    success: bool = Field(..., description="Whether the update succeeded")
    playlist_id: str = Field(..., description="Playlist identifier")
    error: Optional[str] = Field(None, description="Error message if update failed")


# --- PWA Interaction Models ---

class StrudelUserInputRequest(BaseModel):
    """Request to get input from user via PWA."""
    prompt: str = Field(..., description="Prompt message to display to user")
    input_type: str = Field("text", description="Input type: text, textarea, select, etc.")
    timeout_seconds: int = Field(300, description="Timeout in seconds for user response")


class StrudelUserInputResponse(BaseModel):
    """Response containing user input."""
    value: Optional[str] = Field(None, description="User's input value")
    cancelled: bool = Field(False, description="Whether user cancelled the input")
    timed_out: bool = Field(False, description="Whether the request timed out")
    error: Optional[str] = Field(None, description="Error message if request failed")


class StrudelNotificationRequest(BaseModel):
    """Request to send notification to PWA."""
    message: str = Field(..., description="Notification message")
    notification_type: str = Field("info", description="Type: info, warning, error, success")
    duration: int = Field(5000, description="Duration in milliseconds")


class StrudelNotificationResponse(BaseModel):
    """Response for notification operation."""
    success: bool = Field(..., description="Whether the notification was sent")
    error: Optional[str] = Field(None, description="Error message if send failed")


# ============================================================================
# MCP Context
# ============================================================================

class StrudelMCPContext:
    """Context for Strudel MCP server containing session info."""
    
    def __init__(self, session_id: str, project_id: str, item_type: str, item_id: str):
        self.session_id = session_id
        self.project_id = project_id
        self.item_type = item_type
        self.item_id = item_id


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[StrudelMCPContext]:
    """Lifespan context manager for Strudel MCP server."""
    try:
        # Validate required environment variables
        if not all([SESSION_ID, PROJECT_ID, ITEM_TYPE, ITEM_ID]):
            raise ValueError(
                "Missing required environment variables: "
                "STRUDEL_SESSION_ID, STRUDEL_PROJECT_ID, STRUDEL_ITEM_TYPE, STRUDEL_ITEM_ID"
            )
        
        logger.info(f"Strudel MCP server starting for session {SESSION_ID}")
        
        yield StrudelMCPContext(
            session_id=SESSION_ID,
            project_id=PROJECT_ID,
            item_type=ITEM_TYPE,
            item_id=ITEM_ID
        )
    except Exception as e:
        logger.error(f"Failed to initialize Strudel MCP context: {e}")
        raise
    finally:
        logger.info("Strudel MCP server shutting down")


# ============================================================================
# FastMCP Server
# ============================================================================

mcp = FastMCP("strudel-tools", lifespan=lifespan)


# ============================================================================
# Clip Tools
# ============================================================================

@mcp.tool()
async def strudel_get_clip(request: StrudelGetClipRequest, ctx: Context) -> StrudelGetClipResponse:
    """Get Strudel code for a clip.
    
    Retrieves the code and metadata for a specific clip by its ID.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            clip = await get_clip(db, request.clip_id, mcp_ctx.project_id)
            
            if not clip:
                return StrudelGetClipResponse(
                    clip_id=request.clip_id,
                    name="",
                    code="",
                    error=f"Clip '{request.clip_id}' not found"
                )
            
            return StrudelGetClipResponse(
                clip_id=clip.clip_id,
                name=clip.name,
                code=clip.code,
                metadata=clip.metadata_ or {}
            )
    except Exception as e:
        logger.error(f"Error getting clip {request.clip_id}: {e}")
        return StrudelGetClipResponse(
            clip_id=request.clip_id,
            name="",
            code="",
            error=str(e)
        )


@mcp.tool()
async def strudel_update_clip(request: StrudelUpdateClipRequest, ctx: Context) -> StrudelUpdateClipResponse:
    """Update Strudel code for a clip.
    
    Updates the code and optionally metadata for an existing clip.
    Sends update event to frontend PWA.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            clip_update = ClipUpdate(code=request.new_code, metadata=request.metadata)
            updated_clip = await update_clip(db, request.clip_id, mcp_ctx.project_id, clip_update)
            
            if not updated_clip:
                return StrudelUpdateClipResponse(
                    success=False,
                    clip_id=request.clip_id,
                    error=f"Clip '{request.clip_id}' not found"
                )
            
            # Send update event to frontend
            await manager.send_message(
                mcp_ctx.session_id,
                {
                    'type': 'clip_updated',
                    'clip_id': request.clip_id,
                    'new_code': request.new_code,
                    'metadata': request.metadata or {}
                },
                target='pwa'
            )
            
            await ctx.info(f"Updated clip {request.clip_id}")
            
            return StrudelUpdateClipResponse(
                success=True,
                clip_id=request.clip_id
            )
    except Exception as e:
        logger.error(f"Error updating clip {request.clip_id}: {e}")
        return StrudelUpdateClipResponse(
            success=False,
            clip_id=request.clip_id,
            error=str(e)
        )


@mcp.tool()
async def strudel_create_clip(request: StrudelCreateClipRequest, ctx: Context) -> StrudelCreateClipResponse:
    """Create a new Strudel clip.
    
    Creates a new clip with the specified ID, name, code, and optional metadata.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            clip_data = ClipCreate(
                clip_id=request.clip_id,
                project_id=mcp_ctx.project_id,
                name=request.name,
                code=request.code,
                metadata=request.metadata
            )
            clip = await create_clip(db, clip_data)
            
            await ctx.info(f"Created clip {clip.clip_id}")
            
            return StrudelCreateClipResponse(
                success=True,
                clip_id=clip.clip_id
            )
    except Exception as e:
        logger.error(f"Error creating clip {request.clip_id}: {e}")
        return StrudelCreateClipResponse(
            success=False,
            clip_id=request.clip_id,
            error=str(e)
        )


@mcp.tool()
async def strudel_list_clips(ctx: Context) -> StrudelListClipsResponse:
    """List all clips in the current project.
    
    Returns all clips associated with the current project.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            clips = await list_clips(db, mcp_ctx.project_id)
            
            return StrudelListClipsResponse(
                clips=[
                    StrudelGetClipResponse(
                        clip_id=clip.clip_id,
                        name=clip.name,
                        code=clip.code,
                        metadata=clip.metadata_ or {}
                    )
                    for clip in clips
                ]
            )
    except Exception as e:
        logger.error(f"Error listing clips: {e}")
        return StrudelListClipsResponse(clips=[])


@mcp.tool()
async def strudel_delete_clip(request: StrudelDeleteClipRequest, ctx: Context) -> StrudelDeleteClipResponse:
    """Delete a clip from the project.
    
    Permanently removes a clip by its ID.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            success = await delete_clip(db, request.clip_id, mcp_ctx.project_id)
            
            if not success:
                return StrudelDeleteClipResponse(
                    success=False,
                    clip_id=request.clip_id,
                    error=f"Clip '{request.clip_id}' not found"
                )
            
            await ctx.info(f"Deleted clip {request.clip_id}")
            
            return StrudelDeleteClipResponse(
                success=True,
                clip_id=request.clip_id
            )
    except Exception as e:
        logger.error(f"Error deleting clip {request.clip_id}: {e}")
        return StrudelDeleteClipResponse(
            success=False,
            clip_id=request.clip_id,
            error=str(e)
        )


# ============================================================================
# Song Tools
# ============================================================================

@mcp.tool()
async def strudel_get_song(request: StrudelGetSongRequest, ctx: Context) -> StrudelGetSongResponse:
    """Get song composition (list of clip IDs).
    
    Retrieves the song structure including its clip IDs and metadata.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            song = await get_song(db, request.song_id, mcp_ctx.project_id)
            
            if not song:
                return StrudelGetSongResponse(
                    song_id=request.song_id,
                    name="",
                    error=f"Song '{request.song_id}' not found"
                )
            
            return StrudelGetSongResponse(
                song_id=song.song_id,
                name=song.name,
                clip_ids=song.clip_ids or [],
                metadata=song.metadata_ or {}
            )
    except Exception as e:
        logger.error(f"Error getting song {request.song_id}: {e}")
        return StrudelGetSongResponse(
            song_id=request.song_id,
            name="",
            error=str(e)
        )


@mcp.tool()
async def strudel_update_song(request: StrudelUpdateSongRequest, ctx: Context) -> StrudelUpdateSongResponse:
    """Update song composition.
    
    Updates the list of clip IDs and optionally metadata for a song.
    Sends update event to frontend PWA.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            song_update = SongUpdate(clip_ids=request.clip_ids, metadata=request.metadata)
            updated_song = await update_song(db, request.song_id, mcp_ctx.project_id, song_update)
            
            if not updated_song:
                return StrudelUpdateSongResponse(
                    success=False,
                    song_id=request.song_id,
                    error=f"Song '{request.song_id}' not found"
                )
            
            # Send update event to frontend
            await manager.send_message(
                mcp_ctx.session_id,
                {
                    'type': 'song_updated',
                    'song_id': request.song_id,
                    'clip_ids': request.clip_ids,
                    'metadata': request.metadata or {}
                },
                target='pwa'
            )
            
            await ctx.info(f"Updated song {request.song_id}")
            
            return StrudelUpdateSongResponse(
                success=True,
                song_id=request.song_id
            )
    except Exception as e:
        logger.error(f"Error updating song {request.song_id}: {e}")
        return StrudelUpdateSongResponse(
            success=False,
            song_id=request.song_id,
            error=str(e)
        )


@mcp.tool()
async def strudel_create_song(request: StrudelCreateSongRequest, ctx: Context) -> StrudelCreateSongResponse:
    """Create a new song.
    
    Creates a new song with the specified ID, name, clip IDs, and optional metadata.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            song_data = SongCreate(
                song_id=request.song_id,
                project_id=mcp_ctx.project_id,
                name=request.name,
                clip_ids=request.clip_ids,
                metadata=request.metadata
            )
            song = await create_song(db, song_data)
            
            await ctx.info(f"Created song {song.song_id}")
            
            return StrudelCreateSongResponse(
                success=True,
                song_id=song.song_id
            )
    except Exception as e:
        logger.error(f"Error creating song {request.song_id}: {e}")
        return StrudelCreateSongResponse(
            success=False,
            song_id=request.song_id,
            error=str(e)
        )


# ============================================================================
# Playlist Tools
# ============================================================================

@mcp.tool()
async def strudel_get_playlist(request: StrudelGetPlaylistRequest, ctx: Context) -> StrudelGetPlaylistResponse:
    """Get playlist songs.
    
    Retrieves the playlist structure including its song IDs and metadata.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            playlist = await get_playlist(db, request.playlist_id, mcp_ctx.project_id)
            
            if not playlist:
                return StrudelGetPlaylistResponse(
                    playlist_id=request.playlist_id,
                    name="",
                    error=f"Playlist '{request.playlist_id}' not found"
                )
            
            return StrudelGetPlaylistResponse(
                playlist_id=playlist.playlist_id,
                name=playlist.name,
                song_ids=playlist.song_ids or [],
                metadata=playlist.metadata_ or {}
            )
    except Exception as e:
        logger.error(f"Error getting playlist {request.playlist_id}: {e}")
        return StrudelGetPlaylistResponse(
            playlist_id=request.playlist_id,
            name="",
            error=str(e)
        )


@mcp.tool()
async def strudel_update_playlist(request: StrudelUpdatePlaylistRequest, ctx: Context) -> StrudelUpdatePlaylistResponse:
    """Update playlist songs.
    
    Updates the list of song IDs and optionally metadata for a playlist.
    Sends update event to frontend PWA.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        async with async_session() as db:
            playlist_update = PlaylistUpdate(song_ids=request.song_ids, metadata=request.metadata)
            updated_playlist = await update_playlist(
                db, request.playlist_id, mcp_ctx.project_id, playlist_update
            )
            
            if not updated_playlist:
                return StrudelUpdatePlaylistResponse(
                    success=False,
                    playlist_id=request.playlist_id,
                    error=f"Playlist '{request.playlist_id}' not found"
                )
            
            # Send update event to frontend
            await manager.send_message(
                mcp_ctx.session_id,
                {
                    'type': 'playlist_updated',
                    'playlist_id': request.playlist_id,
                    'song_ids': request.song_ids,
                    'metadata': request.metadata or {}
                },
                target='pwa'
            )
            
            await ctx.info(f"Updated playlist {request.playlist_id}")
            
            return StrudelUpdatePlaylistResponse(
                success=True,
                playlist_id=request.playlist_id
            )
    except Exception as e:
        logger.error(f"Error updating playlist {request.playlist_id}: {e}")
        return StrudelUpdatePlaylistResponse(
            success=False,
            playlist_id=request.playlist_id,
            error=str(e)
        )


# ============================================================================
# PWA Interaction Tools
# ============================================================================

@mcp.tool()
async def strudel_request_user_input(request: StrudelUserInputRequest, ctx: Context) -> StrudelUserInputResponse:
    """Request input from user via PWA interface.
    
    Displays an input prompt in the PWA and waits for user response.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        result = await manager.send_tool_request(
            mcp_ctx.session_id,
            'pwa_request_user_input',
            {
                'prompt': request.prompt,
                'input_type': request.input_type,
                'timeout_seconds': request.timeout_seconds,
            },
            timeout_ms=request.timeout_seconds * 1000
        )
        
        return StrudelUserInputResponse(
            value=result.get('value'),
            cancelled=result.get('cancelled', False),
            timed_out=result.get('timed_out', False)
        )
    except Exception as e:
        logger.error(f"Error requesting user input: {e}")
        return StrudelUserInputResponse(
            error=str(e)
        )


@mcp.tool()
async def strudel_send_notification(request: StrudelNotificationRequest, ctx: Context) -> StrudelNotificationResponse:
    """Send notification to PWA interface.
    
    Displays a toast notification in the PWA with the specified message and styling.
    """
    try:
        mcp_ctx: StrudelMCPContext = ctx.request_context.lifespan_context
        
        result = await manager.send_tool_request(
            mcp_ctx.session_id,
            'pwa_send_notification',
            {
                'message': request.message,
                'type': request.notification_type,
                'duration': request.duration,
            },
            timeout_ms=5000
        )
        
        return StrudelNotificationResponse(
            success=result.get('success', True)
        )
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return StrudelNotificationResponse(
            success=False,
            error=str(e)
        )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the Strudel MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
