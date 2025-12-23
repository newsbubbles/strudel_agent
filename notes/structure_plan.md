# Strudel MCP Project Structure Plan

**Date**: 2025-12-22  
**Status**: Planning phase  
**Purpose**: Define complete project structure before implementation

---

## Project Root Structure

```
strudel-mcp/
├── src/
│   ├── __init__.py
│   ├── models.py           # SQLModel database models
│   ├── db.py               # Database connection and setup
│   ├── client.py           # Main client class (service/API layer)
│   ├── knowledge.py        # Knowledge base search functionality
│   ├── validation.py       # Script validation logic
│   ├── patching.py         # Code patching and diff generation
│   ├── analysis.py         # Song structure analysis
│   └── embeddings.py       # Embedding generation (local model)
│
├── knowledge/              # Curated reference knowledge (markdown)
│   ├── notation.md
│   ├── core_functions.md
│   ├── effects.md
│   ├── patterns.md
│   ├── vocabulary.md
│   ├── samples.md
│   ├── synths.md
│   └── best_practices.md
│
├── notes/                  # Design notes and research (not part of runtime)
│   ├── research/
│   ├── toolset/
│   ├── known_packs/
│   └── structure_plan.md (this file)
│
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_knowledge.py
│   ├── test_validation.py
│   ├── test_patching.py
│   └── test_embeddings.py
│
├── mcp_server.py           # MCP server (wraps client.py)
├── agent.py                # CLI agent for end-to-end testing
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project metadata and build config
├── .env.example            # Environment variables template
├── .gitignore
└── README.md
```

---

## Detailed Component Breakdown

### `src/models.py`

**Purpose**: Define SQLModel database schemas for all tables.

**Contents**:
- `Project` - Song projects table
- `Clip` - Reusable pattern library table
- `Pack` - Sample pack catalog table
- `Vocab` - Vocabulary (concept ↔ code) table
- `Function` - Strudel function reference table (optional, might be in knowledge/ instead)

**Key Features**:
- Use SQLModel (Pydantic + SQLAlchemy)
- Include vector columns for embeddings (pgvector)
- Include JSONB columns for extensible metadata
- Define relationships between models
- Include validation constraints

**Example Structure**:
```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String
from pgvector.sqlalchemy import Vector
from typing import Optional, List
import datetime

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    script: str = Field(default="")
    tempo: Optional[int] = None
    key: Optional[str] = None
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    genre: Optional[str] = None
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)
    modified: datetime.datetime = Field(default_factory=datetime.datetime.now)
    data: dict = Field(default_factory=dict, sa_column=Column(JSON))

class Clip(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    description: str
    code: str
    tags: dict = Field(sa_column=Column(JSON))  # {genre: [], feeling: [], ...}
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(768)))
    created: datetime.datetime = Field(default_factory=datetime.datetime.now)
    author: Optional[str] = None
    data: dict = Field(default_factory=dict, sa_column=Column(JSON))

# ... similar for Pack, Vocab, etc.
```

**Questions**:
- Should we include a `Function` table or keep function reference in knowledge files only?
- Do we need a `Session` or `User` table for multi-user support, or single-user for MVP?

---

### `src/db.py`

**Purpose**: Database connection management and initialization.

**Contents**:
- Database connection setup (PostgreSQL with pgvector)
- Connection pooling
- Table creation/migration logic
- Database session management
- Utility functions for database operations

**Key Features**:
- Use SQLModel's `create_engine` with asyncpg or psycopg2
- Enable pgvector extension
- Create tables on first run
- Handle connection errors gracefully
- Support for connection string from environment variables

**Example Structure**:
```python
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/strudel_mcp"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Initialize database: create tables, enable pgvector."""
    # Enable pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create all tables
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Get database session (context manager)."""
    with Session(engine) as session:
        yield session
```

**Questions**:
- Should we use async (asyncpg) or sync (psycopg2) for database operations?
- Do we need migration support (Alembic) or is `create_all()` sufficient for MVP?
- Should we support SQLite for local development/testing?

---

### `src/client.py`

