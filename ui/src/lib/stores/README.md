# Svelte Stores

State management for the Strudel Agent UI using Svelte's built-in store system.

## Overview

This folder contains all application state stores. Each store manages a specific domain of state and provides a clean API for components to interact with.

## Usage

```typescript
// Import stores from the barrel export
import { carousel, currentPanel, sessions, player } from '$lib/stores';

// Use in Svelte components with $ prefix for auto-subscription
$: currentPanelData = $currentPanel;
$: isPlayerPlaying = $isPlaying;

// Call store methods
carousel.loadPanel(newPanel);
player.start();
sessions.getOrCreate('panel-123');
```

## Files

### `carousel.ts`

Manages the panel carousel state.

**State**:
- `panels: Panel[]` - All loaded panels
- `currentIndex: number` - Index of visible panel

**Methods**:
- `loadPanel(panel)` - Load a panel (or navigate if already loaded)
- `closePanel(panelId)` - Close a panel
- `updatePanel(panelId, updates)` - Update panel data
- `goToPanel(index)` - Navigate to specific panel
- `next()` - Navigate to next panel (wraps)
- `previous()` - Navigate to previous panel (wraps)
- `getPanel(panelId)` - Get panel by ID
- `hasPanel(panelId)` - Check if panel is loaded
- `clear()` - Remove all panels
- `reset()` - Reset to initial state

**Derived Stores**:
- `currentPanel` - The currently visible panel (or null)
- `panelCount` - Number of loaded panels
- `currentIndex` - Current panel index
- `panels` - All panels array

**Example**:
```typescript
import { carousel, currentPanel } from '$lib/stores';
import { createClipPanel } from '$lib/types';

// Load a new panel
const clip = createClipPanel({ id: 'clip-1', title: 'Kick Drum' });
carousel.loadPanel(clip);

// Navigate
carousel.next();
carousel.previous();
carousel.goToPanel(2);

// Update panel
carousel.updatePanel('clip-1', { title: 'Updated Title' });

// Close panel
carousel.closePanel('clip-1');

// Subscribe to current panel
$: console.log('Current panel:', $currentPanel);
```

---

### `session.ts`

Manages chat sessions per panel.

**State**:
- `sessions: Map<string, Session>` - Map of panelId to Session

**Methods**:
- `getOrCreate(panelId)` - Get or create session for panel
- `get(panelId)` - Get session (returns null if not found)
- `updateStatus(panelId, status, error?)` - Update session status
- `updateMetadata(panelId, metadata)` - Update session metadata
- `setConnectionId(panelId, connectionId)` - Set WebSocket connection ID
- `touch(panelId)` - Update last active time
- `remove(panelId)` - Remove session
- `has(panelId)` - Check if session exists
- `getAll()` - Get all sessions
- `clear()` - Remove all sessions
- `reset()` - Reset to initial state

**Derived Stores**:
- `sessionCount` - Number of sessions
- `activeSessions` - Sessions with status = 'active'
- `errorSessions` - Sessions with status = 'error'

**Example**:
```typescript
import { sessions } from '$lib/stores';

// Get or create session
const session = sessions.getOrCreate('panel-123');
console.log('Session ID:', session.id);

// Update status
sessions.updateStatus('panel-123', 'active');
sessions.updateStatus('panel-123', 'error', 'Connection failed');

// Touch session (update last active)
sessions.touch('panel-123');

// Remove when panel closes
sessions.remove('panel-123');

// Subscribe to active sessions
$: console.log('Active sessions:', $activeSessions.length);
```

---

### `websocket.ts`

Manages WebSocket connection state.

**State**:
- `state: WebSocketState` - Connection state
- `error: string | null` - Error message
- `messageQueue: ClientMessage[]` - Queued messages
- `reconnectAttempts: number` - Reconnection attempt count
- `lastConnectedAt: Date | null` - Last connection time
- `lastDisconnectedAt: Date | null` - Last disconnection time

**Methods**:
- `setState(state, error?)` - Set connection state
- `queueMessage(message)` - Queue message while disconnected
- `clearQueue()` - Clear queue and return messages
- `incrementReconnectAttempts()` - Increment reconnect counter
- `resetReconnectAttempts()` - Reset reconnect counter
- `getState()` - Get current state
- `isConnected()` - Check if connected
- `isConnecting()` - Check if connecting
- `clear()` - Clear all state
- `reset()` - Reset to initial state

**Derived Stores**:
- `connectionState` - Current connection state
- `isConnected` - Boolean: connected status
- `isConnecting` - Boolean: connecting status
- `hasError` - Boolean: error status
- `errorMessage` - Error message string
- `queuedMessageCount` - Number of queued messages
- `reconnectAttempts` - Reconnection attempt count

**Example**:
```typescript
import { websocket, isConnected, queuedMessageCount } from '$lib/stores';
import { createPingMessage } from '$lib/types';

// Set connection state
websocket.setState('connecting');
websocket.setState('connected');
websocket.setState('error', 'Connection refused');

// Queue messages while disconnected
if (!websocket.isConnected()) {
  websocket.queueMessage(createPingMessage());
}

// Clear queue when connected
if (websocket.isConnected()) {
  const messages = websocket.clearQueue();
  messages.forEach(msg => ws.send(JSON.stringify(msg)));
}

// Subscribe to connection state
$: if ($isConnected) {
  console.log('WebSocket connected!');
}

$: if ($queuedMessageCount > 0) {
  console.log(`${$queuedMessageCount} messages queued`);
}
```

---

### `history.ts`

Manages chat message history per session.

**State**:
- `histories: Map<string, ChatHistory>` - Map of sessionId to ChatHistory

**Methods**:
- `getOrCreate(sessionId)` - Get or create history for session
- `get(sessionId)` - Get history (returns null if not found)
- `addMessage(sessionId, message)` - Add message to history
- `addMessages(sessionId, messages)` - Add multiple messages
- `prependMessages(sessionId, messages)` - Prepend older messages (pagination)
- `updateMessage(sessionId, messageId, updates)` - Update a message
- `removeMessage(sessionId, messageId)` - Remove a message
- `clearHistory(sessionId)` - Clear session's messages
- `remove(sessionId)` - Remove session history entirely
- `getMessageCount(sessionId)` - Get message count
- `has(sessionId)` - Check if history exists
- `getAll()` - Get all histories
- `clear()` - Remove all histories
- `reset()` - Reset to initial state

**Derived Stores**:
- `totalMessageCount` - Total messages across all sessions
- `sessionWithMessagesCount` - Number of sessions with messages

**Example**:
```typescript
import { history } from '$lib/stores';
import { createUserMessage, createAssistantMessage } from '$lib/types';

// Add messages
const userMsg = createUserMessage('session-1', 'Hello');
history.addMessage('session-1', userMsg);

const assistantMsg = createAssistantMessage('session-1', 'Hi there!');
history.addMessage('session-1', assistantMsg);

// Load older messages (pagination)
const olderMessages = await api.getMessages('session-1', beforeIndex);
history.prependMessages('session-1', olderMessages);

// Update message status
history.updateMessage('session-1', userMsg.id, { status: 'sent' });

// Get history
const chatHistory = history.get('session-1');
console.log('Messages:', chatHistory?.messages);

// Clear history
history.clearHistory('session-1');

// Subscribe to total message count
$: console.log('Total messages:', $totalMessageCount);
```

---

### `player.ts`

Manages global Strudel player state.

**State**:
- `state: PlayerState` - Playback state
- `volume: number` - Volume (0-1)
- `cps: number` - Tempo (cycles per second)
- `loadedClips: string[]` - IDs of loaded clips
- `combinedPattern?: string` - Combined pattern code
- `error?: string` - Error message

**Methods**:
- `setPlayer(player)` - Set player instance
- `getPlayer()` - Get player instance
- `setState(state, error?)` - Set player state
- `start()` - Start playback (async)
- `stop()` - Stop playback
- `pause()` - Pause playback
- `resume()` - Resume playback (async)
- `updatePattern(code)` - Update pattern (async)
- `setVolume(volume)` - Set volume (0-1)
- `setCPS(cps)` - Set tempo
- `addClip(clipId)` - Add clip to loaded list
- `removeClip(clipId)` - Remove clip from loaded list
- `setLoadedClips(clipIds)` - Set all loaded clips
- `clearClips()` - Clear all loaded clips
- `getState()` - Get current state
- `isPlaying()` - Check if playing
- `isPaused()` - Check if paused
- `isStopped()` - Check if stopped
- `dispose()` - Dispose player and reset
- `reset()` - Reset state (keeps player instance)

**Derived Stores**:
- `playerState` - Current player state
- `isPlaying` - Boolean: playing status
- `isPaused` - Boolean: paused status
- `isStopped` - Boolean: stopped status
- `isLoading` - Boolean: loading status
- `hasPlayerError` - Boolean: error status
- `volume` - Current volume
- `cps` - Current tempo
- `loadedClips` - Loaded clip IDs array
- `loadedClipCount` - Number of loaded clips

**Example**:
```typescript
import { player, isPlaying, volume } from '$lib/stores';
import { strudelService } from '$lib/services/strudel';

// Initialize player
await strudelService.initialize();
const playerInstance = strudelService.getPlayer();
player.setPlayer(playerInstance);

// Control playback
await player.start();
player.pause();
await player.resume();
player.stop();

// Update pattern
await player.updatePattern('sound("bd").fast(2)');

// Control volume and tempo
player.setVolume(0.8);
player.setCPS(0.6);

// Track loaded clips
player.addClip('clip-1');
player.addClip('clip-2');
player.removeClip('clip-1');

// Subscribe to player state
$: if ($isPlaying) {
  console.log('Player is playing!');
}

$: console.log('Volume:', $volume);
```

---

### `recent.ts`

Manages recently closed panels with LocalStorage persistence.

**State**:
- Array of `RecentItem` objects

**RecentItem Interface**:
```typescript
interface RecentItem {
  id: string;           // Panel ID
  type: PanelType;      // Panel type
  title: string;        // Display title
  closedAt: Date;       // When closed
  metadata?: Record<string, unknown>;
}
```

