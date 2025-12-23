# Strudel MCP Toolset - Design Decisions

**Date**: 2025-12-22  
**Status**: Clarifications from initial brainstorm

## Key Decisions Made

### 1. Clip Pre-population
**Decision**: Pre-populate clips from research notes

- Extract patterns/examples from `notes/research/` and `notes/known_packs/`
- Convert to clip format with appropriate tags
- Gives agent immediate vocabulary to work with
- User can add their own clips over time

**Action Items**:
- Parse research notes for code examples
- Extract patterns with context (genre, technique, etc.)
- Auto-generate initial clip library

---

### 2. Bidirectional Vocab Mapping
**Decision**: Support both Concept → Code AND Code → Concept

**Forward (Concept → Code)**:
- User says "add swing"
- Agent looks up swing → `.late("[0 .01]*4")`
- Direct mapping in vocab table

**Reverse (Code → Concept)**:
- Agent sees `.late("[0 .01]*4")` in code
- Agent identifies this as "swing pattern"
- Uses **embedding-based RAG** for semantic lookup

**Implementation**:
- Store **768D embeddings** of code snippets in clips table
- Use local embedding model (research needed for specific model)
- RAG tool: `identify_pattern(code_snippet)` → returns concepts/tags
- Enables agent to understand existing code semantically

**Benefits**:
- Agent can analyze user's code and describe what it does
- Agent can find similar patterns in clip library
- Agent can suggest alternatives: "This is a swing pattern, here are other swing variations"

---

### 3. Project Context / Conversation History
**Decision**: NOT handled by toolset - agent handles this

- Agent code already manages conversation context
- Toolset focuses on data access and manipulation
- Agent maintains state like "what 'it' refers to"

**No action needed** - toolset remains stateless, agent is stateful

---

### 4. Clip Composition
**Decision**: LLM does composition, toolset provides rich metadata

**Philosophy**: 
- Don't create deterministic "Clip A + Clip B" tools
- Instead, give LLM the information it needs to compose intelligently
- LLM is already good at creative combination

**Implementation**:
- Add `data: jsonb` field to all tables (projects, clips, etc.)
- Store rich metadata in `data` field:
  - Musical relationships ("works well with", "contrasts with")
  - Performance notes ("sounds good at 120-135 BPM")
  - Compatibility info ("requires key of Am or Cm")
  - Structural hints ("best as intro", "good for breakdown")
- Agent reads metadata and makes intelligent composition decisions

**Example Clip Metadata**:
```json
{
  "id": "acid_bassline_am",
  "code": "note(\"c2 eb2 f2 g2\").s(\"bass1\").lpf(600)",
  "tags": {...},
  "data": {
    "works_well_with": ["minimal_techno_kick", "sparse_hats"],
    "tempo_range": [120, 135],
    "key": "Am",
    "compatible_keys": ["Am", "Cm", "Em"],
    "layering_notes": "Sounds best with filtered kick, avoid busy hi-hats",
    "structural_position": ["main", "buildup"],
    "energy_level": "medium"
  }
}
```

Agent can then reason:
- "User wants dark bassline in Am"
- Searches clips: `tags.feeling = dark, tags.instrument = bass`
- Finds `acid_bassline_am`
- Checks `data.works_well_with` → sees it pairs with `minimal_techno_kick`
- Checks current song → already has `minimal_techno_kick`
- Agent: "Perfect match! This bassline is designed to work with your current kick."

---

### 5. Validation Strategy
**Decision**: Validation errors are **descriptive exceptions** that guide the agent

**Technical Stack**:
- FastMCP framework
- Pydantic-AI agents
- BaseModel for tool input validation (handled by FastMCP)

**Validation Layers**:

1. **Input Validation** (automatic via Pydantic)
   - FastMCP validates tool inputs against BaseModel schemas
   - Type errors, missing fields, etc. caught automatically

2. **Syntax Validation** (custom, in `validate_script` tool)
   - Parse Strudel/JavaScript syntax
   - Throw descriptive exceptions:
     ```python
     raise ValidationError(
         message="Syntax error at line 8, column 15",
         line=8,
         column=15,
         suggestion="Expected pattern, found ')'. Did you forget a closing quote?"
     )
     ```