**Purpose**: Main client class that exposes all functionality (service/API layer).

**Contents**:
- `StrudelClient` class that wraps all operations
- Methods corresponding to all 28 tools (19 original + 9 knowledge)
- Database session management
- Error handling and validation
- Business logic for complex operations

**Key Features**:
- Single class that MCP server can instantiate
- Each method maps to one MCP tool
- Methods accept Pydantic request models, return response models
- Handle database operations via `src/db.py`
- Delegate to specialized modules (knowledge, validation, patching, etc.)

**Example Structure**:
```python
from sqlmodel import Session, select
from src.models import Project, Clip, Pack, Vocab
from src.db import get_session, engine
from src.knowledge import KnowledgeBase
from src.validation import validate_strudel_script
from src.patching import apply_patch
from src.analysis import analyze_structure
from src.embeddings import generate_embedding
from typing import Optional, List
import datetime

class StrudelClient:
    """Main client for Strudel MCP operations."""
    
    def __init__(self, knowledge_dir: str = "./knowledge"):
        self.knowledge = KnowledgeBase(knowledge_dir)
    
    # Canvas Tools
    def get_song(self, project_name: str) -> dict:
        """Retrieve song script and metadata."""
        with Session(engine) as session:
            project = session.exec(
                select(Project).where(Project.name == project_name)
            ).first()
            
            if not project:
                raise ValueError(f"Project '{project_name}' not found")
            
            return {
                "project_name": project.name,
                "script": project.script,
                "metadata": {
                    "tempo": project.tempo,
                    "key": project.key,
                    "tags": project.tags,
                    "genre": project.genre,
                    "created": project.created,
                    "modified": project.modified,
                    "line_count": len(project.script.splitlines())
                },
                "data": project.data
            }
    
    def update_song(self, project_name: str, patch_instructions: dict, 
                   auto_validate: bool = True) -> dict:
        """Apply patch to song script."""
        # Implementation using src/patching.py
        pass
    
    def validate_script(self, script_content: str, 
                       project_name: Optional[str] = None) -> dict:
        """Validate Strudel script."""
        # Implementation using src/validation.py
        pass
    
    # Project Tools
    def list_projects(self, filters: Optional[dict] = None, 
                     sort_by: str = "modified", sort_order: str = "desc",
                     limit: int = 50) -> dict:
        """List projects with filtering and sorting."""
        pass
    
    def create_project(self, name: str, description: Optional[str] = None,
                      metadata: Optional[dict] = None, 
                      initial_script: Optional[str] = None) -> dict:
        """Create new project."""
        pass
    
    # ... (all other tool methods)
    
    # Knowledge Tools
    def lookup_notation(self, query: str, context_lines: int = 3) -> dict:
        """Look up mini-notation syntax."""
        return self.knowledge.search('notation', query, context_lines)
    
    def lookup_function(self, query: str, include_examples: bool = True) -> dict:
        """Look up function details."""
        return self.knowledge.search('functions', query, include_examples)
    
    # ... (all other knowledge methods)
```

**Questions**:
- Should `StrudelClient` hold a persistent database session or create new sessions per method?
- Should we use dependency injection for database/knowledge base, or initialize in `__init__`?
- How should we handle transaction management (commit/rollback)?

---

### `src/knowledge.py`

**Purpose**: Knowledge base search and parsing functionality.

**Contents**:
- `KnowledgeBase` class for searching markdown files
- Regex search across knowledge files
- Markdown parsing (sections, code blocks, lists)
- Result structuring and ranking

**Key Features**:
- File-based search (no database needed)
- Parse markdown structure for context
- Extract code examples
- Extract parameter ranges, descriptions
- Support for multiple file search

