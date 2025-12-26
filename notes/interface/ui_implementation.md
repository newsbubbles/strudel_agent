# Strudel Agent - Frontend Implementation Plan

**Date**: 2025-12-25  
**Developer**: Shadster (Frontend Agent)  
**Purpose**: Complete frontend implementation roadmap  
**Status**: Ready for implementation  
**Related**: `ui_specification.md`, `tooler_example_analysis.md`, `database_architecture.md`

---

## Technology Decisions

### State Management: **Svelte Stores**

**Rationale**:
- Native to Svelte, zero dependencies
- Simple, reactive, functional design
- Perfect for "simple but not complex" philosophy
- Easy LocalStorage persistence with custom stores
- Writable stores for UI state, derived stores for computed values

**Store Architecture**:
```typescript
// Core stores
carouselStore        // Loaded panels, current index
sessionStore         // Active sessions per panel
webSocketStore       // Connection state, message queue
historyStore         // Chat history per session
playerStore          // Global player state
recentItemsStore     // Recently closed items (LocalStorage)
```

### Component Library: **shadcn-svelte**

**Rationale**:
- Clean, functional, modern design out of the box
- Carousel component built on Embla (exact spec requirement)
- Drawer component for left/right navigation
- All form inputs, buttons are accessible (WCAG AA)
- Copy-paste approach = you own the code
- Easy to customize later for look/feel

**Key Components Used**:
- `Carousel` (Embla-based) - Main interface
- `Drawer` - Left/right navigation
- `Button`, `Input`, `Textarea` - Forms
- `ScrollArea` - Chat history
- `Badge`, `Separator` - UI elements

### Project Structure

```
strudel_agent/
├── backend/              # (Backend dev working here)
│   ├── server.py
│   ├── agent_factory.py
│   └── ...
├── ui/                   # Frontend implementation
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── ui/           # shadcn-svelte components
│   │   │   │   │   ├── carousel/
│   │   │   │   │   ├── drawer/
│   │   │   │   │   ├── button/
│   │   │   │   │   └── ...
│   │   │   │   ├── panels/       # Panel types
│   │   │   │   │   ├── ClipPanel.svelte
│   │   │   │   │   ├── SongPanel.svelte
│   │   │   │   │   ├── PlaylistPanel.svelte
│   │   │   │   │   └── PackPanel.svelte
│   │   │   │   ├── drawers/      # Drawer content
│   │   │   │   │   ├── LeftDrawer.svelte
│   │   │   │   │   └── RightDrawer.svelte
│   │   │   │   ├── player/       # Player controls
│   │   │   │   │   └── GlobalPlayer.svelte
│   │   │   │   └── layout/       # Layout components
│   │   │   │       └── MainLayout.svelte
│   │   │   ├── stores/           # State management
│   │   │   │   ├── carousel.ts
│   │   │   │   ├── session.ts
│   │   │   │   ├── websocket.ts
│   │   │   │   ├── history.ts
│   │   │   │   ├── player.ts
│   │   │   │   └── recent.ts
│   │   │   ├── services/         # External integrations
│   │   │   │   ├── websocket.ts  # WebSocket client
│   │   │   │   ├── api.ts        # REST API client
│   │   │   │   └── strudel.ts    # @strudel/web integration
│   │   │   ├── types/            # TypeScript definitions
│   │   │   │   ├── panel.ts
│   │   │   │   ├── session.ts
│   │   │   │   ├── message.ts
│   │   │   │   ├── websocket.ts
│   │   │   │   └── strudel.ts
│   │   │   └── utils/            # Helpers
│   │   │       ├── cn.ts         # Tailwind class merger
│   │   │       └── storage.ts    # LocalStorage helpers
│   │   ├── routes/               # SvelteKit routes
│   │   │   └── +page.svelte      # Main app page
│   │   └── app.css               # Tailwind + global styles
│   ├── static/                   # Static assets
│   ├── package.json
│   ├── vite.config.ts
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
└── notes/
    └── interface/
        └── ui_implementation.md  # This file
```

---

## Implementation Phases

### Phase 1: Project Setup ✅
**Goal**: Scaffold Svelte project with all dependencies

**Tasks**:
1. Initialize SvelteKit project with TypeScript
2. Install shadcn-svelte CLI and components
3. Configure Tailwind CSS
4. Set up base folder structure
5. Install dependencies:
   - `@strudel/web` - Strudel player
   - `codemirror` - Code editor
   - `@codemirror/lang-javascript` - JS syntax highlighting
   - Socket client (native WebSocket API)

**Deliverable**: Empty project with all tooling ready

---

### Phase 2: Type Definitions 📝
**Goal**: Define all TypeScript interfaces for type safety

**Files to create**:

#### `src/lib/types/panel.ts`
```typescript
export type PanelType = 'clip' | 'song' | 'playlist' | 'pack';

export interface PanelId {
  type: PanelType;
  itemId: string;
}

export interface BasePanel {
  id: string;              // "clip:kick"
  type: PanelType;
  itemId: string;          // "kick"
  sessionId: string;       // "session_abc123"
  isDirty: boolean;
  lastModified: Date;
}

export interface ClipPanel extends BasePanel {
  type: 'clip';
  data: {
    code: string;
    filename: string;
  };
}

export interface SongPanel extends BasePanel {
  type: 'song';
  data: {
    markdown: string;
    clipRefs: string[];    // Referenced clip IDs
  };
}

export interface PlaylistPanel extends BasePanel {
  type: 'playlist';
  data: {
    markdown: string;
    songRefs: string[];    // Referenced song IDs
  };
}

export interface PackPanel extends BasePanel {
  type: 'pack';
  data: {
    markdown: string;
    packName: string;
    readonly: true;
  };
}

export type Panel = ClipPanel | SongPanel | PlaylistPanel | PackPanel;
```

