#!/usr/bin/env python3
"""Strudel MCP Server - Filesystem-based MVP

Provides tools for managing Strudel music projects:
- Knowledge base search
- Project/clip/song/playlist CRUD operations
- Regex-based search across project content
"""

from pathlib import Path
import json
import re
import yaml
from typing import Any, List
from typing import Optional, Literal
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Strudel Music Assistant")

# Base paths
BASE_DIR = Path(__file__).parent
PROJECTS_DIR = BASE_DIR / "projects"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
KNOWN_PACKS_DIR = BASE_DIR / "known_packs"

# Ensure directories exist
PROJECTS_DIR.mkdir(exist_ok=True)
KNOWLEDGE_DIR.mkdir(exist_ok=True)
KNOWN_PACKS_DIR.mkdir(exist_ok=True)

# ============================================================================
# Response Models
# ============================================================================

class ClipMetadata(BaseModel):
    """Metadata for a Strudel clip"""
    name: str = Field(description="Human-readable clip name")
    tags: list[str] = Field(
        default_factory=list,
        description="Searchable tags for categorizing the clip (e.g., 'drums', 'bass', 'techno')"
    )
    tempo: Optional[int] = Field(
        default=None,
        description="BPM (beats per minute) if relevant to the clip"
    )
    description: str = Field(
        description="What this clip does musically - describe the sound, pattern, or musical function"
    )


class SearchMatch(BaseModel):
    """A single search result match"""
    line_number: int = Field(description="Line number where the match was found")
    content: str = Field(description="The matched line content")
    context: str = Field(description="Surrounding lines for context")


class ClipInfo(BaseModel):
    """Clip listing information"""
    clip_id: str = Field(description="Unique identifier for the clip (filename without extension)")
    name: str = Field(description="Human-readable clip name")
    tags: list[str] = Field(description="Tags associated with the clip")
    tempo: Optional[int] = Field(description="BPM if specified")
    description: str = Field(description="Musical description of the clip")


class SongInfo(BaseModel):
    """Song listing information"""
    song_id: str = Field(description="Unique identifier for the song (filename without extension)")
    title: str = Field(description="Song title from H1 header")
    description: str = Field(description="Song description from second line")


class PlaylistInfo(BaseModel):
    """Playlist listing information"""
    playlist_id: str = Field(description="Unique identifier for the playlist (filename without extension)")
    title: str = Field(description="Playlist title from H1 header")


class ProjectInfo(BaseModel):
    """Project listing information"""
    project_id: str = Field(description="Unique identifier for the project (folder name)")
    name: str = Field(description="Project name from index.md")
    description: str = Field(description="Project description from index.md")
    clip_count: int = Field(description="Number of clips in the project")
    song_count: int = Field(description="Number of songs in the project")
    playlist_count: int = Field(description="Number of playlists in the project")


# ============================================================================
# Request Models
# ============================================================================

class SearchKnowledgeRequest(BaseModel):
    """Request to search the knowledge base"""
    query: str = Field(
        description="Regex pattern to search for in knowledge files (case-insensitive). Use simple patterns like 'filter' or complex ones like 'lpf|hpf|filter'"
    )

class ListKnowledgeRequest(BaseModel):
    """Request to list the available knowledge documents"""
    pass

class ReadKnowledgeDocRequest(BaseModel):
    """Request to read a full knowledge document file"""
    document_filenames: List[str] = Field(..., description="The document filenames to read")


class ListProjectsRequest(BaseModel):
    """Request to list projects"""
    query: Optional[str] = Field(
        default=None,
        description="Optional regex pattern to filter projects by name or description"
    )


class WriteProjectIndexRequest(BaseModel):
    """Request to create or update project index"""
    project_id: str = Field(
        description="Unique identifier for the project (will be used as folder name)"
    )
    content: str = Field(
        description="Full markdown content for the index.md file. Should include H1 title and project description."
    )


class ListClipsRequest(BaseModel):
    """Request to list clips in a project"""
    project_id: str = Field(
        description="Unique identifier for the project containing the clips"
    )
    query: Optional[str] = Field(
        default=None,
        description="Optional regex pattern to filter clips by metadata or code content"
    )


class SearchClipsRequest(BaseModel):
    """Request to search clip code"""
    project_id: str = Field(
        description="Unique identifier for the project to search within"
    )
    query: str = Field(
        description="Regex pattern to search for in clip code (case-insensitive)"
    )


class GetClipsRequest(BaseModel):
    """Request to retrieve specific clips"""
    project_id: str = Field(
        description="Unique identifier for the project containing the clips"
    )
    clip_ids: list[str] = Field(
        description="List of clip IDs (filenames without .js extension) to retrieve"
    )


class SaveNewClipRequest(BaseModel):
    """Request to create a new clip"""
    project_id: str = Field(
        description="Unique identifier for the project where the clip will be created"
    )
    clip_id: str = Field(
        description="Unique identifier for the clip (will be used as filename without extension). Use lowercase with underscores."
    )
    metadata: dict = Field(
        description="Clip metadata dictionary with keys: 'name' (str), 'tags' (list[str]), 'tempo' (int, optional), 'description' (str)"
    )
    strudel_script: str = Field(
        description="JavaScript Strudel code for the clip (without the metadata comment line)"
    )


class UpdateClipRequest(BaseModel):
    """Request to update an existing clip"""
    project_id: str = Field(
        description="Unique identifier for the project containing the clip"
    )
    clip_id: str = Field(
        description="Unique identifier for the clip to update"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Optional new metadata. If None, keeps existing metadata."
    )
    strudel_script: Optional[str] = Field(
        default=None,
        description="Optional new Strudel code. If None, keeps existing code."
    )