**Example Structure**:
```python
import re
from pathlib import Path
from typing import List, Dict, Optional

class KnowledgeBase:
    """Search and parse Strudel knowledge files."""
    
    def __init__(self, knowledge_dir: str):
        self.knowledge_dir = Path(knowledge_dir)
        self.files = {
            'notation': 'notation.md',
            'functions': 'core_functions.md',
            'effects': 'effects.md',
            'patterns': 'patterns.md',
            'vocabulary': 'vocabulary.md',
            'samples': 'samples.md',
            'synths': 'synths.md',
            'best_practices': 'best_practices.md'
        }
    
    def search(self, file_key: str, pattern: str, 
              context_lines: int = 3) -> Dict:
        """Search specific knowledge file by regex pattern."""
        file_path = self.knowledge_dir / self.files[file_key]
        
        if not file_path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {file_path}")
        
        matches = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Search with regex
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Extract context
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = ''.join(lines[start:end])
                
                # Find section header
                section = self._find_section(lines, i)
                
                # Extract example if in code block
                example = self._extract_code_example(lines, i)
                
                matches.append({
                    'section': section,
                    'content': context,
                    'line_number': i + 1,
                    'example': example
                })
        
        return {
            'matches': matches,
            'total_matches': len(matches)
        }
    
    def search_all(self, pattern: str, max_results: int = 20) -> Dict:
        """Search across all knowledge files."""
        results = []
        
        for file_key in self.files.keys():
            file_matches = self.search(file_key, pattern, context_lines=2)
            
            for match in file_matches['matches']:
                results.append({
                    'file': self.files[file_key],
                    'category': file_key,
                    **match
                })
        
        # Rank and limit results
        results = self._rank_results(results)
        results = results[:max_results]
        
        return {
            'results': results,
            'total_matches': len(results),
            'files_searched': list(self.files.values())
        }
    
    def _find_section(self, lines: List[str], current_line: int) -> str:
        """Find the markdown section header above current line."""
        for i in range(current_line, -1, -1):
            if lines[i].startswith('#'):
                return lines[i].strip('#').strip()
        return "Unknown"
    
    def _extract_code_example(self, lines: List[str], 
                             current_line: int) -> Optional[str]:
        """Extract code block near current line."""
        # Look for ```javascript or ``` blocks nearby
        # Implementation here
        pass
    
    def _rank_results(self, results: List[Dict]) -> List[Dict]:
        """Rank results by relevance."""
        # Simple ranking: prefer exact matches, section headers, etc.
        # Implementation here
        pass
```

**Questions**:
- Should we cache parsed knowledge files in memory for performance?
- Should we pre-index knowledge files on startup for faster search?
- Do we need fuzzy matching or is regex sufficient?

---

### `src/validation.py`

**Purpose**: Strudel script syntax and semantic validation.

**Contents**:
- JavaScript/Strudel syntax parsing
- Syntax error detection
- Semantic validation (undefined packs, invalid params)
- Musical validation (key mismatches, etc.)

**Key Features**:
- Parse JavaScript AST (using esprima or similar)
- Detect common Strudel patterns
- Validate against known functions/effects
- Return detailed error messages with line/column

**Example Structure**:
```python
import esprima  # or use subprocess to call node.js validator
from typing import Dict, List

def validate_strudel_script(script: str, context: Optional[Dict] = None) -> Dict:
    """Validate Strudel script syntax and semantics."""
    errors = []
    warnings = []
    
    # Syntax validation
    try:
        ast = esprima.parseScript(script, {'loc': True})
    except Exception as e:
        errors.append({
            'line': getattr(e, 'lineNumber', 0),
            'column': getattr(e, 'column', 0),
            'message': str(e),
            'suggestion': None,
            'code_context': _get_context(script, getattr(e, 'lineNumber', 0))
        })
    
    # Semantic validation
    # - Check for undefined sample packs
    # - Check for invalid function calls
    # - Check parameter ranges
    
    # Musical validation (warnings)
    # - Key mismatches
    # - Tempo issues
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def _get_context(script: str, line_number: int, context_lines: int = 2) -> str:
    """Get code context around error line."""
    lines = script.splitlines()
    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)
    return '\n'.join(lines[start:end])
```

**Questions**:
- Should we use Python-based JS parser (esprima-py) or call Node.js validator?
- How deep should semantic validation go (just syntax vs full Strudel API validation)?
- Should we validate against user's loaded sample packs from their project?

---

### `src/patching.py`

**Purpose**: Code patching and diff generation.

