# Strudel Agent Interface - Deeper Design

**Date**: 2025-12-25  
**Topic**: API endpoints, WebSocket protocol, frontend architecture  
**Related**: `notes/interface/seed.md`, `notes/interface/investigation.md`, `notes/strudel_external_control_research/`

---

## Architecture Overview

### Technology Stack

**Backend**:
- **FastAPI** - HTTP REST API + WebSocket
- **Python 3.10+** - Core logic
- **Whisper** (openai-whisper) - Voice transcription
- **Existing MCP Server** - Agent tool interface (unchanged)

**Frontend**:
- **Svelte** - Component framework (chosen for mobile-first performance)
- **TypeScript** - Type safety
- **Tailwind CSS** - Mobile-first styling
- **CodeMirror** - Code editing with JavaScript syntax highlighting (lighter than Monaco)
- **@strudel/web** - Headless Strudel player (no UI, full control) ⭐
- **Embla Carousel** - Touch-friendly carousel

**Communication**:
- **REST API** - CRUD operations, data fetching
- **WebSocket** - Agent streaming, real-time updates

---

## Backend Architecture

### File Structure

```
strudel_agent/
├── backend/
│   ├── __init__.py
│   ├── server.py           # FastAPI app entry point
│   ├── client.py           # Core business logic (filesystem operations)
│   ├── mcp_server.py       # MCP server (moved here, wraps client.py)
│   ├── models.py           # Pydantic models (shared between MCP and HTTP)
│   ├── agent_runner.py     # Agent execution and context management
│   ├── websocket.py        # WebSocket handlers for agent streaming
│   ├── whisper_service.py  # Voice transcription service
│   └── config.py           # Configuration (paths, settings)
├── ui/                     # Frontend application
├── agents/                 # Agent prompts (unchanged)
├── projects/               # User data (unchanged)
├── knowledge/              # Strudel docs (unchanged)
└── known_packs/            # Sample pack docs (unchanged)
```

### Core Modules

#### `backend/client.py` - Business Logic Layer

**Purpose**: Pure Python functions for all filesystem operations, extracted from current `mcp_server.py`

**Key Functions**:
```python
# Project operations
def list_projects(query: Optional[str] = None) -> List[ProjectInfo]
def get_project(project_id: str) -> Optional[ProjectInfo]
def create_project(project_id: str, content: str) -> bool

# Clip operations
def list_clips(project_id: str, query: Optional[str] = None) -> List[ClipInfo]
def get_clip(project_id: str, clip_id: str) -> Optional[ClipData]
def save_clip(project_id: str, clip_id: str, metadata: dict, code: str) -> bool
def update_clip(project_id: str, clip_id: str, metadata: Optional[dict], code: Optional[str]) -> bool
def delete_clip(project_id: str, clip_id: str) -> bool

# Song operations (similar pattern)
# Playlist operations (similar pattern)
# Knowledge operations (similar pattern)
# Template operations (similar pattern)
```

**No dependencies on**:
- FastAPI (no `Request`, `Response` objects)
- MCP (no `@mcp.tool()` decorators)
- Just pure Python with Pydantic models

#### `backend/server.py` - FastAPI HTTP Server

**Purpose**: REST API wrapping `client.py` functions

**Structure**:
```python
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from . import client
from .models import *
from .websocket import router as ws_router

app = FastAPI(title="Strudel Agent API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket router
app.include_router(ws_router)

# REST endpoints (see below)
```

#### `backend/agent_runner.py` - Agent Execution

**Purpose**: Manage agent state, execute agent with MCP tools, stream responses

**Key Classes**:
```python
class AgentContext:
    """Context passed to agent with each message"""
    project_id: str
    current_clip_id: Optional[str]
    loaded_clips: List[str]  # Clips in carousel
    carousel_index: int
    mode: Literal["live", "production"]
    
class AgentRunner:
    """Executes agent and streams responses"""
    
    async def run_agent(
        self,
        message: str,
        context: AgentContext,
        history: List[Message],
        stream_callback: Callable[[str], Awaitable[None]]
    ) -> AgentResponse:
        """Run agent with MCP tools, stream response chunks"""
        pass
```

#### `backend/websocket.py` - WebSocket Handler

**Purpose**: Real-time agent communication

**Protocol** (see detailed spec below)