class ListSongsRequest(BaseModel):
    """Request to list songs in a project"""
    project_id: str = Field(
        description="Unique identifier for the project containing the songs"
    )
    query: Optional[str] = Field(
        default=None,
        description="Optional regex pattern to filter songs by content"
    )


class GetSongsRequest(BaseModel):
    """Request to retrieve specific songs"""
    project_id: str = Field(
        description="Unique identifier for the project containing the songs"
    )
    song_ids: list[str] = Field(
        description="List of song IDs (filenames without .md extension) to retrieve"
    )


class SaveNewSongRequest(BaseModel):
    """Request to create a new song"""
    project_id: str = Field(
        description="Unique identifier for the project where the song will be created"
    )
    song_id: str = Field(
        description="Unique identifier for the song (will be used as filename without extension). Use lowercase with underscores."
    )
    title: str = Field(
        description="Song title (will become the H1 header)"
    )
    description: str = Field(
        description="Song description (will be placed on the second line)"
    )
    body: str = Field(
        description="Markdown content with clip links and song structure. Use relative links like [clip_name](../clips/clip_id.js)"
    )


class UpdateSongRequest(BaseModel):
    """Request to update an existing song"""
    project_id: str = Field(
        description="Unique identifier for the project containing the song"
    )
    song_id: str = Field(
        description="Unique identifier for the song to update"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional new title. If None, keeps existing title."
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional new description. If None, keeps existing description."
    )
    body: Optional[str] = Field(
        default=None,
        description="Optional new body content. If None, keeps existing body."
    )


class ListPlaylistsRequest(BaseModel):
    """Request to list playlists in a project"""
    project_id: str = Field(
        description="Unique identifier for the project containing the playlists"
    )
    title_query: Optional[str] = Field(
        default=None,
        description="Optional regex pattern to filter playlists by title"
    )
    query: Optional[str] = Field(
        default=None,
        description="Optional regex pattern to filter playlists by content"
    )


class GetPlaylistsRequest(BaseModel):
    """Request to retrieve specific playlists"""
    project_id: str = Field(
        description="Unique identifier for the project containing the playlists"
    )
    playlist_ids: list[str] = Field(
        description="List of playlist IDs (filenames without .md extension) to retrieve"
    )


class SaveNewPlaylistRequest(BaseModel):
    """Request to create a new playlist"""
    project_id: str = Field(
        description="Unique identifier for the project where the playlist will be created"
    )
    playlist_id: str = Field(
        description="Unique identifier for the playlist (will be used as filename without extension). Use lowercase with underscores."
    )
    title: str = Field(
        description="Playlist title (will become the H1 header)"
    )
    body: str = Field(
        description="Markdown content with song links and transitions. Use relative links like [song_name](../songs/song_id.md)"
    )


class UpdatePlaylistRequest(BaseModel):
    """Request to update an existing playlist"""
    project_id: str = Field(
        description="Unique identifier for the project containing the playlist"
    )
    playlist_id: str = Field(
        description="Unique identifier for the playlist to update"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional new title. If None, keeps existing title."
    )
    body: Optional[str] = Field(
        default=None,
        description="Optional new body content. If None, keeps existing body."
    )

# ============================================================================
# Surface Template Request Models
# ============================================================================

class CreateTemplateRequest(BaseModel):
    """Request to create a new surface template"""
    project_id: str = Field(
        description="Unique identifier for the project where template will be created"
    )
    template_id: str = Field(
        description="Unique identifier for the template (filename without .yaml). Use lowercase with underscores."
    )
    template_code: str = Field(
        description="Strudel code with {variable} placeholders for parameterization"
    )
    input_schema: dict = Field(
        description="Schema defining variables. Each key is a variable name with dict containing: type (string/integer/float/boolean/array), default, description, and optional constraints (min, max, options, pattern, required, min_items, max_items)"
    )
    metadata: dict = Field(
        description="Template metadata with keys: name (str), description (str), tags (list[str]), category (str), author (str), created (str)"
    )
    includes: Optional[dict] = Field(
        default=None,
        description="Optional dict mapping placeholder names to template IDs for composition. Example: {'kick_template': 'techno_kick'}"
    )


class ListTemplatesRequest(BaseModel):
    """Request to list surface templates"""
    project_id: str = Field(
        description="Unique identifier for the project containing templates"
    )
    category: Optional[str] = Field(
        default=None,
        description="Filter by category (drums, bass, melody, fx, full_pattern)"
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Filter by tags (returns templates matching any tag)"
    )
    query: Optional[str] = Field(
        default=None,
        description="Regex pattern to search across template metadata"
    )


class GetTemplateSchemaRequest(BaseModel):
    """Request to get full schema for a template"""
    project_id: str = Field(
        description="Unique identifier for the project containing the template"
    )
    template_id: str = Field(
        description="Template ID to inspect"
    )


class GenerateFromTemplateRequest(BaseModel):
    """Request to generate code from a template"""
    project_id: str = Field(
        description="Unique identifier for the project containing the template"
    )
    template_id: str = Field(
        description="Template ID to use for generation"
    )
    variables: dict = Field(
        default_factory=dict,
        description="Variable values to fill into template. Keys are variable names, values are the actual values to use."
    )
    do_validation: bool = Field(
        default=True,
        description="Whether to validate variables against schema before generating"
    )


class UpdateTemplateRequest(BaseModel):
    """Request to update an existing template"""
    project_id: str = Field(
        description="Unique identifier for the project containing the template"
    )
    template_id: str = Field(
        description="Template ID to update"
    )
    template_code: Optional[str] = Field(
        default=None,
        description="Optional new template code. If None, keeps existing."
    )
    input_schema: Optional[dict] = Field(
        default=None,
        description="Optional new schema. If None, keeps existing."
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Optional new metadata. If None, keeps existing."
    )
    includes: Optional[dict] = Field(
        default=None,
        description="Optional new includes. If None, keeps existing."
    )


