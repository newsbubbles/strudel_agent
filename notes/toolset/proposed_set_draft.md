# Strudel MCP Toolset - Proposed Tool Set (Draft)

**Date**: 2025-12-22  
**Status**: Working draft for discussion  
**Purpose**: Define the shape of the toolset before implementation

---

## Overview

This toolset enables an AI agent to collaborate with a user on Strudel live coding in near-realtime. The agent interprets natural language instructions about music, understands the current song context, and makes intelligent edits via structured patching.

**Core Philosophy**: 
- Toolset provides **data-rich access** to projects, clips, and knowledge
- Agent provides **creative intelligence** for composition
- User provides **musical intent** in natural language

---

## Tool Categories

1. **Canvas Tools** - Working with the current song script
2. **Project Tools** - Managing multiple projects
3. **Clip Tools** - Reusable pattern library
4. **Knowledge Tools** - Sample packs, vocab, functions
5. **Analysis Tools** - Understanding code structure and semantics

---

## 1. Canvas Tools

### Why These Tools?

The agent needs to:
- See what the user is currently working on
- Make surgical edits without breaking existing code
- Validate changes before applying them

These tools enable the core workflow: **get context → make changes → validate → apply**.

---

### `get_song`

**Purpose**: Retrieve the current song script and metadata for a project.

**Why**: Agent needs full context to understand what exists before making changes.

**Functionality**:
- Fetch complete script content
- Include metadata: tempo, key, tags, genre, sample packs used
- Include structural info: line count, last modified
- Return in structured format for easy parsing

**Input**:
```python
project_name: str  # Name of project to fetch
```

**Output**:
```python
{
  "project_name": str,
  "script": str,  # Full script content
  "metadata": {
    "tempo": int | None,
    "key": str | None,
    "tags": list[str],
    "genre": str | None,
    "packs_used": list[str],
    "created": datetime,
    "modified": datetime,
    "line_count": int
  },
  "data": dict  # JSONB metadata field
}
```

**Error Cases**:
- Project not found → descriptive error with suggestion to list projects
- Database error → technical error with context

---

### `update_song`

**Purpose**: Apply a patch to the song script based on structured instructions.

**Why**: Agent needs to make precise edits to specific parts of the code without rewriting the entire script.

**Functionality**:
- Accept structured patch instructions (line-based, pattern-based, section-based)
- Generate actual diff/patch
- Optionally validate before applying
- Apply patch to script
- Save updated script
- Return confirmation with diff preview

**Input**:
```python
project_name: str
patch_instructions: PatchInstruction  # Structured patch (see below)
auto_validate: bool = True  # Validate before applying
```

**PatchInstruction Types**:

```python
# Line-based
{
  "action": "replace_line" | "insert_after_line" | "insert_before_line" | "delete_line",
  "line_number": int,
  "new_content": str  # For replace/insert actions
}

# Pattern-based
{
  "action": "replace_pattern" | "insert_after_pattern" | "insert_before_pattern",
  "pattern": str,  # Regex pattern to find
  "new_content": str,
  "occurrence": "first" | "last" | "all" = "first"
}

# Append/Prepend
{
  "action": "append" | "prepend",
  "new_content": str
}

# Section-based (requires structure analysis first)
{
  "action": "insert_after_section" | "replace_section",
  "section": "setup" | "voices" | str,  # Section name from analysis
  "new_content": str
}
```

**Output**:
```python
{
  "success": bool,
  "validation": {
    "valid": bool,
    "errors": list[ValidationError],
    "warnings": list[ValidationWarning]
  },
  "diff": str,  # Unified diff format
  "preview": str,  # Human-readable description of change
  "lines_changed": int
}
```

**Error Cases**:
- Project not found
- Pattern not found (for pattern-based patches)
- Line number out of range (for line-based patches)
- Validation failed (if auto_validate=True)
- Invalid patch instruction format

---

### `validate_script`

**Purpose**: Validate Strudel script syntax and semantics without applying changes.

**Why**: Agent can pre-check changes before applying, avoiding broken code.

**Functionality**:
- Parse JavaScript/Strudel syntax
- Check for syntax errors (unmatched parens, invalid tokens, etc.)
- Check for semantic errors (undefined packs, invalid parameters, etc.)
- Return detailed errors with line/column numbers
- Return warnings for questionable but valid code