3. **Semantic Validation** (custom, in `validate_script` tool)
   - Check for musical/logical errors
   - Throw informative exceptions:
     ```python
     raise ValidationError(
         message="Sample pack 'github:unknown/pack' not found",
         suggestion="Did you mean 'github:tidalcycles/Dirt-Samples'? Or load it first with samples()."
     )
     ```

**Exception Design Principles**:
- **Descriptive**: Explain exactly what's wrong
- **Data-exposing**: Include line numbers, columns, context
- **Actionable**: Suggest fixes when possible
- **Instructive**: Guide agent toward correct usage (sparingly)

**Example Exception**:
```python
class StrudelValidationError(Exception):
    def __init__(self, message: str, line: int = None, column: int = None, 
                 suggestion: str = None, code_context: str = None):
        self.message = message
        self.line = line
        self.column = column
        self.suggestion = suggestion
        self.code_context = code_context
        
    def to_dict(self):
        return {
            "error": self.message,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion,
            "context": self.code_context
        }
```

Agent receives this and can:
- Understand what went wrong
- See where it went wrong (line/column)
- Get suggestions for fixes
- Retry with corrected input

---

## Overall System Philosophy

### User → Agent → Toolset Flow

```
User: "Make it darker and add some swing"
  ↓
Agent (interprets):
  - "darker" → search clips with feeling:dark
  - "swing" → query vocab for swing techniques
  - "it" → refers to current song (from conversation context)
  ↓
Agent (uses tools):
  1. get_song() → see current state
  2. search_clips({"tags.feeling": "dark"}) → find dark patterns
  3. query_vocab("swing") → get swing code
  4. analyze_song_structure() → understand where to add
  ↓
Agent (composes):
  - Decides to add .late() to hi-hats for swing
  - Decides to add dark bassline clip
  - Generates patch instructions
  ↓
Agent (validates & applies):
  5. validate_script(patched_code) → check before applying
  6. update_song(patch_instructions) → apply changes
  ↓
Agent → User: "Added swing to hi-hats and inserted dark Am bassline"
```

### Toolset Responsibilities

**What the toolset DOES**:
- Provide data access (get/search/query)
- Provide data manipulation (update/create/delete)
- Validate syntax and semantics
- Parse and analyze structure
- Store and retrieve embeddings
- Execute patches on code

**What the toolset DOES NOT**:
- Make creative decisions (agent does this)
- Maintain conversation state (agent does this)
- Interpret user intent (agent does this)
- Compose new patterns deterministically (agent does this with LLM creativity)

### Data-Rich, Logic-Light

**Principle**: Toolset provides **rich data**, agent provides **intelligent logic**

- Tables have `data: jsonb` for extensible metadata
- Clips include compatibility, relationships, performance notes
- Agent reads this data and makes smart decisions
- Avoids hard-coding musical rules in toolset
- Keeps system flexible and adaptable

---

## Technical Stack Decisions

### Database
- **PostgreSQL** with **vector extension** (pgvector)
- **SQLModel** ORM for clean Python interface
- Handles embeddings natively
- JSONB support for flexible metadata

### Architecture
- `src/client.py` - Core functionality, database operations, business logic
- `mcp_server.py` - MCP wrapper, exposes tools to agent
- Clean separation: client is reusable, MCP server is thin wrapper

### Embeddings
- **768D embedding model** (local, research specific model)
- Store in vector column in clips table
- Enable semantic search and reverse lookup
- RAG for code → concept identification

---

## Next Steps

1. ✅ Document design decisions (this file)
2. ⏭️ Create proposed toolset draft
3. ⏭️ Research local embedding models (768D)
4. ⏭️ Define database schemas (SQLModel)
5. ⏭️ Define tool request/response models (Pydantic BaseModel)
6. ⏭️ Implement core client functionality
7. ⏭️ Wrap with MCP server
8. ⏭️ Test with agent

---

**Status**: Design decisions locked in. Ready for toolset draft.