#### `src/lib/types/session.ts`
```typescript
export interface Session {
  sessionId: string;
  panelId: string;         // "clip:kick"
  createdAt: Date;
  lastActivity: Date;
  metadata: {
    itemType: string;
    itemId: string;
  };
}
```

#### `src/lib/types/message.ts`
```typescript
export type MessageRole = 'user' | 'agent' | 'system';

export interface Message {
  id: string;
  sessionId: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  index: number;           // For pagination
}

export interface MessageHistory {
  sessionId: string;
  messages: Message[];
  hasMore: boolean;
  oldestIndex: number | null;
}
```

#### `src/lib/types/websocket.ts`
```typescript
// Handshake
export interface HandshakeMessage {
  type: 'handshake';
  session_id: string;
  client_version: string;
}

export interface HandshakeAckMessage {
  type: 'handshake_ack';
  session_id: string;
  is_reconnect: boolean;
}

// User messages
export interface UserMessage {
  type: 'user_message';
  message: string;
}

// Agent responses
export interface AgentResponseMessage {
  type: 'agent_response';
  content: string;
  is_final: boolean;
}

export interface TypingIndicatorMessage {
  type: 'typing_indicator';
  is_typing: boolean;
}

// Tool messages
export interface ToolRequestMessage {
  type: 'tool_request';
  request_id: string;
  tool_name: string;
  parameters: Record<string, any>;
}

export interface ToolResponseMessage {
  type: 'tool_response';
  request_id: string;
  success: boolean;
  data?: any;
  error?: string;
}

export interface ToolReportMessage {
  type: 'tool_report';
  tool_name: string;
}

export interface ToolResultMessage {
  type: 'tool_result';
  tool_name: string;
  content: any;
}

// Strudel-specific updates
export interface ClipUpdatedMessage {
  type: 'clip_updated';
  clip_id: string;
  new_code: string;
}

export interface ClipCreatedMessage {
  type: 'clip_created';
  clip_id: string;
}

export interface SongUpdatedMessage {
  type: 'song_updated';
  song_id: string;
  new_markdown: string;
}

export type WebSocketMessage =
  | HandshakeMessage
  | HandshakeAckMessage
  | UserMessage
  | AgentResponseMessage
  | TypingIndicatorMessage
  | ToolRequestMessage
  | ToolResponseMessage
  | ToolReportMessage
  | ToolResultMessage
  | ClipUpdatedMessage
  | ClipCreatedMessage
  | SongUpdatedMessage;
```

#### `src/lib/types/strudel.ts`
```typescript
// @strudel/web types (simplified)
export interface StrudelPlayer {
  setCode: (code: string) => void;
  start: () => void;
  stop: () => void;
  isPlaying: () => boolean;
}

export interface StrudelOptions {
  prebake: boolean;
  autostart: boolean;
}
```

**Deliverable**: Complete type safety across the app

---

### Phase 3: Store Architecture 🏪
**Goal**: Implement Svelte stores for state management

#### `src/lib/stores/carousel.ts`
```typescript
import { writable, derived } from 'svelte/store';
import type { Panel } from '$lib/types/panel';

interface CarouselState {
  panels: Panel[];
  currentIndex: number;
}

function createCarouselStore() {
  const { subscribe, set, update } = writable<CarouselState>({
    panels: [],
    currentIndex: 0
  });

  return {
    subscribe,
    
    // Load a panel into carousel
    loadPanel: (panel: Panel) => {
      update(state => {
        // Check if already loaded
        const existingIndex = state.panels.findIndex(p => p.id === panel.id);
        if (existingIndex !== -1) {
          // Jump to existing panel
          return { ...state, currentIndex: existingIndex };
        }
        // Add new panel
        return {
          panels: [...state.panels, panel],
          currentIndex: state.panels.length
        };
      });
    },
    
    // Close a panel
    closePanel: (panelId: string) => {
      update(state => {
        const index = state.panels.findIndex(p => p.id === panelId);
        if (index === -1) return state;
        
        const newPanels = state.panels.filter(p => p.id !== panelId);
        const newIndex = Math.min(state.currentIndex, newPanels.length - 1);
        
        return {
          panels: newPanels,
          currentIndex: Math.max(0, newIndex)
        };
      });
    },
    
    // Update panel data
    updatePanel: (panelId: string, updates: Partial<Panel>) => {
      update(state => ({
        ...state,
        panels: state.panels.map(p => 
          p.id === panelId ? { ...p, ...updates, isDirty: true } : p
        )
      }));
    },
    
    // Navigate to panel
    goToPanel: (index: number) => {
      update(state => ({ ...state, currentIndex: index }));
    },
    
    // Get current panel
    getCurrentPanel: derived(
      { subscribe },
      $state => $state.panels[$state.currentIndex] || null
    )
  };
}

export const carouselStore = createCarouselStore();
export const currentPanel = derived(
  carouselStore,
  $carousel => $carousel.panels[$carousel.currentIndex] || null
);
```

