"""MCP server for Strudel-specific tools."""

import os
import sys
import logging
import asyncio
from uuid import UUID

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from backend.src.db import (
    async_session,
    get_clip, create_clip, update_clip, delete_clip, list_clips,
    get_song, create_song, update_song, delete_song, list_songs,
    get_playlist, create_playlist, update_playlist, delete_playlist, list_playlists,
    ClipCreate, ClipUpdate,
    SongCreate, SongUpdate,
    PlaylistCreate, PlaylistUpdate,
)
from backend.src.core.manager import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
SESSION_ID = os.getenv('STRUDEL_SESSION_ID')
PROJECT_ID = os.getenv('STRUDEL_PROJECT_ID')
ITEM_TYPE = os.getenv('STRUDEL_ITEM_TYPE')
ITEM_ID = os.getenv('STRUDEL_ITEM_ID')

if not all([SESSION_ID, PROJECT_ID, ITEM_TYPE, ITEM_ID]):
    raise ValueError("Missing required environment variables")

# Create MCP server
server = Server("strudel-tools")

# ============================================================================
# Clip Tools
# ============================================================================

@server.call_tool()
async def get_clip_code(clip_id: str) -> dict:
    """Get Strudel code for a clip.
    
    Args:
        clip_id: Clip identifier
    
    Returns:
        {"clip_id": str, "code": str, "metadata": dict}
    """
    async with async_session() as db:
        clip = await get_clip(db, clip_id, PROJECT_ID)
        
        if not clip:
            return {"error": f"Clip '{clip_id}' not found"}
        
        return {
            "clip_id": clip.clip_id,
            "name": clip.name,
            "code": clip.code,
            "metadata": clip.metadata_ or {}
        }

@server.call_tool()
async def update_clip_code(clip_id: str, new_code: str, metadata: dict = None) -> dict:
    """Update Strudel code for a clip.
    
    Args:
        clip_id: Clip identifier
        new_code: New Strudel code
        metadata: Optional metadata to update
    
    Returns:
        {"success": bool, "clip_id": str}
    """
    async with async_session() as db:
        clip_update = ClipUpdate(code=new_code, metadata=metadata)
        updated_clip = await update_clip(db, clip_id, PROJECT_ID, clip_update)
        
        if not updated_clip:
            return {"success": False, "error": f"Clip '{clip_id}' not found"}
        
        # Send update event to frontend
        await manager.send_message(
            SESSION_ID,
            {
                'type': 'clip_updated',
                'clip_id': clip_id,
                'new_code': new_code,
                'metadata': metadata or {}
            },
            target='pwa'
        )
        
        return {"success": True, "clip_id": clip_id}

@server.call_tool()
async def create_new_clip(clip_id: str, name: str, code: str, metadata: dict = None) -> dict:
    """Create a new clip.
    
    Args:
        clip_id: Clip identifier
        name: Clip name
        code: Strudel code
        metadata: Optional metadata
    
    Returns:
        {"success": bool, "clip_id": str}
    """
    async with async_session() as db:
        clip_data = ClipCreate(
            clip_id=clip_id,
            project_id=PROJECT_ID,
            name=name,
            code=code,
            metadata=metadata
        )
        clip = await create_clip(db, clip_data)
        
        return {"success": True, "clip_id": clip.clip_id}

@server.call_tool()
async def list_project_clips() -> dict:
    """List all clips in the current project.
    
    Returns:
        {"clips": [{"clip_id": str, "name": str, "code": str}]}
    """
    async with async_session() as db:
        clips = await list_clips(db, PROJECT_ID)
        
        return {
            "clips": [
                {
                    "clip_id": clip.clip_id,
                    "name": clip.name,
                    "code": clip.code,
                    "metadata": clip.metadata_ or {}
                }
                for clip in clips
            ]
        }

# ============================================================================
# Song Tools
# ============================================================================

@server.call_tool()
async def get_song_composition(song_id: str) -> dict:
    """Get song composition (list of clip IDs).
    
    Args:
        song_id: Song identifier
    
    Returns:
        {"song_id": str, "name": str, "clip_ids": list}
    """
    async with async_session() as db:
        song = await get_song(db, song_id, PROJECT_ID)
        
        if not song:
            return {"error": f"Song '{song_id}' not found"}
        
        return {
            "song_id": song.song_id,
            "name": song.name,
            "clip_ids": song.clip_ids or [],
            "metadata": song.metadata_ or {}
        }

