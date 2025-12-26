# Strudel Agent Interface - UI Specification for Frontend Developer

**Date**: 2025-12-25  
**Audience**: Frontend Developer (shadcn agent)  
**Purpose**: Complete UI specification based on design decisions  
**Related**: `notes/interface/seed.md`, `notes/interface/investigation.md`, `notes/interface/deeper_design.md`, `notes/interface/ui_refinement.md`

---

## Overview

This document specifies the complete UI design for the Strudel Agent interface. The design is **carousel-centric** with drawer navigation, built using **shadcn/ui components** on **Embla Carousel**.

**Core principle**: "Your entire interface is this carousel and some drawers"

---

## Technology Stack (Frontend)

- **Framework**: Svelte + TypeScript
- **Component Library**: shadcn/ui (shadcn-svelte)
- **Carousel**: Embla Carousel (via shadcn/ui Carousel component)
- **Code Editor**: CodeMirror with JavaScript syntax highlighting
- **Strudel Player**: @strudel/web (headless)
- **State Management**: Zustand
- **Styling**: Tailwind CSS
- **Icons**: Lucide icons

**Reference**: [shadcn/ui Carousel](https://ui.shadcn.com/docs/components/carousel)

---

## Layout Structure

### Primary Layout

```
┌─────────┬───────────────────────────────────────────────────────┬─────────┐
│         │                                                       │         │
│  Left   │              Carousel (Main Content)                  │  Right  │
│ Drawer  │                                                       │ Drawer  │
│         │  ┌─────────────────────────────────────────────────┐  │         │
│ [Type]  │  │  Panel: kick.js                                 │  │  Chat   │
│ [Type]  │  │  ┌───────────────────────────────────────────┐  │  │ History │
│         │  │  │                                           │  │  │         │
│ Recent  │  │  │  // Kick pattern                          │  │  │ You:    │
│ ────    │  │  │  sound("bd*4")                            │  │  │ Make... │
│ kick.js │  │  │    .bank("TR909")                         │  │  │         │
│ bass.js │  │  │    .gain(0.8)                             │  │  │ Agent:  │
│         │  │  │                                           │  │  │ I'll... │
│ All     │  │  └───────────────────────────────────────────┘  │  │         │
│ ────    │  │                                                 │  │         │
│ 🔍 ...  │  │  [🎤] Make this kick punchier...               │  │         │
│         │  └─────────────────────────────────────────────────┘  │         │
│ kick.js │  ← Swipe to next panel →                             │         │
│ bass.js │                                                       │         │
│ hats.js │  ┌──────────────────────────────────────────────┐    │         │
│         │  │ [▶ Play] [■ Stop] [Update]                   │    │         │
│         │  └──────────────────────────────────────────────┘    │         │
└─────────┴───────────────────────────────────────────────────────┴─────────┘
```

### Mobile Layout

```
┌────────────────────────────┐
│  Carousel Panel            │
│  ┌──────────────────────┐  │
│  │                      │  │
│  │  // Code editor      │  │
│  │  sound("bd*4")       │  │
│  │                      │  │
│  └──────────────────────┘  │
│                            │
│  [🎤] Message input...     │
├────────────────────────────┤
│ [▶] [■] [Update]           │  ← Global player controls
└────────────────────────────┘

[☰] ← Drawer toggle (left)
[💬] ← Drawer toggle (right)
```

---

## Component Hierarchy

```
App
└── Studio (main page)
    ├── LeftDrawer
    │   ├── TypeSelector (Clip/Song/Playlist/Pack buttons)
    │   ├── RecentHistory (recently closed items)
    │   └── ItemBrowser (search + list of all items of selected type)
    │
    ├── MainContent
    │   ├── Carousel (shadcn/ui Carousel component)
    │   │   └── CarouselItem[] (one per loaded panel)
    │   │       ├── PanelHeader (title, metadata)
    │   │       ├── CodeEditor (CodeMirror) OR MarkdownEditor
    │   │       └── MessageInput (text/voice per-panel)
    │   │
    │   └── PlayerControls (global, below carousel)
    │       ├── PlayButton
    │       ├── StopButton
    │       └── UpdateButton
    │
    └── RightDrawer
        └── ChatHistory (messages for current panel's session)
```

---

## Carousel Specification

### Carousel Component

**Use shadcn/ui Carousel component** (built on Embla Carousel)

**Features needed**:
- Swipe/drag navigation
- Keyboard navigation (arrow keys)
- Responsive (mobile-first)
- Smooth transitions
- Support for dynamic panel addition/removal

**Configuration**:
```typescript
// Example Embla options
const carouselOptions = {
  loop: false,
  align: 'start',
  skipSnaps: false,
  dragFree: false
}
```

### Panel Types

Each carousel panel is one of four types:

#### 1. Clip Panel

**Visual structure**:
```
┌─────────────────────────────────────┐
│ kick.js                    [×]      │  ← Header with close button
│ Tags: drums, kick, techno           │
│ Tempo: 130 BPM                      │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │ // Kick pattern               │  │
│  │ sound("bd*4")                 │  │  ← CodeMirror editor
│  │   .bank("TR909")              │  │
│  │   .gain(0.8)                  │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
├─────────────────────────────────────┤
│ [🎤] Make this kick punchier...    │  ← Per-panel message input
└─────────────────────────────────────┘
```

**Data structure**:
```typescript
interface ClipPanel {
  type: 'clip'
  itemId: string  // e.g., "kick"
  sessionId: string
  data: {
    metadata: {
      name: string
      tags: string[]
      tempo: number
      description: string
      media_url?: string  // Background image/video URL
    }
    code: string  // Strudel code
  }
  isDirty: boolean
}
```

**Background media**:
- If `metadata.media_url` exists, display as semi-transparent background
- Image or video (auto-detect from URL)
- Helps visually distinguish panels at a glance
- Code editor has semi-transparent background to show media

#### 2. Song Panel

**Visual structure**:
```
┌─────────────────────────────────────┐
│ Sunset Groove              [×]      │
│ Description: Deep house vibes       │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │ # Sunset Groove               │  │
│  │                               │  │  ← Markdown editor
│  │ ## Intro (0:00 - 0:30)        │  │
│  │ - [kick.js](clip:kick)        │  │  ← Clickable clip links
│  │                               │  │
│  │ ## Build (0:30 - 1:00)        │  │
│  │ - [kick.js](clip:kick)        │  │
│  │ - [bass.js](clip:bass)        │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
├─────────────────────────────────────┤
│ [🎤] Add a breakdown section...    │
└─────────────────────────────────────┘
```

**Data structure**:
```typescript
interface SongPanel {
  type: 'song'
  itemId: string
  sessionId: string
  data: {
    title: string
    description: string
    body: string  // Markdown content
    media_url?: string
  }
  isDirty: boolean
}
```

**Clip link behavior**:
- Links in format: `[clip_name](clip:clip_id)`
- Clicking link → loads that clip into carousel (if not already loaded)
- If already loaded → jumps to that clip panel

#### 3. Playlist Panel

**Visual structure**:
```
┌─────────────────────────────────────┐
│ Live Set 2024                  [×]  │
│ Description: Summer festival set    │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │ # Live Set 2024               │  │
│  │                               │  │  ← Markdown editor
│  │ 1. [Sunset Groove](song:...)  │  │  ← Clickable song links
│  │ 2. [Night Drive](song:...)    │  │
│  │ 3. [Dawn Break](song:...)     │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
├─────────────────────────────────────┤
│ [🎤] Suggest transitions...        │
└─────────────────────────────────────┘
```

**Data structure**:
```typescript
interface PlaylistPanel {
  type: 'playlist'
  itemId: string
  sessionId: string
  data: {
    title: string
    description: string
    body: string  // Markdown with song links
    media_url?: string
  }
  isDirty: boolean
}
```

#### 4. Sample Pack Panel

**Visual structure**:
```
┌─────────────────────────────────────┐
│ dirt_samples                   [×]  │
│ Sample pack documentation           │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │ # Dirt Samples                │  │
│  │                               │  │  ← Markdown viewer (read-only)
│  │ Classic samples from...       │  │
│  │                               │  │
│  │ ## Available samples:         │  │
│  │ - bd (bass drum)              │  │
│  │ - sd (snare drum)             │  │
│  │ - hh (hi-hat)                 │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
├─────────────────────────────────────┤
│ [🎤] Show me kick drum examples... │
└─────────────────────────────────────┘
```

**Data structure**:
```typescript
interface PackPanel {
  type: 'pack'
  itemId: string  // pack name
  sessionId: string
  data: {
    name: string
    documentation: string  // Markdown content (read-only)
  }
  isDirty: false  // Always false (packs are read-only)
}
```

---

## Left Drawer Specification

### Type Selector

**Visual**:
```
┌─────────────────────┐
│ [Clip] [Song]       │  ← Toggle buttons (one active at a time)
│ [Playlist] [Pack]   │
└─────────────────────┘
```

**Behavior**:
- Click button → filters item list to that type
- Active button highlighted
- Default: "Clip" selected

### Recent History

**Visual**:
```
┌─────────────────────┐
│ Recent History      │
│ ─────────────────── │
│ 🎵 kick.js          │  ← Recently closed items
│ 🎵 bass.js          │
│ 🎶 sunset_groove    │
│ 📦 dirt_samples     │
└─────────────────────┘
```

**Behavior**:
- Shows last 10 closed items (any type)
- Click item → loads into carousel
- Icon indicates type (🎵 clip, 🎶 song, 📋 playlist, 📦 pack)

**Storage**: (TO BE PROVIDED - deferred for now)

### Item Browser

**Visual**:
```
┌─────────────────────┐
│ All Clips           │  ← Type label
│ ─────────────────── │
│ 🔍 Search...        │  ← Search input
│                     │
│ 🎵 kick.js          │  ← Filtered list
│ 🎵 bass.js          │
│ 🎵 hats.js          │
│ 🎵 perc_loop.js     │
│ [Scroll for more]   │
└─────────────────────┘
```

**Behavior**:
- Shows all items of selected type (from Type Selector)
- Search filters list in real-time (client-side)
- Click item → loads into carousel
- Lazy loading for large lists (virtualized scrolling)

**Data fetching**:
- Fetch item list from backend API on type change
- Cache results in state
- Refresh on WebSocket events (new item created, item deleted)

---

## Right Drawer Specification

### Chat History

**Visual**:
```
┌─────────────────────┐
│ Chat: kick.js       │  ← Current panel's session
│ ─────────────────── │
│ You: Make it punch  │  ← User message
│                     │
│ Agent: I'll boost   │  ← Agent message (streaming)
│ the gain and add... │
│                     │
│ You: Perfect!       │
│                     │
│ [Scroll for more]   │
└─────────────────────┘
```

**Behavior**:
- Shows chat history for **current carousel panel's session**
- When user swipes to different panel → chat history updates
- Scrolls to bottom on new messages
- Auto-scrolls during agent streaming

**Message types**:
```typescript
interface Message {
  role: 'user' | 'agent'
  content: string
  timestamp: Date
}
```

**Storage**: (TO BE PROVIDED - deferred for now)

---

## Player Controls Specification

### Global Player Controls

**Position**: Below carousel, above bottom of screen (fixed or sticky)

**Visual**:
```
┌──────────────────────────────────────┐
│ [▶ Play] [■ Stop] [🔄 Update]        │
└──────────────────────────────────────┘
```

**Behavior**:

#### Play Button
- Collects all loaded **clip panels**
- Combines code with `stack()`:
  ```javascript
  stack(
    sound("bd*4").bank("TR909"),  // kick.js
    note("c2 ~ c2 ~").sound("sawtooth").lpf(800),  // bass.js
    sound("hh*8").gain(0.5)  // hats.js
  )
  ```
- Evaluates combined code with @strudel/web
- Button changes to "⏸ Pause" or shows playing state

#### Stop Button
- Calls `hush()` to stop all patterns
- Resets play state

#### Update Button
- Re-evaluates all loaded clips
- Used when user edits code manually
- Also triggered automatically on WebSocket updates from agent

**Player integration**: Uses @strudel/web (headless)

---

## State Management

### Global State Structure

```typescript
interface StudioState {
  // Project
  currentProject: {
    project_id: string
    name: string
  } | null
  
  // Carousel
  panels: Panel[]  // Ordered list of loaded panels
  currentPanelIndex: number  // Which panel is visible
  
  // Player
  isPlaying: boolean
  strudelInitialized: boolean
  
  // UI
  leftDrawerOpen: boolean
  rightDrawerOpen: boolean
  selectedType: 'clip' | 'song' | 'playlist' | 'pack'
  
  // Chat (per session)
  chatHistories: Record<string, Message[]>  // sessionId -> messages
}

type Panel = ClipPanel | SongPanel | PlaylistPanel | PackPanel
```

### Panel Operations

**Load panel**:
1. Check if panel already loaded (by `type:itemId`)
2. If yes → jump to that panel index
3. If no → fetch data from API, create panel, add to carousel

**Close panel**:
1. Check if dirty (unsaved changes)
2. If dirty → prompt user to save
3. Add to recent history
4. Remove from panels array
5. Adjust currentPanelIndex if needed

**Switch panel** (on swipe):
1. Update currentPanelIndex
2. Load chat history for new panel's sessionId
3. Update right drawer content

---

## Message Input Specification

### Per-Panel Message Input

**Visual**:
```
┌──────────────────────────────────────┐
│ [🎤] Make this kick punchier...      │  ← Input field
│                          [Send] →    │  ← Send button
└──────────────────────────────────────┘
```

**Features**:
- Text input
- Voice input button (🎤)
- Send button (or Enter key)
- Auto-resize for multi-line input

**Behavior**:
- Input scoped to current panel
- Sends message with full context (see WebSocket section below)
- Clears input after send
- Disables during agent response (streaming)

### Voice Input

**Flow**:
1. User presses/holds 🎤 button
2. Browser requests microphone permission
3. Recording starts (show visual feedback - pulsing icon)
4. User releases button → recording stops
5. Audio sent to backend `/api/voice/transcribe`
6. Transcribed text appears in input field
7. User can edit before sending (or auto-send if preference set)

**Technical**: Uses Web Audio API `MediaRecorder`

---

## Real-time Updates via WebSocket

### WebSocket Connection

**Details**: (TO BE PROVIDED - deferred for now)

**Expected behavior**:
- Frontend connects to WebSocket on app load
- Sends messages with context
- Receives streaming responses from agent
- Receives update events for panels

### Message Context

**When user sends message from a panel**:
```typescript
interface MessageToAgent {
  type: 'message'
  content: string  // User's message
  context: {
    session_type: 'clip' | 'song' | 'playlist' | 'pack'
    session_id: string
    item_id: string
    project_id: string
    current_code?: string  // For clip panels
    current_body?: string  // For song/playlist panels
    metadata: Record<string, any>
    loaded_panels: Array<{
      type: string
      id: string
    }>
    carousel_index: number
  }
}
```

### Update Events from Agent

**Panel update event**:
```typescript
interface PanelUpdateEvent {
  type: 'panel_update'
  panel_type: 'clip' | 'song' | 'playlist'
  item_id: string
  updates: {
    code?: string  // For clips
    body?: string  // For songs/playlists
    metadata?: Record<string, any>
  }
}
```

**Handling**:
1. Frontend receives update event
2. Find panel in carousel by `type:item_id`
3. If found → update panel data in state
4. If panel is currently visible → UI updates immediately
5. Mark panel as clean (not dirty)
6. If playing → trigger re-evaluation (Update button logic)

**Panel creation event**:
```typescript
interface PanelCreateEvent {
  type: 'panel_created'
  panel_type: 'clip' | 'song' | 'playlist'
  item_id: string
  data: ClipData | SongData | PlaylistData
}
```

**Handling**:
1. Add to item browser list (if type matches current filter)
2. Optionally: Auto-load into carousel (TBD)

---

## Background Media (Visual Enhancement)

### Concept

Clips, songs, and playlists can have `media_url` in metadata pointing to:
- Image (jpg, png, gif, webp)
- Video (mp4, webm)

**Purpose**: Visual distinction between panels at a glance

### Implementation

**Panel background**:
```css
.panel {
  position: relative;
  background: url(media_url) center/cover no-repeat;
}

.panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);  /* Dark overlay for readability */
  z-index: 0;
}

.panel-content {
  position: relative;
  z-index: 1;
}
```

**Code editor**:
- Semi-transparent background
- Allows media to show through faintly
- Maintains code readability

**Fallback**: If no `media_url`, use solid background color

---

## Responsive Design

### Mobile (< 768px)

- Carousel takes full width
- Drawers overlay (slide in from sides)
- Player controls fixed at bottom
- Single column layout

### Tablet (768px - 1024px)

- Carousel takes most width
- Left drawer can stay open (side-by-side)
- Right drawer still overlays
- Player controls below carousel

### Desktop (> 1024px)

- Three-column layout (left drawer | carousel | right drawer)
- Both drawers can stay open
- Carousel adapts width
- Optional: Dual carousel (future enhancement)

---

## Deferred Items (To Be Provided Later)

### 1. WebSocket Implementation Details
- Connection setup
- Message protocol
- Reconnection logic
- Error handling

**Status**: Example files will be provided

### 2. Agent Harness Integration
- How agent executes
- How agent sends updates
- Tool execution flow

**Status**: Example files will be provided

### 3. Hooks and State Management Patterns
- Custom hooks structure
- State management best practices
- API client patterns

**Status**: Example files will be provided

### 4. Recent History Storage
- LocalStorage schema
- Persistence logic
- Sync across tabs

**Status**: Example from other project will be provided

### 5. Chat History Storage
- Storage mechanism (LocalStorage vs backend)
- Persistence schema
- Session restoration

**Status**: To be determined after seeing examples

### 6. Maximum Carousel Panels
- Let device memory decide
- No hard limit for now
- Monitor performance, add limit if needed

### 7. Auto-load Clips from Songs
- No auto-load for now
- User manually clicks clip links to load
- Each item type has own "axis" (own view in carousel)
- Carousel component receives array of items for current view

---

## Design Decisions Summary

### Confirmed

1. ✅ **Carousel**: shadcn/ui Carousel (Embla) as primary interface
2. ✅ **Panel types**: Clip, Song, Playlist, Pack
3. ✅ **Sessions**: Per-panel (each panel = one session)
4. ✅ **Message input**: Per-panel (not global)
5. ✅ **Chat history**: Per-session (switches with panels)
6. ✅ **Player controls**: Global (below carousel)
7. ✅ **Left drawer**: Type filter + recent history + search
8. ✅ **Right drawer**: Chat history for current session
9. ✅ **Real-time updates**: Agent can update any loaded panel
10. ✅ **Background media**: Optional image/video in panel background
11. ✅ **Update trigger**: User manual OR auto from WebSocket events
12. ✅ **Cross-panel updates**: Agent can modify multiple panels

### Deferred

1. ⏳ WebSocket protocol details
2. ⏳ Agent harness integration
3. ⏳ Storage mechanisms
4. ⏳ Hooks patterns
5. ⏳ Auto-load behavior
6. ⏳ Panel limits

---

## Next Steps for Frontend Developer

1. **Review this specification** - Understand complete design
2. **Wait for technical examples** - WebSocket, hooks, storage patterns
3. **Set up project structure** - Svelte + shadcn/ui + Tailwind
4. **Implement static layouts** - Carousel, drawers, panels (no data)
5. **Integrate examples** - Once provided, wire up real functionality
6. **Iterate** - Refine based on testing and feedback

---

## Communication Protocol

**Between design agent (me) and frontend agent (you)**:
- All communication via files in `notes/` directory
- Design decisions documented here
- Technical examples to be provided in separate files
- Questions/clarifications via new notes files

**File structure**:
```
notes/interface/
├── seed.md                    # Initial design seed
├── investigation.md           # MCP analysis
├── deeper_design.md           # API + architecture design
├── ui_refinement.md           # UI design refinement
├── ui_specification.md        # This file (complete spec)
└── [future files as needed]
```

---

## End of Specification

This document contains everything the frontend developer needs to understand the UI design. Technical implementation details will be provided separately.

**Design is complete and ready for implementation.**