**Input**:
```python
script_content: str  # Script to validate
project_name: str | None = None  # Optional, for context (e.g., checking pack availability)
```

**Output**:
```python
{
  "valid": bool,
  "errors": list[{
    "line": int,
    "column": int,
    "message": str,
    "suggestion": str | None,
    "code_context": str  # Surrounding lines for context
  }],
  "warnings": list[{
    "line": int,
    "message": str,
    "suggestion": str | None
  }]
}
```

**Validation Checks**:
- Syntax: Unmatched brackets, invalid tokens, malformed patterns
- Semantics: Undefined sample packs, invalid function calls, out-of-range params
- Musical: Key mismatches (warning), tempo issues (warning)
- Performance: Too many voices (warning), excessive nesting (warning)

**Error Cases**:
- Empty script (warning, not error)
- Script too large (warning about performance)

---

## 2. Project Tools

### Why These Tools?

Users work on multiple songs/projects. Agent needs to:
- Switch between projects
- Browse available projects
- Create new projects
- Understand project metadata for context

---

### `list_projects`

**Purpose**: List all projects with optional filtering and searching.

**Why**: Agent needs to browse projects, find relevant ones, help user navigate.

**Functionality**:
- List all projects in database
- Filter by tags, genre, date range
- Search by name/description (regex)
- Sort by various fields
- Return metadata without full scripts (performance)

**Input**:
```python
filters: ProjectFilters | None = None
sort_by: str = "modified"  # "modified" | "created" | "name" | "tempo"
sort_order: str = "desc"  # "asc" | "desc"
limit: int = 50
```

**ProjectFilters**:
```python
{
  "tags": list[str] | None,  # Match any of these tags
  "genre": str | None,
  "name_pattern": str | None,  # Regex
  "description_pattern": str | None,  # Regex
  "created_after": datetime | None,
  "created_before": datetime | None,
  "modified_after": datetime | None,
  "modified_before": datetime | None,
  "tempo_min": int | None,
  "tempo_max": int | None
}
```

**Output**:
```python
{
  "projects": list[{
    "name": str,
    "description": str | None,
    "tags": list[str],
    "genre": str | None,
    "tempo": int | None,
    "key": str | None,
    "created": datetime,
    "modified": datetime,
    "line_count": int,
    "data": dict  # JSONB metadata
  }],
  "total_count": int,
  "filtered_count": int
}
```

---

### `create_project`

**Purpose**: Create a new project with optional metadata and initial script.

**Why**: Agent can help user start new songs with appropriate templates.

**Functionality**:
- Create new project entry in database
- Initialize with blank script or template
- Set metadata (tempo, key, tags, etc.)
- Return confirmation

**Input**:
```python
name: str  # Unique project name
description: str | None = None
metadata: ProjectMetadata | None = None
initial_script: str | None = None  # Blank if None
```

**ProjectMetadata**:
```python
{
  "tempo": int | None,
  "key": str | None,
  "tags": list[str] = [],
  "genre": str | None,
  "data": dict = {}  # JSONB metadata
}
```

**Output**:
```python
{
  "success": bool,
  "project_name": str,
  "message": str
}
```

**Error Cases**:
- Project name already exists
- Invalid project name (special characters, too long, etc.)

---

### `get_project_metadata`

**Purpose**: Get project metadata without fetching full script.

**Why**: Fast lookup for browsing, checking context without loading large scripts.

**Functionality**:
- Fetch metadata only (no script content)
- Return structured metadata

**Input**:
```python
project_name: str
```

**Output**:
```python
{
  "name": str,
  "description": str | None,
  "tags": list[str],
  "genre": str | None,
  "tempo": int | None,
  "key": str | None,
  "created": datetime,
  "modified": datetime,
  "line_count": int,
  "data": dict
}
```

---

### `update_project_metadata`

**Purpose**: Update project metadata without touching script.

**Why**: Agent can update tags, tempo, key as it learns about the song.

**Functionality**:
- Update metadata fields
- Merge or replace data JSONB field
- Return confirmation

**Input**:
```python
project_name: str
metadata_updates: ProjectMetadata
merge_data: bool = True  # If True, merge; if False, replace
```

