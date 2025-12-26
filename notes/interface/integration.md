# Backend Integration Guide for Frontend Developer

**Date**: 2025-12-25  
**Purpose**: Complete API specification and WebSocket protocol for Strudel Agent frontend integration  
**Status**: ✅ Backend Phase 1 Complete - Ready for Integration

---

## Overview

The Strudel Agent backend is **fully implemented** and ready for frontend integration. This document provides:
- Complete REST API specification
- WebSocket protocol details
- Message formats
- Authentication requirements
- Example requests/responses

---

## Server Configuration

### Development Server

```bash
# Backend URL
http://localhost:8000

# WebSocket URL
ws://localhost:8000/ws

# Health check
GET http://localhost:8000/health
```

### Environment Variables

```bash
# .env file
STRUDEL_DB_URL=postgresql+asyncpg://user:password@localhost:5432/strudel_agent
OPENROUTER_API_KEY=sk-or-v1-...
HOST=0.0.0.0
PORT=8000
```

### Starting the Server

```bash
cd backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

---

## REST API Endpoints

### Sessions

#### Create Session

```http
POST /api/sessions
Content-Type: application/json

{
  "agent_name": "strudel",
  "model_name": "x-ai/grok-beta",
  "provider": "openrouter",
  "session_type": "clip",
  "item_id": "kick",
  "project_id": "house_project",
  "session_name": "Kick Drum Session" // optional
}
```

**Response**:
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "agent_name": "strudel",
  "model_name": "x-ai/grok-beta",
  "provider": "openrouter",
  "session_type": "clip",
  "item_id": "kick",
  "project_id": "house_project",
  "created_at": "2025-12-25T01:35:06.123Z",
  "last_activity": "2025-12-25T01:35:06.123Z",
  "status": "active",
  "message_count": 0
}
```

**Session Types**:
- `"clip"` - Single clip editing
- `"song"` - Song composition (multiple clips)
- `"playlist"` - Playlist management (multiple songs)
- `"pack"` - Sample pack exploration

---

#### List Sessions

```http
GET /api/sessions?status=active&project_id=house_project
```

**Query Parameters**:
- `status` (optional): `active`, `idle`, `terminated`
- `project_id` (optional): Filter by project

**Response**:
```json
[
  {
    "session_id": "...",
    "session_type": "clip",
    "item_id": "kick",
    "project_id": "house_project",
    "message_count": 12,
    "status": "active",
    "created_at": "2025-12-25T01:35:06.123Z",
    "last_activity": "2025-12-25T01:40:15.456Z"
  }
]
```

---

#### Delete Session

```http
DELETE /api/sessions/{session_id}
```

**Response**:
```json
{"success": true}
```

---

#### Update Session Name

```http
PATCH /api/sessions/{session_id}/name
Content-Type: application/json

{
  "name": "New Session Name"  // null to clear
}
```

---

### Messages

#### Get Paginated Messages

```http
GET /api/messages/{session_id}?page_size=50&before_index=100
```

**Query Parameters**:
- `page_size` (default: 50): Number of messages to return
- `before_index` (optional): Load messages before this index (for pagination)

**Response**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Make the kick punchier",
      "timestamp": "2025-12-25T01:35:06.123Z",
      "message_index": 0
    },
    {
      "role": "assistant",
      "content": "I'll increase the gain and add some distortion...",
      "timestamp": "2025-12-25T01:35:12.456Z",
      "message_index": 1
    }
  ]
}
```

**Pagination Flow**:
```javascript
// Initial load (most recent 50)
const response = await fetch(`/api/messages/${sessionId}?page_size=50`);

// Load more (scroll up)
if (hasMore) {
    const oldestIndex = messages[0].message_index;
    const response = await fetch(
        `/api/messages/${sessionId}?page_size=50&before_index=${oldestIndex}`
    );
}
```

---

### Clips

#### Create Clip

```http
POST /api/clips
Content-Type: application/json

