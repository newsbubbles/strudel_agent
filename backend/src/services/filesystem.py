"""Filesystem service for Strudel content management.

Ports filesystem operations from mcp_server.py to provide REST API access
to projects, clips, songs, and playlists stored on the filesystem.
"""

import json
import re
from pathlib import Path
from datetime import datetime, date as date_module
from typing import Optional, Any

# Base paths - relative to backend directory, go up to project root
BACKEND_DIR = Path(__file__).parent.parent.parent
BASE_DIR = BACKEND_DIR.parent  # strudel_agent/
PROJECTS_DIR = BASE_DIR / "projects"

# Ensure directories exist
PROJECTS_DIR.mkdir(exist_ok=True)


class FilesystemService:
    """Service for filesystem-based content operations."""
    
    # ========================================================================
    # Utility Functions (ported from mcp_server.py)
    # ========================================================================
    
    @staticmethod
    def get_project_path(project_id: str) -> Path:
        """Get path to project directory."""
        return PROJECTS_DIR / project_id
    
    @staticmethod
    def ensure_project_structure(project_id: str) -> None:
        """Ensure project directory structure exists."""
        project_path = FilesystemService.get_project_path(project_id)
        project_path.mkdir(exist_ok=True)
        (project_path / "clips").mkdir(exist_ok=True)
        (project_path / "songs").mkdir(exist_ok=True)
        (project_path / "playlists").mkdir(exist_ok=True)
    
    @staticmethod
    def parse_clip_metadata(file_path: Path) -> Optional[dict]:
        """Parse metadata from first line of clip file.
        
        Format: // {"name": "...", "tags": [...], ...}
        """
        try:
            first_line = file_path.read_text(encoding='utf-8').split('\n')[0]
            # Extract JSON from comment: // {"key": "value"}
            json_match = re.search(r'//\s*({.+})', first_line)
            if json_match:
                metadata = json.loads(json_match.group(1))
                
                # Backward compatibility: fill in missing fields
                if 'author' not in metadata:
                    metadata['author'] = None
                if 'version' not in metadata:
                    metadata['version'] = "1.0.0"
                if 'date' not in metadata:
                    mtime = file_path.stat().st_mtime
                    metadata['date'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                
                return metadata
        except Exception:
            pass
        return None
    
    @staticmethod
    def parse_markdown_header(file_path: Path) -> tuple[Optional[str], Optional[str]]:
        """Parse title (H1) and description (second non-empty line) from markdown file."""
        try:
            lines = file_path.read_text(encoding='utf-8').split('\n')
            title = None
            description = None
            
            # Find H1
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    title = line[2:].strip()
                    # Description is next non-empty line
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip():
                            description = lines[j].strip()
                            break
                    break
            
            return title, description
        except Exception:
            return None, None
    
    @staticmethod
    def get_file_timestamps(file_path: Path) -> tuple[datetime, datetime]:
        """Get created_at and updated_at from file stats."""
        stat = file_path.stat()
        # Use mtime for both since ctime on Unix is inode change time
        mtime = datetime.fromtimestamp(stat.st_mtime)
        return mtime, mtime
    
    @staticmethod
    def bump_semantic_version(version: str, bump_type: str = "patch") -> str:
        """Bump semantic version string."""
        try:
            parts = version.split('.')
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            if bump_type == "major":
                return f"{major + 1}.0.0"
            elif bump_type == "minor":
                return f"{major}.{minor + 1}.0"
            else:  # patch
                return f"{major}.{minor}.{patch + 1}"
        except Exception:
            return "1.0.1"
    
    # ========================================================================
    # Project Operations
    # ========================================================================
    
    @staticmethod
    def list_projects(query: Optional[str] = None) -> dict:
        """List all projects with optional regex filter."""
        projects = []
        
        for project_dir in PROJECTS_DIR.iterdir():
            if not project_dir.is_dir():
                continue
            
            project_id = project_dir.name
            index_file = project_dir / "index.md"
            
            # Parse index file
            name = project_id
            description = ""
            if index_file.exists():
                title, desc = FilesystemService.parse_markdown_header(index_file)
                if title:
                    name = title
                if desc:
                    description = desc
            
            # Apply filter if provided
            if query:
                regex = re.compile(query, re.IGNORECASE)
                if not (regex.search(name) or regex.search(description)):
                    continue
            
            # Count items
            clips_dir = project_dir / "clips"
            songs_dir = project_dir / "songs"
            playlists_dir = project_dir / "playlists"
            
            clip_count = len(list(clips_dir.glob("*.js"))) if clips_dir.exists() else 0
            song_count = len(list(songs_dir.glob("*.md"))) if songs_dir.exists() else 0
            playlist_count = len(list(playlists_dir.glob("*.md"))) if playlists_dir.exists() else 0
            
            projects.append({
                "project_id": project_id,
                "name": name,
                "description": description,
                "clip_count": clip_count,
                "song_count": song_count,
                "playlist_count": playlist_count
            })
        
        return {"projects": projects, "total": len(projects)}
    
    @staticmethod
    def get_project(project_id: str) -> Optional[dict]:
        """Get a single project's details."""
        project_path = FilesystemService.get_project_path(project_id)
        if not project_path.exists():
            return None
        
        index_file = project_path / "index.md"
        name = project_id
        description = ""
        
        if index_file.exists():
            title, desc = FilesystemService.parse_markdown_header(index_file)
            if title:
                name = title
            if desc:
                description = desc
        
        clips_dir = project_path / "clips"
        songs_dir = project_path / "songs"
        playlists_dir = project_path / "playlists"
        
        return {
            "project_id": project_id,
            "name": name,
            "description": description,
            "clip_count": len(list(clips_dir.glob("*.js"))) if clips_dir.exists() else 0,
            "song_count": len(list(songs_dir.glob("*.md"))) if songs_dir.exists() else 0,
            "playlist_count": len(list(playlists_dir.glob("*.md"))) if playlists_dir.exists() else 0
        }
    
    @staticmethod
    def create_project(project_id: str, name: str, description: str = "") -> dict:
        """Create a new project."""
        project_path = FilesystemService.get_project_path(project_id)
        
        if project_path.exists():
            return {"error": f"Project '{project_id}' already exists", "success": False}
        
        FilesystemService.ensure_project_structure(project_id)
        
        # Create index.md
        index_content = f"# {name}\n\n{description}"
        (project_path / "index.md").write_text(index_content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "message": f"Project '{project_id}' created successfully"
        }
    
    @staticmethod
    def update_project(project_id: str, name: Optional[str] = None, description: Optional[str] = None) -> dict:
        """Update project index."""
        project_path = FilesystemService.get_project_path(project_id)
        
        if not project_path.exists():
            return {"error": f"Project '{project_id}' not found", "success": False}
        
        index_file = project_path / "index.md"
        
        # Get existing values
        existing_name = project_id
        existing_desc = ""
        if index_file.exists():
            title, desc = FilesystemService.parse_markdown_header(index_file)
            if title:
                existing_name = title
            if desc:
                existing_desc = desc
        
        # Use new or keep existing
        new_name = name if name is not None else existing_name
        new_desc = description if description is not None else existing_desc
        
        # Write updated index
        index_content = f"# {new_name}\n\n{new_desc}"
        index_file.write_text(index_content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "message": f"Project '{project_id}' updated successfully"
        }
    
    # ========================================================================
    # Clip Operations
    # ========================================================================
    
    @staticmethod
    def list_clips(project_id: str, query: Optional[str] = None) -> list[dict]:
        """List clips in a project with optional regex filter."""
        project_path = FilesystemService.get_project_path(project_id)
        if not project_path.exists():
            return []
        
        clips_dir = project_path / "clips"
        if not clips_dir.exists():
            return []
        
        clips = []
        for clip_file in clips_dir.glob("*.js"):
            clip_id = clip_file.stem
            metadata = FilesystemService.parse_clip_metadata(clip_file)
            
            if not metadata:
                # Create minimal metadata for clips without proper headers
                metadata = {
                    "name": clip_id,
                    "tags": [],
                    "tempo": None,
                    "description": "",
                    "author": None,
                    "version": "1.0.0",
                    "date": datetime.fromtimestamp(clip_file.stat().st_mtime).strftime('%Y-%m-%d')
                }
            
            # Apply filter if provided
            if query:
                regex = re.compile(query, re.IGNORECASE)
                full_content = clip_file.read_text(encoding='utf-8')
                metadata_str = json.dumps(metadata)
                if not (regex.search(metadata_str) or regex.search(full_content)):
                    continue
            
            created_at, updated_at = FilesystemService.get_file_timestamps(clip_file)
            
            clips.append({
                "clip_id": clip_id,
                "project_id": project_id,
                "name": metadata.get("name", clip_id),
                "code": "",  # Don't include full code in list
                "created_at": metadata.get("date", created_at.isoformat()),
                "updated_at": updated_at.isoformat(),
                "metadata": metadata
            })
        
        return clips
    
    @staticmethod
    def get_clip(project_id: str, clip_id: str) -> Optional[dict]:
        """Get a single clip with full content."""
        project_path = FilesystemService.get_project_path(project_id)
        clip_file = project_path / "clips" / f"{clip_id}.js"
        
        if not clip_file.exists():
            return None
        
        content = clip_file.read_text(encoding='utf-8')
        metadata = FilesystemService.parse_clip_metadata(clip_file)
        
        # Extract code (everything after first line)
        code = '\n'.join(content.split('\n')[1:])
        
        if not metadata:
            metadata = {
                "name": clip_id,
                "tags": [],
                "tempo": None,
                "description": "",
                "author": None,
                "version": "1.0.0",
                "date": datetime.fromtimestamp(clip_file.stat().st_mtime).strftime('%Y-%m-%d')
            }
        
        created_at, updated_at = FilesystemService.get_file_timestamps(clip_file)
        
        return {
            "clip_id": clip_id,
            "project_id": project_id,
            "name": metadata.get("name", clip_id),
            "code": code,
            "created_at": metadata.get("date", created_at.isoformat()),
            "updated_at": updated_at.isoformat(),
            "metadata": metadata
        }
    
    @staticmethod
    def create_clip(
        project_id: str,
        clip_id: str,
        name: str,
        code: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """Create a new clip."""
        FilesystemService.ensure_project_structure(project_id)
        clips_dir = FilesystemService.get_project_path(project_id) / "clips"
        clip_file = clips_dir / f"{clip_id}.js"
        
        if clip_file.exists():
            return {"error": f"Clip '{clip_id}' already exists", "success": False}
        
        # Build metadata
        clip_metadata = metadata or {}
        clip_metadata["name"] = name
        if "tags" not in clip_metadata:
            clip_metadata["tags"] = []
        if "tempo" not in clip_metadata:
            clip_metadata["tempo"] = None
        if "description" not in clip_metadata:
            clip_metadata["description"] = ""
        if "author" not in clip_metadata:
            clip_metadata["author"] = None
        if "version" not in clip_metadata:
            clip_metadata["version"] = "1.0.0"
        if "date" not in clip_metadata:
            clip_metadata["date"] = date_module.today().strftime('%Y-%m-%d')
        
        # Create file content
        metadata_json = json.dumps(clip_metadata)
        content = f"// {metadata_json}\n{code}"
        clip_file.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "clip_id": clip_id,
            "message": f"Clip '{clip_id}' created successfully"
        }
    
    @staticmethod
    def update_clip(
        project_id: str,
        clip_id: str,
        name: Optional[str] = None,
        code: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """Update an existing clip."""
        clips_dir = FilesystemService.get_project_path(project_id) / "clips"
        clip_file = clips_dir / f"{clip_id}.js"
        
        if not clip_file.exists():
            return {"error": f"Clip '{clip_id}' not found", "success": False}
        
        # Read existing
        existing_content = clip_file.read_text(encoding='utf-8')
        existing_metadata = FilesystemService.parse_clip_metadata(clip_file) or {}
        existing_code = '\n'.join(existing_content.split('\n')[1:])
        
        # Merge metadata
        new_metadata = existing_metadata.copy()
        if metadata:
            new_metadata.update(metadata)
        if name is not None:
            new_metadata["name"] = name
        
        # Update date
        new_metadata["date"] = date_module.today().strftime('%Y-%m-%d')
        
        # Use new code or keep existing
        new_code = code if code is not None else existing_code
        
        # Write updated content
        metadata_json = json.dumps(new_metadata)
        content = f"// {metadata_json}\n{new_code}"
        clip_file.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "clip_id": clip_id,
            "message": f"Clip '{clip_id}' updated successfully"
        }
    
    @staticmethod
    def delete_clip(project_id: str, clip_id: str) -> dict:
        """Delete a clip."""
        clips_dir = FilesystemService.get_project_path(project_id) / "clips"
        clip_file = clips_dir / f"{clip_id}.js"
        
        if not clip_file.exists():
            return {"error": f"Clip '{clip_id}' not found", "success": False}
        
        clip_file.unlink()
        
        return {
            "success": True,
            "project_id": project_id,
            "clip_id": clip_id,
            "message": f"Clip '{clip_id}' deleted successfully"
        }
    
    # ========================================================================
    # Song Operations
    # ========================================================================
    
    @staticmethod
    def list_songs(project_id: str, query: Optional[str] = None) -> list[dict]:
        """List songs in a project with optional regex filter."""
        project_path = FilesystemService.get_project_path(project_id)
        if not project_path.exists():
            return []
        
        songs_dir = project_path / "songs"
        if not songs_dir.exists():
            return []
        
        songs = []
        for song_file in songs_dir.glob("*.md"):
            song_id = song_file.stem
            title, description = FilesystemService.parse_markdown_header(song_file)
            
            # Apply filter if provided
            if query:
                regex = re.compile(query, re.IGNORECASE)
                full_content = song_file.read_text(encoding='utf-8')
                if not regex.search(full_content):
                    continue
            
            created_at, updated_at = FilesystemService.get_file_timestamps(song_file)
            
            songs.append({
                "song_id": song_id,
                "project_id": project_id,
                "name": title or song_id,
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
                "clip_ids": [],  # Could parse from body if needed
                "metadata": {
                    "title": title or song_id,
                    "description": description or ""
                }
            })
        
        return songs
    
    @staticmethod
    def get_song(project_id: str, song_id: str) -> Optional[dict]:
        """Get a single song with full content."""
        project_path = FilesystemService.get_project_path(project_id)
        song_file = project_path / "songs" / f"{song_id}.md"
        
        if not song_file.exists():
            return None
        
        content = song_file.read_text(encoding='utf-8')
        title, description = FilesystemService.parse_markdown_header(song_file)
        created_at, updated_at = FilesystemService.get_file_timestamps(song_file)
        
        return {
            "song_id": song_id,
            "project_id": project_id,
            "name": title or song_id,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
            "clip_ids": [],
            "metadata": {
                "title": title or song_id,
                "description": description or "",
                "body": content
            }
        }
    
    @staticmethod
    def create_song(
        project_id: str,
        song_id: str,
        name: str,
        clip_ids: Optional[list] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """Create a new song."""
        FilesystemService.ensure_project_structure(project_id)
        songs_dir = FilesystemService.get_project_path(project_id) / "songs"
        song_file = songs_dir / f"{song_id}.md"
        
        if song_file.exists():
            return {"error": f"Song '{song_id}' already exists", "success": False}
        
        description = metadata.get("description", "") if metadata else ""
        body = metadata.get("body", "") if metadata else ""
        
        content = f"# {name}\n\n{description}\n\n{body}"
        song_file.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "song_id": song_id,
            "message": f"Song '{song_id}' created successfully"
        }
    
    @staticmethod
    def update_song(
        project_id: str,
        song_id: str,
        name: Optional[str] = None,
        clip_ids: Optional[list] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """Update an existing song."""
        songs_dir = FilesystemService.get_project_path(project_id) / "songs"
        song_file = songs_dir / f"{song_id}.md"
        
        if not song_file.exists():
            return {"error": f"Song '{song_id}' not found", "success": False}
        
        # Read existing
        existing_content = song_file.read_text(encoding='utf-8')
        existing_title, existing_desc = FilesystemService.parse_markdown_header(song_file)
        
        # Extract existing body
        lines = existing_content.split('\n')
        body_start = 0
        found_title = False
        found_desc = False
        for i, line in enumerate(lines):
            if line.startswith('# ') and not found_title:
                found_title = True
                continue
            if found_title and not found_desc and line.strip():
                found_desc = True
                body_start = i + 1
                break
        existing_body = '\n'.join(lines[body_start:])
        
        # Use new or keep existing
        new_title = name if name is not None else existing_title
        new_desc = metadata.get("description", existing_desc) if metadata else existing_desc
        new_body = metadata.get("body", existing_body) if metadata else existing_body
        
        content = f"# {new_title}\n\n{new_desc}\n\n{new_body}"
        song_file.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "song_id": song_id,
            "message": f"Song '{song_id}' updated successfully"
        }
    
    @staticmethod
    def delete_song(project_id: str, song_id: str) -> dict:
        """Delete a song."""
        songs_dir = FilesystemService.get_project_path(project_id) / "songs"
        song_file = songs_dir / f"{song_id}.md"
        
        if not song_file.exists():
            return {"error": f"Song '{song_id}' not found", "success": False}
        
        song_file.unlink()
        
        return {
            "success": True,
            "project_id": project_id,
            "song_id": song_id,
            "message": f"Song '{song_id}' deleted successfully"
        }
    
    # ========================================================================
    # Playlist Operations
    # ========================================================================
    
    @staticmethod
    def list_playlists(project_id: str, query: Optional[str] = None) -> list[dict]:
        """List playlists in a project with optional regex filter."""
        project_path = FilesystemService.get_project_path(project_id)
        if not project_path.exists():
            return []
        
        playlists_dir = project_path / "playlists"
        if not playlists_dir.exists():
            return []
        
        playlists = []
        for playlist_file in playlists_dir.glob("*.md"):
            playlist_id = playlist_file.stem
            title, _ = FilesystemService.parse_markdown_header(playlist_file)
            
            # Apply filter if provided
            if query:
                regex = re.compile(query, re.IGNORECASE)
                full_content = playlist_file.read_text(encoding='utf-8')
                if not regex.search(full_content):
                    continue
            
            created_at, updated_at = FilesystemService.get_file_timestamps(playlist_file)
            
            playlists.append({
                "playlist_id": playlist_id,
                "project_id": project_id,
                "name": title or playlist_id,
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
                "song_ids": [],  # Could parse from body if needed
                "metadata": {
                    "title": title or playlist_id
                }
            })
        
        return playlists
    
    @staticmethod
    def get_playlist(project_id: str, playlist_id: str) -> Optional[dict]:
        """Get a single playlist with full content."""
        project_path = FilesystemService.get_project_path(project_id)
        playlist_file = project_path / "playlists" / f"{playlist_id}.md"
        
        if not playlist_file.exists():
            return None
        
        content = playlist_file.read_text(encoding='utf-8')
        title, _ = FilesystemService.parse_markdown_header(playlist_file)
        created_at, updated_at = FilesystemService.get_file_timestamps(playlist_file)
        
        return {
            "playlist_id": playlist_id,
            "project_id": project_id,
            "name": title or playlist_id,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
            "song_ids": [],
            "metadata": {
                "title": title or playlist_id,
                "body": content
            }
        }
    
    @staticmethod
    def create_playlist(
        project_id: str,
        playlist_id: str,
        name: str,
        song_ids: Optional[list] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """Create a new playlist."""
        FilesystemService.ensure_project_structure(project_id)
        playlists_dir = FilesystemService.get_project_path(project_id) / "playlists"
        playlist_file = playlists_dir / f"{playlist_id}.md"
        
        if playlist_file.exists():
            return {"error": f"Playlist '{playlist_id}' already exists", "success": False}
        
        body = metadata.get("body", "") if metadata else ""
        
        content = f"# {name}\n\n{body}"
        playlist_file.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "playlist_id": playlist_id,
            "message": f"Playlist '{playlist_id}' created successfully"
        }
    
    @staticmethod
    def update_playlist(
        project_id: str,
        playlist_id: str,
        name: Optional[str] = None,
        song_ids: Optional[list] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """Update an existing playlist."""
        playlists_dir = FilesystemService.get_project_path(project_id) / "playlists"
        playlist_file = playlists_dir / f"{playlist_id}.md"
        
        if not playlist_file.exists():
            return {"error": f"Playlist '{playlist_id}' not found", "success": False}
        
        # Read existing
        existing_content = playlist_file.read_text(encoding='utf-8')
        existing_title, _ = FilesystemService.parse_markdown_header(playlist_file)
        
        # Extract existing body
        lines = existing_content.split('\n')
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                body_start = i + 1
                break
        # Skip empty lines after title
        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1
        existing_body = '\n'.join(lines[body_start:])
        
        # Use new or keep existing
        new_title = name if name is not None else existing_title
        new_body = metadata.get("body", existing_body) if metadata else existing_body
        
        content = f"# {new_title}\n\n{new_body}"
        playlist_file.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "project_id": project_id,
            "playlist_id": playlist_id,
            "message": f"Playlist '{playlist_id}' updated successfully"
        }
    
    @staticmethod
    def delete_playlist(project_id: str, playlist_id: str) -> dict:
        """Delete a playlist."""
        playlists_dir = FilesystemService.get_project_path(project_id) / "playlists"
        playlist_file = playlists_dir / f"{playlist_id}.md"
        
        if not playlist_file.exists():
            return {"error": f"Playlist '{playlist_id}' not found", "success": False}
        
        playlist_file.unlink()
        
        return {
            "success": True,
            "project_id": project_id,
            "playlist_id": playlist_id,
            "message": f"Playlist '{playlist_id}' deleted successfully"
        }