**Output**:
```python
{
  "success": bool,
  "message": str
}
```

---

### `delete_project`

**Purpose**: Delete a project (with confirmation).

**Why**: Cleanup, remove old projects.

**Functionality**:
- Delete project from database
- Return confirmation

**Input**:
```python
project_name: str
confirm: bool = False  # Safety flag
```

**Output**:
```python
{
  "success": bool,
  "message": str
}
```

---

## 3. Clip Tools

### Why These Tools?

Clips are the agent's **vocabulary** of musical patterns. Agent needs to:
- Search for relevant patterns based on user intent
- Retrieve clip code to insert into songs
- Add new clips as user creates interesting patterns
- Understand what clips exist and their relationships

---

### `search_clips`

**Purpose**: Search clip library using regex queries on tags, code, metadata.

**Why**: Agent needs to find relevant patterns based on user's musical intent (genre, feeling, technique, etc.).

**Functionality**:
- Query clips by regex on any field
- Search tags (genre, feeling, technique, instrument, complexity, element)
- Search code content
- Search metadata (tempo range, key, etc.)
- Return ranked results (by relevance if semantic search enabled)
- Include clip metadata and code

**Input**:
```python
query: ClipQuery
limit: int = 20
```

**ClipQuery**:
```python
{
  # Regex queries on tags
  "genre": str | None,  # Regex pattern
  "feeling": str | None,
  "technique": str | None,
  "instrument": str | None,
  "complexity": str | None,  # "beginner" | "intermediate" | "advanced"
  "element": str | None,  # "rhythm" | "melody" | "harmony" | "texture" | "fx"
  
  # Regex on other fields
  "name_pattern": str | None,
  "description_pattern": str | None,
  "code_pattern": str | None,
  
  # Metadata filters
  "tempo_min": int | None,
  "tempo_max": int | None,
  "key": str | None,
  "requires_packs": list[str] | None  # Must have these packs
}
```

**Output**:
```python
{
  "clips": list[{
    "id": str,
    "name": str,
    "description": str,
    "code": str,
    "tags": {
      "genre": list[str],
      "feeling": list[str],
      "technique": list[str],
      "instrument": list[str],
      "complexity": str,
      "element": str
    },
    "metadata": {
      "tempo_range": [int, int] | None,
      "key": str | None,
      "requires_packs": list[str],
      "created": datetime,
      "author": str | None
    },
    "data": dict,  # JSONB with rich metadata
    "relevance_score": float | None  # If semantic search used
  }],
  "total_count": int
}
```

---

### `get_clip`

**Purpose**: Get full clip details by ID.

**Why**: After search, agent may want full details of specific clip.

**Functionality**:
- Fetch clip by ID
- Return complete clip data

**Input**:
```python
clip_id: str
```

**Output**:
```python
{
  "id": str,
  "name": str,
  "description": str,
  "code": str,
  "tags": {...},
  "metadata": {...},
  "data": dict,
  "embedding": list[float] | None  # 768D embedding if available
}
```

---

### `save_clip`

**Purpose**: Save a new clip to the library.

**Why**: Agent can help user save interesting patterns they create for reuse.

**Functionality**:
- Create new clip entry
- Generate embedding for code
- Auto-suggest tags based on code analysis (optional)
- Return confirmation with clip ID

**Input**:
```python
clip_data: ClipData
auto_generate_tags: bool = False  # Use code analysis to suggest tags
```

**ClipData**:
```python
{
  "name": str,
  "description": str,
  "code": str,
  "tags": ClipTags,
  "metadata": ClipMetadata | None = None,
  "data": dict = {}  # JSONB metadata
}
```

**Output**:
```python
{
  "success": bool,
  "clip_id": str,
  "suggested_tags": ClipTags | None,  # If auto_generate_tags=True
  "message": str
}
```

---

### `update_clip`

**Purpose**: Update an existing clip.

**Why**: Refine clips, add metadata, fix code.

**Functionality**:
- Update clip fields
- Regenerate embedding if code changed
- Merge or replace data JSONB

**Input**:
```python
clip_id: str
updates: ClipData  # Partial updates
merge_data: bool = True
```

**Output**:
```python
{
  "success": bool,
  "message": str
}
```

---

### `delete_clip`

**Purpose**: Remove clip from library.

