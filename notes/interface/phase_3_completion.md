# Phase 3: Store Architecture - COMPLETE ✅

**Date**: 2025-12-25  
**Status**: ✅ Complete  
**Next Phase**: Phase 4 - WebSocket Service  

---

## Summary

Successfully implemented comprehensive Svelte store architecture for state management. All stores are fully typed, reactive, and follow Svelte best practices. The `recent` store includes LocalStorage persistence for cross-session availability.

---

## Files Created

### Store Files (8 files)

1. ✅ **`ui/src/lib/stores/carousel.ts`** (~200 lines)
   - Panel carousel state management
   - 12 methods + 4 derived stores
   - Navigation, loading, closing, updating panels

2. ✅ **`ui/src/lib/stores/session.ts`** (~130 lines)
   - Session management per panel
   - 11 methods + 3 derived stores
   - Session lifecycle, status tracking

3. ✅ **`ui/src/lib/stores/websocket.ts`** (~150 lines)
   - WebSocket connection state
   - 10 methods + 7 derived stores
   - Connection tracking, message queueing, reconnection

4. ✅ **`ui/src/lib/stores/history.ts`** (~180 lines)
   - Chat message history per session
   - 13 methods + 2 derived stores
   - Message management, pagination support

5. ✅ **`ui/src/lib/stores/player.ts`** (~220 lines)
   - Global Strudel player state
   - 20 methods + 10 derived stores
   - Playback control, volume, tempo, clip tracking

6. ✅ **`ui/src/lib/stores/recent.ts`** (~200 lines)
   - Recently closed panels with LocalStorage
   - 9 methods + 7 derived stores
   - Persistence, filtering by type and date

7. ✅ **`ui/src/lib/stores/index.ts`** (~50 lines)
   - Barrel export for all stores
   - Convenient single import point

8. ✅ **`ui/src/lib/stores/README.md`** (~550 lines)
   - Comprehensive documentation
   - Usage examples for each store
   - Best practices and testing guidelines

**Total: 8 files, ~1,680 lines of code**

---

## Store Architecture

### 1. **Carousel Store** (`carousel.ts`)

**Purpose**: Manage loaded panels and navigation

**State**:
```typescript
interface CarouselState {
  panels: Panel[];
  currentIndex: number;
}
```

**Key Methods**:
- `loadPanel(panel)` - Load or navigate to panel
- `closePanel(panelId)` - Close panel with index adjustment
- `updatePanel(panelId, updates)` - Update panel data
- `goToPanel(index)` - Navigate to specific index
- `next()` / `previous()` - Navigate with wrapping
- `getPanel(panelId)` - Get panel by ID
- `hasPanel(panelId)` - Check if loaded
- `clear()` - Remove all panels

**Derived Stores**:
- `currentPanel` - Currently visible panel (or null)
- `panelCount` - Number of loaded panels
- `currentIndex` - Current panel index
- `panels` - All panels array

**Features**:
- ✅ Automatic index adjustment on close
- ✅ Navigation wrapping (next/previous)
- ✅ Duplicate prevention (navigates instead)
- ✅ Type-safe panel updates

---

### 2. **Session Store** (`session.ts`)

**Purpose**: Manage chat sessions per panel

**State**:
```typescript
interface SessionState {
  sessions: Map<string, Session>;
}
```

**Key Methods**:
- `getOrCreate(panelId)` - Get or create session
- `get(panelId)` - Get session (returns null if not found)
- `updateStatus(panelId, status, error?)` - Update status
- `updateMetadata(panelId, metadata)` - Update metadata
- `setConnectionId(panelId, connectionId)` - Set WebSocket ID
- `touch(panelId)` - Update last active time
- `remove(panelId)` - Remove session
- `has(panelId)` - Check existence
- `getAll()` - Get all sessions

**Derived Stores**:
- `sessionCount` - Number of sessions
- `activeSessions` - Sessions with status = 'active'
- `errorSessions` - Sessions with status = 'error'

**Features**:
- ✅ On-demand session creation
- ✅ Automatic last active tracking
- ✅ Status and error management
- ✅ WebSocket connection tracking

---

### 3. **WebSocket Store** (`websocket.ts`)

**Purpose**: Manage WebSocket connection state

**State**:
```typescript
interface WSStoreState {
  state: WebSocketState;
  error: string | null;
  messageQueue: ClientMessage[];
  reconnectAttempts: number;
  lastConnectedAt: Date | null;
  lastDisconnectedAt: Date | null;
}
```