# ============================================================================
# Utility Functions
# ============================================================================

def regex_search_file(file_path: Path, pattern: str, context_lines: int = 2) -> list[SearchMatch]:
    """Search a file for regex pattern and return matches with context"""
    if not file_path.exists():
        return []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        matches = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for i, line in enumerate(lines):
            if regex.search(line):
                # Get context lines
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = '\n'.join(lines[start:end])
                
                matches.append(SearchMatch(
                    line_number=i + 1,
                    content=line,
                    context=context
                ))
        
        return matches
    except Exception as e:
        return []


def parse_clip_metadata(file_path: Path) -> Optional[ClipMetadata]:
    """Parse metadata from first line of clip file"""
    try:
        first_line = file_path.read_text(encoding='utf-8').split('\n')[0]
        # Extract JSON from comment: // {"key": "value"}
        json_match = re.search(r'//\s*({.+})', first_line)
        if json_match:
            metadata_dict = json.loads(json_match.group(1))
            return ClipMetadata(**metadata_dict)
    except Exception:
        pass
    return None


def parse_markdown_header(file_path: Path) -> tuple[Optional[str], Optional[str]]:
    """Parse title (H1) and description (second line) from markdown file"""
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


def get_project_path(project_id: str) -> Path:
    """Get path to project directory"""
    return PROJECTS_DIR / project_id


def ensure_project_structure(project_id: str):
    """Ensure project directory structure exists"""
    project_path = get_project_path(project_id)
    project_path.mkdir(exist_ok=True)
    (project_path / "clips").mkdir(exist_ok=True)
    (project_path / "songs").mkdir(exist_ok=True)
    (project_path / "playlists").mkdir(exist_ok=True)

# ============================================================================
# Surface Template Utility Functions
# ============================================================================

def validate_variable(name: str, value: Any, schema_def: dict) -> list[str]:
    """Validate a variable value against its schema definition"""
    errors = []
    
    # Type validation
    type_map = {
        'string': str,
        'integer': int,
        'float': (int, float),
        'boolean': bool,
        'array': list
    }
    
    expected_type = schema_def.get('type')
    if expected_type not in type_map:
        errors.append(f"{name}: Unknown type '{expected_type}'")
        return errors
    
    if not isinstance(value, type_map[expected_type]):
        errors.append(f"{name}: Expected {expected_type}, got {type(value).__name__}")
        return errors
    
    # Range validation (numbers)
    if expected_type in ['integer', 'float']:
        if 'min' in schema_def and value < schema_def['min']:
            errors.append(f"{name}: Value {value} below minimum {schema_def['min']}")
        if 'max' in schema_def and value > schema_def['max']:
            errors.append(f"{name}: Value {value} above maximum {schema_def['max']}")
    
    # Enum validation
    if 'options' in schema_def:
        if value not in schema_def['options']:
            errors.append(f"{name}: Value '{value}' not in allowed options: {schema_def['options']}")
    
    # Pattern validation (strings)
    if expected_type == 'string' and 'pattern' in schema_def:
        if not re.match(schema_def['pattern'], str(value)):
            errors.append(f"{name}: Value '{value}' does not match pattern '{schema_def['pattern']}'")
    
    # String length validation
    if expected_type == 'string':
        if 'min_length' in schema_def and len(value) < schema_def['min_length']:
            errors.append(f"{name}: String too short (min {schema_def['min_length']})")
        if 'max_length' in schema_def and len(value) > schema_def['max_length']:
            errors.append(f"{name}: String too long (max {schema_def['max_length']})")
    
    # Array constraints
    if expected_type == 'array':
        if 'min_items' in schema_def and len(value) < schema_def['min_items']:
            errors.append(f"{name}: Array too short (min {schema_def['min_items']} items)")
        if 'max_items' in schema_def and len(value) > schema_def['max_items']:
            errors.append(f"{name}: Array too long (max {schema_def['max_items']} items)")
        
        # Validate array item types
        if 'items_type' in schema_def:
            items_type_map = type_map.get(schema_def['items_type'])
            for i, item in enumerate(value):
                if not isinstance(item, items_type_map):
                    errors.append(f"{name}[{i}]: Expected {schema_def['items_type']}, got {type(item).__name__}")
    
    return errors


def load_template_yaml(project_id: str, template_id: str) -> Optional[dict]:
    """Load and parse template YAML file"""
    template_path = get_project_path(project_id) / "surfaces" / f"{template_id}.yaml"
    
    if not template_path.exists():
        return None
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        return None


def resolve_template_includes(project_id: str, template_data: dict, resolution_stack: Optional[list] = None) -> tuple[str, list[str]]:
    """Recursively resolve template includes
    
    Returns:
        (resolved_template_code, errors)
    """
    if resolution_stack is None:
        resolution_stack = []
    
    template_code = template_data.get('template', '')
    includes = template_data.get('includes', {})
    errors = []
    
    if not includes:
        return template_code, errors
    
    # Resolve each include
    resolved_includes = {}
    for placeholder, included_template_id in includes.items():
        # Check for circular dependency
        if included_template_id in resolution_stack:
            errors.append(f"Circular dependency: {' -> '.join(resolution_stack + [included_template_id])}")
            continue
        
        # Load included template
        included_data = load_template_yaml(project_id, included_template_id)
        if not included_data:
            errors.append(f"Included template '{included_template_id}' not found")
            continue
        
        # Recursively resolve includes
        new_stack = resolution_stack + [included_template_id]
        resolved_code, include_errors = resolve_template_includes(project_id, included_data, new_stack)
        errors.extend(include_errors)
        
        # Render included template with its defaults
        included_schema = included_data.get('schema', {})
        included_vars = {name: def_data.get('default', '') for name, def_data in included_schema.items()}
        
        try:
            rendered_include = resolved_code.format(**included_vars)
            resolved_includes[placeholder] = rendered_include
        except KeyError as e:
            errors.append(f"Missing variable in included template '{included_template_id}': {e}")
            resolved_includes[placeholder] = resolved_code
    
    # Replace include placeholders
    try:
        final_code = template_code.format(**resolved_includes)
    except KeyError as e:
        errors.append(f"Missing include placeholder: {e}")
        final_code = template_code
    
    return final_code, errors