#### `backend/whisper_service.py` - Voice Transcription

**Purpose**: Transcribe voice messages using Whisper

```python
import whisper

class WhisperService:
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)
    
    def transcribe(self, audio_file_path: str) -> str:
        """Transcribe audio file to text"""
        result = self.model.transcribe(audio_file_path)
        return result["text"]
```

---

## REST API Endpoints

### Base URL: `http://localhost:8000/api`

### Projects

#### `GET /projects`
List all projects with optional filter

**Query Params**:
- `query` (optional): Regex pattern to filter projects

**Response**:
```json
{
  "projects": [
    {
      "project_id": "house_project",
      "name": "House Music Project",
      "description": "Exploring deep house vibes",
      "clip_count": 12,
      "song_count": 3,
      "playlist_count": 1
    }
  ],
  "total": 1
}
```

#### `GET /projects/{project_id}`
Get project details

**Response**: Single `ProjectInfo` object

#### `POST /projects`
Create new project

**Body**:
```json
{
  "project_id": "techno_project",
  "content": "# Techno Project\n\nMinimal techno experiments"
}
```

---

### Clips

#### `GET /projects/{project_id}/clips`
List clips in project

**Query Params**:
- `query` (optional): Regex filter

**Response**:
```json
{
  "clips": [
    {
      "clip_id": "kick_main",
      "name": "Main Kick",
      "tags": ["drums", "kick", "techno"],
      "tempo": 130,
      "description": "Heavy techno kick"
    }
  ],
  "total": 1,
  "project_id": "techno_project"
}
```

#### `GET /projects/{project_id}/clips/{clip_id}`
Get full clip data

**Response**:
```json
{
  "clip_id": "kick_main",
  "metadata": {
    "name": "Main Kick",
    "tags": ["drums", "kick", "techno"],
    "tempo": 130,
    "description": "Heavy techno kick"
  },
  "code": "sound(\"bd*4\").bank(\"RolandTR909\").gain(0.9)"
}
```

#### `POST /projects/{project_id}/clips`
Create new clip

**Body**:
```json
{
  "clip_id": "bass_main",
  "metadata": {
    "name": "Main Bass",
    "tags": ["bass", "techno"],
    "tempo": 130,
    "description": "Filtered bass line"
  },
  "strudel_script": "note(\"c2 ~ c2 ~\").sound(\"sawtooth\").lpf(800)"
}
```

#### `PUT /projects/{project_id}/clips/{clip_id}`
Update existing clip

**Body** (all fields optional):
```json
{
  "metadata": { /* updated metadata */ },
  "strudel_script": "/* updated code */"
}
```

#### `DELETE /projects/{project_id}/clips/{clip_id}`
Delete clip

**Response**: `{"success": true}`

---

### Songs

#### `GET /projects/{project_id}/songs`
List songs

#### `GET /projects/{project_id}/songs/{song_id}`
Get full song content

**Response**:
```json
{
  "song_id": "track_one",
  "title": "Track One",
  "description": "First complete track",
  "body": "# Track One\n\n...full markdown..."
}
```

#### `POST /projects/{project_id}/songs`
Create song

#### `PUT /projects/{project_id}/songs/{song_id}`
Update song

#### `DELETE /projects/{project_id}/songs/{song_id}`
Delete song

---

### Playlists

*(Similar CRUD pattern as Songs)*

---

### Knowledge

#### `GET /knowledge`
List knowledge documents

**Response**:
```json
{
  "documents": ["functions.md", "patterns.md", "effects.md"],
  "total": 3
}
```

#### `GET /knowledge/search`
Search knowledge base

**Query Params**:
- `q`: Regex search pattern

**Response**:
```json
{
  "results": [
    {
      "file": "functions.md",
      "matches": [
        {
          "line_number": 42,
          "content": "lpf(cutoff) - Low pass filter",
          "context": "...surrounding lines..."
        }
      ]
    }
  ],
  "total_files": 1
}
```

#### `POST /knowledge/read`
Read multiple knowledge documents

**Body**:
```json
{
  "document_filenames": ["functions.md", "patterns.md"]
}
```

---

### Known Packs

#### `GET /packs/search`
Search sample packs

**Query Params**:
- `q` (optional): Regex search pattern

#### `POST /packs/details`
Get pack details