#### `src/lib/stores/session.ts`
```typescript
import { writable } from 'svelte/store';
import type { Session } from '$lib/types/session';

interface SessionState {
  sessions: Map<string, Session>; // panelId -> Session
}

function createSessionStore() {
  const { subscribe, set, update } = writable<SessionState>({
    sessions: new Map()
  });

  return {
    subscribe,
    
    // Create or get session for panel
    getOrCreateSession: (panelId: string, itemType: string, itemId: string): Session => {
      let session: Session;
      
      update(state => {
        if (state.sessions.has(panelId)) {
          session = state.sessions.get(panelId)!;
        } else {
          session = {
            sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            panelId,
            createdAt: new Date(),
            lastActivity: new Date(),
            metadata: { itemType, itemId }
          };
          state.sessions.set(panelId, session);
        }
        return state;
      });
      
      return session!;
    },
    
    // Remove session
    removeSession: (panelId: string) => {
      update(state => {
        state.sessions.delete(panelId);
        return state;
      });
    },
    
    // Update last activity
    touchSession: (panelId: string) => {
      update(state => {
        const session = state.sessions.get(panelId);
        if (session) {
          session.lastActivity = new Date();
        }
        return state;
      });
    }
  };
}

export const sessionStore = createSessionStore();
```

#### `src/lib/stores/websocket.ts`
```typescript
import { writable } from 'svelte/store';
import type { WebSocketMessage } from '$lib/types/websocket';

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

interface WebSocketState {
  state: ConnectionState;
  error: string | null;
  messageQueue: WebSocketMessage[];
}

function createWebSocketStore() {
  const { subscribe, set, update } = writable<WebSocketState>({
    state: 'disconnected',
    error: null,
    messageQueue: []
  });

  return {
    subscribe,
    
    setState: (state: ConnectionState, error: string | null = null) => {
      update(s => ({ ...s, state, error }));
    },
    
    queueMessage: (message: WebSocketMessage) => {
      update(s => ({
        ...s,
        messageQueue: [...s.messageQueue, message]
      }));
    },
    
    clearQueue: () => {
      update(s => ({ ...s, messageQueue: [] }));
    }
  };
}

export const webSocketStore = createWebSocketStore();
```

#### `src/lib/stores/history.ts`
```typescript
import { writable } from 'svelte/store';
import type { Message, MessageHistory } from '$lib/types/message';

interface HistoryState {
  histories: Map<string, MessageHistory>; // sessionId -> MessageHistory
}

function createHistoryStore() {
  const { subscribe, set, update } = writable<HistoryState>({
    histories: new Map()
  });

  return {
    subscribe,
    
    // Add message to history
    addMessage: (sessionId: string, message: Message) => {
      update(state => {
        const history = state.histories.get(sessionId) || {
          sessionId,
          messages: [],
          hasMore: false,
          oldestIndex: null
        };
        
        history.messages.push(message);
        state.histories.set(sessionId, history);
        return state;
      });
    },
    
    // Load older messages (pagination)
    prependMessages: (sessionId: string, messages: Message[], hasMore: boolean) => {
      update(state => {
        const history = state.histories.get(sessionId);
        if (!history) return state;
        
        history.messages = [...messages, ...history.messages];
        history.hasMore = hasMore;
        history.oldestIndex = messages.length > 0 ? messages[0].index : null;
        
        return state;
      });
    },
    
    // Get history for session
    getHistory: (sessionId: string): MessageHistory | null => {
      let result: MessageHistory | null = null;
      subscribe(state => {
        result = state.histories.get(sessionId) || null;
      })();
      return result;
    }
  };
}

export const historyStore = createHistoryStore();
```

#### `src/lib/stores/player.ts`
```typescript
import { writable, derived } from 'svelte/store';
import type { StrudelPlayer } from '$lib/types/strudel';

interface PlayerState {
  isPlaying: boolean;
  player: StrudelPlayer | null;
  loadedClipIds: string[];
}

function createPlayerStore() {
  const { subscribe, set, update } = writable<PlayerState>({
    isPlaying: false,
    player: null,
    loadedClipIds: []
  });

  return {
    subscribe,
    
    setPlayer: (player: StrudelPlayer) => {
      update(s => ({ ...s, player }));
    },
    
    play: () => {
      update(s => {
        s.player?.start();
        return { ...s, isPlaying: true };
      });
    },
    
    stop: () => {
      update(s => {
        s.player?.stop();
        return { ...s, isPlaying: false };
      });
    },
    
    updateCode: (combinedCode: string) => {
      update(s => {
        s.player?.setCode(combinedCode);
        return s;
      });
    }
  };
}

export const playerStore = createPlayerStore();
```

#### `src/lib/stores/recent.ts`
```typescript
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import type { PanelType } from '$lib/types/panel';

interface RecentItem {
  id: string;              // "clip:kick"
  type: PanelType;
  itemId: string;
  closedAt: Date;
}

const STORAGE_KEY = 'strudel_recent_items';
const MAX_RECENT = 20;

function loadFromStorage(): RecentItem[] {
  if (!browser) return [];
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    
    const items = JSON.parse(stored);
    return items.map((item: any) => ({
      ...item,
      closedAt: new Date(item.closedAt)
    }));
  } catch {
    return [];
  }
}

function saveToStorage(items: RecentItem[]) {
  if (!browser) return;
  
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  } catch (e) {
    console.error('Failed to save recent items:', e);
  }
}

function createRecentStore() {
  const { subscribe, set, update } = writable<RecentItem[]>(loadFromStorage());

  return {
    subscribe,
    
    addRecent: (item: RecentItem) => {
      update(items => {
        // Remove if already exists
        const filtered = items.filter(i => i.id !== item.id);
        
        // Add to front
        const updated = [item, ...filtered].slice(0, MAX_RECENT);
        
        saveToStorage(updated);
        return updated;
      });
    },
    
    removeRecent: (itemId: string) => {
      update(items => {
        const updated = items.filter(i => i.id !== itemId);
        saveToStorage(updated);
        return updated;
      });
    },
    
    clearRecent: () => {
      set([]);
      saveToStorage([]);
    }
  };
}

export const recentStore = createRecentStore();
```