def generate_code_from_template(project_id: str, template_id: str, variables: dict, validate: bool = True) -> dict:
    """Generate Strudel code from template with variable substitution
    
    Returns:
        Dict with 'code', 'errors', 'variables_used'
    """
    # Load template
    template_data = load_template_yaml(project_id, template_id)
    if not template_data:
        return {
            'code': None,
            'errors': [f"Template '{template_id}' not found"],
            'variables_used': {}
        }
    
    schema = template_data.get('schema', {})
    errors = []
    
    # Merge provided variables with defaults
    final_vars = {}
    for var_name, var_schema in schema.items():
        if var_name in variables:
            final_vars[var_name] = variables[var_name]
        elif 'default' in var_schema:
            final_vars[var_name] = var_schema['default']
        elif var_schema.get('required', False):
            errors.append(f"Required variable '{var_name}' not provided")
    
    # Validate variables
    if validate:
        for var_name, var_value in final_vars.items():
            if var_name in schema:
                var_errors = validate_variable(var_name, var_value, schema[var_name])
                errors.extend(var_errors)
    
    # Stop if validation errors
    if errors:
        return {
            'code': None,
            'errors': errors,
            'variables_used': final_vars
        }
    
    # Resolve includes
    template_code, include_errors = resolve_template_includes(project_id, template_data)
    errors.extend(include_errors)
    
    if errors:
        return {
            'code': None,
            'errors': errors,
            'variables_used': final_vars
        }
    
    # Render template
    try:
        generated_code = template_code.format(**final_vars)
    except KeyError as e:
        errors.append(f"Missing variable in template: {e}")
        return {
            'code': None,
            'errors': errors,
            'variables_used': final_vars
        }
    
    return {
        'code': generated_code,
        'errors': [],
        'variables_used': final_vars
    }


# ============================================================================
# Knowledge Tools
# ============================================================================

@mcp.tool()
def search_knowledge(request: SearchKnowledgeRequest) -> dict:
    """
    Search Strudel reference knowledge base using regex.
    
    Returns:
        Dictionary with search results from knowledge files
    """
    results = []
    
    if not KNOWLEDGE_DIR.exists():
        return {"results": [], "message": "Knowledge directory not found"}
    
    for md_file in KNOWLEDGE_DIR.glob("*.md"):
        matches = regex_search_file(md_file, request.query)
        if matches:
            results.append({
                "file": md_file.name,
                "matches": [m.model_dump() for m in matches]
            })
    
    return {
        "results": results,
        "total_files": len(results),
        "query": request.query
    }


@mcp.tool()
def list_knowledgebase_docs(request: ListKnowledgeRequest) -> dict:
    """Use this tool when you need to get the full context of some topic and search is not giving you the full context, perhaps during debugging"""
    docs = []
    for knowledge_doc in KNOWLEDGE_DIR.iterdir():
        if not knowledge_doc.is_dir():
            continue
        
        docs.append(knowledge_doc.name)
        
    return {"knowledge_documents": docs}

@mcp.tool()
def read_full_knowledge_docs(request: ReadKnowledgeDocRequest) -> dict:
    """Use this tool after calling list_knowledgebase_docs in order to read multiple documents at a time"""
    content = []
    for doc in request.document_filenames:
        path = KNOWLEDGE_DIR / doc
        with open(path, 'r') as f:
            content.append({
                "document_filename": doc,
                "content": f.read()
            })
    return {"documents": content}

# ============================================================================
# Project Tools
# ============================================================================

@mcp.tool()
def list_projects(request: ListProjectsRequest) -> dict:
    """
    List all projects with optional regex filter.
    
    Returns:
        List of projects with metadata
    """
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
            title, desc = parse_markdown_header(index_file)
            if title:
                name = title
            if desc:
                description = desc
        
        # Apply filter if provided
        if request.query:
            regex = re.compile(request.query, re.IGNORECASE)
            if not (regex.search(name) or regex.search(description)):
                continue
        
        # Count items
        clip_count = len(list((project_dir / "clips").glob("*.js"))) if (project_dir / "clips").exists() else 0
        song_count = len(list((project_dir / "songs").glob("*.md"))) if (project_dir / "songs").exists() else 0
        playlist_count = len(list((project_dir / "playlists").glob("*.md"))) if (project_dir / "playlists").exists() else 0
        
        projects.append(ProjectInfo(
            project_id=project_id,
            name=name,
            description=description,
            clip_count=clip_count,
            song_count=song_count,
            playlist_count=playlist_count
        ).model_dump())
    
    return {"projects": projects, "total": len(projects)}


@mcp.tool()
def write_project_index(request: WriteProjectIndexRequest) -> dict:
    """
    Create or update project index file.
    
    Returns:
        Success confirmation
    """
    ensure_project_structure(request.project_id)
    index_file = get_project_path(request.project_id) / "index.md"
    index_file.write_text(request.content, encoding='utf-8')
    
    return {
        "success": True,
        "project_id": request.project_id,
        "message": f"Project index updated for '{request.project_id}'"
    }


# ============================================================================
# Clip Tools
# ============================================================================

