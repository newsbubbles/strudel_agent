# Strudel MCP Server Toolset - Initial Ideation

**Date**: 2025-12-22  
**Status**: Brainstorming / Design Phase

## Core Concept

An MCP server that enables an AI agent to collaborate with a user in **near-realtime** on Strudel live coding compositions. The agent should be able to:
- Understand natural language instructions about music
- Inspect the current "canvas" (song script)
- Make surgical edits via intelligent patching
- Validate changes before applying
- Remember and reuse musical "licks" (clips/skills/patterns)
- Query knowledge bases (packs, vocab, projects, clips)

## Mental Model

### The Canvas
- **Canvas** = Current working Strudel script for a project/song
- Agent sees the full script in context
- Agent generates a **diff/patch** to modify specific parts
- Changes are validated before application
- Think: collaborative live coding session where agent is your pair programmer

### The Clip Library (Skills/Licks)
- **Clips** = Reusable code snippets with musical meaning
- Tagged by: genre, feeling, technique, instrument, complexity
- Queryable via regex patterns
- Can be inserted at appropriate points in canvas
- Think: a musician's vocabulary of riffs, grooves, fills

### The Knowledge Bases
- **Packs Table**: Sample pack metadata, tags, loading syntax
- **Vocab Map**: Strudel functions, mini-notation, patterns mapped to musical concepts
- **Projects Table**: Project metadata, tags, genres, last modified

---

## Tool Categories

### 1. Canvas Tools (Core Workflow)

#### `get_song(project_name)`
- Returns current script for a project
- Full script context for agent analysis
- Metadata: tempo, key, genre tags, sample packs used

**Response**:
```json
{
  "project_name": "techno_jam_01",
  "script": "setcpm(128/4)\n\n$: sound(\"bd*4\")...",
  "metadata": {
    "tempo": 128,
    "key": "Am",
    "tags": ["techno", "minimal", "dark"],
    "packs_used": ["github:tidalcycles/Dirt-Samples"],
    "last_modified": "2025-12-22T10:30:00Z",
    "line_count": 45
  }
}
```

#### `update_song(project_name, patch_instructions)`
- Agent provides instructions for what to change
- System generates and applies patch
- Validates before applying
- Returns diff preview + success/error

**Request**:
```json
{
  "project_name": "techno_jam_01",
  "patch_instructions": {
    "action": "replace_line",  // or "insert_after", "delete_lines", "append"
    "target": {"line_number": 5},  // or {"pattern": "sound(\"bd*4\")"}
    "new_content": "$: sound(\"bd*4\").lpf(sine.range(400, 2000).slow(4))"
  }
}
```

Or more flexible:
```json
{
  "project_name": "techno_jam_01",
  "patch_instructions": {
    "action": "insert_after",
    "target": {"pattern": "setcpm\\(.*\\)"},  // Regex to find location
    "new_content": "\n// Bass layer\n$: note(\"c2 eb2 f2 g2\").s(\"bass1\").lpf(600)\n"
  }
}
```

**Response**:
```json
{
  "success": true,
  "validation": {"valid": true, "errors": []},
  "diff": "@@ -5,1 +5,1 @@\n-$: sound(\"bd*4\")\n+$: sound(\"bd*4\").lpf(sine.range(400, 2000).slow(4))",
  "preview": "Line 5 changed: Added filter sweep to kick"
}
```

#### `validate_script(script_content)`
- Validates Strudel syntax
- Checks for common errors
- Returns errors with line numbers
- Can be called before `update_song` to pre-validate

