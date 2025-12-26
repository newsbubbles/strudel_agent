"""Pydantic models for WebSocket messages."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# ============================================================================
# WebSocket Protocol Messages
# ============================================================================

class Handshake(BaseModel):
    """Initial handshake from client."""
    type: str = Field(default="handshake")
    session_id: str
    client_type: Optional[str] = Field(default="pwa", description="pwa or mcp")
    client_version: Optional[str] = None

class HandshakeAck(BaseModel):
    """Handshake acknowledgment from server."""
    type: str = Field(default="handshake_ack")
    session_id: str
    connection_id: str
    is_reconnect: bool = False
    session_info: Optional[Dict[str, Any]] = None

class UserMessage(BaseModel):
    """User message to agent."""
    type: str = Field(default="user_message")
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Item context (clip, song, playlist)"
    )

class AgentResponse(BaseModel):
    """Agent response to user."""
    type: str = Field(default="agent_response")
    content: str
    is_final: bool = True

class TypingIndicator(BaseModel):
    """Typing indicator."""
    type: str = Field(default="typing_indicator")
    is_typing: bool
    text: Optional[str] = None

class ToolReport(BaseModel):
    """Tool execution started."""
    type: str = Field(default="tool_report")
    tool_name: str
    tool_call_id: Optional[str] = None

class ToolResult(BaseModel):
    """Tool execution result."""
    type: str = Field(default="tool_result")
    tool_name: str
    content: Any

class ToolRequest(BaseModel):
    """Tool request from server to client."""
    type: str = Field(default="tool_request")
    request_id: str
    tool_name: str
    parameters: Dict[str, Any]
    timeout_ms: int = 30000

class ToolResponse(BaseModel):
    """Tool response from client to server."""
    type: str = Field(default="tool_response")
    request_id: str
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

# ============================================================================
# Strudel-specific Update Events
# ============================================================================

class ClipUpdated(BaseModel):
    """Clip code updated."""
    type: str = Field(default="clip_updated")
    clip_id: str
    new_code: str
    metadata: Optional[Dict[str, Any]] = None

class SongUpdated(BaseModel):
    """Song updated."""
    type: str = Field(default="song_updated")
    song_id: str
    clip_ids: list
    metadata: Optional[Dict[str, Any]] = None

class PlaylistUpdated(BaseModel):
    """Playlist updated."""
    type: str = Field(default="playlist_updated")
    playlist_id: str
    song_ids: list
    metadata: Optional[Dict[str, Any]] = None

class PlayerStateUpdate(BaseModel):
    """Player state update."""
    type: str = Field(default="player_state_update")
    is_playing: bool
    loaded_clips: Optional[list] = None
    current_bpm: Optional[int] = None
