# Phase 5: API Service - COMPLETE ✅

**Date**: 2025-12-25  
**Status**: ✅ Complete  
**Next Phase**: Phase 6 - Strudel Player Integration  

---

## Summary

Successfully implemented a type-safe REST API client with comprehensive CRUD operations for sessions, messages, clips, songs, and playlists. Includes error handling, timeout support, and automatic URL detection.

---

## Files Created

### Service Files (2 files)

✅ **`ui/src/lib/services/api.ts`** (~380 lines)
   - Type-safe HTTP client
   - Session management (create, list, delete, update name)
   - Message history with pagination
   - Clip CRUD operations
   - Song CRUD operations
   - Playlist CRUD operations
   - Health check endpoint
   - Error handling with custom APIError class
   - Request timeout support

✅ **`ui/src/lib/services/index.ts`** (~20 lines)
   - Barrel export for all services
   - Type exports

**Total: 2 files, ~400 lines of code**

---

## API Service Architecture

### **Class: `APIService`**

**Purpose**: Type-safe HTTP client for all backend REST API endpoints

**Configuration**:
```typescript
interface APIConfig {
  baseUrl: string;      // Base API URL (auto-detected)
  timeout: number;      // Request timeout in ms (default: 30000)
}
```

**Default Behavior**:
- Auto-detects base URL from `window.location`
- Uses same protocol as frontend (http/https)
- Connects to port 8000 by default
- Example: `http://localhost:8000/api`

---

## Key Features

### ✅ **1. Type-Safe HTTP Client**

**Generic fetch method**:
```typescript
private async fetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T>
```

**Features**:
- Type-safe return values
- Automatic JSON parsing
- Error handling
- Timeout support (30 seconds default)
- Content-Type headers

**Usage**:
```typescript
const clip = await apiService.getClip('project1', 'kick');
// clip is typed as ClipData
```

---

### ✅ **2. Error Handling**

**Custom APIError class**:
```typescript
export class APIError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string
  )
}
```

**Error scenarios**:
- HTTP errors (4xx, 5xx) - Throws APIError with status code
- Network errors - Throws APIError with status 0
- Timeout errors - Throws APIError with 'Timeout' message
- Parse errors - Extracts `detail` from JSON response

**Example**:
```typescript
try {
  const clip = await apiService.getClip('project1', 'nonexistent');
} catch (error) {
  if (error instanceof APIError) {
    console.error(`API Error ${error.status}: ${error.message}`);
    // API Error 404: Clip not found
  }
}
```

---

### ✅ **3. Request Timeout**

**Automatic timeout**:
- Default: 30 seconds
- Uses AbortController
- Throws APIError on timeout

**Code**:
```typescript
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

const response = await fetch(url, {
  ...options,
  signal: controller.signal
});

clearTimeout(timeoutId);
```

**Custom timeout**:
```typescript
const api = new APIService({ timeout: 60000 }); // 60 seconds
```

---

## API Methods

### **Sessions**

#### Create Session
```typescript
async createSession(request: CreateSessionRequest): Promise<SessionResponse>
```

**Request**:
```typescript
interface CreateSessionRequest {
  agent_name: string;           // 'strudel'
  model_name: string;           // 'x-ai/grok-beta'
  provider: string;             // 'openrouter'
  session_type: SessionType;    // 'clip' | 'song' | 'playlist' | 'pack'
  item_id: string;              // ID of item
  project_id: string;           // Project ID
  session_name?: string;        // Optional name
}
```

**Usage**:
```typescript
const session = await apiService.createSession({
  agent_name: 'strudel',
  model_name: 'x-ai/grok-beta',
  provider: 'openrouter',
  session_type: 'clip',
  item_id: 'kick',
  project_id: 'house_project'
});

console.log('Session ID:', session.session_id);
```

---

#### List Sessions
```typescript
async listSessions(filters?: {
  status?: SessionStatus;
  project_id?: string;
}): Promise<SessionResponse[]>
```

**Usage**:
```typescript
// Get all active sessions
const active = await apiService.listSessions({ status: 'active' });

// Get sessions for a project
const projectSessions = await apiService.listSessions({ 
  project_id: 'house_project' 
});

// Get all sessions
const all = await apiService.listSessions();
```