@mcp.tool()
def list_clips(request: ListClipsRequest) -> dict:
    """
    List clips in a project with optional regex filter.
    
    Returns:
        List of clips with metadata
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "clips": []}
    
    clips_dir = project_path / "clips"
    if not clips_dir.exists():
        return {"clips": [], "total": 0}
    
    clips = []
    for clip_file in clips_dir.glob("*.js"):
        clip_id = clip_file.stem
        metadata = parse_clip_metadata(clip_file)
        
        if not metadata:
            continue
        
        # Apply filter if provided
        if request.query:
            regex = re.compile(request.query, re.IGNORECASE)
            # Search in metadata and code
            full_content = clip_file.read_text(encoding='utf-8')
            metadata_str = json.dumps(metadata.model_dump())
            if not (regex.search(metadata_str) or regex.search(full_content)):
                continue
        
        clips.append(ClipInfo(
            clip_id=clip_id,
            name=metadata.name,
            tags=metadata.tags,
            tempo=metadata.tempo,
            description=metadata.description
        ).model_dump())
    
    return {"clips": clips, "total": len(clips), "project_id": request.project_id}


@mcp.tool()
def search_clips(request: SearchClipsRequest) -> dict:
    """
    Full-text regex search across all clip code in a project.
    
    Returns:
        Search results with matches and context
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "results": []}
    
    clips_dir = project_path / "clips"
    if not clips_dir.exists():
        return {"results": [], "total": 0}
    
    results = []
    for clip_file in clips_dir.glob("*.js"):
        matches = regex_search_file(clip_file, request.query)
        if matches:
            metadata = parse_clip_metadata(clip_file)
            results.append({
                "clip_id": clip_file.stem,
                "metadata": metadata.model_dump() if metadata else {},
                "matches": [m.model_dump() for m in matches]
            })
    
    return {
        "results": results,
        "total": len(results),
        "project_id": request.project_id,
        "query": request.query
    }


@mcp.tool()
def get_clips(request: GetClipsRequest) -> dict:
    """
    Retrieve full content of specific clips.
    
    Returns:
        Full clip data including metadata and code
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "clips": []}
    
    clips_dir = project_path / "clips"
    clips = []
    
    for clip_id in request.clip_ids:
        clip_file = clips_dir / f"{clip_id}.js"
        if not clip_file.exists():
            clips.append({
                "clip_id": clip_id,
                "error": "Clip not found"
            })
            continue
        
        content = clip_file.read_text(encoding='utf-8')
        metadata = parse_clip_metadata(clip_file)
        
        # Extract code (everything after first line)
        code = '\n'.join(content.split('\n')[1:])
        
        clips.append({
            "clip_id": clip_id,
            "metadata": metadata.model_dump() if metadata else {},
            "code": code
        })
    
    return {"clips": clips, "project_id": request.project_id}


@mcp.tool()
def save_new_clip(request: SaveNewClipRequest) -> dict:
    """
    Create a new clip.
    
    Returns:
        Success confirmation
    """
    ensure_project_structure(request.project_id)
    clips_dir = get_project_path(request.project_id) / "clips"
    clip_file = clips_dir / f"{request.clip_id}.js"
    
    if clip_file.exists():
        return {
            "error": f"Clip '{request.clip_id}' already exists. Use update_clip to modify.",
            "success": False
        }
    
    # Validate metadata
    try:
        clip_metadata = ClipMetadata(**request.metadata)
    except Exception as e:
        return {"error": f"Invalid metadata: {str(e)}", "success": False}
    
    # Create file content
    metadata_json = json.dumps(clip_metadata.model_dump())
    content = f"// {metadata_json}\n{request.strudel_script}"
    
    clip_file.write_text(content, encoding='utf-8')
    
    return {
        "success": True,
        "project_id": request.project_id,
        "clip_id": request.clip_id,
        "message": f"Clip '{request.clip_id}' created successfully"
    }


@mcp.tool()
def update_clip(request: UpdateClipRequest) -> dict:
    """
    Update existing clip (overwrites file).
    
    Returns:
        Success confirmation
    """
    clips_dir = get_project_path(request.project_id) / "clips"
    clip_file = clips_dir / f"{request.clip_id}.js"
    
    if not clip_file.exists():
        return {
            "error": f"Clip '{request.clip_id}' not found. Use save_new_clip to create.",
            "success": False
        }
    
    # Read existing content
    existing_content = clip_file.read_text(encoding='utf-8')
    existing_metadata = parse_clip_metadata(clip_file)
    existing_code = '\n'.join(existing_content.split('\n')[1:])
    
    # Use new or keep existing
    if request.metadata:
        try:
            new_metadata = ClipMetadata(**request.metadata)
        except Exception as e:
            return {"error": f"Invalid metadata: {str(e)}", "success": False}
    else:
        new_metadata = existing_metadata
    
    new_code = request.strudel_script if request.strudel_script is not None else existing_code
    
    # Write updated content
    metadata_json = json.dumps(new_metadata.model_dump())
    content = f"// {metadata_json}\n{new_code}"
    clip_file.write_text(content, encoding='utf-8')
    
    return {
        "success": True,
        "project_id": request.project_id,
        "clip_id": request.clip_id,
        "message": f"Clip '{request.clip_id}' updated successfully"
    }


# ============================================================================
# Song Tools
# ============================================================================

@mcp.tool()
def list_songs(request: ListSongsRequest) -> dict:
    """
    List songs with optional regex filter.
    
    Returns:
        List of songs with title and description
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "songs": []}
    
    songs_dir = project_path / "songs"
    if not songs_dir.exists():
        return {"songs": [], "total": 0}
    
    songs = []
    for song_file in songs_dir.glob("*.md"):
        song_id = song_file.stem
        title, description = parse_markdown_header(song_file)
        
        # Apply filter if provided
        if request.query:
            regex = re.compile(request.query, re.IGNORECASE)
            full_content = song_file.read_text(encoding='utf-8')
            if not regex.search(full_content):
                continue
        
        songs.append(SongInfo(
            song_id=song_id,
            title=title or song_id,
            description=description or ""
        ).model_dump())
    
    return {"songs": songs, "total": len(songs), "project_id": request.project_id}