{
  "clip_id": "kick",
  "project_id": "house_project",
  "name": "Kick Drum",
  "code": "sound(\"bd*4\").gain(0.8)",
  "metadata": {
    "bpm": 120,
    "tags": ["drums", "kick"]
  }
}
```

**Response**:
```json
{
  "id": 1,
  "clip_id": "kick",
  "project_id": "house_project",
  "name": "Kick Drum",
  "code": "sound(\"bd*4\").gain(0.8)",
  "created_at": "2025-12-25T01:35:06.123Z",
  "updated_at": "2025-12-25T01:35:06.123Z",
  "metadata": {
    "bpm": 120,
    "tags": ["drums", "kick"]
  }
}
```

---

#### Get Clip

```http
GET /api/clips/{project_id}/{clip_id}
```

**Response**: Same as create response

---

#### List Clips

```http
GET /api/clips/{project_id}
```

**Response**: Array of clip objects

---

#### Update Clip

```http
PUT /api/clips/{project_id}/{clip_id}
Content-Type: application/json

{
  "name": "Punchy Kick",  // optional
  "code": "sound(\"bd*4\").gain(1.2).distort(0.3)",  // optional
  "metadata": {"bpm": 128}  // optional
}
```

**Note**: Only include fields you want to update.

---

#### Delete Clip

```http
DELETE /api/clips/{project_id}/{clip_id}
```

---

### Songs

#### Create Song

```http
POST /api/songs
Content-Type: application/json

