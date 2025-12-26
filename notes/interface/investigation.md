# Strudel Agent Interface - Investigation

**Date**: 2025-12-25  
**Topic**: Understanding the current system architecture to inform API/UI design  
**Related**: `notes/interface/seed.md`

---

## Investigation Goal

Understand how the current strudel_agent system works to design a web-based interface that wraps the existing MCP server functionality with a FastAPI backend and mobile-first UI.

---

## Current System Architecture

### Core Components

#### 1. MCP Server (`mcp_server.py`)

**Location**: `strudel_agent/mcp_server.py`  
**Purpose**: FastMCP-based tool server providing filesystem-based operations  
**Technology**: FastMCP (MCP protocol implementation)

**Tool Categories**:

1. **Knowledge Tools** (3 tools)
   - `search_knowledge()` - Regex search through knowledge base
   - `list_knowledgebase_docs()` - List available knowledge documents
   - `read_full_knowledge_docs()` - Read multiple knowledge docs at once

2. **Project Tools** (2 tools)
   - `list_projects()` - List all projects with metadata
   - `write_project_index()` - Create/update project index.md

3. **Clip Tools** (5 tools)
   - `list_clips()` - List clips with optional regex filter
   - `search_clips()` - Full-text regex search in clip code
   - `get_clips()` - Retrieve full clip content
   - `save_new_clip()` - Create new clip
   - `update_clip()` - Update existing clip

4. **Song Tools** (4 tools)
   - `list_songs()` - List songs with optional filter
   - `get_songs()` - Retrieve full song content
   - `save_new_song()` - Create new song
   - `update_song()` - Update existing song

5. **Playlist Tools** (4 tools)
   - `list_playlists()` - List playlists with optional filters
   - `get_playlists()` - Retrieve full playlist content
   - `save_new_playlist()` - Create new playlist
   - `update_playlist()` - Update existing playlist

6. **Known Packs Tools** (2 tools)
   - `search_packs()` - Search sample pack database
   - `get_pack_details()` - Get full pack documentation

7. **Surface Template Tools** (5 tools)
   - `create_new_template()` - Create parameterized code template
   - `list_templates()` - List available templates
   - `get_template_schema()` - Get template schema details
   - `generate_from_template()` - Generate code from template
   - `update_template()` - Update existing template

**Total**: 25 tools

---

### Data Model & File Structure

#### Filesystem Hierarchy

```
strudel_agent/
├── projects/
│   └── {project_id}/
│       ├── index.md              # Project metadata (title, description)
│       ├── clips/
│       │   └── {clip_id}.js      # Strudel code with JSON metadata in first line
│       ├── songs/
│       │   └── {song_id}.md      # Markdown with clip links and structure
│       ├── playlists/
│       │   └── {playlist_id}.md  # Markdown with song links
│       └── surfaces/
│           └── {template_id}.yaml # YAML template with schema
├── knowledge/            # Strudel reference docs (*.md)
└── known_packs/          # Sample pack documentation (*.md)
```

#### Data Hierarchy

**Clips < Songs < Projects**
- User focuses on **one project at a time**
- **Clips** are reusable Strudel code snippets (building blocks)
- **Songs** combine multiple clips with structure/transitions
- **Playlists** sequence multiple songs for performance

#### Clip File Format

```javascript
// {"name": "House Kick", "tags": ["drums", "kick", "house"], "tempo": 120, "description": "Classic four-on-floor house kick pattern"}
sound("bd*4").bank("RolandTR909").gain(0.8)
```

**Line 1**: JSON metadata in comment  
**Line 2+**: Strudel JavaScript code

#### Song File Format

```markdown
# Sunset House Groove

A warm, groovy house track with filtered bass and steady drums.

## Structure

### Intro (0-16 bars)
- Start with [kick.js](../clips/kick.js) - four-on-floor foundation
- Add [hats.js](../clips/hats.js) at bar 8 for groove
```

**Line 1**: H1 title  
**Line 2**: Description  
**Rest**: Markdown body with relative links to clips

---

### Agent Design

**Location**: `strudel_agent/agents/StrudelMusicAssistant.md`

**Agent Modes**:
1. **Creation Mode** - Deep focus, fast code output, live performance
2. **Exploration Mode** - Browsing projects, searching, discovering
3. **Learning Mode** - Understanding Strudel syntax, techniques

**Key Agent Behaviors**:
- **Always search knowledge first** before generating code
- Output JavaScript directly for clips
- Keep commentary in comments or markdown (not in responses)
- Act as "smart recombinator" - merge clips into new clips
- Understand musical intent before generating code

**Agent Workflow Pattern**:
1. Understand musical intent (genre, vibe, instruments, energy)
2. Search existing clips to avoid duplication
3. Check knowledge base for Strudel patterns
4. Generate/modify code
5. Save with good metadata

---

## Key Insights for Interface Design

### 1. Carousel = Loaded Clips in Memory

**Current User Clarification**:
> "Carousel loads current script into memory, so if you're using this for live, and you've got it playing, those are the current clips you have loaded in your song"