**Body**:
```json
{
  "pack_names": ["dirt_samples", "garden"]
}
```

---

### Templates

#### `GET /projects/{project_id}/templates`
List templates with filters

**Query Params**:
- `category` (optional): Filter by category
- `tags` (optional): Comma-separated tags
- `query` (optional): Regex search

#### `GET /projects/{project_id}/templates/{template_id}`
Get template schema

#### `POST /projects/{project_id}/templates`
Create template

#### `POST /projects/{project_id}/templates/{template_id}/generate`
Generate code from template

**Body**:
```json
{
  "variables": {
    "tempo": 130,
    "pattern": "bd*4",
    "filter_cutoff": 800
  },
  "do_validation": true
}
```

**Response**:
```json
{
  "success": true,
  "code": "/* generated Strudel code */",
  "variables_used": { /* ... */ }
}
```

---

### Voice Transcription

#### `POST /voice/transcribe`
Transcribe audio to text

**Body**: `multipart/form-data`
- `audio`: Audio file (webm, mp3, wav, etc.)

**Response**:
```json
{
  "text": "Make the bass more aggressive",
  "language": "en"
}
```

**Implementation**:
```python
@app.post("/api/voice/transcribe")
async def transcribe_voice(audio: UploadFile):
    # Save uploaded file temporarily
    temp_path = f"/tmp/{audio.filename}"
    with open(temp_path, "wb") as f:
        f.write(await audio.read())
    
    # Transcribe with Whisper
    whisper_service = WhisperService()
    text = whisper_service.transcribe(temp_path)
    
    # Clean up
    os.remove(temp_path)
    
    return {"text": text, "language": "en"}
```

---

## WebSocket Protocol

### Endpoint: `ws://localhost:8000/ws/agent`

### Connection Flow

1. **Client connects** with query params:
   ```
   ws://localhost:8000/ws/agent?project_id=house_project
   ```

2. **Server sends** connection confirmation:
   ```json
   {
     "type": "connected",
     "session_id": "uuid-here"
   }
   ```

3. **Client sends** messages with context:
   ```json
   {
     "type": "message",
     "content": "Make the bass more aggressive",
     "context": {
       "project_id": "house_project",
       "current_clip_id": "bass_main",
       "loaded_clips": ["kick_main", "bass_main", "hats_main"],
       "carousel_index": 1,
       "mode": "live"
     }
   }
   ```

4. **Server streams** agent response:
   ```json
   {"type": "chunk", "content": "I'll "}
   {"type": "chunk", "content": "increase "}
   {"type": "chunk", "content": "the filter"}
   // ...
   ```

5. **Server sends** completion with metadata:
   ```json
   {
     "type": "complete",
     "clips_modified": ["bass_main"],
     "clips_created": [],
     "tool_calls": [
       {
         "tool": "update_clip",
         "args": {"project_id": "house_project", "clip_id": "bass_main"}
       }
     ]
   }
   ```

### Message Types

#### Client → Server

**`message`** - User message to agent
```json
{
  "type": "message",
  "content": "string",
  "context": {
    "project_id": "string",
    "current_clip_id": "string | null",
    "loaded_clips": ["string"],
    "carousel_index": "number",
    "mode": "live | production"
  }
}
```

**`interrupt`** - Stop agent mid-response
```json
{
  "type": "interrupt"
}
```

#### Server → Client

**`connected`** - Connection established
```json
{
  "type": "connected",
  "session_id": "string"
}
```

**`chunk`** - Streaming response chunk
```json
{
  "type": "chunk",
  "content": "string"
}
```

**`complete`** - Response finished
```json
{
  "type": "complete",
  "clips_modified": ["string"],
  "clips_created": ["string"],
  "tool_calls": [
    {
      "tool": "string",
      "args": {}
    }
  ]
}
```

**`error`** - Error occurred
```json
{
  "type": "error",
  "message": "string",
  "code": "string"
}
```

**`player_update`** - Agent requests player update
```json
{
  "type": "player_update",
  "action": "reload_clip",
  "clip_id": "string"
}
```

---

## Frontend Architecture

### Component Hierarchy