**Contents**:
- Parse patch instructions (line-based, pattern-based, section-based)
- Apply patches to code
- Generate diffs
- Handle patch conflicts/errors

**Key Features**:
- Support multiple patch types (replace line, insert after pattern, etc.)
- Generate unified diff format
- Validate patch before applying
- Rollback on error

**Example Structure**:
```python
import difflib
import re
from typing import Dict, List

def apply_patch(script: str, patch_instruction: Dict) -> Dict:
    """Apply patch instruction to script."""
    action = patch_instruction['action']
    
    if action in ['replace_line', 'insert_after_line', 'insert_before_line', 'delete_line']:
        result = _apply_line_patch(script, patch_instruction)
    elif action in ['replace_pattern', 'insert_after_pattern', 'insert_before_pattern']:
        result = _apply_pattern_patch(script, patch_instruction)
    elif action in ['append', 'prepend']:
        result = _apply_append_patch(script, patch_instruction)
    else:
        raise ValueError(f"Unknown patch action: {action}")
    
    # Generate diff
    diff = generate_diff(script, result['patched_script'])
    
    return {
        'success': True,
        'patched_script': result['patched_script'],
        'diff': diff,
        'preview': result['preview'],
        'lines_changed': result['lines_changed']
    }

def _apply_line_patch(script: str, instruction: Dict) -> Dict:
    """Apply line-based patch."""
    lines = script.splitlines()
    line_number = instruction['line_number']
    action = instruction['action']
    
    # Validate line number
    if line_number < 1 or line_number > len(lines) + 1:
        raise ValueError(f"Line number {line_number} out of range (1-{len(lines)})")
    
    # Apply patch based on action
    # Implementation here
    pass

def _apply_pattern_patch(script: str, instruction: Dict) -> Dict:
    """Apply pattern-based patch using regex."""
    pattern = instruction['pattern']
    new_content = instruction['new_content']
    occurrence = instruction.get('occurrence', 'first')
    
    # Find pattern matches
    matches = list(re.finditer(pattern, script))
    
    if not matches:
        raise ValueError(f"Pattern not found: {pattern}")
    
    # Apply patch based on occurrence
    # Implementation here
    pass

def generate_diff(original: str, modified: str) -> str:
    """Generate unified diff."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile='original',
        tofile='modified'
    )
    return ''.join(diff)
```

**Questions**:
- Should we support multi-patch operations (array of patches) in single call?
- Should we validate patches against current script before applying?
- How should we handle patch conflicts (e.g., line already modified)?

---

### `src/analysis.py`

**Purpose**: Song structure analysis and voice detection.

**Contents**:
- Parse Strudel script into structural components
- Identify voices, patterns, sections
- Detect effects chains
- Map line numbers to structural elements

**Key Features**:
- Parse JavaScript AST
- Identify Strudel patterns (sound(), note(), etc.)
- Detect voice definitions ($:, _$:)
- Identify sections (setup, voices, composition)
- Map effects to voices

**Example Structure**:
```python
import esprima
from typing import Dict, List

def analyze_structure(script: str) -> Dict:
    """Analyze song structure."""
    lines = script.splitlines()
    
    # Parse AST
    try:
        ast = esprima.parseScript(script, {'loc': True})
    except:
        return {'error': 'Failed to parse script'}
    
    # Identify sections
    setup = _identify_setup(lines)
    voices = _identify_voices(lines, ast)
    sections = _identify_sections(voices)
    
    return {
        'structure': {
            'setup': setup,
            'voices': voices,
            'sections': sections
        },
        'summary': {
            'total_lines': len(lines),
            'voice_count': len(voices),
            'section_count': len(sections),
            'complexity': _calculate_complexity(voices)
        }
    }

def _identify_setup(lines: List[str]) -> Dict:
    """Identify setup section (setcpm, samples, etc.)."""
    # Look for setcpm, setcps, samples() calls
    pass

def _identify_voices(lines: List[str], ast) -> List[Dict]:
    """Identify individual voices/patterns."""
    # Look for $:, _$:, sound(), note() patterns
    pass

def _identify_sections(voices: List[Dict]) -> List[Dict]:
    """Identify sections (intro, main, breakdown, etc.)."""
    # Group voices by proximity, detect structural patterns
    pass

def _calculate_complexity(voices: List[Dict]) -> str:
    """Calculate complexity level."""
    # Simple heuristic based on voice count, nesting, etc.
    if len(voices) <= 3:
        return 'simple'
    elif len(voices) <= 8:
        return 'moderate'
    else:
        return 'complex'
```