**Methods**:
- `add(item)` - Add item to recent (auto-timestamps)
- `remove(itemId)` - Remove item from recent
- `clear()` - Clear all recent items
- `getByType(type)` - Get recent items of specific type
- `has(itemId)` - Check if item is in recent
- `getMostRecent()` - Get most recently closed item
- `getRecent(limit)` - Get recent items up to limit
- `refresh()` - Refresh from LocalStorage

**Derived Stores**:
- `recentCount` - Number of recent items
- `recentClips` - Recent clip panels
- `recentSongs` - Recent song panels
- `recentPlaylists` - Recent playlist panels
- `recentPacks` - Recent pack panels
- `recentToday` - Items closed today
- `recentThisWeek` - Items closed this week

**Example**:
```typescript
import { recent, recentClips, recentToday } from '$lib/stores';

// Add item when panel closes
recent.add({
  id: 'clip-123',
  type: 'clip',
  title: 'Kick Drum',
  metadata: { filename: 'kick.js' }
});

// Get recent clips
const clips = recent.getByType('clip');

// Remove item
recent.remove('clip-123');

// Clear all
recent.clear();

// Subscribe to recent clips
$: console.log('Recent clips:', $recentClips);

$: console.log('Closed today:', $recentToday.length);
```

---

## Store Architecture Patterns

### 1. **Writable Stores**

All stores are created with `writable()` and expose custom methods:

```typescript
function createMyStore() {
  const { subscribe, set, update } = writable(initialState);
  
  return {
    subscribe,
    myMethod: () => update(state => ({ ...state, /* changes */ })),
    // More methods...
  };
}

export const myStore = createMyStore();
```

### 2. **Derived Stores**

Derived stores compute values from base stores:

```typescript
export const currentPanel = derived(
  carousel,
  $carousel => $carousel.panels[$carousel.currentIndex] || null
);
```

### 3. **LocalStorage Persistence**

The `recent` store persists to LocalStorage:

```typescript
// Load on init
const initial = loadFromStorage();

// Save on every change
function saveToStorage(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}
```

### 4. **Type Safety**

All stores are fully typed with TypeScript:

```typescript
interface CarouselState {
  panels: Panel[];
  currentIndex: number;
}

const { subscribe, set, update } = writable<CarouselState>(initialState);
```

---

## Best Practices

### 1. **Auto-subscription in Components**

Use `$` prefix for automatic subscription:

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

### 2. **Reactive Statements**

Use `$:` for reactive updates:

```svelte
<script>
  import { currentPanel, sessions } from '$lib/stores';
  
  $: session = $currentPanel ? sessions.getOrCreate($currentPanel.id) : null;
  $: console.log('Session changed:', session);
</script>
```

### 3. **Cleanup on Component Destroy**

Manual subscriptions need cleanup:

```svelte
<script>
  import { onDestroy } from 'svelte';
  import { carousel } from '$lib/stores';
  
  const unsubscribe = carousel.subscribe(state => {
    console.log('Carousel changed:', state);
  });
  
  onDestroy(unsubscribe);
</script>
```

### 4. **Batch Updates**

Use `update()` for multiple changes:

```typescript
carousel.update(state => ({
  ...state,
  panels: [...state.panels, newPanel],
  currentIndex: state.panels.length
}));
```

### 5. **Avoid Mutations**

Always return new objects:

```typescript
// Bad - mutates state
update(state => {
  state.panels.push(newPanel);
  return state;
});

// Good - returns new state
update(state => ({
  ...state,
  panels: [...state.panels, newPanel]
}));
```

---

## Testing Stores

### Unit Testing

```typescript
import { get } from 'svelte/store';
import { carousel } from './carousel';
import { createClipPanel } from '$lib/types';

test('carousel loads panel', () => {
  const panel = createClipPanel({ id: 'test', title: 'Test' });
  carousel.loadPanel(panel);
  
  const state = get(carousel);
  expect(state.panels).toHaveLength(1);
  expect(state.panels[0].id).toBe('test');
});

test('carousel navigates to existing panel', () => {
  const panel1 = createClipPanel({ id: 'p1', title: 'P1' });
  const panel2 = createClipPanel({ id: 'p2', title: 'P2' });
  
  carousel.loadPanel(panel1);
  carousel.loadPanel(panel2);
  
  // Load panel1 again - should navigate, not duplicate
  carousel.loadPanel(panel1);
  
  const state = get(carousel);
  expect(state.panels).toHaveLength(2);
  expect(state.currentIndex).toBe(0); // Navigated to panel1
});
```

---

## Resources

- **Svelte Stores Docs**: https://svelte.dev/docs/svelte-store
- **SvelteKit Docs**: https://kit.svelte.dev/docs
- **TypeScript + Svelte**: https://svelte.dev/docs/typescript

---

## Adding New Stores

When adding a new store:

1. **Create the file** in this directory
2. **Define the state interface** with TypeScript
3. **Create the store** with `writable()` or `derived()`
4. **Export methods** for state manipulation
5. **Add to `index.ts`** barrel export
6. **Document in this README** with examples
7. **Write tests** for store logic