```
App
├── Studio (main page)
    ├── LeftDrawer
    │   ├── ProjectPicker
    │   ├── ClipBrowser
    │   ├── SongBrowser
    │   ├── PlaylistBrowser
    │   ├── KnowledgeBrowser
    │   └── PacksBrowser
    ├── MainContent
    │   ├── Carousel (or DualCarousel on desktop)
    │   │   └── CarouselPane[]
    │   │       └── CodeEditor
    │   └── MessageInput
    │       ├── TextInput
    │       ├── SendButton
    │       └── VoiceButton
    ├── RightDrawer
    │   └── ChatHistory
    └── PlayerControls (fixed position)
        ├── PlayButton
        ├── StopButton
        ├── UpdateButton
        └── DrawerToggle
```

### State Management

**Global State** (Zustand):
```typescript
interface StudioState {
  // Project state
  currentProject: Project | null
  
  // Carousel state
  loadedClips: LoadedClip[]  // Clips in carousel
  currentCarouselIndex: number
  
  // Player state
  isPlaying: boolean
  strudelInitialized: boolean
  
  // Agent state
  chatHistory: Message[]
  isAgentThinking: boolean
  
  // UI state
  leftDrawerOpen: boolean
  rightDrawerOpen: boolean
  mode: 'live' | 'production'
}

interface LoadedClip {
  clip_id: string
  code: string
  metadata: ClipMetadata
  isDirty: boolean  // Has unsaved changes
}
```

### Key Hooks

#### `useCarousel()`
```typescript
function useCarousel() {
  const loadedClips = useStore(state => state.loadedClips)
  const currentIndex = useStore(state => state.currentCarouselIndex)
  
  const addClip = async (clipId: string) => {
    // Fetch clip from API
    const clip = await api.getClip(projectId, clipId)
    // Add to loaded clips
    store.addLoadedClip(clip)
  }
  
  const removeClip = (index: number) => {
    // Remove from loaded clips
    store.removeLoadedClip(index)
  }
  
  const updateClipCode = (index: number, code: string) => {
    // Update code in state (mark as dirty)
    store.updateLoadedClipCode(index, code)
  }
  
  const saveClip = async (index: number) => {
    // Save to backend
    const clip = loadedClips[index]
    await api.updateClip(projectId, clip.clip_id, { strudel_script: clip.code })
    // Mark as clean
    store.markClipClean(index)
  }
  
  return { loadedClips, currentIndex, addClip, removeClip, updateClipCode, saveClip }
}
```

#### `useStrudelPlayer()` - Using @strudel/web

```typescript
import { initStrudel, evaluate, hush } from '@strudel/web'

function useStrudelPlayer() {
  const loadedClips = useStore(state => state.loadedClips)
  const [isInitialized, setIsInitialized] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  
  useEffect(() => {
    // Initialize Strudel once on mount
    initStrudel({
      prebake: async () => {
        // Load default samples
        await samples('github:tidalcycles/dirt-samples')
      }
    }).then(() => {
      setIsInitialized(true)
      console.log('Strudel initialized')
    })
  }, [])
  
  const play = async () => {
    if (!isInitialized) {
      console.warn('Strudel not initialized yet')
      return
    }
    
    // Combine all loaded clips into single Strudel code
    // Stack them vertically so they play simultaneously
    const combinedCode = loadedClips.length > 0
      ? `stack(\n${loadedClips.map(c => `  ${c.code}`).join(',\n')}\n)`
      : 'silence()'
    
    try {
      await evaluate(combinedCode)
      setIsPlaying(true)
    } catch (err) {
      console.error('Evaluation error:', err)
    }
  }
  
  const stop = () => {
    hush()  // Stop all patterns
    setIsPlaying(false)
  }
  
  const updateClip = async (clipIndex: number) => {
    // Re-evaluate with updated clip
    if (isPlaying) {
      await play()  // This will re-evaluate with all clips
    }
  }
  
  const reloadAllClips = async () => {
    // Force re-evaluation (called after agent modifies clips)
    if (isPlaying) {
      await play()
    }
  }
  
  return { 
    play, 
    stop, 
    updateClip, 
    reloadAllClips,
    isPlaying, 
    isInitialized 
  }
}
```