**Questions**:
- How sophisticated should structure analysis be for MVP?
- Should we use heuristics or ML for section detection?
- Should we detect musical structure (intro/verse/chorus) or just code structure?

---

### `src/embeddings.py`

**Purpose**: Generate embeddings for code snippets using local model.

**Contents**:
- Load local embedding model (768D)
- Generate embeddings for code/text
- Cache model in memory
- Handle batch embedding generation

**Key Features**:
- Use local transformer model (e.g., CodeBERT, sentence-transformers)
- 768-dimensional embeddings
- Efficient batching
- Model caching

**Example Structure**:
```python
from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np

# Load model once (module-level)
_model = None

def get_embedding_model():
    """Get or load embedding model (singleton)."""
    global _model
    if _model is None:
        # TODO: Research best 768D model for code
        _model = SentenceTransformer('all-mpnet-base-v2')  # Placeholder
    return _model

def generate_embedding(text: str) -> List[float]:
    """Generate embedding for single text."""
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()

def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for batch of texts."""
    model = get_embedding_model()
    embeddings = model.encode(texts)
    return embeddings.tolist()

def cosine_similarity(embedding1: List[float], 
                     embedding2: List[float]) -> float:
    """Calculate cosine similarity between embeddings."""
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

**Questions**:
- Which 768D embedding model should we use? (CodeBERT, GraphCodeBERT, sentence-transformers?)
- Should we fine-tune on Strudel code examples?
- Should embeddings be generated on-demand or pre-computed for all clips?

---

## Root Level Files

### `mcp_server.py`

**Purpose**: MCP server that wraps `StrudelClient` and exposes tools.

**Contents**:
- FastMCP server setup
- Tool definitions (all 28 tools)
- Request/response models (Pydantic)
- Error handling
- Client initialization

**Generation Method**:
- Use `get_mcp_server_coding_instructions` tool
- Provide `client_path="src/client.py"`
- Follow FastMCP best practices

**Key Features**:
- Thin wrapper around `StrudelClient`
- Each tool maps to one client method
- Pydantic models for validation
- Descriptive error messages
- Resource exposure (if needed)

**Example Structure**:
```python
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from src.client import StrudelClient
from typing import Optional, List

# Initialize MCP server
mcp = FastMCP("Strudel MCP Server")

# Initialize client
client = StrudelClient(knowledge_dir="./knowledge")

# Request/Response models
class GetSongRequest(BaseModel):
    project_name: str = Field(description="Name of project to fetch")

class GetSongResponse(BaseModel):
    project_name: str
    script: str
    metadata: dict
    data: dict

# Tool definitions
@mcp.tool()
def get_song(request: GetSongRequest) -> GetSongResponse:
    """Retrieve song script and metadata for a project."""
    result = client.get_song(request.project_name)
    return GetSongResponse(**result)

# ... (all other 27 tools)

if __name__ == "__main__":
    mcp.run()
```

**Questions**:
- Should we use FastMCP's built-in error handling or custom exceptions?
- Should we expose any resources (e.g., current project state)?
- Should we support server configuration via environment variables?

---

### `agent.py`

**Purpose**: CLI agent for end-to-end testing and demonstration.

**Contents**:
- Pydantic-AI agent setup
- MCP client connection
- Interactive CLI loop
- Agent system prompt
- Conversation history

**Generation Method**:
- Use `get_agent_coding_instructions` tool
- Provide `agent_name="strudel"` (or similar)
- Follow Pydantic-AI best practices

**Key Features**:
- Connect to MCP server
- Use all 28 tools
- Interactive conversation
- Handle user input
- Display results

**Example Structure**:
```python
import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Agent system prompt
SYSTEM_PROMPT = """
You are a Strudel live coding assistant...
[Include tool usage triggers, workflow guidance, etc.]
"""