**Key Methods**:
- `setState(state, error?)` - Set connection state
- `queueMessage(message)` - Queue message while disconnected
- `clearQueue()` - Clear and return queued messages
- `incrementReconnectAttempts()` - Track reconnection
- `resetReconnectAttempts()` - Reset counter
- `getState()` - Get current state
- `isConnected()` - Check if connected
- `isConnecting()` - Check if connecting

**Derived Stores**:
- `connectionState` - Current state
- `isConnected` - Boolean: connected
- `isConnecting` - Boolean: connecting/reconnecting
- `hasError` - Boolean: error state
- `errorMessage` - Error message string
- `queuedMessageCount` - Number of queued messages
- `reconnectAttempts` - Reconnection count

**Features**:
- ✅ Message queueing while disconnected
- ✅ Reconnection attempt tracking
- ✅ Connection/disconnection timestamps
- ✅ Error state management

---

### 4. **History Store** (`history.ts`)

**Purpose**: Manage chat message history per session

**State**:
```typescript
interface HistoryState {
  histories: Map<string, ChatHistory>;
}
```

**Key Methods**:
- `getOrCreate(sessionId)` - Get or create history
- `get(sessionId)` - Get history (returns null if not found)
- `addMessage(sessionId, message)` - Add single message
- `addMessages(sessionId, messages)` - Add multiple messages
- `prependMessages(sessionId, messages)` - Prepend older (pagination)
- `updateMessage(sessionId, messageId, updates)` - Update message
- `removeMessage(sessionId, messageId)` - Remove message
- `clearHistory(sessionId)` - Clear messages
- `remove(sessionId)` - Remove history entirely
- `getMessageCount(sessionId)` - Get count
- `has(sessionId)` - Check existence
- `getAll()` - Get all histories

**Derived Stores**:
- `totalMessageCount` - Total messages across all sessions
- `sessionWithMessagesCount` - Number of sessions with messages

**Features**:
- ✅ Pagination support (prepend older messages)
- ✅ Message updates (for status changes)
- ✅ Per-session isolation
- ✅ Automatic timestamp tracking

---

### 5. **Player Store** (`player.ts`)

**Purpose**: Manage global Strudel player state

**State**:
```typescript
interface GlobalPlayerState {
  state: PlayerState;
  volume: number;
  cps: number;
  loadedClips: string[];
  combinedPattern?: string;
  error?: string;
}
```

**Key Methods**:
- `setPlayer(player)` - Set player instance
- `getPlayer()` - Get player instance
- `setState(state, error?)` - Set state
- `start()` - Start playback (async)
- `stop()` - Stop playback
- `pause()` - Pause playback
- `resume()` - Resume playback (async)
- `updatePattern(code)` - Update pattern (async)
- `setVolume(volume)` - Set volume (0-1)
- `setCPS(cps)` - Set tempo
- `addClip(clipId)` - Add to loaded clips
- `removeClip(clipId)` - Remove from loaded clips
- `setLoadedClips(clipIds)` - Set all loaded clips
- `clearClips()` - Clear loaded clips
- `getState()` - Get current state
- `isPlaying()` / `isPaused()` / `isStopped()` - State checks
- `dispose()` - Dispose player and reset
- `reset()` - Reset state (keeps instance)

**Derived Stores**:
- `playerState` - Current state
- `isPlaying` - Boolean: playing
- `isPaused` - Boolean: paused
- `isStopped` - Boolean: stopped
- `isLoading` - Boolean: loading
- `hasPlayerError` - Boolean: error
- `volume` - Current volume
- `cps` - Current tempo
- `loadedClips` - Loaded clip IDs
- `loadedClipCount` - Number of loaded clips

**Features**:
- ✅ Async playback control
- ✅ Volume/tempo clamping
- ✅ Clip tracking for combining
- ✅ Error handling
- ✅ Player instance management

---

### 6. **Recent Store** (`recent.ts`)

**Purpose**: Track recently closed panels with LocalStorage persistence

**State**:
```typescript
interface RecentItem {
  id: string;
  type: PanelType;
  title: string;
  closedAt: Date;
  metadata?: Record<string, unknown>;
}

type State = RecentItem[];
```

**Key Methods**:
- `add(item)` - Add recent item (auto-timestamps)
- `remove(itemId)` - Remove item
- `clear()` - Clear all items
- `getByType(type)` - Filter by panel type
- `has(itemId)` - Check existence
- `getMostRecent()` - Get most recent item
- `getRecent(limit)` - Get recent items up to limit
- `refresh()` - Refresh from LocalStorage

**Derived Stores**:
- `recentCount` - Number of recent items
- `recentClips` - Recent clips
- `recentSongs` - Recent songs
- `recentPlaylists` - Recent playlists
- `recentPacks` - Recent packs
- `recentToday` - Items closed today
- `recentThisWeek` - Items closed this week