---

#### Delete Session
```typescript
async deleteSession(sessionId: string): Promise<{ success: boolean }>
```

**Usage**:
```typescript
await apiService.deleteSession('session-123');
```

---

#### Update Session Name
```typescript
async updateSessionName(
  sessionId: string,
  name: string | null
): Promise<void>
```

**Usage**:
```typescript
// Set name
await apiService.updateSessionName('session-123', 'My Session');

// Clear name
await apiService.updateSessionName('session-123', null);
```

---

### **Messages**

#### Get Message History
```typescript
async getMessages(
  sessionId: string,
  options?: {
    page_size?: number;
    before_index?: number;
  }
): Promise<MessageHistoryResponse>
```

**Response**:
```typescript
interface MessageHistoryResponse {
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    message_index: number;
  }>;
}
```

**Usage**:
```typescript
// Load initial messages (most recent 50)
const history = await apiService.getMessages('session-123', {
  page_size: 50
});

// Load more (pagination)
const oldestIndex = history.messages[0].message_index;
const older = await apiService.getMessages('session-123', {
  page_size: 50,
  before_index: oldestIndex
});
```

**Pagination Pattern**:
```typescript
let messages = [];
let hasMore = true;

// Initial load
const initial = await apiService.getMessages(sessionId, { page_size: 50 });
messages = initial.messages;

// Load more on scroll
while (hasMore && shouldLoadMore) {
  const oldestIndex = messages[0].message_index;
  const older = await apiService.getMessages(sessionId, {
    page_size: 50,
    before_index: oldestIndex
  });
  
  if (older.messages.length === 0) {
    hasMore = false;
  } else {
    messages = [...older.messages, ...messages];
  }
}
```

---

### **Clips**

#### Create Clip
```typescript
async createClip(
  clip: Omit<ClipData, 'id' | 'created_at' | 'updated_at'>
): Promise<ClipData>
```

**Usage**:
```typescript
const clip = await apiService.createClip({
  clip_id: 'kick',
  project_id: 'house_project',
  name: 'Kick Drum',
  code: 'sound("bd*4").gain(0.8)',
  metadata: {
    bpm: 120,
    tags: ['drums', 'kick']
  }
});
```

---

#### Get Clip
```typescript
async getClip(projectId: string, clipId: string): Promise<ClipData>
```

**Usage**:
```typescript
const clip = await apiService.getClip('house_project', 'kick');
console.log('Clip code:', clip.code);
```

---

#### List Clips
```typescript
async listClips(projectId: string): Promise<ClipData[]>
```

**Usage**:
```typescript
const clips = await apiService.listClips('house_project');
clips.forEach(clip => console.log(clip.name));
```

---

#### Update Clip
```typescript
async updateClip(
  projectId: string,
  clipId: string,
  updates: Partial<Pick<ClipData, 'name' | 'code' | 'metadata'>>
): Promise<ClipData>
```

**Usage**:
```typescript
// Update code only
const updated = await apiService.updateClip('house_project', 'kick', {
  code: 'sound("bd*4").gain(1.2).distort(0.3)'
});

// Update name and metadata
await apiService.updateClip('house_project', 'kick', {
  name: 'Punchy Kick',
  metadata: { bpm: 128 }
});
```

---

#### Delete Clip
```typescript
async deleteClip(
  projectId: string,
  clipId: string
): Promise<{ success: boolean }>
```

**Usage**:
```typescript
await apiService.deleteClip('house_project', 'kick');
```

---

### **Songs**

#### Create Song
```typescript
async createSong(
  song: Omit<SongData, 'id' | 'created_at' | 'updated_at'>
): Promise<SongData>
```

**Usage**:
```typescript
const song = await apiService.createSong({
  song_id: 'house_track',
  project_id: 'house_project',
  name: 'House Track',
  clip_ids: ['kick', 'bass', 'hats'],
  metadata: {
    bpm: 120,
    key: 'C minor'
  }
});
```

---

#### Get/List/Update/Delete Song