**Deliverable**: Complete state management with LocalStorage persistence

---

### Phase 4: WebSocket Service 🔌
**Goal**: Implement WebSocket client with event handling

#### `src/lib/services/websocket.ts`
```typescript
import { webSocketStore } from '$lib/stores/websocket';
import { historyStore } from '$lib/stores/history';
import { carouselStore } from '$lib/stores/carousel';
import type { WebSocketMessage } from '$lib/types/websocket';

type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private currentSessionId: string | null = null;
  
  constructor(private url: string) {}
  
  connect(sessionId: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }
    
    this.currentSessionId = sessionId;
    webSocketStore.setState('connecting');
    
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => this.handleOpen();
      this.ws.onmessage = (event) => this.handleMessage(event);
      this.ws.onerror = (error) => this.handleError(error);
      this.ws.onclose = () => this.handleClose();
    } catch (error) {
      webSocketStore.setState('error', error.message);
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    webSocketStore.setState('disconnected');
  }
  
  send(message: WebSocketMessage) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket not connected');
      webSocketStore.queueMessage(message);
    }
  }
  
  on(messageType: string, handler: MessageHandler) {
    if (!this.handlers.has(messageType)) {
      this.handlers.set(messageType, []);
    }
    this.handlers.get(messageType)!.push(handler);
  }
  
  off(messageType: string, handler: MessageHandler) {
    const handlers = this.handlers.get(messageType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }
  
  private handleOpen() {
    console.log('WebSocket connected');
    webSocketStore.setState('connected');
    this.reconnectAttempts = 0;
    
    // Send handshake
    if (this.currentSessionId) {
      this.send({
        type: 'handshake',
        session_id: this.currentSessionId,
        client_version: '1.0.0'
      });
    }
    
    // Send queued messages
    // (Would need to access store value here)
  }
  
  private handleMessage(event: MessageEvent) {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Emit to specific handlers
      const handlers = this.handlers.get(message.type) || [];
      handlers.forEach(handler => handler(message));
      
      // Handle built-in message types
      this.handleBuiltInMessage(message);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }
  
  private handleBuiltInMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'handshake_ack':
        console.log('Handshake acknowledged:', message);
        break;
        
      case 'agent_response':
        // Add to history
        if (this.currentSessionId) {
          historyStore.addMessage(this.currentSessionId, {
            id: `msg_${Date.now()}`,
            sessionId: this.currentSessionId,
            role: 'agent',
            content: message.content,
            timestamp: new Date(),
            index: -1 // Backend will assign proper index
          });
        }
        break;
        
      case 'clip_updated':
        // Update panel in carousel
        carouselStore.updatePanel(`clip:${message.clip_id}`, {
          data: { code: message.new_code }
        } as any);
        break;
        
      case 'song_updated':
        // Update song panel
        carouselStore.updatePanel(`song:${message.song_id}`, {
          data: { markdown: message.new_markdown }
        } as any);
        break;
        
      // Add more handlers as needed
    }
  }
  
  private handleError(error: Event) {
    console.error('WebSocket error:', error);
    webSocketStore.setState('error', 'Connection error');
  }
  
  private handleClose() {
    console.log('WebSocket closed');
    webSocketStore.setState('disconnected');
    
    // Attempt reconnect
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => {
        if (this.currentSessionId) {
          this.connect(this.currentSessionId);
        }
      }, delay);
    }
  }
}

// Singleton instance
export const wsService = new WebSocketService(
  `ws://${window.location.hostname}:8000/ws`
);
```

**Deliverable**: Robust WebSocket client with reconnection logic

---

### Phase 5: API Service 🌐
**Goal**: REST API client for fetching items and history

#### `src/lib/services/api.ts`
```typescript
import type { Panel, ClipPanel, SongPanel, PlaylistPanel, PackPanel } from '$lib/types/panel';
import type { Message } from '$lib/types/message';

const API_BASE = `http://${window.location.hostname}:8000/api`;

class ApiService {
  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers
      }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  // Clips
  async getClip(clipId: string): Promise<ClipPanel['data']> {
    return this.fetch(`/clips/${clipId}`);
  }
  
  async listClips(): Promise<Array<{ id: string; filename: string }>> {
    return this.fetch('/clips');
  }
  
  async updateClip(clipId: string, code: string): Promise<void> {
    return this.fetch(`/clips/${clipId}`, {
      method: 'PUT',
      body: JSON.stringify({ code })
    });
  }
  
  // Songs
  async getSong(songId: string): Promise<SongPanel['data']> {
    return this.fetch(`/songs/${songId}`);
  }
  
  async listSongs(): Promise<Array<{ id: string; title: string }>> {
    return this.fetch('/songs');
  }
  
  // Playlists
  async getPlaylist(playlistId: string): Promise<PlaylistPanel['data']> {
    return this.fetch(`/playlists/${playlistId}`);
  }
  
  async listPlaylists(): Promise<Array<{ id: string; title: string }>> {
    return this.fetch('/playlists');
  }
  
  // Packs
  async getPack(packName: string): Promise<PackPanel['data']> {
    return this.fetch(`/packs/${packName}`);
  }
  
  async listPacks(): Promise<Array<{ name: string; title: string }>> {
    return this.fetch('/packs');
  }
  
  // Messages
  async getMessages(
    sessionId: string,
    beforeIndex?: number,
    limit: number = 50
  ): Promise<{ messages: Message[]; has_more: boolean }> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (beforeIndex !== undefined) {
      params.append('before_index', beforeIndex.toString());
    }
    
    return this.fetch(`/sessions/${sessionId}/messages?${params}`);
  }
}

export const apiService = new ApiService();
```

**Deliverable**: Type-safe API client for all backend endpoints

---

### Phase 6: Strudel Player Integration 🎵
**Goal**: Integrate @strudel/web headless player

#### `src/lib/services/strudel.ts`
```typescript
import { repl } from '@strudel/web';
import type { StrudelPlayer } from '$lib/types/strudel';
import { playerStore } from '$lib/stores/player';
import { carouselStore } from '$lib/stores/carousel';
import { get } from 'svelte/store';

class StrudelService {
  private player: any = null;
  
  async initialize() {
    // Initialize Strudel REPL
    this.player = repl({
      prebake: true,
      autostart: false
    });
    
    // Store player instance
    playerStore.setPlayer({
      setCode: (code: string) => this.player.setCode(code),
      start: () => this.player.start(),
      stop: () => this.player.stop(),
      isPlaying: () => this.player.started
    });
  }
  
  // Combine all loaded clip panels into single code string
  combineClips(): string {
    const carousel = get(carouselStore);
    const clipPanels = carousel.panels.filter(p => p.type === 'clip');
    
    if (clipPanels.length === 0) return '';
    if (clipPanels.length === 1) return (clipPanels[0] as any).data.code;
    
    // Multiple clips: wrap in stack()
    const clipCodes = clipPanels.map(p => (p as any).data.code);
    return `stack(\n${clipCodes.map(code => `  ${code}`).join(',\n')}\n)`;
  }
  
  // Update player with current clips
  updatePlayer() {
    const combinedCode = this.combineClips();
    playerStore.updateCode(combinedCode);
  }
}

export const strudelService = new StrudelService();
```

**Deliverable**: Working Strudel player that combines clips

---

### Phase 7: UI Components - Layout 🎨
**Goal**: Build main layout structure with carousel and drawers

#### Install shadcn-svelte components
```bash
npx shadcn-svelte@latest init
npx shadcn-svelte@latest add carousel
npx shadcn-svelte@latest add drawer
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add input
npx shadcn-svelte@latest add scroll-area
npx shadcn-svelte@latest add separator
npx shadcn-svelte@latest add badge
```

#### `src/lib/components/layout/MainLayout.svelte`
```svelte
<script lang="ts">
  import { Drawer } from '$lib/components/ui/drawer';
  import { Carousel } from '$lib/components/ui/carousel';
  import LeftDrawer from '$lib/components/drawers/LeftDrawer.svelte';
  import RightDrawer from '$lib/components/drawers/RightDrawer.svelte';
  import GlobalPlayer from '$lib/components/player/GlobalPlayer.svelte';
  import PanelRenderer from '$lib/components/panels/PanelRenderer.svelte';
  import { carouselStore } from '$lib/stores/carousel';
  
  let leftDrawerOpen = false;
  let rightDrawerOpen = false;
  
  $: panels = $carouselStore.panels;
  $: currentIndex = $carouselStore.currentIndex;
</script>

<div class="flex h-screen w-screen overflow-hidden">
  <!-- Left Drawer -->
  <Drawer bind:open={leftDrawerOpen} side="left">
    <LeftDrawer />
  </Drawer>
  
  <!-- Main Content Area -->
  <div class="flex-1 flex flex-col">
    <!-- Carousel -->
    <div class="flex-1 overflow-hidden">
      {#if panels.length === 0}
        <div class="flex items-center justify-center h-full text-muted-foreground">
          <p>No items loaded. Open the left drawer to browse.</p>
        </div>
      {:else}
        <Carousel 
          bind:currentIndex={currentIndex}
          class="h-full"
        >
          {#each panels as panel (panel.id)}
            <div class="h-full">
              <PanelRenderer {panel} />
            </div>
          {/each}
        </Carousel>
      {/if}
    </div>
    
    <!-- Global Player Controls -->
    <GlobalPlayer />
  </div>
  
  <!-- Right Drawer -->
  <Drawer bind:open={rightDrawerOpen} side="right">
    <RightDrawer />
  </Drawer>
  
  <!-- Drawer Toggle Buttons -->
  <button 
    class="fixed left-4 top-4 z-50"
    on:click={() => leftDrawerOpen = !leftDrawerOpen}
  >
    ☰
  </button>
  
  <button 
    class="fixed right-4 top-4 z-50"
    on:click={() => rightDrawerOpen = !rightDrawerOpen}
  >
    💬
  </button>
</div>
```

**Deliverable**: Functional layout with drawer navigation

---

### Phase 8: Panel Components 📄
**Goal**: Build panel types (Clip, Song, Playlist, Pack)

#### `src/lib/components/panels/PanelRenderer.svelte`
```svelte
<script lang="ts">
  import type { Panel } from '$lib/types/panel';
  import ClipPanel from './ClipPanel.svelte';
  import SongPanel from './SongPanel.svelte';
  import PlaylistPanel from './PlaylistPanel.svelte';
  import PackPanel from './PackPanel.svelte';
  
  export let panel: Panel;
</script>

{#if panel.type === 'clip'}
  <ClipPanel panel={panel} />
{:else if panel.type === 'song'}
  <SongPanel panel={panel} />
{:else if panel.type === 'playlist'}
  <PlaylistPanel panel={panel} />
{:else if panel.type === 'pack'}
  <PackPanel panel={panel} />
{/if}
```

#### `src/lib/components/panels/ClipPanel.svelte`
```svelte
<script lang="ts">
  import type { ClipPanel } from '$lib/types/panel';
  import { Input } from '$lib/components/ui/input';
  import { Button } from '$lib/components/ui/button';
  import CodeEditor from './CodeEditor.svelte';
  import MessageInput from './MessageInput.svelte';
  import { carouselStore } from '$lib/stores/carousel';
  import { apiService } from '$lib/services/api';
  
  export let panel: ClipPanel;
  
  let code = panel.data.code;
  
  // Update code in store when edited
  function handleCodeChange(newCode: string) {
    code = newCode;
    carouselStore.updatePanel(panel.id, {
      data: { ...panel.data, code: newCode }
    } as any);
  }
  
  // Save to backend
  async function handleSave() {
    await apiService.updateClip(panel.itemId, code);
    carouselStore.updatePanel(panel.id, { isDirty: false } as any);
  }
</script>

<div class="flex flex-col h-full p-4">
  <!-- Header -->
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-lg font-semibold">{panel.data.filename}</h2>
    <div class="flex gap-2">
      {#if panel.isDirty}
        <Button size="sm" on:click={handleSave}>Save</Button>
      {/if}
    </div>
  </div>
  
  <!-- Code Editor -->
  <div class="flex-1 mb-4 border rounded-lg overflow-hidden">
    <CodeEditor 
      value={code} 
      on:change={(e) => handleCodeChange(e.detail)}
    />
  </div>
  
  <!-- Message Input -->
  <MessageInput panelId={panel.id} sessionId={panel.sessionId} />
</div>
```

#### `src/lib/components/panels/CodeEditor.svelte`
```svelte
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { EditorView, basicSetup } from 'codemirror';
  import { javascript } from '@codemirror/lang-javascript';
  
  export let value: string;
  
  const dispatch = createEventDispatcher();
  let editorElement: HTMLDivElement;
  let editorView: EditorView;
  
  onMount(() => {
    editorView = new EditorView({
      doc: value,
      extensions: [
        basicSetup,
        javascript(),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            dispatch('change', update.state.doc.toString());
          }
        })
      ],
      parent: editorElement
    });
    
    return () => {
      editorView.destroy();
    };
  });
  
  // Update editor when value prop changes externally
  $: if (editorView && value !== editorView.state.doc.toString()) {
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: value
      }
    });
  }
</script>

<div bind:this={editorElement} class="h-full"></div>

<style>
  /* CodeMirror styling */
  :global(.cm-editor) {
    height: 100%;
    font-family: 'JetBrains Mono', monospace;
  }
</style>
```

#### `src/lib/components/panels/MessageInput.svelte`
```svelte
<script lang="ts">
  import { Input } from '$lib/components/ui/input';
  import { Button } from '$lib/components/ui/button';
  import { wsService } from '$lib/services/websocket';
  import { historyStore } from '$lib/stores/history';
  
  export let panelId: string;
  export let sessionId: string;
  
  let message = '';
  
  function handleSend() {
    if (!message.trim()) return;
    
    // Add to local history
    historyStore.addMessage(sessionId, {
      id: `msg_${Date.now()}`,
      sessionId,
      role: 'user',
      content: message,
      timestamp: new Date(),
      index: -1
    });
    
    // Send via WebSocket
    wsService.send({
      type: 'user_message',
      message
    });
    
    message = '';
  }
  
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }
</script>

<div class="flex gap-2">
  <Input 
    bind:value={message}
    placeholder="Ask about this clip..."
    on:keydown={handleKeyDown}
    class="flex-1"
  />
  <Button on:click={handleSend}>Send</Button>