**Features**:
- ✅ LocalStorage persistence
- ✅ Automatic timestamp on add
- ✅ Duplicate prevention (moves to front)
- ✅ Max 20 items (configurable)
- ✅ Type-based filtering
- ✅ Date-based filtering

---

## Statistics

### Code Metrics

- **Total Lines**: ~1,680
- **Store Files**: 6
- **Derived Stores**: 28
- **Methods Implemented**: 70+
- **LocalStorage Integration**: 1 (recent)
- **Documentation**: Comprehensive README

### Store Coverage

✅ **Carousel Management**: Complete  
✅ **Session Management**: Complete  
✅ **WebSocket State**: Complete  
✅ **Message History**: Complete  
✅ **Player State**: Complete  
✅ **Recent Items**: Complete  
✅ **Barrel Exports**: Complete  
✅ **Documentation**: Complete  

---

## Key Features

### ✅ **Type Safety**

All stores are fully typed with TypeScript:

```typescript
interface CarouselState {
  panels: Panel[];
  currentIndex: number;
}

const { subscribe, set, update } = writable<CarouselState>(initialState);
```

### ✅ **Reactive Derived Stores**

Computed values update automatically:

```typescript
export const currentPanel = derived(
  carousel,
  $carousel => $carousel.panels[$carousel.currentIndex] || null
);
```

### ✅ **LocalStorage Persistence**

Recent items persist across sessions:

```typescript
function loadFromStorage(): RecentItem[] {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : [];
}

function saveToStorage(items: RecentItem[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}
```

### ✅ **Immutable Updates**

All updates return new state objects:

```typescript
update(state => ({
  ...state,
  panels: [...state.panels, newPanel]
}));
```

### ✅ **Comprehensive API**

Each store provides a complete API for its domain:

```typescript
carousel.loadPanel(panel);
carousel.closePanel(panelId);
carousel.updatePanel(panelId, updates);
carousel.next();
carousel.previous();
```

---

## Usage Examples

### Carousel Navigation

```typescript
import { carousel, currentPanel } from '$lib/stores';
import { createClipPanel } from '$lib/types';

// Load panel
const clip = createClipPanel({ id: 'clip-1', title: 'Kick' });
carousel.loadPanel(clip);

// Navigate
carousel.next();
carousel.previous();
carousel.goToPanel(2);

// Update
carousel.updatePanel('clip-1', { title: 'Updated' });

// Close
carousel.closePanel('clip-1');

// Subscribe
$: console.log('Current:', $currentPanel);
```

### Session Management

```typescript
import { sessions, activeSessions } from '$lib/stores';

// Get or create
const session = sessions.getOrCreate('panel-123');

// Update status
sessions.updateStatus('panel-123', 'active');
sessions.updateStatus('panel-123', 'error', 'Connection failed');

// Touch
sessions.touch('panel-123');

// Remove
sessions.remove('panel-123');

// Subscribe
$: console.log('Active:', $activeSessions.length);
```

### WebSocket State

```typescript
import { websocket, isConnected, queuedMessageCount } from '$lib/stores';
import { createPingMessage } from '$lib/types';

// Set state
websocket.setState('connecting');
websocket.setState('connected');
websocket.setState('error', 'Connection refused');

// Queue messages
if (!websocket.isConnected()) {
  websocket.queueMessage(createPingMessage());
}

// Clear queue
if (websocket.isConnected()) {
  const messages = websocket.clearQueue();
  messages.forEach(msg => ws.send(JSON.stringify(msg)));
}

// Subscribe
$: if ($isConnected) console.log('Connected!');
$: console.log('Queued:', $queuedMessageCount);
```

### Message History

```typescript
import { history, totalMessageCount } from '$lib/stores';
import { createUserMessage, createAssistantMessage } from '$lib/types';

// Add messages
history.addMessage('session-1', createUserMessage('session-1', 'Hello'));
history.addMessage('session-1', createAssistantMessage('session-1', 'Hi!'));

// Load older (pagination)
const older = await api.getMessages('session-1', beforeIndex);
history.prependMessages('session-1', older);

// Update message
history.updateMessage('session-1', msgId, { status: 'sent' });

// Subscribe
$: console.log('Total messages:', $totalMessageCount);
```

### Player Control

```typescript
import { player, isPlaying, volume } from '$lib/stores';

// Initialize
await strudelService.initialize();
player.setPlayer(strudelService.getPlayer());

// Control
await player.start();
player.pause();
await player.resume();
player.stop();

// Update pattern
await player.updatePattern('sound("bd").fast(2)');

// Volume/tempo
player.setVolume(0.8);
player.setCPS(0.6);

// Track clips
player.addClip('clip-1');
player.removeClip('clip-1');

// Subscribe
$: if ($isPlaying) console.log('Playing!');
$: console.log('Volume:', $volume);
```