**Response**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {"line": 12, "message": "High gain value (1.5) may clip"}
  ]
}
```

Or on error:
```json
{
  "valid": false,
  "errors": [
    {"line": 8, "column": 15, "message": "Unexpected token ')', expected pattern"}
  ],
  "warnings": []
}
```

---

### 2. Project Management Tools

#### `list_projects(filters?)`
- List all projects with metadata
- Filter by tags, genre, date range
- Search by regex pattern in name/description

**Request**:
```json
{
  "filters": {
    "tags": ["techno"],
    "genre": "electronic",
    "name_pattern": "jam.*",  // Regex
    "modified_after": "2025-12-01"
  }
}
```

**Response**:
```json
{
  "projects": [
    {
      "name": "techno_jam_01",
      "description": "Minimal techno exploration",
      "tags": ["techno", "minimal", "dark"],
      "tempo": 128,
      "created": "2025-12-20T10:00:00Z",
      "modified": "2025-12-22T10:30:00Z",
      "line_count": 45
    }
  ]
}
```

#### `create_project(name, metadata?)`
- Create new project with optional metadata
- Initialize with template or blank canvas

#### `switch_project(name)`
- Set active project for subsequent operations
- Returns confirmation + project metadata

#### `delete_project(name)`
- Delete project (with confirmation)

#### `get_project_metadata(name)`
- Get metadata without full script
- Faster for browsing

---

### 3. Clip Library Tools (Skills/Licks)

**Concept**: Clips are reusable musical patterns/techniques that the agent can insert or suggest.

#### Clip Structure
```json
{
  "id": "minimal_techno_kick",
  "name": "Minimal Techno Kick Pattern",
  "description": "Four-on-the-floor with filter sweep",
  "code": "sound(\"bd*4\").lpf(sine.range(400, 2000).slow(4))",
  "tags": {
    "genre": ["techno", "minimal"],
    "feeling": ["driving", "hypnotic"],
    "technique": ["filter-sweep", "four-on-floor"],
    "instrument": ["kick", "bass-drum"],
    "complexity": "beginner",
    "element": "rhythm"  // rhythm, melody, harmony, texture, fx
  },
  "metadata": {
    "tempo_range": [120, 135],
    "key_agnostic": true,
    "requires_packs": ["github:tidalcycles/Dirt-Samples"],
    "created": "2025-12-22",
    "author": "user"
  }
}
```

#### `search_clips(query)`
- Query clips by regex on tags, name, description, code
- Returns matching clips

**Request**:
```json
{
  "query": {
    "tags.genre": "techno|house",  // Regex
    "tags.feeling": "dark",
    "tags.instrument": "kick",
    "complexity": "beginner|intermediate"
  }
}
```

**Response**:
```json
{
  "clips": [
    {
      "id": "minimal_techno_kick",
      "name": "Minimal Techno Kick Pattern",
      "code": "sound(\"bd*4\").lpf(sine.range(400, 2000).slow(4))",
      "tags": {...},
      "relevance_score": 0.95
    }
  ]
}
```

#### `get_clip(id)`
- Get full clip by ID

#### `save_clip(clip_data)`
- Save new clip to library
- Auto-generate tags from code analysis?

#### `update_clip(id, updates)`
- Update existing clip

#### `delete_clip(id)`
- Remove clip from library

#### `suggest_clips(context)`
- Agent provides current song context
- System suggests relevant clips
- Uses tags, tempo, key, genre to match

**Request**:
```json
{
  "context": {
    "current_script": "setcpm(128/4)\n$: sound(\"bd*4\")",
    "tags": ["techno", "minimal"],
    "tempo": 128,
    "key": "Am",
    "missing_elements": ["melody", "texture"]  // Agent's analysis
  }
}
```

**Response**:
```json
{
  "suggestions": [
    {
      "clip_id": "acid_bassline_am",
      "reason": "Matches key (Am), genre (techno), adds missing melody element",
      "confidence": 0.88
    }
  ]
}
```

---

### 4. Knowledge Base Tools

#### `query_packs(search_query)`
- Search sample packs database
- Regex on name, tags, description, categories

**Request**:
```json
{
  "query": {
    "tags": "analog|warm",
    "type": "drums"
  }
}
```

**Response**:
```json
{
  "packs": [
    {
      "name": "Garden",
      "github": "github:mot4i/garden",
      "tags": ["analog", "warm", "curated", "drums"],
      "description": "Analog-processed drum samples",
      "categories": ["garden_bd", "garden_sd", "garden_hh", ...]
    }
  ]
}
```

#### `query_vocab(concept)`
- Map musical concept to Strudel code
- Regex search through vocab map

**Request**:
```json
{
  "concept": "swing|shuffle|groove"
}
```

**Response**:
```json
{
  "matches": [
    {
      "concept": "swing",
      "strudel_code": ".late(\"[0 .01]*4\")",
      "description": "Add swing feel by delaying alternating notes",
      "example": "sound(\"hh*8\").late(\"[0 .01]*4\")"
    },
    {
      "concept": "shuffle",
      "strudel_code": ".shuffle(n)",
      "description": "Randomize pattern order",
      "example": "n(\"0 1 2 3\").shuffle()"
    }
  ]
}
```

#### `get_function_info(function_name)`
- Get detailed info about Strudel function
- Parameters, examples, related functions

---

### 5. Structural Analysis Tools

#### `analyze_song_structure(project_name)`
- Parse script into logical sections
- Identify patterns, voices, effects chains
- Return structural map

**Response**:
```json
{
  "structure": {
    "setup": {
      "lines": [1, 2],
      "content": ["setcpm(128/4)", "samples('github:mot4i/garden')"]
    },
    "voices": [
      {
        "id": "voice_1",
        "lines": [4, 5],
        "type": "rhythm",
        "instrument": "kick",
        "pattern": "sound(\"bd*4\").lpf(...)"
      },
      {
        "id": "voice_2",
        "lines": [7, 8],
        "type": "rhythm",
        "instrument": "snare",
        "pattern": "sound(\"[~ sd]*2\")"
      }
    ],
    "sections": [
      {
        "name": "intro",
        "lines": [4, 12],
        "voices": ["voice_1", "voice_2"]
      }
    ]
  }
}
```

This enables:
- Agent can say "add a hi-hat to the rhythm section"
- Agent can say "make the intro more sparse"
- Agent can target specific structural elements

---

## Patching Strategy

Since Strudel scripts have **structure**, we can be smart about patching:

### Structural Awareness

1. **Setup Section** (lines 1-N): `setcpm()`, `samples()`, imports
2. **Voice Definitions** (lines N-M): Individual `$:` pattern assignments
3. **Stack/Composition** (lines M-end): `stack()`, layering, arrangement

### Patch Operations

#### 1. **Line-based Patching**
```json
{
  "action": "replace_line",
  "line_number": 5,
  "new_content": "..."
}
```

#### 2. **Pattern-based Patching**
```json
{
  "action": "replace_pattern",
  "pattern": "sound\\(\"bd\\*4\"\\)",  // Regex to find
  "new_content": "sound(\"bd*4\").lpf(800)",
  "occurrence": "first"  // or "all", "last"
}
```

#### 3. **Section-based Patching**
```json
{
  "action": "insert_after_section",
  "section": "setup",
  "new_content": "// Melody\n$: note(...).s(\"arpy\")"
}
```

#### 4. **Voice-based Patching**
```json
{
  "action": "modify_voice",
  "voice_id": "voice_1",  // From structure analysis
  "modification": "add_effect",
  "effect": ".room(0.5)"
}
```

---

## Validation Strategy

### Syntax Validation
- Parse JavaScript/Strudel syntax
- Check for:
  - Unmatched parens/brackets
  - Invalid function names
  - Malformed patterns
  - Type errors (where detectable)

### Semantic Validation
- Check for:
  - Undefined sample packs
  - Invalid note names
  - Out-of-range parameters (e.g., `gain(100)`)
  - Conflicting patterns

### Runtime Validation (Optional)
- Could spin up Strudel evaluator
- Actually run the code in sandbox
- Catch runtime errors
- Return audio analysis?

---

## Agent Workflow Example

**User**: "Make the kick more punchy and add a dark bassline"

**Agent thinks**:
1. Call `get_song("current_project")` → Get full script
2. Call `analyze_song_structure("current_project")` → Find kick voice
3. Call `search_clips({"tags.instrument": "bass", "tags.feeling": "dark"})` → Find bassline clips
4. Generate patch:
   - Modify kick voice: add `.shape(0.4).gain(1.1)` for punch
   - Insert bassline clip after kick voice
5. Call `validate_script(patched_script)` → Check validity
6. Call `update_song("current_project", patch_instructions)` → Apply
7. Respond to user: "Added punch to kick with distortion and gain. Inserted dark bassline in Am."

---

## Data Storage

### Projects
- Stored as individual `.js` files in `projects/{name}/song.js`
- Metadata in `projects/{name}/metadata.json`

### Clips Library
- Stored in `clips/` directory
- Each clip as JSON file: `clips/{id}.json`
- Index file: `clips/index.json` for fast searching

### Knowledge Bases
- `knowledge/packs.json` - Sample packs database
- `knowledge/vocab.json` - Concept → Strudel mapping
- `knowledge/functions.json` - Function reference

---

## Open Questions / To Discuss

### 1. Clip Granularity
- Should clips be:
  - Single patterns? (e.g., just a kick pattern)
  - Multi-voice arrangements? (e.g., full drum kit)
  - Full sections? (e.g., intro, breakdown)
  - All of the above with different tags?

**Thought**: Probably all of the above. Tags can distinguish:
- `element: pattern` - Single voice
- `element: arrangement` - Multi-voice
- `element: section` - Full section

### 2. Tagging System
- How deep should tags go?
- Should we auto-generate tags from code analysis?
- Should tags be hierarchical? (e.g., `genre.techno.minimal`)

**Thought**: 
- Keep tags flat for regex simplicity
- Auto-generate basic tags (instrument, technique) from code
- Let user add subjective tags (feeling, genre)

### 3. Patching Intelligence
- Should agent generate exact patches or high-level instructions?
- Should we have a "patch DSL" or just use JSON?

**Thought**:
- JSON for structure
- Agent provides high-level intent
- Server translates to actual patch
- Allows for smarter patching logic on server side

### 4. Real-time Collaboration
- Should we support live preview of changes?
- WebSocket updates to Strudel REPL?
- Audio feedback loop?

**Thought**: 
- Phase 1: File-based (agent modifies, user reloads)
- Phase 2: WebSocket integration for live updates
- Phase 3: Audio analysis feedback

### 5. Clip Discovery
- How does agent learn what clips exist?
- Should clips have "similarity" scores?
- Should we use embeddings for semantic search?

**Thought**:
- Start with regex/tag-based search
- Later: Add embeddings for semantic similarity
- Agent can ask: "Find clips similar to [code snippet]"

### 6. Multi-file Projects
- Should projects support multiple files?
- How to handle imports/dependencies?

**Thought**:
- Phase 1: Single file per project
- Phase 2: Support modular structure
- Use Strudel's import system if available

### 7. Version Control
- Should we track changes to songs?
- Git integration?
- Undo/redo functionality?

**Thought**:
- Store git commits for each update
- Agent can say "undo last change"
- User can browse history

---

## Next Steps

1. **Define data schemas** (projects, clips, knowledge bases)
2. **Design patch DSL** (JSON structure for patch operations)
3. **Build validation system** (syntax + semantic checks)
4. **Implement core tools** (`get_song`, `update_song`, `search_clips`)
5. **Create knowledge bases** (populate from research)
6. **Build structural analyzer** (parse Strudel scripts)
7. **Test with agent** (iterate on UX)

---

## Tool Summary Table

| Tool | Purpose | Priority |
|------|---------|----------|
| `get_song` | Get current script | HIGH |
| `update_song` | Apply patches | HIGH |
| `validate_script` | Check syntax/semantics | HIGH |
| `list_projects` | Browse projects | HIGH |
| `create_project` | New project | MEDIUM |
| `switch_project` | Change active project | MEDIUM |
| `search_clips` | Find reusable patterns | HIGH |
| `get_clip` | Get clip details | MEDIUM |
| `save_clip` | Add to library | MEDIUM |
| `suggest_clips` | AI-powered suggestions | LOW (v2) |
| `query_packs` | Find sample packs | MEDIUM |
| `query_vocab` | Concept → code mapping | MEDIUM |
| `get_function_info` | Function reference | LOW |
| `analyze_song_structure` | Parse structure | MEDIUM |
| `delete_project` | Remove project | LOW |
| `update_clip` | Modify clip | LOW |
| `delete_clip` | Remove clip | LOW |

---

**Status**: Initial brainstorm complete. Ready for schema design and implementation planning.