**Why**: Cleanup, remove outdated patterns.

**Input**:
```python
clip_id: str
confirm: bool = False
```

**Output**:
```python
{
  "success": bool,
  "message": str
}
```

---

## 4. Knowledge Tools

### Why These Tools?

Agent needs access to **reference knowledge**:
- Sample packs available and how to use them
- Strudel vocabulary (functions, patterns, techniques)
- Bidirectional mapping between concepts and code

---

### `query_packs`

**Purpose**: Search sample packs database (from our research!).

**Why**: Agent can recommend packs based on user's genre/sound preferences.

**Functionality**:
- Search packs by tags, name, description
- Filter by type (drums, synths, etc.)
- Return pack info with loading syntax

**Input**:
```python
query: PackQuery
limit: int = 20
```

**PackQuery**:
```python
{
  "name_pattern": str | None,  # Regex
  "tags": str | None,  # Regex on tags
  "type": str | None,  # "drums" | "synths" | "bass" | etc.
  "character": str | None,  # "analog" | "digital" | "lo-fi" | etc.
  "licensed": bool | None  # Only show packs with clear licenses
}
```

**Output**:
```python
{
  "packs": list[{
    "name": str,
    "github": str,  # "github:user/repo"
    "description": str,
    "tags": list[str],
    "categories": list[str],  # Sample categories available
    "license": str | None,
    "loading_syntax": str,  # "samples('github:user/repo')"
    "data": dict  # JSONB metadata
  }],
  "total_count": int
}
```

---

### `query_vocab`

**Purpose**: Map musical concepts to Strudel code (forward lookup).

**Why**: User says "add swing" → agent needs to know what code implements swing.

**Functionality**:
- Search vocab by concept (regex)
- Return Strudel code, description, examples
- Support multiple matches (e.g., "swing" could be `.late()` or `.shuffle()`)

**Input**:
```python
concept: str  # Regex pattern for concept search
limit: int = 10
```

**Output**:
```python
{
  "matches": list[{
    "concept": str,
    "strudel_code": str,
    "description": str,
    "example": str,
    "category": str,  # "rhythm" | "melody" | "effects" | etc.
    "related_concepts": list[str]
  }],
  "total_count": int
}
```

---

### `identify_pattern`

**Purpose**: Identify what a code snippet does (reverse lookup using embeddings).

**Why**: Agent sees code and needs to understand its musical meaning.

**Functionality**:
- Take code snippet
- Generate embedding
- Use RAG to find similar clips/vocab entries
- Return concepts, techniques, tags

**Input**:
```python
code_snippet: str
top_k: int = 5  # Return top K similar patterns
```

**Output**:
```python
{
  "identified_patterns": list[{
    "concept": str,
    "description": str,
    "similarity_score": float,
    "tags": list[str],
    "source": "clip" | "vocab",  # Where match came from
    "source_id": str  # Clip ID or vocab entry ID
  }]
}
```

**Example**:
```python
Input: code_snippet = ".late('[0 .01]*4')"

Output: {
  "identified_patterns": [
    {
      "concept": "swing",
      "description": "Add swing feel by delaying alternating notes",
      "similarity_score": 0.95,
      "tags": ["rhythm", "groove", "timing"],
      "source": "vocab",
      "source_id": "vocab_swing_001"
    }
  ]
}
```

---

### `get_function_info`

**Purpose**: Get reference documentation for a Strudel function.

**Why**: Agent needs to understand function parameters, usage, examples.

**Functionality**:
- Fetch function documentation
- Include parameters, return type, examples
- Include related functions

**Input**:
```python
function_name: str
```

**Output**:
```python
{
  "name": str,
  "description": str,
  "parameters": list[{
    "name": str,
    "type": str,
    "description": str,
    "default": any | None,
    "required": bool
  }],
  "return_type": str,
  "examples": list[str],
  "related_functions": list[str],
  "category": str
}
```

---

## 5. Analysis Tools

### Why These Tools?

Agent needs to **understand** code structure to make intelligent edits:
- Parse script into logical sections
- Identify voices, patterns, effects
- Understand relationships between parts
- Enable targeted modifications ("add reverb to the snare")

---

### `analyze_song_structure`

**Purpose**: Parse song script into structural components.