Same pattern as clips:
```typescript
getSong(projectId, songId)           // Get single song
listSongs(projectId)                 // List all songs
updateSong(projectId, songId, {...}) // Update song
deleteSong(projectId, songId)        // Delete song
```

**Update example**:
```typescript
// Add a clip to song
const song = await apiService.getSong('house_project', 'house_track');
await apiService.updateSong('house_project', 'house_track', {
  clip_ids: [...song.clip_ids, 'melody']
});
```

---

### **Playlists**

#### Create Playlist
```typescript
async createPlaylist(
  playlist: Omit<PlaylistData, 'id' | 'created_at' | 'updated_at'>
): Promise<PlaylistData>
```

**Usage**:
```typescript
const playlist = await apiService.createPlaylist({
  playlist_id: 'favorites',
  project_id: 'house_project',
  name: 'My Favorites',
  song_ids: ['house_track', 'techno_track']
});
```

---

#### Get/List/Update/Delete Playlist

Same pattern as clips and songs:
```typescript
getPlaylist(projectId, playlistId)           // Get single playlist
listPlaylists(projectId)                     // List all playlists
updatePlaylist(projectId, playlistId, {...}) // Update playlist
deletePlaylist(projectId, playlistId)        // Delete playlist
```

---

### **Health Check**

#### Check API Health
```typescript
async healthCheck(): Promise<{ status: string }>
```

**Usage**:
```typescript
try {
  const health = await apiService.healthCheck();
  console.log('API Status:', health.status);
} catch (error) {
  console.error('API is down');
}
```

---

## Type Definitions

### **ClipData**
```typescript
interface ClipData {
  id?: number;
  clip_id: string;
  project_id: string;
  name: string;
  code: string;
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}
```

### **SongData**
```typescript
interface SongData {
  id?: number;
  song_id: string;
  project_id: string;
  name: string;
  clip_ids: string[];
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}
```

### **PlaylistData**
```typescript
interface PlaylistData {
  id?: number;
  playlist_id: string;
  project_id: string;
  name: string;
  song_ids: string[];
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}
```

### **SessionResponse**
```typescript
interface SessionResponse {
  session_id: string;
  agent_name: string;
  model_name: string;
  provider: string;
  session_type: SessionType;
  item_id: string;
  project_id: string;
  created_at: string;
  last_activity: string;
  status: SessionStatus;
  message_count: number;
  session_name?: string;
}
```

---

## Usage Examples

### **1. Complete Session Flow**

```typescript
import { apiService } from '$lib/services';

// 1. Create session
const session = await apiService.createSession({
  agent_name: 'strudel',
  model_name: 'x-ai/grok-beta',
  provider: 'openrouter',
  session_type: 'clip',
  item_id: 'kick',
  project_id: 'house_project'
});

// 2. Load message history
const history = await apiService.getMessages(session.session_id);

// 3. Get clip data
const clip = await apiService.getClip('house_project', 'kick');

// 4. Update clip name
await apiService.updateSessionName(session.session_id, 'Kick Session');

// 5. Clean up
await apiService.deleteSession(session.session_id);
```

---

### **2. Clip Management**

```typescript
import { apiService } from '$lib/services';

// Create clip
const clip = await apiService.createClip({
  clip_id: 'kick',
  project_id: 'house_project',
  name: 'Kick Drum',
  code: 'sound("bd*4").gain(0.8)'
});

// Update code
await apiService.updateClip('house_project', 'kick', {
  code: 'sound("bd*4").gain(1.2).distort(0.3)'
});

// List all clips
const clips = await apiService.listClips('house_project');

// Delete clip
await apiService.deleteClip('house_project', 'kick');
```

---

### **3. Error Handling**

```typescript
import { apiService, APIError } from '$lib/services';

try {
  const clip = await apiService.getClip('house_project', 'nonexistent');
} catch (error) {
  if (error instanceof APIError) {
    if (error.status === 404) {
      console.log('Clip not found');
    } else if (error.status === 0) {
      console.log('Network error or timeout');
    } else {
      console.error(`API Error ${error.status}: ${error.message}`);
    }
  }
}
```

---

### **4. Pagination**