{
  "song_id": "house_track",
  "project_id": "house_project",
  "name": "House Track",
  "clip_ids": ["kick", "bass", "hats"],
  "metadata": {
    "bpm": 120,
    "key": "C minor"
  }
}
```

**Response**:
```json
{
  "id": 1,
  "song_id": "house_track",
  "project_id": "house_project",
  "name": "House Track",
  "clip_ids": ["kick", "bass", "hats"],
  "created_at": "2025-12-25T01:35:06.123Z",
  "updated_at": "2025-12-25T01:35:06.123Z",
  "metadata": {
    "bpm": 120,
    "key": "C minor"
  }
}
```

---

#### Get/List/Update/Delete Song

Same pattern as clips:
```
GET    /api/songs/{project_id}/{song_id}
GET    /api/songs/{project_id}
PUT    /api/songs/{project_id}/{song_id}
DELETE /api/songs/{project_id}/{song_id}
```

---

### Playlists

Same pattern as songs:
```
POST   /api/playlists
GET    /api/playlists/{project_id}/{playlist_id}
GET    /api/playlists/{project_id}
PUT    /api/playlists/{project_id}/{playlist_id}
DELETE /api/playlists/{project_id}/{playlist_id}
```

**Playlist fields**:
- `playlist_id`: Unique identifier
- `project_id`: Project identifier
- `name`: Playlist name
- `song_ids`: Array of song IDs
- `metadata`: Optional metadata

---

## WebSocket Protocol

### Connection Flow

```javascript
// 1. Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    // 2. Send handshake
    ws.send(JSON.stringify({
        type: 'handshake',
        session_id: '123e4567-e89b-12d3-a456-426614174000',
        client_type: 'pwa',
        client_version: '1.0.0'
    }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    // 3. Handle handshake acknowledgment
    if (message.type === 'handshake_ack') {
        console.log('Connected!', message.session_info);
        // Ready to send user messages
    }
    
    // 4. Handle other messages
    handleMessage(message);
};
```

---

### Message Types

#### 1. Handshake (Client → Server)

```json
{
  "type": "handshake",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "client_type": "pwa",
  "client_version": "1.0.0"
}
```

---

#### 2. Handshake Ack (Server → Client)

```json
{
  "type": "handshake_ack",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "connection_id": "pwa-abc123de",
  "is_reconnect": false,
  "session_info": {
    "session_type": "clip",
    "item_id": "kick",
    "project_id": "house_project",
    "message_count": 12
  }
}
```

---

#### 3. User Message (Client → Server)

```json
{
  "type": "user_message",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Make the kick punchier",
  "context": {
    "current_code": "sound(\"bd*4\").gain(0.8)",
    "bpm": 120
  }
}
```

**Context field** (optional): Include any relevant context about the current state (current code, BPM, etc.)

---

#### 4. Typing Indicator (Server → Client)

```json
{
  "type": "typing_indicator",
  "is_typing": true,
  "text": "Analyzing code..."  // optional
}
```

---

#### 5. Tool Report (Server → Client)

Sent when agent starts using a tool:

```json
{
  "type": "tool_report",
  "tool_name": "update_clip_code",
  "tool_call_id": "call_abc123"
}
```

**Use this to show**: "Updating clip..." or "Calling `update_clip_code`"

---

#### 6. Tool Result (Server → Client)

Sent when tool execution completes:

```json
{
  "type": "tool_result",
  "tool_name": "update_clip_code",
  "content": {"success": true, "clip_id": "kick"}
}
```

---

#### 7. Agent Response (Server → Client)

Final agent reply:

```json
{
  "type": "agent_response",
  "content": "I've made the kick punchier by increasing the gain to 1.2 and adding some distortion.",
  "is_final": true
}
```

---

#### 8. Clip Updated (Server → Client)

Sent when clip code is updated:

```json
{
  "type": "clip_updated",
  "clip_id": "kick",
  "new_code": "sound(\"bd*4\").gain(1.2).distort(0.3)",
  "metadata": {}
}
```

**Action**: Update code editor with `new_code`

---

#### 9. Song Updated (Server → Client)

```json
{
  "type": "song_updated",
  "song_id": "house_track",
  "clip_ids": ["kick", "bass", "hats", "melody"],
  "metadata": {}
}
```

**Action**: Update song composition

---

#### 10. Playlist Updated (Server → Client)

```json
{
  "type": "playlist_updated",
  "playlist_id": "favorites",
  "song_ids": ["house_track", "techno_track"],
  "metadata": {}
}
```

---

#### 11. Tool Request (Server → Client)

Agent requests user input:

```json
{
  "type": "tool_request",
  "request_id": "req_xyz789",
  "tool_name": "pwa_request_user_input",
  "parameters": {
    "prompt": "What BPM do you want?",
    "input_type": "text",
    "timeout_seconds": 300
  },
  "timeout_ms": 300000
}
```

**Action**: Show input form, wait for user response, send tool_response

---

#### 12. Tool Response (Client → Server)

User responds to tool request:

```json
{
  "type": "tool_response",
  "request_id": "req_xyz789",
  "success": true,
  "data": "128"
}
```

**Or error**:
```json
{
  "type": "tool_response",
  "request_id": "req_xyz789",
  "success": false,
  "error": "User cancelled"
}
```

---

## WebSocket Client Example

```javascript
class StrudelWSClient {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.ws = null;
        this.handlers = {};
        this.pendingRequests = new Map();
    }
    
    connect() {
        this.ws = new WebSocket('ws://localhost:8000/ws');
        
        this.ws.onopen = () => {
            // Send handshake
            this.send({
                type: 'handshake',
                session_id: this.sessionId,
                client_type: 'pwa',
                client_version: '1.0.0'
            });
        };
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket closed');
            // Implement reconnection logic
        };
    }
    
    handleMessage(message) {
        const { type } = message;
        
        // Handle tool requests
        if (type === 'tool_request') {
            this.handleToolRequest(message);
            return;
        }
        
        // Emit to registered handlers
        if (this.handlers[type]) {
            this.handlers[type].forEach(handler => handler(message));
        }
    }
    
    async handleToolRequest(message) {
        const { request_id, tool_name, parameters } = message;
        
        try {
            let result;
            
            if (tool_name === 'pwa_request_user_input') {
                result = await this.showInputForm(parameters);
            } else if (tool_name === 'pwa_send_notification') {
                result = await this.showNotification(parameters);
            }
            
            // Send response
            this.send({
                type: 'tool_response',
                request_id,
                success: true,
                data: result
            });
        } catch (error) {
            this.send({
                type: 'tool_response',
                request_id,
                success: false,
                error: error.message
            });
        }
    }
    
    on(type, handler) {
        if (!this.handlers[type]) {
            this.handlers[type] = [];
        }
        this.handlers[type].push(handler);
    }
    
    sendUserMessage(message, context = null) {
        this.send({
            type: 'user_message',
            session_id: this.sessionId,
            message,
            context
        });
    }
    
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
    
    async showInputForm(params) {
        // Implement input form UI
        return new Promise((resolve) => {
            // Show form, wait for user input
            const value = prompt(params.prompt);
            resolve(value);
        });
    }
    
    async showNotification(params) {
        // Implement notification UI
        alert(params.message);
        return { success: true };
    }
}