**Why**: Agent can target specific parts ("make the intro more sparse", "add hi-hat to rhythm section").

**Functionality**:
- Parse script into sections (setup, voices, composition)
- Identify individual voices/patterns
- Detect effects chains
- Map line numbers to structural elements
- Return structured representation

**Input**:
```python
project_name: str | None = None  # If None, analyze provided script
script_content: str | None = None  # If project_name is None
```

**Output**:
```python
{
  "structure": {
    "setup": {
      "lines": [int, int],  # Start and end line numbers
      "content": list[str],
      "tempo": int | None,
      "packs": list[str]
    },
    "voices": list[{
      "id": str,  # Generated ID like "voice_1"
      "lines": [int, int],
      "type": str,  # "rhythm" | "melody" | "bass" | "texture" | "fx"
      "instrument": str | None,  # Detected instrument
      "pattern": str,  # The actual code
      "effects": list[str]  # Detected effects (.lpf, .room, etc.)
    }],
    "sections": list[{
      "name": str,  # "intro" | "main" | "breakdown" | etc.
      "lines": [int, int],
      "voices": list[str],  # Voice IDs in this section
      "description": str | None
    }]
  },
  "summary": {
    "total_lines": int,
    "voice_count": int,
    "section_count": int,
    "complexity": str  # "simple" | "moderate" | "complex"
  }
}
```

**Use Cases**:
- Agent: "Add hi-hat to rhythm section" → finds voices with type="rhythm", inserts after
- Agent: "Make intro more sparse" → finds section="intro", modifies voices
- Agent: "Add reverb to the snare" → finds voice with instrument="snare", adds `.room()`

---

### `find_similar_clips`

**Purpose**: Find clips similar to a given code snippet (semantic search).

**Why**: Agent can suggest variations: "Here are other patterns similar to your current bassline".

**Functionality**:
- Take code snippet from song
- Generate embedding
- Search clip library by vector similarity
- Return ranked similar clips

**Input**:
```python
code_snippet: str
top_k: int = 10
filters: ClipQuery | None = None  # Optional filters (genre, etc.)
```

**Output**:
```python
{
  "similar_clips": list[{
    "clip_id": str,
    "name": str,
    "code": str,
    "similarity_score": float,
    "tags": {...},
    "description": str
  }]
}
```

**Use Cases**:
- User: "Give me variations of this bassline"
- Agent: Uses `find_similar_clips()` with current bassline code
- Agent: "Here are 5 similar basslines with different feels"

---

## Tool Priority Summary

### High Priority (Core Functionality)

**Must have for MVP**:

1. `get_song` - See current state
2. `update_song` - Make changes
3. `validate_script` - Check before applying
4. `search_clips` - Find patterns
5. `list_projects` - Browse projects
6. `query_packs` - Find sample packs
7. `query_vocab` - Concept → code lookup

### Medium Priority (Enhanced Workflow)

**Nice to have for v1**:

8. `create_project` - Start new songs
9. `get_project_metadata` - Fast metadata lookup
10. `update_project_metadata` - Update tags/tempo/etc.
11. `get_clip` - Clip details
12. `save_clip` - Add to library
13. `analyze_song_structure` - Structural understanding
14. `identify_pattern` - Code → concept (reverse lookup)

### Low Priority (v2 Features)

**Future enhancements**:

15. `delete_project` - Cleanup
16. `delete_clip` - Cleanup
17. `update_clip` - Refine clips
18. `get_function_info` - Reference docs
19. `find_similar_clips` - Semantic clip search

---

## Data Flow Example

### Scenario: User says "Make it darker and add some swing"