```typescript
import { apiService } from '$lib/services';

let allMessages = [];
let hasMore = true;
let oldestIndex = undefined;

while (hasMore) {
  const response = await apiService.getMessages(sessionId, {
    page_size: 50,
    before_index: oldestIndex
  });
  
  if (response.messages.length === 0) {
    hasMore = false;
  } else {
    allMessages = [...response.messages, ...allMessages];
    oldestIndex = response.messages[0].message_index;
  }
}

console.log('Loaded', allMessages.length, 'messages');
```

---

### **5. Svelte Component Integration**

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { apiService, type ClipData } from '$lib/services';
  
  let clips: ClipData[] = [];
  let loading = true;
  let error: string | null = null;
  
  onMount(async () => {
    try {
      clips = await apiService.listClips('house_project');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load clips';
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <p>Loading clips...</p>
{:else if error}
  <p class="text-red-500">Error: {error}</p>
{:else}
  <ul>
    {#each clips as clip}
      <li>{clip.name}</li>
    {/each}
  </ul>
{/if}
```

---

## Configuration

### **Custom Base URL**

```typescript
import { APIService } from '$lib/services';

const api = new APIService({
  baseUrl: 'https://production.example.com/api'
});

const clips = await api.listClips('project1');
```

### **Custom Timeout**

```typescript
const api = new APIService({
  timeout: 60000  // 60 seconds
});
```

### **Both**

```typescript
const api = new APIService({
  baseUrl: 'https://api.example.com/api',
  timeout: 45000
});
```

---

## Statistics

**Code Metrics**:
- 2 files created
- ~400 lines of code
- 30+ methods
- Full TypeScript typing
- Comprehensive error handling

**Features**:
- ✅ Type-safe HTTP client
- ✅ Session management (4 methods)
- ✅ Message history with pagination
- ✅ Clip CRUD (5 methods)
- ✅ Song CRUD (5 methods)
- ✅ Playlist CRUD (5 methods)
- ✅ Health check
- ✅ Custom error class
- ✅ Request timeout
- ✅ Auto URL detection
- ✅ Query parameter building

---

## What's Next: Phase 6 - Strudel Player Integration

Now we'll integrate the Strudel web player:

**File to create**: `ui/src/lib/services/strudel.ts`

**Features**:
- Initialize Strudel player
- Load and evaluate patterns
- Control playback (start, stop, pause)
- Volume and tempo control
- Sample loading
- Integration with player store

**Estimated**: 45-60 minutes  
**Lines**: ~200-250  

---

## Technical Decisions

### **Fetch API**
**Decision**: Use native `fetch()` instead of axios  
**Reason**: No dependencies, built-in, modern browsers support

### **AbortController**
**Decision**: Use AbortController for timeout  
**Reason**: Standard API, works with fetch, clean cancellation

### **Custom Error Class**
**Decision**: Create APIError extending Error  
**Reason**: Type-safe error handling, status code access

### **Singleton Pattern**
**Decision**: Export singleton `apiService` instance  
**Reason**: Single HTTP client shared across app, consistent config

### **Type Safety**
**Decision**: Full TypeScript typing for all methods  
**Reason**: Catch errors at compile time, better DX, autocomplete

---

## Resources

- **Service Definition**: `ui/src/lib/services/api.ts`
- **Backend Integration Guide**: `notes/interface/integration.md`
- **Type Definitions**: `ui/src/lib/types/panel.ts`, `message.ts`, `session.ts`
- **Implementation Plan**: `notes/interface/ui_implementation.md`

---

## Success Metrics

✅ **API service implemented**: Full REST client  
✅ **Session management**: Create, list, delete, update name  
✅ **Message history**: Pagination support  
✅ **Clip CRUD**: All operations  
✅ **Song CRUD**: All operations  
✅ **Playlist CRUD**: All operations  
✅ **Error handling**: Custom APIError class  
✅ **Timeout support**: 30-second default  
✅ **Type safety**: Full TypeScript coverage  
✅ **Auto URL detection**: Based on window.location  

**Phase 5 Status**: ✅ **COMPLETE**

---

**Ready for Phase 6!** 🚀