// Usage
const client = new StrudelWSClient(sessionId);
client.connect();

client.on('handshake_ack', (message) => {
    console.log('Connected!', message.session_info);
});

client.on('agent_response', (message) => {
    console.log('Agent:', message.content);
});

client.on('clip_updated', (message) => {
    // Update code editor
    editor.setValue(message.new_code);
});

client.on('typing_indicator', (message) => {
    if (message.is_typing) {
        showTypingIndicator();
    } else {
        hideTypingIndicator();
    }
});

// Send user message
client.sendUserMessage('Make the kick punchier', {
    current_code: editor.getValue(),
    bpm: 120
});
```

---

## Error Handling

### HTTP Errors

```javascript
try {
    const response = await fetch('/api/clips/project/kick');
    
    if (!response.ok) {
        const error = await response.json();
        console.error('API Error:', error.detail);
        // Handle error
    }
    
    const clip = await response.json();
} catch (error) {
    console.error('Network error:', error);
}
```

### WebSocket Errors

```javascript
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    // Show error to user
};

ws.onclose = (event) => {
    if (!event.wasClean) {
        console.error('WebSocket closed unexpectedly:', event.code, event.reason);
        // Attempt reconnection
    }
};
```

---

## CORS Configuration

CORS is configured to allow all origins in development. For production, update `backend/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing the Backend

### Health Check

```bash
curl http://localhost:8000/health
```

### Create Session

```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "strudel",
    "model_name": "x-ai/grok-beta",
    "provider": "openrouter",
    "session_type": "clip",
    "item_id": "kick",
    "project_id": "test_project"
  }'
```

### Create Clip

```bash
curl -X POST http://localhost:8000/api/clips \
  -H "Content-Type: application/json" \
  -d '{
    "clip_id": "kick",
    "project_id": "test_project",
    "name": "Kick Drum",
    "code": "sound(\"bd*4\").gain(0.8)"
  }'
```

### WebSocket Test (using `wscat`)

```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c ws://localhost:8000/ws

# Send handshake
{"type":"handshake","session_id":"YOUR_SESSION_ID","client_type":"pwa"}

# Send user message
{"type":"user_message","session_id":"YOUR_SESSION_ID","message":"Hello!"}
```

---

## Next Steps for Frontend

### Phase 1: Basic Connection

- [ ] Implement WebSocket client
- [ ] Handle handshake protocol
- [ ] Test connection with backend
- [ ] Implement message sending/receiving

### Phase 2: UI Integration

- [ ] Connect code editor to `clip_updated` events
- [ ] Show typing indicator
- [ ] Display agent responses
- [ ] Handle tool requests (user input, notifications)

### Phase 3: Data Management

- [ ] Implement REST API calls for clips/songs/playlists
- [ ] Load message history on session open
- [ ] Implement pagination for chat history
- [ ] Sync state with backend

### Phase 4: Polish

- [ ] Error handling
- [ ] Reconnection logic
- [ ] Loading states
- [ ] Optimistic updates

---

## Support

If you encounter any issues or need clarification:

1. Check backend logs: `uvicorn` output
2. Verify database connection: `STRUDEL_DB_URL` in `.env`
3. Test endpoints with `curl` or Postman
4. Check WebSocket connection with `wscat`

---

## Summary

✅ **Backend is ready**  
✅ **All endpoints implemented**  
✅ **WebSocket protocol defined**  
✅ **Database configured**  
✅ **Agent factory working**  

**You can now**:
- Create sessions via REST API
- Connect to WebSocket
- Send user messages
- Receive agent responses
- Update clips/songs/playlists
- Load message history

**Start with**: WebSocket client implementation, then connect to your Svelte UI components!