```
1. Agent interprets:
   - "darker" = search for clips with feeling:dark
   - "swing" = query vocab for swing techniques
   - "it" = current song (from conversation context)

2. Agent calls tools:
   get_song("current_project")
   → Returns full script + metadata
   
   search_clips({"feeling": "dark", "element": "melody|bass"})
   → Returns dark bassline clips
   
   query_vocab("swing")
   → Returns: {"concept": "swing", "code": ".late('[0 .01]*4')"}
   
   analyze_song_structure("current_project")
   → Returns structure with voice IDs

3. Agent composes changes:
   - Find hi-hat voice from structure
   - Add .late('[0 .01]*4') to hi-hat for swing
   - Insert dark bassline clip after kick

4. Agent generates patch:
   patch_instructions = {
     "action": "replace_pattern",
     "pattern": "sound\\(\"hh\\*8\"\\)",
     "new_content": "sound(\"hh*8\").late('[0 .01]*4')"
   }
   
   patch_instructions_2 = {
     "action": "insert_after_pattern",
     "pattern": "sound\\(\"bd\\*4\"\\)",
     "new_content": "\n$: note(\"c2 eb2 f2 g2\").s(\"bass1\").lpf(600)\n"
   }

5. Agent validates:
   validate_script(patched_script)
   → {"valid": true, "errors": []}

6. Agent applies:
   update_song("current_project", patch_instructions)
   update_song("current_project", patch_instructions_2)
   → Both return success

7. Agent responds:
   "Added swing to hi-hats with .late() timing offset. 
    Inserted dark Am bassline after the kick."
```

---

## Technical Implementation Notes

### Database Schema (High-Level)

**Projects Table**:
```sql
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR UNIQUE NOT NULL,
  description TEXT,
  script TEXT NOT NULL,
  tempo INT,
  key VARCHAR,
  tags TEXT[],
  genre VARCHAR,
  created TIMESTAMP DEFAULT NOW(),
  modified TIMESTAMP DEFAULT NOW(),
  data JSONB DEFAULT '{}'  -- Extensible metadata
);
```

**Clips Table**:
```sql
CREATE TABLE clips (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  description TEXT,
  code TEXT NOT NULL,
  tags JSONB NOT NULL,  -- {genre: [], feeling: [], ...}
  metadata JSONB,  -- {tempo_range: [120, 135], ...}
  embedding VECTOR(768),  -- pgvector for semantic search
  created TIMESTAMP DEFAULT NOW(),
  author VARCHAR,
  data JSONB DEFAULT '{}'  -- Extensible metadata
);

CREATE INDEX ON clips USING ivfflat (embedding vector_cosine_ops);  -- Vector index
```

**Packs Table** (from research):
```sql
CREATE TABLE packs (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  github VARCHAR NOT NULL,
  description TEXT,
  tags TEXT[],
  categories TEXT[],  -- Sample categories
  license VARCHAR,
  data JSONB DEFAULT '{}'
);
```

**Vocab Table**:
```sql
CREATE TABLE vocab (
  id VARCHAR PRIMARY KEY,
  concept VARCHAR NOT NULL,
  strudel_code TEXT NOT NULL,
  description TEXT,
  example TEXT,
  category VARCHAR,
  embedding VECTOR(768),  -- For reverse lookup
  data JSONB DEFAULT '{}'
);

CREATE INDEX ON vocab USING ivfflat (embedding vector_cosine_ops);
```

### Client Architecture

```
src/
  client.py
    - Database connection (SQLModel + psycopg2)
    - CRUD operations for projects, clips, packs, vocab
    - Embedding generation (local model)
    - Vector search (pgvector)
    - Validation logic
    - Patching logic
    - Structure analysis
    
  models.py
    - SQLModel definitions for tables
    - Pydantic models for tool requests/responses
    
  embeddings.py
    - Embedding model wrapper
    - Generate embeddings for code/text
    
  validation.py
    - Script validation logic
    - Syntax parsing
    - Semantic checks
    
  patching.py
    - Patch generation and application
    - Diff generation
    
  analysis.py
    - Structure analysis
    - Voice detection
    - Section identification

mcp_server.py
  - FastMCP server
  - Tool definitions (wrap client methods)
  - Error handling
  - Response formatting
```

---

## Next Steps

1. ✅ Define tool set (this document)
2. ⏭️ Research local embedding models (768D)
3. ⏭️ Define detailed database schemas (SQLModel)
4. ⏭️ Define Pydantic request/response models
5. ⏭️ Implement client.py (core logic)
6. ⏭️ Implement validation.py
7. ⏭️ Implement patching.py
8. ⏭️ Implement analysis.py
9. ⏭️ Implement embeddings.py
10. ⏭️ Wrap with mcp_server.py
11. ⏭️ Populate knowledge bases from research
12. ⏭️ Test with agent

---

**Status**: Proposed toolset draft complete. Ready for review and refinement before implementation.
