# Type Definitions

TypeScript type definitions for the Strudel Agent UI.

## Overview

This folder contains all TypeScript interfaces, types, and type utilities used throughout the application. All types are exported through `index.ts` for convenient importing.

## Usage

```typescript
// Import types from the barrel export
import { Panel, Session, Message, createClipPanel } from '$lib/types';

// Use in your code
const panel: Panel = createClipPanel({
  id: 'clip-1',
  title: 'My First Clip',
  code: 'sound("bd").fast(2)'
});
```

## Files

### `panel.ts`

Defines panel types and interfaces:

- **`PanelType`**: Union type of all panel types (`'clip' | 'song' | 'playlist' | 'pack'`)
- **`BasePanel`**: Common properties for all panels
- **`ClipPanel`**: Editable Strudel code panel
- **`SongPanel`**: Markdown content with clip references
- **`PlaylistPanel`**: Collection of songs
- **`PackPanel`**: Read-only documentation
- **`Panel`**: Union type of all panel types

**Type Guards**:
- `isClipPanel(panel)` - Check if panel is a ClipPanel
- `isSongPanel(panel)` - Check if panel is a SongPanel
- `isPlaylistPanel(panel)` - Check if panel is a PlaylistPanel
- `isPackPanel(panel)` - Check if panel is a PackPanel

**Helpers**:
- `createClipPanel(partial)` - Create a new clip panel
- `createSongPanel(partial)` - Create a new song panel
- `createPlaylistPanel(partial)` - Create a new playlist panel
- `createPackPanel(partial)` - Create a new pack panel

### `session.ts`

Defines session management types:

- **`SessionStatus`**: Session state (`'idle' | 'connecting' | 'active' | 'error' | 'closed'`)
- **`Session`**: Active conversation with the agent
- **`SessionWithPanel`**: Session + associated panel data

**Type Guards**:
- `isSessionActive(session)` - Check if session is active
- `isSessionError(session)` - Check if session has an error

**Helpers**:
- `createSession(panelId, sessionId?)` - Create a new session

### `message.ts`

Defines message and chat history types:

- **`MessageRole`**: Who sent the message (`'user' | 'assistant' | 'system'`)
- **`MessageStatus`**: Delivery state (`'pending' | 'sending' | 'sent' | 'error'`)
- **`Message`**: Base message interface
- **`UserMessage`**: Message from user
- **`AssistantMessage`**: Message from AI agent
- **`SystemMessage`**: Automated system message
- **`AnyMessage`**: Union of all message types
- **`ChatHistory`**: Collection of messages for a session

**Type Guards**:
- `isUserMessage(message)` - Check if message is from user
- `isAssistantMessage(message)` - Check if message is from assistant
- `isSystemMessage(message)` - Check if message is a system message

**Helpers**:
- `createUserMessage(sessionId, content, messageId?)` - Create user message
- `createAssistantMessage(sessionId, content, messageId?)` - Create assistant message
- `createSystemMessage(sessionId, content, type?, messageId?)` - Create system message
- `createChatHistory(sessionId)` - Create empty chat history

### `websocket.ts`

Defines WebSocket message protocol:

- **`WebSocketState`**: Connection state (`'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'error'`)
- **`ClientMessageType`**: Message types sent to server
- **`ServerMessageType`**: Message types received from server
- **`ClientMessage`**: Union of all client messages
- **`ServerMessage`**: Union of all server messages
- **`WSMessage`**: Union of all WebSocket messages

**Message Types**:

**Client → Server**:
- `PingMessage` - Heartbeat
- `CreateSessionMessage` - Create new session
- `CloseSessionMessage` - Close session
- `SendMessageMessage` - Send chat message
- `UpdatePanelMessage` - Update panel content
- `DeletePanelMessage` - Delete panel

**Server → Client**:
- `PongMessage` - Heartbeat response
- `SessionCreatedMessage` - Session created confirmation
- `SessionClosedMessage` - Session closed confirmation
- `MessageReceivedMessage` - Message received acknowledgment
- `MessageResponseMessage` - Agent response
- `PanelUpdatedMessage` - Panel updated notification
- `PanelCreatedMessage` - New panel created by agent
- `PanelDeletedMessage` - Panel deleted confirmation
- `ErrorMessage` - Error notification

**Type Guards**:
- `isServerMessage(message)` - Check if message is from server
- `isErrorMessage(message)` - Check if message is an error

**Helpers**:
- `createPingMessage()` - Create ping message
- `createSessionMessage(sessionId, panelId)` - Create session creation message
- `createSendMessage(sessionId, message)` - Create message send message
- `createPanelUpdateMessage(panel)` - Create panel update message

### `strudel.ts`

Defines Strudel player integration types:

- **`PlayerState`**: Player state (`'stopped' | 'playing' | 'paused' | 'loading' | 'error'`)
- **`StrudelPattern`**: Compilable Strudel code
- **`PlayerConfig`**: Player configuration options
- **`StrudelPlayer`**: Player instance interface
- **`GlobalPlayerState`**: Global player state
- **`EvaluationResult`**: Code evaluation result
- **`StrudelGlobal`**: Global Strudel functions from CDN

**Type Guards**:
- `isPlayerActive(state)` - Check if player is active
- `canStartPlayer(state)` - Check if player can be started
- `canStopPlayer(state)` - Check if player can be stopped

**Helpers**:
- `createDefaultPlayerState()` - Create default player state

**Global Types**:
- Extends `Window` interface with Strudel globals (`initStrudel`, `evaluate`, `stack`)

### `index.ts`

Barrel export file that re-exports all types, type guards, and helpers from the other files.

## Type Safety Guidelines

### 1. Use Type Guards

Always use type guards when working with union types:

```typescript
function handlePanel(panel: Panel) {
  if (isClipPanel(panel)) {
    // TypeScript knows panel is ClipPanel here
    console.log(panel.code);
  } else if (isSongPanel(panel)) {
    // TypeScript knows panel is SongPanel here
    console.log(panel.clips);
  }
}
```

### 2. Use Helper Functions

Use helper functions to create objects with correct defaults:

```typescript
// Good - uses helper with defaults
const clip = createClipPanel({
  id: 'clip-1',
  title: 'My Clip'
});

// Avoid - manual object creation
const clip: ClipPanel = {
  id: 'clip-1',
  type: 'clip',
  title: 'My Clip',
  code: '',
  createdAt: new Date(),
  updatedAt: new Date()
};
```

### 3. Avoid `any`

Never use `any` - use proper types or `unknown` with type guards:

```typescript
// Bad
function processMessage(msg: any) {
  console.log(msg.content);
}

// Good
function processMessage(msg: AnyMessage) {
  if (isUserMessage(msg)) {
    console.log(msg.content);
  }
}
```

### 4. Use Discriminated Unions

All union types use discriminated unions (common `type` field):

```typescript
// Panel union is discriminated by 'type' field
type Panel = ClipPanel | SongPanel | PlaylistPanel | PackPanel;

// TypeScript can narrow based on 'type'
function getPanelTitle(panel: Panel): string {
  switch (panel.type) {
    case 'clip':
      return `Clip: ${panel.title}`;
    case 'song':
      return `Song: ${panel.title}`;
    case 'playlist':
      return `Playlist: ${panel.title}`;
    case 'pack':
      return `Pack: ${panel.title}`;
  }
}
```

## Examples

### Creating a Clip Panel

```typescript
import { createClipPanel } from '$lib/types';

const clip = createClipPanel({
  id: crypto.randomUUID(),
  title: 'Kick Drum Pattern',
  code: 'sound("bd").fast(2)',
  tags: ['drums', 'basic']
});
```

### Creating a Session

```typescript
import { createSession } from '$lib/types';

const session = createSession('panel-123');
console.log(session.status); // 'idle'
```

### Creating Messages

```typescript
import { createUserMessage, createAssistantMessage } from '$lib/types';

const userMsg = createUserMessage(
  'session-1',
  'Create a kick drum pattern'
);

const assistantMsg = createAssistantMessage(
  'session-1',
  'Here\'s a kick drum pattern: `sound("bd").fast(2)`'
);
```

### Working with WebSocket Messages

```typescript
import { createSessionMessage, isServerMessage } from '$lib/types';

// Send message to server
const msg = createSessionMessage('session-1', 'panel-1');
webSocket.send(JSON.stringify(msg));

// Handle incoming message
webSocket.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if (isServerMessage(msg)) {
    // Handle server message
    if (msg.type === 'session.created') {
      console.log('Session created:', msg.payload.sessionId);
    }
  }
};
```

### Working with Strudel Player

```typescript
import { createDefaultPlayerState, canStartPlayer } from '$lib/types';

let playerState = createDefaultPlayerState();

if (canStartPlayer(playerState.state)) {
  // Start playback
  playerState = { ...playerState, state: 'playing' };
}
```

## Testing Types

All types should be tested for:

1. **Correct structure** - All required fields present
2. **Type guards work** - Type narrowing functions correctly
3. **Helpers create valid objects** - Helper functions produce valid instances
4. **Discriminated unions** - Union types can be narrowed by discriminator

## Adding New Types

When adding new types:

1. **Create the file** in this directory
2. **Export types and helpers** from the file
3. **Add to `index.ts`** barrel export
4. **Document in this README** with examples
5. **Add type guards** if using union types
6. **Add helper functions** for object creation

## Resources

- **TypeScript Handbook**: https://www.typescriptlang.org/docs/handbook/
- **Discriminated Unions**: https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions
- **Type Guards**: https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates
