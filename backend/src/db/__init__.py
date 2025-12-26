"""Database module."""

from .connection import init_db, get_session, close_db, async_session
from .models import (
    Session, SessionCreate, SessionRead, SessionNameUpdate,
    Message, MessageCreate,
    MemoryFile, MemoryFileCreate,
    Clip, ClipCreate, ClipUpdate, ClipRead,
    Song, SongCreate, SongUpdate, SongRead,
    Playlist, PlaylistCreate, PlaylistUpdate, PlaylistRead,
)
from .crud import (
    create_session, get_session as get_session_by_id, list_sessions,
    update_session_activity, update_session_status, update_session_name,
    delete_session,
    save_display_messages, load_messages_paginated, get_message_count,
    create_memory_file, get_session_memory_files, get_primary_memory_file,
    create_clip, get_clip, list_clips, update_clip, delete_clip,
    create_song, get_song, list_songs, update_song, delete_song,
    create_playlist, get_playlist, list_playlists, update_playlist, delete_playlist,
)

__all__ = [
    # Connection
    'init_db', 'get_session', 'close_db', 'async_session',
    # Models
    'Session', 'SessionCreate', 'SessionRead', 'SessionNameUpdate',
    'Message', 'MessageCreate',
    'MemoryFile', 'MemoryFileCreate',
    'Clip', 'ClipCreate', 'ClipUpdate', 'ClipRead',
    'Song', 'SongCreate', 'SongUpdate', 'SongRead',
    'Playlist', 'PlaylistCreate', 'PlaylistUpdate', 'PlaylistRead',
    # CRUD
    'create_session', 'get_session_by_id', 'list_sessions',
    'update_session_activity', 'update_session_status', 'update_session_name',
    'delete_session',
    'save_display_messages', 'load_messages_paginated', 'get_message_count',
    'create_memory_file', 'get_session_memory_files', 'get_primary_memory_file',
    'create_clip', 'get_clip', 'list_clips', 'update_clip', 'delete_clip',
    'create_song', 'get_song', 'list_songs', 'update_song', 'delete_song',
    'create_playlist', 'get_playlist', 'list_playlists', 'update_playlist', 'delete_playlist',
]