### Recent Items

```typescript
import { recent, recentClips, recentToday } from '$lib/stores';

// Add when closing
recent.add({
  id: 'clip-123',
  type: 'clip',
  title: 'Kick Drum'
});

// Get by type
const clips = recent.getByType('clip');

// Remove
recent.remove('clip-123');

// Subscribe
$: console.log('Recent clips:', $recentClips);
$: console.log('Closed today:', $recentToday.length);
```

---

## Svelte Integration

### Auto-Subscription

Use `$` prefix in Svelte components:

```svelte
<script>
  import { currentPanel, isPlaying } from '$lib/stores';
</script>

{#if $currentPanel}
  <h1>{$currentPanel.title}</h1>
{/if}

{#if $isPlaying}
  <p>Player is running!</p>
{/if}
```

### Reactive Statements

Use `$:` for reactive logic:

```svelte
<script>
  import { currentPanel, sessions } from '$lib/stores';
  
  $: session = $currentPanel 
    ? sessions.getOrCreate($currentPanel.id) 
    : null;
    
  $: console.log('Session:', session);
</script>
```

### Manual Cleanup

For manual subscriptions:

```svelte
<script>
  import { onDestroy } from 'svelte';
  import { carousel } from '$lib/stores';
  
  const unsubscribe = carousel.subscribe(state => {
    console.log('Carousel:', state);
  });
  
  onDestroy(unsubscribe);
</script>
```

---

## Best Practices Implemented

### 1. **Immutable Updates**

```typescript
// Always return new objects
update(state => ({
  ...state,
  panels: [...state.panels, newPanel]
}));
```

### 2. **Type Safety**

```typescript
// Fully typed state and methods
interface CarouselState {
  panels: Panel[];
  currentIndex: number;
}
```

### 3. **Derived Stores**

```typescript
// Computed values
export const currentPanel = derived(
  carousel,
  $carousel => $carousel.panels[$carousel.currentIndex] || null
);
```

### 4. **Clean API**

```typescript
// Intuitive method names
carousel.loadPanel(panel);
carousel.closePanel(panelId);
carousel.next();
```

### 5. **Persistence**

```typescript
// LocalStorage for recent items
function saveToStorage(items: RecentItem[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}
```

---

## What's Next

### Phase 4: WebSocket Service

Now that we have state management, we'll implement the WebSocket client service.

**Files to create**:
1. `ui/src/lib/services/websocket.ts` - WebSocket client
2. `ui/src/lib/services/api.ts` - REST API client
3. `ui/src/lib/services/strudel.ts` - Strudel player integration
4. `ui/src/lib/services/index.ts` - Barrel export

**Estimated time**: 1-1.5 hours  
**Lines of code**: ~500-700  

---

## Technical Decisions

### Svelte Stores vs Redux/Zustand
**Decision**: Use Svelte's built-in stores  
**Reason**: Native to Svelte, zero dependencies, perfect for our needs

### LocalStorage for Recent Items
**Decision**: Persist recent items to LocalStorage  
**Reason**: Cross-session availability, simple implementation

### Derived Stores
**Decision**: Provide derived stores for common computed values  
**Reason**: Automatic reactivity, DRY principle, better performance

### Map for Sessions/Histories
**Decision**: Use `Map<string, T>` for sessions and histories  
**Reason**: O(1) lookups by ID, clean API

### Immutable Updates
**Decision**: Always return new state objects  
**Reason**: Svelte reactivity requirement, prevents bugs

---

## Resources

- **Store Definitions**: `ui/src/lib/stores/`
- **Documentation**: `ui/src/lib/stores/README.md`
- **Implementation Plan**: `notes/interface/ui_implementation.md`
- **Phase 2 Completion**: `notes/interface/phase_2_completion.md`

---

## Success Metrics

✅ **All stores implemented**: Carousel, Session, WebSocket, History, Player, Recent  
✅ **70+ methods**: Complete API for each store  
✅ **28 derived stores**: Computed values for common use cases  
✅ **LocalStorage persistence**: Recent items persist across sessions  
✅ **Type safety**: Full TypeScript coverage  
✅ **Documentation**: Comprehensive README with examples  
✅ **Immutable updates**: All state changes return new objects  
✅ **Clean API**: Intuitive method names and signatures  

**Phase 3 Status**: ✅ **COMPLETE**

---

**Ready for Phase 4!** 🚀