#### `useAgent()`
```typescript
function useAgent() {
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [isThinking, setIsThinking] = useState(false)
  const chatHistory = useStore(state => state.chatHistory)
  const { reloadAllClips } = useStrudelPlayer()
  
  useEffect(() => {
    // Connect WebSocket
    const socket = new WebSocket('ws://localhost:8000/ws/agent')
    
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch (data.type) {
        case 'chunk':
          // Append to current message
          store.appendToLastMessage(data.content)
          break
        
        case 'complete':
          setIsThinking(false)
          // Reload modified clips
          if (data.clips_modified.length > 0 || data.clips_created.length > 0) {
            reloadClipsFromBackend(data.clips_modified, data.clips_created)
          }
          break
        
        case 'player_update':
          // Handle player update request from agent
          if (data.action === 'reload_clip') {
            reloadAllClips()
          }
          break
      }
    }
    
    setWs(socket)
    return () => socket.close()
  }, [])
  
  const reloadClipsFromBackend = async (modifiedIds: string[], createdIds: string[]) => {
    // Fetch updated clip data from backend
    const allIds = [...modifiedIds, ...createdIds]
    
    for (const clipId of allIds) {
      const clipData = await api.getClip(projectId, clipId)
      
      // Update in loaded clips if already loaded
      const index = store.loadedClips.findIndex(c => c.clip_id === clipId)
      if (index >= 0) {
        store.updateLoadedClip(index, clipData)
      }
    }
    
    // Reload player if playing
    reloadAllClips()
  }
  
  const sendMessage = (content: string) => {
    if (!ws) return
    
    setIsThinking(true)
    store.addMessage({ role: 'user', content })
    
    // Get current context
    const context = {
      project_id: store.currentProject.project_id,
      current_clip_id: store.loadedClips[store.currentCarouselIndex]?.clip_id || null,
      loaded_clips: store.loadedClips.map(c => c.clip_id),
      carousel_index: store.currentCarouselIndex,
      mode: store.mode
    }
    
    ws.send(JSON.stringify({
      type: 'message',
      content,
      context
    }))
  }
  
  return { sendMessage, isThinking, chatHistory }
}
```

---

## Strudel Player Integration

### Using @strudel/web (Headless) ⭐ RECOMMENDED

**Why headless?**
- No editor UI (we have our own CodeMirror editor in carousel)
- Full programmatic control
- Lightweight bundle
- Perfect for custom UI integration

**Installation**:
```bash
npm install @strudel/web
```

**Usage in Svelte Component**:

```svelte
<script lang="ts">
  import { onMount } from 'svelte'
  import { initStrudel, evaluate, hush, samples } from '@strudel/web'
  import { loadedClips, isPlaying } from './stores'
  
  let initialized = false
  
  onMount(async () => {
    // Initialize Strudel
    await initStrudel({
      prebake: async () => {
        // Preload sample packs
        await samples('github:tidalcycles/dirt-samples')
      }
    })
    initialized = true
  })
  
  async function play() {
    if (!initialized) return
    
    // Stack all loaded clips
    const code = $loadedClips.length > 0
      ? `stack(\n${$loadedClips.map(c => `  ${c.code}`).join(',\n')}\n)`
      : 'silence()'
    
    await evaluate(code)
    $isPlaying = true
  }
  
  function stop() {
    hush()
    $isPlaying = false
  }
</script>

<!-- No Strudel UI elements needed - it's headless! -->
<div class="player-controls">
  <button on:click={play} disabled={!initialized}>
    {$isPlaying ? 'Playing...' : 'Play'}
  </button>
  <button on:click={stop} disabled={!$isPlaying}>
    Stop
  </button>
</div>
```

**Key API Functions**:

```typescript
// Initialize (call once)
await initStrudel(options?: {
  prebake?: () => Promise<void>  // Preload samples
})

// Evaluate and play pattern
await evaluate(code: string, autostart?: boolean)

// Stop all patterns
hush()

// Load samples
await samples('github:tidalcycles/dirt-samples')
await samples({ custom: { kick: 'url.wav' } })

// All Strudel pattern functions available:
note('c e g').sound('piano')
stack(pattern1, pattern2, pattern3)
// etc.
```

**Integration Flow**:

```
User edits code in CodeMirror
    ↓
Code saved to loadedClips state
    ↓
User clicks "Update" or agent modifies clip
    ↓
Combine all loadedClips with stack()
    ↓
evaluate(combinedCode)
    ↓
Strudel plays audio via Web Audio API
    ↓
🔊 Sound output
```

