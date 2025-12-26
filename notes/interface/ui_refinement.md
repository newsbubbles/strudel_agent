# Strudel Agent Interface - UI Refinement

**Date**: 2025-12-25  
**Topic**: Detailed UI design based on shadcn carousel and drawer patterns  
**Related**: `notes/interface/seed.md`, `notes/interface/investigation.md`, `notes/interface/deeper_design.md`

---

## Core UI Insight

> "Your entire interface is this carousel and some drawers"

**Key Component**: [shadcn/ui Carousel](https://ui.shadcn.com/docs/components/carousel)
- Motion and swipe built on Embla
- Minimal chrome
- Drag-friendly
- Perfect for mobile-first

---

## Main Viewer/Player Structure

### Carousel as Primary Interface

**Each carousel panel contains**:
1. **Code/Player area** - CodeMirror editor with Strudel code
2. **Message input** - Text/voice input for agent (per-panel context)

**Carousel behavior**:
- Swipe/drag to navigate between loaded items
- Think of it like **tabs**, but with swipe navigation
- Each panel = one loaded item (clip, song, playlist, sample pack)

**Visual concept**:
```
┌────────────────────────────────────┐
│  Panel 1: kick.js                  │
│  ┌──────────────────────────────┐  │
│  │ // Kick pattern              │  │
│  │ sound("bd*4")                │  │
│  │   .bank("TR909")             │  │
│  │   .gain(0.8)                 │  │
│  └──────────────────────────────┘  │
│                                    │
│  [🎤] Make this kick punchier...  │
└────────────────────────────────────┘
         ← Swipe to next panel →
```

---

## Session = Single Item

**Critical insight**: Each session is tied to ONE item type:
- Session for a **clip** (e.g., `kick.js`)
- Session for a **song** (e.g., `sunset_groove.md`)
- Session for a **playlist**
- Session for a **sample pack**

**What this means**:
- Chat history is **per-session** (per-item)
- When you switch items, you switch sessions
- Agent context is scoped to current session/item

**Example flow**:
1. User opens `kick.js` clip
   - New session starts for `kick.js`
   - Chat history empty
   - User: "Make this more aggressive"
   - Agent modifies code
   - Chat history saved for `kick.js` session

2. User switches to `bass.js` clip
   - Different session for `bass.js`
   - Different chat history
   - Agent context switches to `bass.js`

3. User returns to `kick.js`
   - Original session restored
   - Chat history still there

---

## Right Drawer - Chat History

**Purpose**: Show chat history for **current session**

**Content**:
- Messages between user and agent
- Scoped to the currently active item (clip/song/playlist/pack)
- Scrollable history

**Behavior**:
- Slides in from right
- Shows only messages for current session
- When user switches carousel panels → chat history updates to that panel's session

**Visual concept**:
```
┌─────────────────────┐
│ Chat: kick.js       │
│ ─────────────────── │
│ You: Make it punch  │
│                     │
│ Agent: I'll boost   │
│ the gain and add... │
│                     │
│ You: Perfect!       │
│                     │
│ [Scroll for more]   │
└─────────────────────┘
```

---

## Left Drawer - Item Browser

**Purpose**: Browse and load items into carousel

**Top section - Type selector**:
```
┌─────────────────────┐
│ [Clip] [Song]       │
│ [Playlist] [Pack]   │  ← Filter by type
└─────────────────────┘
```

**Main section - Recent history + search**:
```
┌─────────────────────┐
│ Recent History      │
│ ─────────────────── │
│ 🎵 kick.js          │  ← Recently closed
│ 🎵 bass.js          │
│ 🎶 sunset_groove    │
│ 📦 dirt_samples     │
│                     │
│ All Clips           │
│ ─────────────────── │
│ 🔍 Search...        │
│                     │
│ 🎵 kick.js          │
│ 🎵 bass.js          │
│ 🎵 hats.js          │
│ [Scroll for more]   │
└─────────────────────┘
```

**Behavior**:
- Click on item → loads into carousel
- If item already loaded → jumps to that panel
- If item not loaded → adds new panel to carousel
- Recent history shows recently **closed** items (easy to reopen)

**Type filtering**:
- Click "Clip" → shows only clips in list
- Click "Song" → shows only songs
- Click "Playlist" → shows only playlists
- Click "Pack" → shows only sample packs

---

## Carousel Panel Types

### 1. Clip Panel

**Contains**:
- Clip metadata (name, tags, tempo, description)
- CodeMirror editor with Strudel code
- Message input for agent

**Session context**:
- `type: "clip"`
- `clip_id: "kick"`
- `project_id: "house_project"`

**Agent capabilities**:
- Modify clip code
- Explain code
- Suggest variations
- Search knowledge base

### 2. Song Panel

**Contains**:
- Song metadata (title, description)
- Markdown editor with song structure
- Links to clips (clickable → loads clip into carousel)
- Message input for agent

**Session context**:
- `type: "song"`
- `song_id: "sunset_groove"`
- `project_id: "house_project"`

**Agent capabilities**:
- Modify song structure
- Add/remove clip references
- Suggest arrangement ideas
- Generate new clips for song

### 3. Playlist Panel

**Contains**:
- Playlist metadata (title, description)
- List of songs (clickable → loads song into carousel)
- Message input for agent

**Session context**:
- `type: "playlist"`
- `playlist_id: "live_set_2024"`
- `project_id: "house_project"`

**Agent capabilities**:
- Modify playlist order
- Add/remove songs
- Suggest transitions
- Generate setlist notes

### 4. Sample Pack Panel

**Contains**:
- Pack documentation (from `known_packs/`)
- Sample list
- Usage examples
- Message input for agent

**Session context**:
- `type: "pack"`
- `pack_name: "dirt_samples"`

**Agent capabilities**:
- Search pack for sounds
- Show usage examples
- Generate code using pack samples
- Explain sample names

---

## Real-time Updates

**Agent has two-way control**:

### Agent → UI Updates

**When agent modifies a clip**:
1. Agent calls `update_clip()` tool
2. Backend saves changes to filesystem
3. WebSocket sends update message to frontend
4. Frontend receives: `{type: "clip_updated", clip_id: "kick", new_code: "..."}`
5. **If clip is loaded in carousel** → update that panel's code in real-time
6. **If clip is not loaded** → no action (will fetch fresh when loaded)

**When agent creates a new clip**:
1. Agent calls `save_new_clip()` tool
2. Backend creates new file
3. WebSocket sends: `{type: "clip_created", clip_id: "new_bass"}`
4. Frontend can optionally auto-load into carousel

**When agent modifies a song**:
1. Agent calls `update_song()` tool
2. Backend saves changes
3. WebSocket sends: `{type: "song_updated", song_id: "sunset_groove", new_body: "..."}`
4. **If song is loaded in carousel** → update that panel's markdown

### UI → Agent Updates

**User edits code in carousel**:
1. User types in CodeMirror
2. Code saved to local state (marked as dirty)
3. User clicks "Update" or "Save" → backend saves
4. OR auto-save after debounce (500ms)

**User sends message to agent**:
1. User types/speaks message in panel's input
2. Message sent via WebSocket with **current panel context**:
   ```json
   {
     "type": "message",
     "content": "Make this more aggressive",
     "context": {
       "session_type": "clip",
       "clip_id": "kick",
       "project_id": "house_project",
       "current_code": "sound(\"bd*4\")...",
       "loaded_panels": ["kick", "bass", "hats"]
     }
   }
   ```
3. Agent receives context and knows exactly what to modify

---

## Carousel State Management

### In-Memory Carousel Set

**Think of carousel like browser tabs**:
- Each panel = one "tab" (one loaded item)
- User can have multiple items loaded at once
- Swipe to switch between them
- Close panels (remove from carousel)
- Reopen from left drawer

**State structure**:
```typescript
interface CarouselState {
  panels: Panel[]  // Ordered list of loaded panels
  currentIndex: number  // Which panel is visible
}

interface Panel {
  id: string  // Unique panel ID (e.g., "clip:kick", "song:sunset_groove")
  type: 'clip' | 'song' | 'playlist' | 'pack'
  itemId: string  // The actual clip_id, song_id, etc.
  sessionId: string  // Unique session ID for chat history
  data: ClipData | SongData | PlaylistData | PackData
  isDirty: boolean  // Has unsaved changes
}
```

**Example carousel state**:
```typescript
{
  panels: [
    {
      id: "clip:kick",
      type: "clip",
      itemId: "kick",
      sessionId: "session_abc123",
      data: { metadata: {...}, code: "sound(...)" },
      isDirty: false
    },
    {
      id: "clip:bass",
      type: "clip",
      itemId: "bass",
      sessionId: "session_def456",
      data: { metadata: {...}, code: "note(...)" },
      isDirty: true
    },
    {
      id: "song:sunset_groove",
      type: "song",
      itemId: "sunset_groove",
      sessionId: "session_ghi789",
      data: { title: "...", body: "..." },
      isDirty: false
    }
  ],
  currentIndex: 1  // Currently viewing "bass" panel
}
```

### Panel Operations

**Load panel** (from left drawer):
```typescript
function loadPanel(type: string, itemId: string) {
  // Check if already loaded
  const existingIndex = panels.findIndex(p => p.id === `${type}:${itemId}`)
  if (existingIndex >= 0) {
    // Already loaded → jump to it
    setCurrentIndex(existingIndex)
    return
  }
  
  // Not loaded → fetch data and add new panel
  const data = await fetchItemData(type, itemId)
  const newPanel = {
    id: `${type}:${itemId}`,
    type,
    itemId,
    sessionId: generateSessionId(),
    data,
    isDirty: false
  }
  
  addPanel(newPanel)
  setCurrentIndex(panels.length)  // Jump to new panel
}
```

**Close panel**:
```typescript
function closePanel(index: number) {
  // If dirty, prompt to save
  if (panels[index].isDirty) {
    const shouldSave = confirm('Save changes?')
    if (shouldSave) await savePanel(index)
  }
  
  // Add to recent history in left drawer
  addToRecentHistory(panels[index])
  
  // Remove from carousel
  removePanel(index)
  
  // Adjust current index if needed
  if (currentIndex >= panels.length) {
    setCurrentIndex(panels.length - 1)
  }
}
```

**Switch panel** (swipe/drag):
```typescript
function switchPanel(newIndex: number) {
  // Update current index
  setCurrentIndex(newIndex)
  
  // Load chat history for new panel's session
  loadChatHistory(panels[newIndex].sessionId)
  
  // Update agent context
  updateAgentContext(panels[newIndex])
}
```

---

## Agent Context Awareness

### Context Sent with Every Message

**When user sends message from a panel**:
```json
{
  "type": "message",
  "content": "Make the bass more aggressive",
  "context": {
    // Current panel info
    "session_type": "clip",
    "session_id": "session_def456",
    "item_id": "bass",
    "project_id": "house_project",
    
    // Current panel data
    "current_code": "note(\"c2 ~ c2 ~\").sound(\"sawtooth\").lpf(800)",
    "metadata": {
      "name": "Main Bass",
      "tags": ["bass", "techno"],
      "tempo": 130
    },
    
    // All loaded panels (for cross-referencing)
    "loaded_panels": [
      {"type": "clip", "id": "kick"},
      {"type": "clip", "id": "bass"},  // ← Current
      {"type": "song", "id": "sunset_groove"}
    ],
    
    // Current carousel position
    "carousel_index": 1
  }
}
```

**Agent knows**:
- What type of item user is working on (clip, song, playlist, pack)
- The exact item ID
- Current code/content
- What other items are loaded
- Full chat history for this session

**Agent can**:
- Modify current item
- Reference other loaded items
- Create new items and load them into carousel
- Update multiple panels at once

---

## Message Input Per-Panel

**Each carousel panel has its own message input**:

**Why?**
- Context is clear (message always about current panel)
- No ambiguity about what user is asking
- Session history stays with the panel

**Visual placement**:
```
┌────────────────────────────────────┐
│  Panel: bass.js                    │
│  ┌──────────────────────────────┐  │
│  │ note("c2 ~ c2 ~")            │  │
│  │   .sound("sawtooth")         │  │
│  │   .lpf(800)                  │  │
│  └──────────────────────────────┘  │
│                                    │
│  ┌──────────────────────────────┐  │
│  │ [🎤] Message input...        │  │  ← Per-panel
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

**Behavior**:
- Input always sends message in context of current panel
- When user swipes to different panel → input context switches
- Chat history in right drawer updates to match current panel

---

## Player Integration with Carousel

### Multi-Clip Playback

**When user has multiple clips loaded**:
1. User loads `kick.js`, `bass.js`, `hats.js` into carousel
2. User clicks "Play" (global control, not per-panel)
3. All loaded **clip** panels are combined:
   ```javascript
   stack(
     sound("bd*4").bank("TR909"),  // kick.js
     note("c2 ~ c2 ~").sound("sawtooth").lpf(800),  // bass.js
     sound("hh*8").gain(0.5)  // hats.js
   )
   ```
4. Strudel evaluates combined code
5. All clips play simultaneously

**When user edits a clip while playing**:
1. User swipes to `bass.js` panel
2. User edits code: changes `lpf(800)` to `lpf(1200)`
3. User clicks "Update" button (per-panel or global)
4. Frontend re-combines all clips and re-evaluates
5. Bass filter changes in real-time

### Song Playback

**When user loads a song panel**:
- Song panel shows markdown structure with clip links
- Clicking a clip link → loads that clip into carousel
- User can then play individual clips or all loaded clips together

**Agent can**:
- Suggest loading specific clips for a song
- Auto-load clips when user opens a song panel
- Modify song structure based on what's playing

---

## Reconciliation with Previous Design

### What Changes

**From previous design**:
- ❌ Single global message input at bottom
- ❌ Carousel only for clips
- ❌ Chat history for entire project

**New design**:
- ✅ Message input per carousel panel
- ✅ Carousel for clips, songs, playlists, AND sample packs
- ✅ Chat history per session (per item)

### What Stays the Same

- ✅ Carousel as primary interface (confirmed)
- ✅ Left drawer for browsing items (confirmed)
- ✅ Right drawer for chat history (confirmed, but per-session now)
- ✅ Real-time updates from agent (confirmed)
- ✅ Lazy loading of items (confirmed)
- ✅ Voice input (confirmed, per-panel now)
- ✅ @strudel/web headless player (confirmed)
- ✅ shadcn/ui carousel component (confirmed)
- ✅ Embla Carousel foundation (confirmed)

### Backend Implications (Light Notes)

**Session management**:
- Need to track chat history per session ID
- Session ID = unique identifier for each item instance
- When item reopened from recent history → restore session

**WebSocket context**:
- Each message includes session context
- Agent responses tagged with session ID
- Frontend routes responses to correct panel

**Real-time updates**:
- Agent can update any loaded panel
- WebSocket broadcasts updates to all connected clients
- Frontend applies updates to matching panels

---

## Open Questions

### 1. Global vs. Per-Panel Player Controls

**Option A: Global controls** (one Play/Stop for all clips)
- User clicks Play → all loaded clips play together
- User clicks Stop → everything stops
- Simple, clear

**Option B: Per-panel controls** (each panel has own Play/Stop)
- User can play individual clips in isolation
- More complex UI
- More flexible for experimentation

**Recommendation**: Start with **global controls**, add per-panel later if needed

### 2. Recent History Persistence

**Where to store recent history?**
- LocalStorage (browser-based, per-device)
- Backend database (synced across devices)

**Recommendation**: Start with **LocalStorage** for MVP

### 3. Maximum Carousel Panels

**Should there be a limit?**
- Unlimited → could get cluttered
- Limited (e.g., 10 max) → forces cleanup

**Recommendation**: Start **unlimited**, add limit if performance issues

### 4. Auto-Load Clips from Song

**When user opens a song panel, should it auto-load referenced clips?**
- Yes → convenient, but could clutter carousel
- No → user manually loads clips by clicking links

**Recommendation**: **Manual loading** (click links), optional auto-load later

### 5. Cross-Panel Agent Actions

**Can agent modify multiple panels in one response?**
- Example: User asks "Make the whole track more aggressive"
- Agent modifies kick, bass, and hats clips simultaneously
- All three panels update in real-time

**Recommendation**: **Yes, support this** - agent can update multiple panels

---

## Next Steps

**Design is getting clearer!**

Waiting for more notes from you before proceeding. Key areas to clarify:

1. ✅ Carousel as primary interface (confirmed)
2. ✅ Per-panel message input (confirmed)
3. ✅ Per-session chat history (confirmed)
4. ✅ Left drawer type filtering (confirmed)
5. ✅ Recent history in left drawer (confirmed)
6. ✅ Real-time updates (confirmed)
7. ❓ Global vs. per-panel player controls?
8. ❓ Auto-load clips from songs?
9. ❓ Any other UI patterns or behaviors?

**Ready for more brain dumps!** 🧠