**Implication**: 
- Carousel is NOT just a code editor with tabs
- It represents the **currently loaded/playing clips**
- Each pane = one clip loaded in the Strudel player
- Swiping changes which clip's code is visible/editable
- Last pane = "add new clip"

**Live Performance Use Case**:
- User loads multiple clips into carousel (e.g., kick, bass, hats)
- All are playing simultaneously in Strudel
- User can swipe to edit any clip's code on the fly
- Changes update the live performance

### 2. Agent Context Awareness

**User Clarification**:
> "Agent receives user message and essentially already has agent history so it knows what the user is talking about, plus we can send it some metadata telling it what the user is looking at currently"

**Context Metadata to Send**:
- `current_project_id` - Which project is active
- `current_clip_id` - Which carousel pane is visible
- `loaded_clips` - All clips currently in carousel
- `carousel_index` - Which pane user is viewing
- `mode` - Live vs Production mode

**Agent Decision Making**:
- Agent is **not brittle** - it decides what to edit based on:
  - User's natural language request
  - Conversation history
  - Current context metadata
  - Musical intent

### 3. Lazy Loading Pattern

**User Clarification**:
> "When user switches to a panel, it should use some sort of lazy loading with some way in the agent responses to roughly include clips that were touched"

**Implementation Pattern**:
- Don't preload all clips from a song
- Load clip code only when user switches to that pane
- Agent responses include list of clip IDs that were modified
- Frontend uses that list to refresh only touched panes

**Agent Response Format** (proposed):
```json
{
  "message": "I've made the bass more aggressive...",
  "clips_modified": ["bass_main", "bass_variation"],
  "clips_created": ["bass_heavy"]
}
```

### 4. Desktop: Dual Carousel (Split Screen)

**User Clarification**:
> "It could very well be that there are two carousel elements (like split screen tab editors) on the desktop UI"

**Use Case**:
- Compare two clips side-by-side
- Edit two parts of a song simultaneously
- Copy/paste between clips
- Agent could work on both carousels independently

### 5. Data Management Philosophy

**User Clarification**:
> "I don't think massive amounts of data should be loaded in there, just a well-designed api endpoint and some lazy loading"

**Implication**:
- Left drawer (Projects/Clips/Songs/Playlists/Knowledge/Packs) uses **search/filter**
- As user types, query hits backend API
- Results stream back (paginated, filtered)
- Don't load entire project tree into frontend
- Think: **Spotify/VSCode file explorer** pattern

---

## Backend Restructure Plan

### Current Structure

```
strudel_agent/
├── mcp_server.py       # MCP tool server (CLI-focused)
├── agent.py            # CLI agent runner
└── agents/             # Agent prompt definitions
```

### Proposed Structure

```
strudel_agent/
├── backend/
│   ├── server.py           # FastAPI app with HTTP endpoints
│   ├── client.py           # Core business logic (extracted from mcp_server.py)
│   ├── mcp_server.py       # MCP server (wraps client.py)
│   ├── models.py           # Pydantic models (shared)
│   ├── agent_runner.py     # Agent execution logic
│   └── websocket.py        # WebSocket for agent streaming
├── ui/                     # Frontend (React/Vue/Svelte)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Carousel.tsx
│   │   │   ├── CodeEditor.tsx
│   │   │   ├── LeftDrawer.tsx
│   │   │   ├── RightDrawer.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── PlayerControls.tsx
│   │   ├── hooks/
│   │   │   ├── useCarousel.ts
│   │   │   ├── useStrudelPlayer.ts
│   │   │   └── useAgent.ts
│   │   └── pages/
│   │       └── Studio.tsx
│   └── public/
├── agents/                 # Agent prompts (unchanged)
├── projects/               # Data (unchanged)
├── knowledge/              # Data (unchanged)
└── known_packs/            # Data (unchanged)
```

### Separation of Concerns

**`backend/client.py`**:
- Extract all utility functions from `mcp_server.py`
- Core business logic (file operations, parsing, validation)
- No MCP-specific code
- No FastAPI-specific code
- Pure Python functions that can be used by both MCP and HTTP

**`backend/mcp_server.py`**:
- MCP tool definitions
- Wraps `client.py` functions
- Stays in `backend/` folder for organization

**`backend/server.py`**:
- FastAPI HTTP endpoints
- Wraps same `client.py` functions
- REST API for frontend
- WebSocket endpoint for agent streaming

**`backend/agent_runner.py`**:
- Agent execution logic
- Manages agent state, context, history
- Can be called by both MCP tools and HTTP endpoints

---

## Confidence Level

**HIGH** - I have a clear understanding of:
- Current MCP server tool surface (25 tools across 7 categories)
- File structure and data model (clips < songs < projects)
- Agent behavior and workflow patterns
- User's vision for carousel as "loaded clips in memory"
- Need for lazy loading and context-aware agent

**Next Step**: Create `deeper_design.md` with:
1. Complete API endpoint specifications
2. WebSocket protocol for agent communication
3. Frontend component architecture
4. State management strategy
5. Strudel player integration pattern