</div>
```

**Note**: SongPanel, PlaylistPanel, PackPanel follow similar structure but with appropriate content renderers (markdown viewer, list view, etc.)

**Deliverable**: Working panel components with code editing

---

### Phase 9: Drawer Components 🗂️
**Goal**: Build left drawer (browse) and right drawer (chat history)

#### `src/lib/components/drawers/LeftDrawer.svelte`
```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Badge } from '$lib/components/ui/badge';
  import { ScrollArea } from '$lib/components/ui/scroll-area';
  import { Separator } from '$lib/components/ui/separator';
  import type { PanelType } from '$lib/types/panel';
  import { carouselStore } from '$lib/stores/carousel';
  import { recentStore } from '$lib/stores/recent';
  import { apiService } from '$lib/services/api';
  import { onMount } from 'svelte';
  
  let selectedType: PanelType = 'clip';
  let searchQuery = '';
  let items: Array<{ id: string; label: string }> = [];
  
  $: recentItems = $recentStore.filter(item => item.type === selectedType);
  
  async function loadItems() {
    switch (selectedType) {
      case 'clip':
        const clips = await apiService.listClips();
        items = clips.map(c => ({ id: c.id, label: c.filename }));
        break;
      case 'song':
        const songs = await apiService.listSongs();
        items = songs.map(s => ({ id: s.id, label: s.title }));
        break;
      case 'playlist':
        const playlists = await apiService.listPlaylists();
        items = playlists.map(p => ({ id: p.id, label: p.title }));
        break;
      case 'pack':
        const packs = await apiService.listPacks();
        items = packs.map(p => ({ id: p.name, label: p.title }));
        break;
    }
  }
  
  onMount(() => {
    loadItems();
  });
  
  $: if (selectedType) loadItems();
  
  $: filteredItems = items.filter(item => 
    item.label.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  async function handleItemClick(itemId: string) {
    // Load panel data and add to carousel
    // (Implementation depends on panel type)
    // This is a simplified version
    const panelId = `${selectedType}:${itemId}`;
    
    // Check if already loaded
    const existing = $carouselStore.panels.find(p => p.id === panelId);
    if (existing) {
      const index = $carouselStore.panels.indexOf(existing);
      carouselStore.goToPanel(index);
      return;
    }
    
    // Fetch data and create panel
    // (Simplified - real implementation would fetch proper data)
    const panel = {
      id: panelId,
      type: selectedType,
      itemId: itemId,
      sessionId: `session_${Date.now()}`,
      isDirty: false,
      lastModified: new Date(),
      data: {} // Fetch actual data here
    };
    
    carouselStore.loadPanel(panel as any);
  }
</script>

<div class="flex flex-col h-full w-80 p-4">
  <!-- Type Selector -->
  <div class="flex gap-2 mb-4">
    <Button 
      variant={selectedType === 'clip' ? 'default' : 'outline'}
      size="sm"
      on:click={() => selectedType = 'clip'}
    >
      Clips
    </Button>
    <Button 
      variant={selectedType === 'song' ? 'default' : 'outline'}
      size="sm"
      on:click={() => selectedType = 'song'}
    >
      Songs
    </Button>
    <Button 
      variant={selectedType === 'playlist' ? 'default' : 'outline'}
      size="sm"
      on:click={() => selectedType = 'playlist'}
    >
      Playlists
    </Button>
    <Button 
      variant={selectedType === 'pack' ? 'default' : 'outline'}
      size="sm"
      on:click={() => selectedType = 'pack'}
    >
      Packs
    </Button>
  </div>
  
  <!-- Search -->
  <Input 
    bind:value={searchQuery}
    placeholder="Search {selectedType}s..."
    class="mb-4"
  />
  
  <!-- Recent Items -->
  {#if recentItems.length > 0}
    <div class="mb-4">
      <h3 class="text-sm font-semibold mb-2">Recent</h3>
      <ScrollArea class="h-32">
        {#each recentItems as item}
          <button
            class="w-full text-left p-2 hover:bg-accent rounded-md"
            on:click={() => handleItemClick(item.itemId)}
          >
            {item.itemId}
          </button>
        {/each}
      </ScrollArea>
    </div>
    <Separator class="my-4" />
  {/if}
  
  <!-- All Items -->
  <div class="flex-1 overflow-hidden">
    <h3 class="text-sm font-semibold mb-2">All {selectedType}s</h3>
    <ScrollArea class="h-full">
      {#each filteredItems as item}
        <button
          class="w-full text-left p-2 hover:bg-accent rounded-md"
          on:click={() => handleItemClick(item.id)}
        >
          {item.label}
        </button>
      {/each}
    </ScrollArea>
  </div>
</div>
```

#### `src/lib/components/drawers/RightDrawer.svelte`
```svelte
<script lang="ts">
  import { ScrollArea } from '$lib/components/ui/scroll-area';
  import { Badge } from '$lib/components/ui/badge';
  import { currentPanel } from '$lib/stores/carousel';
  import { historyStore } from '$lib/stores/history';
  import { apiService } from '$lib/services/api';
  
  $: sessionId = $currentPanel?.sessionId;
  $: history = sessionId ? $historyStore.histories.get(sessionId) : null;
  
  async function loadOlderMessages() {
    if (!sessionId || !history?.hasMore) return;
    
    const result = await apiService.getMessages(
      sessionId,
      history.oldestIndex || undefined
    );
    
    historyStore.prependMessages(
      sessionId,
      result.messages,
      result.has_more
    );
  }
</script>

<div class="flex flex-col h-full w-80 p-4">
  {#if !$currentPanel}
    <p class="text-muted-foreground">No panel selected</p>
  {:else}
    <div class="mb-4">
      <h3 class="text-sm font-semibold">Chat History</h3>
      <p class="text-xs text-muted-foreground">
        {$currentPanel.type}: {$currentPanel.itemId}
      </p>
    </div>
    
    <ScrollArea class="flex-1">
      {#if history?.hasMore}
        <button 
          class="w-full text-sm text-muted-foreground mb-2"
          on:click={loadOlderMessages}
        >
          Load older messages...
        </button>
      {/if}
      
      {#if history?.messages}
        {#each history.messages as message}
          <div class="mb-4">
            <div class="flex items-center gap-2 mb-1">
              <Badge variant={message.role === 'user' ? 'default' : 'secondary'}>
                {message.role}
              </Badge>
              <span class="text-xs text-muted-foreground">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <p class="text-sm">{message.content}</p>
          </div>
        {/each}
      {:else}
        <p class="text-sm text-muted-foreground">No messages yet</p>
      {/if}
    </ScrollArea>
  {/if}
</div>
```

**Deliverable**: Functional navigation and chat history

---

### Phase 10: Global Player Controls 🎮
**Goal**: Build player UI with play/stop/update buttons

#### `src/lib/components/player/GlobalPlayer.svelte`
```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { playerStore } from '$lib/stores/player';
  import { strudelService } from '$lib/services/strudel';
  import { onMount } from 'svelte';
  
  $: isPlaying = $playerStore.isPlaying;
  
  onMount(async () => {
    await strudelService.initialize();
  });
  
  function handlePlay() {
    strudelService.updatePlayer();
    playerStore.play();
  }
  
  function handleStop() {
    playerStore.stop();
  }
  
  function handleUpdate() {
    strudelService.updatePlayer();
  }
</script>

<div class="border-t p-4 flex items-center justify-center gap-4">
  {#if isPlaying}
    <Button variant="destructive" on:click={handleStop}>
      ■ Stop
    </Button>
  {:else}
    <Button on:click={handlePlay}>
      ▶ Play
    </Button>
  {/if}
  
  <Button variant="outline" on:click={handleUpdate}>
    ↻ Update
  </Button>
</div>
```

**Deliverable**: Working player controls

---

### Phase 11: Main App Integration 🔗
**Goal**: Wire everything together

#### `src/routes/+page.svelte`
```svelte
<script lang="ts">
  import MainLayout from '$lib/components/layout/MainLayout.svelte';
  import { wsService } from '$lib/services/websocket';
  import { onMount, onDestroy } from 'svelte';
  
  onMount(() => {
    // Connect WebSocket
    const sessionId = `session_${Date.now()}`;
    wsService.connect(sessionId);
  });
  
  onDestroy(() => {
    wsService.disconnect();
  });
</script>

<MainLayout />
```

**Deliverable**: Fully integrated application

---

## Testing Strategy 🧪

### Unit Tests
- Store logic (carousel, session, history)
- WebSocket message handling
- API service methods
- Utility functions

### Component Tests
- Panel rendering
- Code editor functionality
- Message input/send
- Drawer navigation

### Integration Tests
- WebSocket connection flow
- Panel load/close lifecycle
- Real-time updates from agent
- Player combining clips

### E2E Tests (Optional)
- Full user workflows
- Multi-panel sessions
- Agent conversation flow

---

## Development Workflow 🔄

### Phase Execution Order
1. **Setup** (Phase 1) - Get project running
2. **Types** (Phase 2) - Define contracts
3. **Stores** (Phase 3) - Build state layer
4. **Services** (Phase 4-6) - External integrations
5. **UI** (Phase 7-10) - Build components
6. **Integration** (Phase 11) - Wire it all together

### Parallel Work with Backend Dev
- Frontend builds UI with mock data initially
- Backend implements API endpoints and WebSocket protocol
- Integration happens in Phase 11
- Use TypeScript interfaces as contract between frontend/backend

### Mock Data Strategy (Until Backend Ready)
```typescript
// src/lib/services/mock-api.ts
export const mockApiService = {
  async getClip(clipId: string) {
    return {
      code: '// Mock clip\nsound("bd").bank("TR909")',
      filename: `${clipId}.js`
    };
  },
  // ... more mocks
};
```

---

## Open Questions / Decisions Needed 🤔

### 1. SvelteKit vs Vite + Svelte?
- **SvelteKit**: Full framework with routing, SSR capability
- **Vite + Svelte**: Lighter, SPA only
- **Recommendation**: SvelteKit (better DX, room to grow)

### 2. Voice Input Implementation?
- Spec mentions voice input (🎤 icon)
- Need Web Speech API integration?
- Or defer to Phase 2 of development?

### 3. Mobile Responsiveness Priority?
- Spec says "mobile-first"
- How much mobile testing before launch?
- Touch gestures for carousel?

### 4. Offline Support?
- LocalStorage for recent items ✅
- Service worker for offline mode?
- Or always-online assumption?

### 5. Authentication?
- No mention in spec
- Single-user assumption?
- Or multi-user with auth later?

---

## Next Steps 🚀

1. **Get approval** on this implementation plan
2. **Create `ui/` folder** in project
3. **Execute Phase 1** (project setup)
4. **Begin Phase 2** (type definitions)
5. **Coordinate with backend dev** on API contracts
6. **Build iteratively** through phases
7. **Test integration** as backend comes online

---

## Notes for Backend Developer 📬

### API Endpoints Needed
```
GET    /api/clips                    # List all clips
GET    /api/clips/:id                # Get clip data
PUT    /api/clips/:id                # Update clip code

GET    /api/songs                    # List all songs
GET    /api/songs/:id                # Get song data

GET    /api/playlists                # List all playlists
GET    /api/playlists/:id            # Get playlist data

GET    /api/packs                    # List all packs
GET    /api/packs/:name              # Get pack documentation

GET    /api/sessions/:id/messages    # Get message history
  ?before_index=N&limit=50           # Pagination params
```

### WebSocket Protocol
See `src/lib/types/websocket.ts` for complete message type definitions.

### Session Management
- Frontend creates session IDs: `session_${timestamp}_${random}`
- Backend should accept and track these IDs
- Each panel gets its own session
- Session metadata includes `itemType` and `itemId`

---

**End of Implementation Plan**