@mcp.tool()
def get_songs(request: GetSongsRequest) -> dict:
    """
    Retrieve full song content.
    
    Returns:
        Full song data including title, description, and body
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "songs": []}
    
    songs_dir = project_path / "songs"
    songs = []
    
    for song_id in request.song_ids:
        song_file = songs_dir / f"{song_id}.md"
        if not song_file.exists():
            songs.append({
                "song_id": song_id,
                "error": "Song not found"
            })
            continue
        
        content = song_file.read_text(encoding='utf-8')
        title, description = parse_markdown_header(song_file)
        
        songs.append({
            "song_id": song_id,
            "title": title or song_id,
            "description": description or "",
            "body": content
        })
    
    return {"songs": songs, "project_id": request.project_id}


@mcp.tool()
def save_new_song(request: SaveNewSongRequest) -> dict:
    """
    Create a new song.
    
    Returns:
        Success confirmation
    """
    ensure_project_structure(request.project_id)
    songs_dir = get_project_path(request.project_id) / "songs"
    song_file = songs_dir / f"{request.song_id}.md"
    
    if song_file.exists():
        return {
            "error": f"Song '{request.song_id}' already exists. Use update_song to modify.",
            "success": False
        }
    
    # Create markdown content
    content = f"# {request.title}\n\n{request.description}\n\n{request.body}"
    song_file.write_text(content, encoding='utf-8')
    
    return {
        "success": True,
        "project_id": request.project_id,
        "song_id": request.song_id,
        "message": f"Song '{request.song_id}' created successfully"
    }


@mcp.tool()
def update_song(request: UpdateSongRequest) -> dict:
    """
    Update existing song.
    
    Returns:
        Success confirmation
    """
    songs_dir = get_project_path(request.project_id) / "songs"
    song_file = songs_dir / f"{request.song_id}.md"
    
    if not song_file.exists():
        return {
            "error": f"Song '{request.song_id}' not found. Use save_new_song to create.",
            "success": False
        }
    
    # Read existing content
    existing_content = song_file.read_text(encoding='utf-8')
    existing_title, existing_description = parse_markdown_header(song_file)
    
    # Extract existing body (skip title and description lines)
    lines = existing_content.split('\n')
    existing_body_start = 0
    found_title = False
    found_description = False
    for i, line in enumerate(lines):
        if line.startswith('# ') and not found_title:
            found_title = True
            continue
        if found_title and not found_description and line.strip():
            found_description = True
            existing_body_start = i + 1
            break
    existing_body = '\n'.join(lines[existing_body_start:])
    
    # Use new or keep existing
    new_title = request.title if request.title is not None else existing_title
    new_description = request.description if request.description is not None else existing_description
    new_body = request.body if request.body is not None else existing_body
    
    # Write updated content
    content = f"# {new_title}\n\n{new_description}\n\n{new_body}"
    song_file.write_text(content, encoding='utf-8')
    
    return {
        "success": True,
        "project_id": request.project_id,
        "song_id": request.song_id,
        "message": f"Song '{request.song_id}' updated successfully"
    }


# ============================================================================
# Playlist Tools
# ============================================================================

@mcp.tool()
def list_playlists(request: ListPlaylistsRequest) -> dict:
    """
    List playlists with optional regex filters.
    
    Returns:
        List of playlists with titles
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "playlists": []}
    
    playlists_dir = project_path / "playlists"
    if not playlists_dir.exists():
        return {"playlists": [], "total": 0}
    
    playlists = []
    for playlist_file in playlists_dir.glob("*.md"):
        playlist_id = playlist_file.stem
        title, _ = parse_markdown_header(playlist_file)
        
        # Apply filters if provided
        if request.title_query:
            regex = re.compile(request.title_query, re.IGNORECASE)
            if not regex.search(title or playlist_id):
                continue
        
        if request.query:
            regex = re.compile(request.query, re.IGNORECASE)
            full_content = playlist_file.read_text(encoding='utf-8')
            if not regex.search(full_content):
                continue
        
        playlists.append(PlaylistInfo(
            playlist_id=playlist_id,
            title=title or playlist_id
        ).model_dump())
    
    return {"playlists": playlists, "total": len(playlists), "project_id": request.project_id}


@mcp.tool()
def get_playlists(request: GetPlaylistsRequest) -> dict:
    """
    Retrieve full playlist content.
    
    Returns:
        Full playlist data
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "playlists": []}
    
    playlists_dir = project_path / "playlists"
    playlists = []
    
    for playlist_id in request.playlist_ids:
        playlist_file = playlists_dir / f"{playlist_id}.md"
        if not playlist_file.exists():
            playlists.append({
                "playlist_id": playlist_id,
                "error": "Playlist not found"
            })
            continue
        
        content = playlist_file.read_text(encoding='utf-8')
        title, _ = parse_markdown_header(playlist_file)
        
        playlists.append({
            "playlist_id": playlist_id,
            "title": title or playlist_id,
            "body": content
        })
    
    return {"playlists": playlists, "project_id": request.project_id}


@mcp.tool()
def save_new_playlist(request: SaveNewPlaylistRequest) -> dict:
    """
    Create a new playlist.
    
    Returns:
        Success confirmation
    """
    ensure_project_structure(request.project_id)
    playlists_dir = get_project_path(request.project_id) / "playlists"
    playlist_file = playlists_dir / f"{request.playlist_id}.md"
    
    if playlist_file.exists():
        return {
            "error": f"Playlist '{request.playlist_id}' already exists. Use update_playlist to modify.",
            "success": False
        }
    
    # Create markdown content
    content = f"# {request.title}\n\n{request.body}"
    playlist_file.write_text(content, encoding='utf-8')
    
    return {
        "success": True,
        "project_id": request.project_id,
        "playlist_id": request.playlist_id,
        "message": f"Playlist '{request.playlist_id}' created successfully"
    }


@mcp.tool()
def update_playlist(request: UpdatePlaylistRequest) -> dict:
    """
    Update existing playlist.
    
    Returns:
        Success confirmation
    """
    playlists_dir = get_project_path(request.project_id) / "playlists"
    playlist_file = playlists_dir / f"{request.playlist_id}.md"
    
    if not playlist_file.exists():
        return {
            "error": f"Playlist '{request.playlist_id}' not found. Use save_new_playlist to create.",
            "success": False
        }
    
    # Read existing content
    existing_content = playlist_file.read_text(encoding='utf-8')
    existing_title, _ = parse_markdown_header(playlist_file)
    
    # Extract existing body (skip title line)
    lines = existing_content.split('\n')
    existing_body_start = 0
    for i, line in enumerate(lines):
        if line.startswith('# '):
            existing_body_start = i + 1
            break
    # Skip empty lines after title
    while existing_body_start < len(lines) and not lines[existing_body_start].strip():
        existing_body_start += 1
    existing_body = '\n'.join(lines[existing_body_start:])
    
    # Use new or keep existing
    new_title = request.title if request.title is not None else existing_title
    new_body = request.body if request.body is not None else existing_body
    
    # Write updated content
    content = f"# {new_title}\n\n{new_body}"
    playlist_file.write_text(content, encoding='utf-8')
    
    return {
        "success": True,
        "project_id": request.project_id,
        "playlist_id": request.playlist_id,
        "message": f"Playlist '{request.playlist_id}' updated successfully"
    }

# ============================================================================
# Known Packs Tools
# ============================================================================

class SearchPacksRequest(BaseModel):
    """Request to search known sample packs"""
    query: Optional[str] = Field(
        default=None,
        description="Optional regex pattern to search for packs by name, tags, description, or content. Examples: 'drum', 'analog', 'break', 'garden|dirt'"
    )

class GetPackDetailsRequest(BaseModel):
    """Request to get details about specific packs"""
    pack_names: list[str] = Field(
        description="List of pack names to retrieve details for. Use names from search results or known packs like 'dirt_samples', 'garden', 'clean_breaks'"
    )


@mcp.tool()
def search_packs(request: SearchPacksRequest) -> dict:
    """
    Search known sample packs database to find packs you can use to enhance clips.
    
    Use this when you need to:
    - Find sample packs for specific sounds (drums, bass, synths, fx)
    - Discover packs by genre (techno, house, hip-hop, breaks)
    - Look up packs by character (analog, vintage, lo-fi)
    - Find licensed/clean packs for production use
    
    Returns:
        Search results with pack information, GitHub URLs, and tags
    """
    known_packs_dir = KNOWN_PACKS_DIR
    
    if not known_packs_dir.exists():
        return {"error": "Known packs directory not found", "results": []}
    
    results = []
    
    for md_file in known_packs_dir.glob("*.md"):
        # Skip README
        if md_file.name == "README.md":
            continue
            
        content = md_file.read_text(encoding='utf-8')
        
        # Apply filter if provided
        if request.query:
            regex = re.compile(request.query, re.IGNORECASE)
            if not regex.search(content):
                continue
        
        # Parse title
        title = None
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        results.append({
            "file": md_file.name,
            "title": title or md_file.stem,
            "preview": content[:500] + "..." if len(content) > 500 else content
        })
    
    return {
        "results": results,
        "total": len(results),
        "query": request.query,
        "message": f"Found {len(results)} pack(s). Use get_pack_details to see full documentation."
    }


@mcp.tool()
def get_pack_details(request: GetPackDetailsRequest) -> dict:
    """
    Get detailed documentation for specific sample packs.
    
    Use this after searching to get full information about:
    - How to load the pack in Strudel
    - Available sound categories
    - Usage examples
    - License information
    - Tags and characteristics
    
    Returns:
        Full documentation for requested packs
    """
    known_packs_dir = KNOWN_PACKS_DIR
    
    if not known_packs_dir.exists():
        return {"error": "Known packs directory not found", "packs": []}
    
    packs = []
    
    for pack_name in request.pack_names:
        # Try to find matching file
        found = False
        
        for md_file in known_packs_dir.glob("*.md"):
            # Match by filename (with or without number prefix)
            stem = md_file.stem.lower()
            if pack_name.lower() in stem or stem.endswith(pack_name.lower()):
                content = md_file.read_text(encoding='utf-8')
                
                # Parse title
                title = None
                for line in content.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                packs.append({
                    "pack_name": pack_name,
                    "file": md_file.name,
                    "title": title or md_file.stem,
                    "content": content
                })
                found = True
                break
        
        if not found:
            packs.append({
                "pack_name": pack_name,
                "error": f"Pack '{pack_name}' not found. Try search_packs to find available packs."
            })
    
    return {"packs": packs, "total": len(packs)}

# ============================================================================
# Surface Template Tools
# ============================================================================

@mcp.tool()
def create_new_template(request: CreateTemplateRequest) -> dict:
    """
    Create a new surface template for parameterized code generation.
    
    Templates provide a control surface for the agent - pre-structured Strudel
    patterns with validated variables. Use templates to ensure consistent,
    validated code generation.
    
    Returns:
        Success confirmation with template details
    """
    ensure_project_structure(request.project_id)
    surfaces_dir = get_project_path(request.project_id) / "surfaces"
    surfaces_dir.mkdir(exist_ok=True)
    
    template_file = surfaces_dir / f"{request.template_id}.yaml"
    
    if template_file.exists():
        return {
            "error": f"Template '{request.template_id}' already exists. Use update_template to modify.",
            "success": False
        }
    
    # Build YAML structure
    template_yaml = {
        'metadata': request.metadata,
        'template': request.template_code,
        'schema': request.input_schema
    }
    
    if request.includes:
        template_yaml['includes'] = request.includes
    
    # Write YAML file
    try:
        with open(template_file, 'w', encoding='utf-8') as f:
            yaml.dump(template_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception as e:
        return {
            "error": f"Failed to write template: {str(e)}",
            "success": False
        }
    
    return {
        "success": True,
        "project_id": request.project_id,
        "template_id": request.template_id,
        "message": f"Template '{request.template_id}' created successfully",
        "file_path": str(template_file)
    }


@mcp.tool()
def list_templates(request: ListTemplatesRequest) -> dict:
    """
    List available surface templates with schema preview.
    
    Use this to discover what templates are available for code generation.
    Templates can be filtered by category, tags, or searched with regex.
    
    Returns:
        List of templates with metadata and schema preview
    """
    project_path = get_project_path(request.project_id)
    if not project_path.exists():
        return {"error": f"Project '{request.project_id}' not found", "templates": []}
    
    surfaces_dir = project_path / "surfaces"
    if not surfaces_dir.exists():
        return {"templates": [], "total": 0}
    
    templates = []
    
    for template_file in surfaces_dir.glob("*.yaml"):
        template_id = template_file.stem
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
        except Exception:
            continue
        
        metadata = template_data.get('metadata', {})
        schema = template_data.get('schema', {})
        includes = template_data.get('includes', {})
        
        # Apply category filter
        if request.category and metadata.get('category') != request.category:
            continue
        
        # Apply tags filter (any match)
        if request.tags:
            template_tags = metadata.get('tags', [])
            if not any(tag in template_tags for tag in request.tags):
                continue
        
        # Apply query filter
        if request.query:
            regex = re.compile(request.query, re.IGNORECASE)
            metadata_str = json.dumps(metadata)
            if not regex.search(metadata_str):
                continue
        
        # Build schema preview (just names and types)
        schema_preview = {
            name: {
                'type': def_data.get('type'),
                'default': def_data.get('default'),
                'description': def_data.get('description', '')
            }
            for name, def_data in schema.items()
        }
        
        templates.append({
            'template_id': template_id,
            'metadata': metadata,
            'schema_preview': schema_preview,
            'has_includes': bool(includes)
        })
    
    # Sort by category, then name
    templates.sort(key=lambda t: (t['metadata'].get('category', ''), t['metadata'].get('name', '')))
    
    return {
        "templates": templates,
        "total": len(templates),
        "project_id": request.project_id
    }


@mcp.tool()
def get_template_schema(request: GetTemplateSchemaRequest) -> dict:
    """
    Get full schema and details for a specific template.
    
    Use this to understand what variables a template needs and what
    constraints apply to each variable before generating code.
    
    Returns:
        Full template metadata, schema, and code
    """
    template_data = load_template_yaml(request.project_id, request.template_id)
    
    if not template_data:
        return {
            "error": f"Template '{request.template_id}' not found",
            "success": False
        }
    
    return {
        "success": True,
        "template_id": request.template_id,
        "metadata": template_data.get('metadata', {}),
        "schema": template_data.get('schema', {}),
        "template_code": template_data.get('template', ''),
        "includes": template_data.get('includes', {})
    }


@mcp.tool()
def generate_from_template(request: GenerateFromTemplateRequest) -> dict:
    """
    Generate Strudel code from a template by filling in variables.
    
    This is the primary tool for using templates. Provide variable values
    and get back ready-to-use Strudel code. Variables are validated against
    the template schema unless validate=False.
    
    Returns:
        Generated Strudel code ready to paste into strudel.cc
    """
    result = generate_code_from_template(
        request.project_id,
        request.template_id,
        request.variables,
        request.do_validation
    )
    
    if result['errors']:
        return {
            "success": False,
            "errors": result['errors'],
            "variables_used": result['variables_used']
        }
    
    return {
        "success": True,
        "code": result['code'],
        "variables_used": result['variables_used'],
        "template_id": request.template_id,
        "project_id": request.project_id
    }


@mcp.tool()
def update_template(request: UpdateTemplateRequest) -> dict:
    """
    Update an existing surface template.
    
    Allows updating template code, schema, metadata, or includes.
    Only provided fields are updated; others remain unchanged.
    
    Returns:
        Success confirmation
    """
    surfaces_dir = get_project_path(request.project_id) / "surfaces"
    template_file = surfaces_dir / f"{request.template_id}.yaml"
    
    if not template_file.exists():
        return {
            "error": f"Template '{request.template_id}' not found. Use create_new_template to create.",
            "success": False
        }
    
    # Load existing template
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f)
    except Exception as e:
        return {
            "error": f"Failed to read template: {str(e)}",
            "success": False
        }
    
    # Update fields
    if request.template_code is not None:
        template_data['template'] = request.template_code
    
    if request.input_schema is not None:
        template_data['schema'] = request.input_schema
    
    if request.metadata is not None:
        template_data['metadata'] = request.metadata
    
    if request.includes is not None:
        template_data['includes'] = request.includes
    
    # Write updated template
    try:
        with open(template_file, 'w', encoding='utf-8') as f:
            yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception as e:
        return {
            "error": f"Failed to write template: {str(e)}",
            "success": False
        }
    
    return {
        "success": True,
        "project_id": request.project_id,
        "template_id": request.template_id,
        "message": f"Template '{request.template_id}' updated successfully"
    }


if __name__ == "__main__":
    mcp.run()