@server.call_tool()
async def update_song_composition(song_id: str, clip_ids: list, metadata: dict = None) -> dict:
    """Update song composition.
    
    Args:
        song_id: Song identifier
        clip_ids: List of clip IDs
        metadata: Optional metadata
    
    Returns:
        {"success": bool, "song_id": str}
    """
    async with async_session() as db:
        song_update = SongUpdate(clip_ids=clip_ids, metadata=metadata)
        updated_song = await update_song(db, song_id, PROJECT_ID, song_update)
        
        if not updated_song:
            return {"success": False, "error": f"Song '{song_id}' not found"}
        
        # Send update event to frontend
        await manager.send_message(
            SESSION_ID,
            {
                'type': 'song_updated',
                'song_id': song_id,
                'clip_ids': clip_ids,
                'metadata': metadata or {}
            },
            target='pwa'
        )
        
        return {"success": True, "song_id": song_id}

@server.call_tool()
async def create_new_song(song_id: str, name: str, clip_ids: list = None, metadata: dict = None) -> dict:
    """Create a new song.
    
    Args:
        song_id: Song identifier
        name: Song name
        clip_ids: List of clip IDs
        metadata: Optional metadata
    
    Returns:
        {"success": bool, "song_id": str}
    """
    async with async_session() as db:
        song_data = SongCreate(
            song_id=song_id,
            project_id=PROJECT_ID,
            name=name,
            clip_ids=clip_ids,
            metadata=metadata
        )
        song = await create_song(db, song_data)
        
        return {"success": True, "song_id": song.song_id}

# ============================================================================
# Playlist Tools
# ============================================================================

@server.call_tool()
async def get_playlist_songs(playlist_id: str) -> dict:
    """Get playlist songs.
    
    Args:
        playlist_id: Playlist identifier
    
    Returns:
        {"playlist_id": str, "name": str, "song_ids": list}
    """
    async with async_session() as db:
        playlist = await get_playlist(db, playlist_id, PROJECT_ID)
        
        if not playlist:
            return {"error": f"Playlist '{playlist_id}' not found"}
        
        return {
            "playlist_id": playlist.playlist_id,
            "name": playlist.name,
            "song_ids": playlist.song_ids or [],
            "metadata": playlist.metadata_ or {}
        }

@server.call_tool()
async def update_playlist_songs(playlist_id: str, song_ids: list, metadata: dict = None) -> dict:
    """Update playlist songs.
    
    Args:
        playlist_id: Playlist identifier
        song_ids: List of song IDs
        metadata: Optional metadata
    
    Returns:
        {"success": bool, "playlist_id": str}
    """
    async with async_session() as db:
        playlist_update = PlaylistUpdate(song_ids=song_ids, metadata=metadata)
        updated_playlist = await update_playlist(db, playlist_id, PROJECT_ID, playlist_update)
        
        if not updated_playlist:
            return {"success": False, "error": f"Playlist '{playlist_id}' not found"}
        
        # Send update event to frontend
        await manager.send_message(
            SESSION_ID,
            {
                'type': 'playlist_updated',
                'playlist_id': playlist_id,
                'song_ids': song_ids,
                'metadata': metadata or {}
            },
            target='pwa'
        )
        
        return {"success": True, "playlist_id": playlist_id}

# ============================================================================
# PWA Tools (via tool request protocol)
# ============================================================================

@server.call_tool()
async def request_user_input(prompt: str, input_type: str = 'text', timeout_seconds: int = 300) -> dict:
    """Request input from user via PWA interface.
    
    Args:
        prompt: Prompt message
        input_type: Input type (text, textarea, select, etc.)
        timeout_seconds: Timeout in seconds
    
    Returns:
        User's input value
    """
    result = await manager.send_tool_request(
        SESSION_ID,
        'pwa_request_user_input',
        {
            'prompt': prompt,
            'input_type': input_type,
            'timeout_seconds': timeout_seconds,
        },
        timeout_ms=timeout_seconds * 1000
    )
    return result

@server.call_tool()
async def send_notification(message: str, notification_type: str = 'info', duration: int = 5000) -> dict:
    """Send notification to PWA interface.
    
    Args:
        message: Notification message
        notification_type: Type (info, warning, error, success)
        duration: Duration in milliseconds
    
    Returns:
        {"success": bool}
    """
    result = await manager.send_tool_request(
        SESSION_ID,
        'pwa_send_notification',
        {
            'message': message,
            'type': notification_type,
            'duration': duration,
        },
        timeout_ms=5000
    )
    return result

# ============================================================================
# Main
# ============================================================================

async def main():
    """Run MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