**Live Editing Pattern**:

```typescript
// User edits clip in carousel
function onCodeChange(clipIndex: number, newCode: string) {
  // Update state
  updateLoadedClip(clipIndex, newCode)
  
  // Don't auto-update player - wait for user to click "Update"
  // OR implement debounced auto-update for live coding feel
}

// User clicks "Update" button
function onUpdateClick() {
  // Re-evaluate with new code
  play()  // This re-evaluates all clips
}

// OR: Debounced auto-update for live coding
const debouncedUpdate = debounce(() => {
  if (isPlaying) {
    play()  // Re-evaluate while playing
  }
}, 500)

function onCodeChange(clipIndex: number, newCode: string) {
  updateLoadedClip(clipIndex, newCode)
  debouncedUpdate()
}
```

**Alternative: Manual Integration** (if @strudel/web doesn't exist)

```bash
npm install @strudel/core @strudel/webaudio @strudel/transpiler
```

```typescript
import { repl } from '@strudel/core'
import { webaudioOutput, getAudioContext } from '@strudel/webaudio'
import { transpiler } from '@strudel/transpiler'

const ctx = getAudioContext()
const replInstance = repl({
  defaultOutput: webaudioOutput,
  getTime: () => ctx.currentTime,
  transpiler,
})

// Evaluate
await replInstance.evaluate(code, true)

// Stop
replInstance.scheduler.stop()
```

---

## Mobile-First UI Design

### Layout Breakpoints

```css
/* Mobile (default) */
@media (min-width: 0px) {
  /* Single carousel, bottom controls, drawers overlay */
}

/* Tablet */
@media (min-width: 768px) {
  /* Left drawer can stay open, larger code editor */
}

/* Desktop */
@media (min-width: 1024px) {
  /* Dual carousel option, both drawers open, side-by-side layout */
}
```

### Mobile Layout

```
┌────────────────────────┐
│  [Carousel: Clip Code]  │  ← Swipeable
│                        │
│  sound("bd*4")          │
│    .bank("TR909")       │
│    .gain(0.8)           │
│                        │
├────────────────────────┤
│  [🎤] Message input...  │  ← Voice/text
├────────────────────────┤
│ [☰] [▶] [■] [Update] │  ← Fixed bottom
└────────────────────────┘
```

**Left Drawer** (slides in from left):
```
┌────────────────────┐
│ Projects            │
│ ────────────────── │
│ 🔍 Search...        │
│                    │
│ ● House Project     │  ← Active
│ ○ Techno Jams       │
│                    │
│ [Clips] [Songs] ... │  ← Tabs
└────────────────────┘
```

**Right Drawer** (slides in from right):
```
┌────────────────────┐
│ Chat History        │
│ ────────────────── │
│ You: Make bass...   │
│                    │
│ Agent: I'll add... │
│                    │
│ [Other Chats ▼]    │
└────────────────────┘
```

### Desktop Layout

```
┌─────────┬────────────────────────────────────────────────────────────┬─────────┐
│ Left    │  Carousel 1           Carousel 2          │ Right   │
│ Drawer  │  [Clip 1 Code]        [Clip 3 Code]       │ Drawer  │
│         │                                           │         │
│ Project │  sound("bd*4")        note("c2 e2")       │ Chat    │
│ Clips   │                                           │ History │
│ Songs   │                                           │         │
│ ...     ├──────────────────────────────────────────────┤         │
│         │  [🎤] Message input...                  │         │
├─────────┼────────────────────────────────────────────────────────────┼─────────┤
│         │  [▶] [■] [Update]                        │         │
└─────────┴────────────────────────────────────────────────────────────┴─────────┘
```

---

## Voice Input Flow

### User Experience

1. **User presses mic button**
   - Button shows recording state (pulsing red)
   - Waveform visualization appears in message input area

2. **User speaks**
   - Audio is recorded (WebRTC `MediaRecorder`)
   - Waveform animates based on audio levels

3. **User releases mic button** (or auto-stop after silence)
   - Recording stops
   - Audio file sent to `/api/voice/transcribe`
   - Loading indicator shows

4. **Transcription received**
   - Text appears in message input
   - User can edit before sending
   - OR auto-send if user preference set

5. **Message sent to agent**
   - Normal WebSocket flow continues

### Implementation

```typescript
function VoiceButton() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mediaRecorder = new MediaRecorder(stream)
    const chunks: Blob[] = []
    
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'audio/webm' })
      setAudioBlob(blob)
      transcribe(blob)
    }
    
    mediaRecorder.start()
    mediaRecorderRef.current = mediaRecorder
    setIsRecording(true)
  }
  
  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
    setIsRecording(false)
  }
  
  const transcribe = async (blob: Blob) => {
    const formData = new FormData()
    formData.append('audio', blob, 'recording.webm')
    
    const response = await fetch('/api/voice/transcribe', {
      method: 'POST',
      body: formData
    })
    
    const { text } = await response.json()
    setMessageInput(text)  // Populate message input
  }
  
  return (
    <button
      onMouseDown={startRecording}
      onMouseUp={stopRecording}
      onTouchStart={startRecording}
      onTouchEnd={stopRecording}
      className={isRecording ? 'recording' : ''}
    >
      🎤
    </button>
  )
}
```

---

## Implementation Phases

### Phase 1: Backend Foundation
- [ ] Extract `client.py` from `mcp_server.py`
- [ ] Create `backend/server.py` with basic FastAPI app
- [ ] Implement REST endpoints for Projects, Clips, Songs
- [ ] Move `mcp_server.py` to `backend/` and update imports
- [ ] Test MCP server still works with new structure

### Phase 2: Agent WebSocket
- [ ] Implement `backend/agent_runner.py`
- [ ] Create `backend/websocket.py` with WebSocket handler
- [ ] Integrate agent execution with context passing
- [ ] Test agent streaming and tool execution

### Phase 3: Voice Transcription
- [ ] Add Whisper dependency
- [ ] Implement `backend/whisper_service.py`
- [ ] Create `/api/voice/transcribe` endpoint
- [ ] Test transcription accuracy

### Phase 4: Frontend Scaffold
- [ ] Set up Svelte project with TypeScript + Vite
- [ ] Create basic component structure
- [ ] Set up state management (Zustand)
- [ ] Install Tailwind CSS

### Phase 5: Carousel & Code Editor
- [ ] Implement `Carousel` component with Embla
- [ ] Integrate CodeMirror with JavaScript syntax highlighting
- [ ] Implement lazy loading for clip code
- [ ] Add "add new clip" pane at end of carousel

### Phase 6: Player Integration
- [ ] Install @strudel/web
- [ ] Create `useStrudelPlayer` hook
- [ ] Implement play/stop/update controls
- [ ] Test multi-clip playback with stack()

### Phase 7: Agent Chat UI
- [ ] Create `MessageInput` component with voice button
- [ ] Implement WebSocket connection with `useAgent` hook
- [ ] Add chat history display in right drawer
- [ ] Test streaming responses

### Phase 8: Left Drawer Navigation
- [ ] Implement project/clip/song browsers
- [ ] Add search/filter functionality
- [ ] Implement lazy loading for large lists
- [ ] Add knowledge and packs browsers

### Phase 9: Desktop Enhancements
- [ ] Implement dual carousel layout
- [ ] Add responsive breakpoints
- [ ] Optimize drawer behavior for desktop

### Phase 10: Polish & Testing
- [ ] Mobile UX testing
- [ ] Voice input testing on various devices
- [ ] Performance optimization
- [ ] Error handling and edge cases
- [ ] Documentation

---

## Tech Stack Summary

### Decisions Made

| Component | Choice | Reason |
|-----------|--------|--------|
| Frontend Framework | **Svelte** | Smaller bundle, better mobile performance |
| Code Editor | **CodeMirror** | Lighter than Monaco, mobile-friendly |
| Strudel Integration | **@strudel/web** | Headless, full control, no UI conflicts |
| State Management | **Zustand** | Lightweight, simple API |
| Carousel | **Embla Carousel** | Touch-friendly, performant |
| Styling | **Tailwind CSS** | Rapid development, mobile-first |
| Whisper Model | **base** | Good balance of speed/accuracy |
| Chat Persistence | **LocalStorage** | Simple, no auth needed for MVP |

---

## Next Steps

**Ready to proceed to implementation!**

I recommend starting with **Phase 1** (Backend Foundation) to get the core API working.

Should I create an `implementation.md` with detailed code for Phase 1?