# Initialize agent
agent = Agent(
    model=OpenAIModel('gpt-4'),
    system_prompt=SYSTEM_PROMPT
)

async def main():
    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()
            
            # Get available tools
            tools = await session.list_tools()
            
            # Interactive loop
            print("Strudel Agent ready! Type 'exit' to quit.")
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == 'exit':
                    break
                
                # Run agent
                result = await agent.run(user_input, tools=tools)
                print(f"\nAgent: {result.data}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Questions**:
- Should agent support streaming responses?
- Should we save conversation history to file?
- Should agent have access to current project context across sessions?

---

### `requirements.txt`

**Purpose**: Python dependencies.

**Contents**:
```
# Core
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9  # or asyncpg for async
pgvector>=0.2.4

# MCP
fastmcp>=0.1.0
pydantic>=2.0.0
pydantic-ai>=0.0.1  # For agent

# Embeddings
sentence-transformers>=2.2.0  # Or specific model
torch>=2.0.0  # For transformers

# Validation
esprima>=4.0.1  # JS parser

# Utilities
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

**Questions**:
- Should we pin exact versions or use minimum versions?
- Should we separate dev dependencies (testing, linting)?
- Should we use poetry or pip for dependency management?

---

### `pyproject.toml`

**Purpose**: Project metadata and build configuration.

**Contents**:
```toml
[project]
name = "strudel-mcp"
version = "0.1.0"
description = "MCP server for Strudel live coding assistance"
authors = [{name = "Your Name", email = "your.email@example.com"}]
requires-python = ">=3.10"
dependencies = [
    # From requirements.txt
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0"
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"
```

---

### `.env.example`

**Purpose**: Template for environment variables.

**Contents**:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/strudel_mcp

# OpenAI (for agent)
OPENAI_API_KEY=your_openai_api_key_here

# Embedding Model (if using API instead of local)
# EMBEDDING_MODEL=all-mpnet-base-v2

# MCP Server
# MCP_HOST=localhost
# MCP_PORT=3000
```

---

### `README.md`

**Purpose**: Project documentation.

**Contents**:
- Project overview
- Installation instructions
- Database setup
- Usage examples
- MCP server setup
- Agent usage
- Development guide
- Contributing guidelines

---

## Knowledge Files

### Structure

All files in `knowledge/` directory, curated from `notes/research/`:

1. **`notation.md`** ← from `notes/research/02_mini_notation_cheatsheet.md`
2. **`core_functions.md`** ← from `notes/research/03_core_functions_reference.md`
3. **`effects.md`** ← from `notes/research/04_effects_reference.md`
4. **`patterns.md`** ← from `notes/research/07_musical_patterns_library.md`
5. **`vocabulary.md`** ← from `notes/research/08_strudel_vocabulary_glossary.md`
6. **`samples.md`** ← from `notes/research/05_samples_drums_reference.md`
7. **`synths.md`** ← from `notes/research/06_synths_reference.md`
8. **`best_practices.md`** ← new, curated from research + tips

### Curation Process

1. Copy content from research notes
2. Add consistent section headers
3. Add searchable keywords/synonyms
4. Format parameter ranges consistently
5. Add more code examples
6. Cross-reference related concepts
7. Optimize for regex search

---

## Tests Structure

### Test Files

- `test_client.py` - Test all `StrudelClient` methods
- `test_knowledge.py` - Test knowledge base search
- `test_validation.py` - Test script validation
- `test_patching.py` - Test patching logic
- `test_embeddings.py` - Test embedding generation
- `test_mcp_server.py` - Test MCP server tools (optional)

### Test Database

- Use SQLite for testing (faster, no setup)
- Or use Docker container with PostgreSQL + pgvector
- Create test fixtures for projects, clips, etc.

---

## Development Workflow

### Initial Setup

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure
4. Setup PostgreSQL with pgvector extension
5. Initialize database: `python -c "from src.db import init_db; init_db()"`
6. Curate knowledge files from research notes
7. Populate initial data (sample packs from research)

### Running MCP Server

```bash
python mcp_server.py
```

### Running Agent

```bash
python agent.py
```

### Running Tests

```bash
pytest tests/
```

---

## Open Questions

### Database

1. **Async vs Sync**: Should we use asyncpg (async) or psycopg2 (sync)?
   - **Recommendation**: Start with psycopg2 (sync) for simplicity, migrate to async if needed

2. **Migrations**: Do we need Alembic for migrations or is `create_all()` sufficient?
   - **Recommendation**: `create_all()` for MVP, add Alembic later if schema changes frequently

3. **SQLite Support**: Should we support SQLite for local dev/testing?
   - **Recommendation**: Yes, use SQLite for tests, PostgreSQL for production

### Client Architecture

4. **Session Management**: Should `StrudelClient` hold persistent session or create per-method?
   - **Recommendation**: Create session per method (context manager) for thread safety

5. **Dependency Injection**: Should we use DI for db/knowledge or initialize in `__init__`?
   - **Recommendation**: Initialize in `__init__` for simplicity

### Validation

6. **JS Parser**: Use Python esprima or call Node.js validator?
   - **Recommendation**: Use esprima-py (Python) to avoid Node.js dependency

7. **Validation Depth**: Just syntax or full Strudel API validation?
   - **Recommendation**: Syntax + basic semantic (undefined packs, common errors) for MVP

### Embeddings

8. **Embedding Model**: Which 768D model? (CodeBERT, sentence-transformers, etc.)
   - **Recommendation**: Research needed - see notes/toolset/embedding_model_research.md (TODO)

9. **Fine-tuning**: Should we fine-tune on Strudel examples?
   - **Recommendation**: Not for MVP, use pre-trained model first

### Knowledge

10. **Caching**: Should we cache parsed knowledge files?
    - **Recommendation**: Yes, load all files on startup and cache in memory

11. **Indexing**: Should we pre-index for faster search?
    - **Recommendation**: Not for MVP, files are small enough for on-demand regex

### MCP Server

12. **Error Handling**: Use FastMCP built-in or custom exceptions?
    - **Recommendation**: Use FastMCP built-in, add custom `StrudelError` class for domain errors

13. **Resources**: Should we expose resources (e.g., current project)?
    - **Recommendation**: Not for MVP, tools are sufficient

### Agent

14. **Streaming**: Should agent support streaming responses?
    - **Recommendation**: Not for MVP, add later if needed

15. **History**: Should we save conversation history?
    - **Recommendation**: Yes, save to file for debugging/analysis

---

## Implementation Order

### Phase 1: Core Infrastructure

1. Setup project structure
2. Create `src/models.py` (database models)
3. Create `src/db.py` (database connection)
4. Create basic `src/client.py` (empty methods)
5. Setup tests

### Phase 2: Knowledge System

6. Curate `knowledge/` files from research
7. Implement `src/knowledge.py`
8. Test knowledge search
9. Implement knowledge tools in client

### Phase 3: Core Tools

10. Implement `src/validation.py`
11. Implement `src/patching.py`
12. Implement `src/analysis.py`
13. Implement canvas tools in client
14. Implement project tools in client

### Phase 4: Clip System

15. Implement `src/embeddings.py`
16. Implement clip tools in client
17. Populate initial clip library

### Phase 5: MCP & Agent

18. Generate `mcp_server.py` using tool
19. Test MCP server
20. Generate `agent.py` using tool
21. Test agent end-to-end

### Phase 6: Polish

22. Add comprehensive tests
23. Add error handling
24. Write documentation
25. Performance optimization

---

## Next Steps

1. **Answer open questions** (especially embedding model choice)
2. **Create project structure** (folders, empty files)
3. **Setup database** (PostgreSQL + pgvector)
4. **Curate knowledge files** (from research notes)
5. **Start Phase 1 implementation** (models, db, client skeleton)

---

**Status**: Structure plan complete. Ready to answer questions and begin implementation.
