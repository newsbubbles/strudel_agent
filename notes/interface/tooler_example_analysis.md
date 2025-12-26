# Tooler Example Analysis - WebSocket, Agent Factory, and Frontend Architecture

**Date**: 2025-12-25  
**Purpose**: Document how tooler_example implements WebSocket communication, agent factory, session management, and frontend integration  
**For**: Frontend developer and backend implementation  
**Source**: `tooler_example_for_answers/`

---

## Documentation Index

1. **This document** - WebSocket, Agent Factory, Frontend Architecture
2. **[Database Architecture](./database_architecture.md)** - PostgreSQL schema, SQLModel, CRUD operations

---

## Overview

The Tooler example demonstrates a **multi-session PWA chat interface** with:
- FastAPI backend with WebSocket support
- Pydantic-AI agent factory
- Session-based architecture (multiple concurrent sessions)
- Real-time bidirectional communication
- Tool request/response protocol
- Message persistence (database + pickle files)

**Key difference for Strudel Agent**:
- Tooler: Multiple sessions, chat-based
- Strudel Agent: Single-session per item (clip/song/playlist), carousel-based

---

## Backend Architecture

### File Structure

```
backend/
├── server.py              # FastAPI app, WebSocket endpoint, routes
├── agent_factory.py       # Agent creation, MCP server setup
├── session_manager.py     # Session lifecycle, history persistence
├── manager.py             # WebSocket connection manager
├── models.py              # Pydantic models for messages
├── mcp_server.py          # Internal MCP server for PWA tools
└── message_filtering.py   # Message history filtering

src/db/
├── connection.py          # Database engine and session factory
├── models.py              # SQLModel definitions
├── crud.py                # CRUD operations
└── schema.sql             # Reference schema
```

**See [database_architecture.md](./database_architecture.md) for complete database documentation.**

---

## 1. FastAPI Server (`server.py`)

### Key Components

#### Lifespan Manager

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await restore_active_sessions()
    cleanup_task = asyncio.create_task(cleanup_sessions())
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    await close_db()
```

**Purpose**: Initialize database, restore sessions on startup, cleanup on shutdown

#### WebSocket Endpoint

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    session_id: str | None = None
    connection_id: str | None = None
    connection_type: str = 'pwa'  # or 'mcp'
    
    try:
        await websocket.accept()
        
        # Wait for handshake
        handshake_data = await websocket.receive_json()
        handshake = Handshake(**handshake_data)
        session_id = handshake.session_id
        connection_type = handshake.client_type or 'pwa'
        
        # Register connection
        context, connection_id = await manager.connect(
            websocket, session_id, connection_type
        )
        
        # Get or restore session
        session_state = await session_manager.get_session(UUID(session_id))
        if not session_state:
            session_state = await session_manager.restore_session(
                UUID(session_id), 
                auth_callback=auth_callback
            )
        
        # Send handshake ack
        await manager.send_handshake_ack(
            session_id=session_id,
            is_reconnect=is_reconnect,
            connection_type=connection_type,
            session_info={...}
        )
        
        # Start MCP servers for PWA connections
        if connection_type == 'pwa':
            async with session_state.agent.run_mcp_servers():
                await handle_websocket_messages(
                    websocket, session_id, connection_type, session_state
                )
        else:
            await handle_websocket_messages(
                websocket, session_id, connection_type, session_state
            )
    
    except WebSocketDisconnect:
        manager.disconnect(session_id, connection_id)
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}")
```

**Key points**:
- **Handshake protocol**: First message must be handshake with `session_id`
- **Connection types**: `pwa` (frontend) or `mcp` (MCP client)
- **Connection ID**: Unique auto-generated ID per connection
- **Session restoration**: Loads session from database if not in memory
- **MCP servers**: Started only for PWA connections (not MCP)

#### Message Handling Loop

```python
async def handle_websocket_messages(
    websocket: WebSocket,
    session_id: str,
    connection_type: str,
    session_state: SessionState
):
    while True:
        data = await websocket.receive_json()
        msg_type = data.get("type")
        
        if msg_type == "user_message":
            asyncio.create_task(
                handle_user_message(session_id, data, session_state)
            )
        elif msg_type == "tool_response":
            await manager.handle_tool_response(session_id, data)
        elif msg_type == "tool_request":
            await handle_pwa_tool_request(session_id, data)
```

**Message types**:
- `user_message`: User sends message to agent
- `tool_response`: PWA responds to tool request
- `tool_request`: PWA requests tool execution (rare)

#### User Message Handling

```python
async def handle_user_message(
    session_id: str,
    data: dict,
    session_state: SessionState
):
    message = UserMessage(**data)
    
    # Send typing indicator
    await manager.send_message(session_id, {
        "type": "typing_indicator",
        "is_typing": True,
    }, target='pwa')
    
    # Event stream handler for tool calls
    async def event_stream_handler(ctx, stream):
        async for event in stream:
            if isinstance(event, PartStartEvent):
                if isinstance(event.part, ToolCallPart):
                    await manager.send_message(session_id, {
                        "type": "tool_report",
                        "tool_name": event.part.tool_name,
                        "tool_call_id": event.part.tool_call_id,
                    }, target='pwa')
            
            elif isinstance(event, FunctionToolResultEvent):
                await manager.send_message(session_id, {
                    "type": "tool_result",
                    "tool_name": event.result.tool_name,
                    "content": event.result.content,
                }, target='pwa')
    
    # Run agent
    response = await session_state.agent.run(
        message.message,
        message_history=filtered_message_history(
            session_state.conversation_history
        ),
        event_stream_handler=event_stream_handler
    )
    
    # Send response
    await manager.send_message(session_id, {
        "type": "agent_response",
        "content": response.output,
        "is_final": True,
    }, target='pwa')
    
    # Update history
    await session_state.add_messages(response.new_messages())
    
    # Background reflection task
    asyncio.create_task(
        reflect_on_conversation(session_id, session_state, response.new_messages())
    )
```

**Flow**:
1. Receive user message
2. Send typing indicator to PWA
3. Run agent with event stream handler
4. Stream tool events to PWA (`tool_report`, `tool_result`)
5. Send final response to PWA
6. Save messages to history (pickle + database)
7. Trigger background reflection (memory updates)

#### REST API Endpoints

```python
# Session management
GET  /api/sessions                    # List all sessions
POST /api/sessions                    # Create new session
DELETE /api/sessions/{session_id}     # Terminate session
PATCH /api/sessions/{session_id}/name # Update session name

# Message history
GET /api/messages/{session_id}        # Get paginated messages

# File serving
GET /api/projects/{session_id}/files/{file_path:path}  # Serve project files
```

**For Strudel Agent**:
- Add endpoints for clips, songs, playlists
- File serving for Strudel code files
- Metadata endpoints

---

## 2. Agent Factory (`agent_factory.py`)

### Agent Creation

```python
def create_agent(
    session_id: UUID,
    config: SessionCreate,
    current_project: str,
    auth_callback=None
) -> Agent:
    # Load agent prompt
    prompt = load_agent_prompt(config.agent_name)
    
    # Create model
    model = create_model(config, auth_callback=auth_callback)
    
    # Create MCP servers
    mcp_servers = create_mcp_servers(
        session_id, config.agent_name, current_project
    )
    
    # Create agent
    agent = Agent(
        model=model,
        mcp_servers=mcp_servers,
        system_prompt=prompt,
    )
    
    return agent
```

### Model Creation

```python
def create_model(config: SessionCreate, auth_callback=None):
    # Claude Code mode (not used for Strudel Agent)
    if config.use_claude_code:
        return ClaudeCodeModel(
            model_name=DEFAULT_MODEL,
            settings=ClaudeCodeModelSettings(max_tokens=48192),
            input_callback=auth_callback
        )
    
    # OpenRouter mode (THIS IS WHAT WE USE)
    model_name = config.model_name or "x-ai/grok-4-fast"
    return OpenAIModel(
        model_name,
        provider=OpenAIProvider(
            base_url='https://openrouter.ai/api/v1',
            api_key=os.getenv('OPENROUTER_API_KEY')
        )
    )
```

**For Strudel Agent**: Use OpenRouter with OpenAIModel (skip Claude Code)

### MCP Server Setup

```python
def create_mcp_servers(session_id: UUID, agent_name: str, current_project: str):
    mcp_servers = [
        # Project tools (file management, git, etc.)
        MCPServerStdio(
            'python',
            ['project_tools/project_tools.py'],
            env={
                'ROOT_FOLDER': tooler_workspace,
                'SESSION_ID': str(session_id),
                'TOOLER_CURRENT_PROJECT': current_project or "__none__",
            }
        ),
        
        # Web scraping tools
        MCPServerStdio(
            'python',
            ['project_tools/serper_scrape_mcp.py'],
            env={'SESSION_ID': str(session_id)}
        ),
        
        # Hypergraph memory
        MCPServerStdio(
            'python',
            ['../hypergraph_memory/src/server.py'],
            env={
                'HYPERGRAPH_MEMORY_FILE': f"memory/sessions/{session_id}/memory.json",
                'SESSION_ID': str(session_id),
            }
        ),
        
        # Internal PWA tools
        MCPServerStdio(
            'python',
            ['backend/mcp_server.py'],
            env={
                'TOOLER_SESSION_ID': str(session_id),
                'WORKING_DIR': working_dir,
            }
        ),
    ]
    
    return mcp_servers
```

**For Strudel Agent**:
- Add `mcp_server.py` for Strudel-specific tools
- Keep hypergraph memory
- Add Strudel player control tools
- Add sample pack tools

### Agent Prompt Loading

```python
def load_agent_prompt(agent_name: str) -> str:
    prompt_path = Path(f"src/agents/{agent_name}.md")
    prompt = prompt_path.read_text()
    
    # Replace variables
    prompt = prompt.replace('{time_now}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Load .variables.json if exists
    variables_path = Path(".variables.json")
    if variables_path.exists():
        variables = json.loads(variables_path.read_text())
        for key, value in variables.items():
            prompt = prompt.replace(f'{{{key}}}', str(value))
    
    return prompt
```

**For Strudel Agent**: Create `agents/strudel.md` with system prompt

---

## 3. Session Manager (`session_manager.py`)

### SessionState Class

```python
class SessionState:
    def __init__(self, session_id: UUID, config: SessionCreate, auth_callback=None):
        self.session_id = session_id
        self.config = config
        self.agent: Optional[Agent] = None
        self.reflection_agent: Optional[Agent] = None
        self.conversation_history: list[ModelMessage] = []
        self.last_activity = datetime.now()
        self.current_project = None
        self.auth_callback = auth_callback
    
    async def initialize_agent(self):
        self.agent = create_agent(
            self.session_id, 
            self.config, 
            self.current_project, 
            auth_callback=self.auth_callback
        )
    
    async def add_messages(self, new_messages_obj: List[ModelMessage]):
        # Append to in-memory history
        self.conversation_history.extend(new_messages_obj)
        
        # Save to pickle file
        await self.save_conversation_history_to_file()
        
        # Extract display messages for database
        display_messages = self._extract_display_messages_from_objects(new_messages_obj)
        
        # Save to database
        async with async_session() as db:
            await save_display_messages(db, self.session_id, display_messages)
            await update_session_activity(db, self.session_id)
```

**Key points**:
- **Dual storage**: Full history in pickle, simplified in database
- **Pickle file**: For agent message history (ModelMessage objects)
- **Database**: For frontend display (simplified {role, content, timestamp})

**See [database_architecture.md](./database_architecture.md) for message storage details.**

### Message Extraction

```python
def _extract_display_messages_from_objects(self, messages_obj: List[ModelMessage]):
    # Find LAST ModelResponse (final reply)
    last_response_index = None
    for i in range(len(messages_obj) - 1, -1, -1):
        if isinstance(messages_obj[i], ModelResponse):
            last_response_index = i
            break
    
    display_messages = []
    for i, msg in enumerate(messages_obj):
        if isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, UserPromptPart):
                    display_messages.append({
                        "role": "user",
                        "content": part.content,
                        "timestamp": timestamp
                    })
        
        # Only process LAST ModelResponse
        elif isinstance(msg, ModelResponse) and i == last_response_index:
            for part in msg.parts:
                if isinstance(part, TextPart):
                    display_messages.append({
                        "role": "assistant",
                        "content": part.content,
                        "timestamp": timestamp
                    })
    
    return display_messages
```

**Why only last ModelResponse?**
- Pydantic-AI returns one ModelResponse per tool call
- Plus a final ModelResponse with the actual reply
- Only the final reply should be displayed to user

### Session Manager

```python
class SessionManager:
    def __init__(self):
        self.sessions: Dict[UUID, SessionState] = {}
    
    async def create_session(self, config: SessionCreate) -> SessionState:
        session_id = uuid4()
        
        # Create in database
        async with async_session() as db:
            db_session = await db_create_session(db, config)
            session_id = db_session.session_id
        
        # Initialize memory
        await self._initialize_memory(session_id)
        
        # Create session state
        session_state = SessionState(session_id, config)
        await session_state.initialize_agent()
        
        self.sessions[session_id] = session_state
        return session_state
    
    async def restore_session(self, session_id: UUID) -> SessionState:
        # Load from database
        async with async_session() as db:
            db_session = await db_get_session(db, session_id)
        
        # Create config from database
        config = SessionCreate(
            agent_name=db_session.agent_name,
            model_name=db_session.model_name,
            ...
        )
        
        # Create session state
        session_state = SessionState(session_id, config)
        await session_state.initialize_agent()
        await session_state.load_history()  # Load from pickle
        
        self.sessions[session_id] = session_state
        return session_state
```

**For Strudel Agent**:
- Session per item (clip/song/playlist)
- Store item type in session metadata
- Initialize with item data

---

## 4. Connection Manager (`manager.py`)

### Connection Management

```python
class ConnectionManager:
    def __init__(self):
        # session_id -> {connection_id -> WebSocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
        # session_id -> SessionContext
        self.session_contexts: Dict[str, SessionContext] = {}
        
        # session_id -> {request_id -> Future}
        self.pending_tool_requests: Dict[str, Dict[str, asyncio.Future]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, connection_type: str):
        # Generate unique connection ID
        connection_id = f"{connection_type}-{uuid.uuid4().hex[:8]}"
        
        # Store connection
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        self.active_connections[session_id][connection_id] = websocket
        
        # Get or create session context
        if session_id in self.session_contexts:
            context = self.session_contexts[session_id]
        else:
            context = SessionContext(session_id=session_id)
            self.session_contexts[session_id] = context
        
        return context, connection_id
```

**Key points**:
- **Multiple connections per session**: PWA + MCP clients
- **Unique connection IDs**: `pwa-abc123de`, `mcp-xyz789ij`
- **Connection types**: `pwa` or `mcp`

### Message Routing

```python
async def send_message(self, session_id: str, message: Dict, target: str = 'pwa'):
    if session_id not in self.active_connections:
        return False
    
    connections = self.active_connections[session_id]
    
    # Determine targets
    if target == 'all':
        targets = list(connections.items())
    else:
        # Find connections matching type prefix
        targets = [
            (conn_id, ws) for conn_id, ws in connections.items()
            if conn_id.startswith(f"{target}-")
        ]
    
    # Send to all matched connections
    for conn_id, ws in targets:
        await ws.send_json(message)
```

**Routing**:
- `target='pwa'` → all PWA connections
- `target='mcp'` → all MCP connections
- `target='all'` → all connections

### Tool Request/Response Protocol

```python
async def send_tool_request(
    self, session_id: str, tool_name: str, parameters: dict, timeout_ms: int = 30000
) -> dict:
    request_id = str(uuid.uuid4())
    
    # Create future for response
    future = asyncio.get_running_loop().create_future()
    if session_id not in self.pending_tool_requests:
        self.pending_tool_requests[session_id] = {}
    self.pending_tool_requests[session_id][request_id] = future
    
    # Send tool request to PWA
    await self.send_message(session_id, {
        'type': 'tool_request',
        'request_id': request_id,
        'tool_name': tool_name,
        'parameters': parameters,
        'timeout_ms': timeout_ms,
    }, target='pwa')
    
    # Wait for response
    result = await asyncio.wait_for(future, timeout=timeout_ms/1000.0)
    return result

async def handle_tool_response(self, session_id: str, response_data: dict):
    request_id = response_data.get('request_id')
    
    if (session_id in self.pending_tool_requests and
        request_id in self.pending_tool_requests[session_id]):
        future = self.pending_tool_requests[session_id][request_id]
        
        if response_data.get('success'):
            future.set_result(response_data.get('data'))
        else:
            future.set_exception(RuntimeError(response_data.get('error')))
```

**Flow**:
1. MCP server calls `send_tool_request()` (blocks)
2. Request sent to PWA via WebSocket
3. PWA shows UI (form, input, etc.)
4. User responds
5. PWA sends `tool_response` back
6. Future resolves, MCP server gets result

---

## 5. Frontend Architecture

### File Structure

```
web/
├── pwa/
│   ├── index.html         # PWA shell
│   ├── app.js             # Main PWA app
│   └── styles.css         # Styles
└── js/
    ├── ws_client.js       # WebSocket client
    └── chat_ui.js         # Chat UI component
```

### PWA App (`app.js`)

```javascript
class ToolerPWA {
    constructor() {
        // Multi-session state
        this.sessions = new Map(); // sessionId -> { ws, ui, container, unreadCount }
        this.activeSessionId = null;
        
        this.backendUrl = this.getBackendUrl();
        this.init();
    }
    
    async init() {
        this.setupVisibilityTracking();
        await this.showSessionPicker();
        this.setupEventListeners();
    }
    
    async createSession(sessionId) {
        // Create container
        const container = document.createElement('div');
        container.id = `session-${sessionId}`;
        container.className = 'chat-session-container';
        document.body.appendChild(container);
        
        // Create WebSocket client
        const wsClient = new WSClient(sessionId, {
            url: this.backendUrl,
            clientVersion: '1.0.0-pwa',
        });
        
        // Create Chat UI
        const chatUI = new ChatUI(container, wsClient);
        
        // Store session
        this.sessions.set(sessionId, {
            ws: wsClient,
            ui: chatUI,
            container: container,
            unreadCount: 0,
        });
        
        // Load message history BEFORE connecting
        await this.loadMessageHistory(sessionId, chatUI);
        
        // Setup WebSocket handlers
        this.setupWebSocketHandlers(sessionId, wsClient);
        
        // Connect
        wsClient.connect();
    }
    
    setupWebSocketHandlers(sessionId, wsClient) {
        const session = this.sessions.get(sessionId);
        const chatUI = session.ui;
        
        wsClient.on('agent_response', (message) => {
            // Increment unread if not active session
            if (this.activeSessionId !== sessionId) {
                session.unreadCount++;
                this.showNotification('New message');
            }
        });
        
        wsClient.on('tool_report', (event) => {
            chatUI.updateTypingText(`Calling \`${event.tool_name}\``);
        });
        
        wsClient.on('tool_result', (event) => {
            chatUI.addToolReturnMessage({
                type: 'result',
                tool_name: event.tool_name,
                data: event.content,
            });
        });
    }
}
```

**Key points**:
- **Multi-session**: Each session has own WS client, UI, container
- **Session switching**: Hide/show containers
- **Unread counts**: Track when session not active
- **Message history**: Load from API before connecting WS

### WebSocket Client (`ws_client.js`)

```javascript
class WSClient extends EventEmitter {
    constructor(sessionId, config = {}) {
        super();
        this.sessionId = sessionId;
        this.config = {
            url: config.url || 'ws://127.0.0.1:8000/ws',
            maxReconnectAttempts: config.maxReconnectAttempts || 5,
        };
        
        this.connected = false;
        this.handshakeComplete = false;
        this.messageQueue = [];
    }
    
    connect() {
        this.ws = new WebSocket(this.config.url);
        this.ws.onopen = () => this.handleOpen();
        this.ws.onclose = (event) => this.handleClose(event);
        this.ws.onmessage = (event) => this.handleMessage(event);
    }
    
    handleOpen() {
        this.connected = true;
        this.sendHandshake();
        this.emit('connected');
    }
    
    sendHandshake() {
        this.ws.send(JSON.stringify({
            type: 'handshake',
            session_id: this.sessionId,
            client_version: this.config.clientVersion,
        }));
    }
    
    handleMessage(event) {
        const message = JSON.parse(event.data);
        
        switch (message.type) {
            case 'handshake_ack':
                this.handleHandshakeAck(message);
                break;
            case 'agent_response':
                this.emit('agent_response', message);
                break;
            case 'tool_request':
                // PWA tools handled directly
                if (message.tool_name.startsWith('pwa_')) {
                    this.handlePwaToolRequest(message);
                } else {
                    this.emit('tool_request', message);
                }
                break;
            case 'tool_report':
                this.emit('tool_report', message);
                break;
            case 'tool_result':
                this.emit('tool_result', message);
                break;
        }
    }
    
    async handlePwaToolRequest(message) {
        let result = { success: false, error: 'Unknown PWA tool' };
        
        switch(message.tool_name) {
            case 'pwa_send_notification':
                result = await this.handleSendNotification(message.parameters);
                break;
            case 'pwa_request_user_input':
                result = await this.handleRequestUserInput(message.parameters);
                break;
            case 'pwa_send_custom_form':
                result = await this.handleSendCustomForm(message.parameters);
                break;
        }
        
        // Send response back
        this.send({
            type: "tool_response",
            request_id: message.request_id,
            success: result.success,
            data: result
        });
    }
    
    send(message) {
        if (!message.session_id) {
            message.session_id = this.sessionId;
        }
        
        // Queue if not ready
        if (!this.connected || !this.handshakeComplete) {
            this.messageQueue.push(message);
            return;
        }
        
        this.ws.send(JSON.stringify(message));
    }
}
```

**Key points**:
- **Event-driven**: Emits events for message types
- **PWA tools**: Handled directly in client (no event emission)
- **Message queueing**: Queue messages until handshake complete
- **Reconnection**: Automatic with exponential backoff

---

## 6. PWA Tool Protocol

### Flow Diagram

```
MCP Server (backend/mcp_server.py)
    ↓
    Calls manager.send_tool_request(session_id, tool_name, params)
    ↓
ConnectionManager
    Creates Future
    Sends tool_request to PWA
    ↓
WebSocket
    ↓
WSClient (frontend)
    Receives tool_request
    Calls handlePwaToolRequest()
    ↓
ChatUI
    Shows form/input/notification
    User interacts
    ↓
WSClient
    Sends tool_response back
    ↓
WebSocket
    ↓
ConnectionManager
    Resolves Future with response
    ↓
MCP Server
    Returns result to agent
```

### Example: User Input Request

**MCP Server** (`backend/mcp_server.py`):
```python
@server.call_tool()
async def pwa_request_user_input(prompt: str, input_type: str = 'text') -> dict:
    result = await manager.send_tool_request(
        session_id=SESSION_ID,
        tool_name='pwa_request_user_input',
        parameters={
            'prompt': prompt,
            'input_type': input_type,
            'timeout_seconds': 300,
        },
        timeout_ms=300000
    )
    return result
```

**Frontend** (`ws_client.js`):
```javascript
async handleRequestUserInput(params) {
    if (!window.FL_JS?.chatUI) {
        throw new Error('ChatUI not available');
    }
    
    // Show input form and wait for user
    const userValue = await window.FL_JS.chatUI.showInputForm(params);
    
    return { success: true, data: userValue };
}
```

**ChatUI** (`chat_ui.js`):
```javascript
showInputForm(params) {
    return new Promise((resolve) => {
        // Create input form
        const form = document.createElement('form');
        const input = document.createElement('input');
        const submit = document.createElement('button');
        
        form.onsubmit = (e) => {
            e.preventDefault();
            resolve(input.value);
            form.remove();
        };
        
        this.container.appendChild(form);
    });
}
```

---

## 7. Message History & Pagination

**See [database_architecture.md](./database_architecture.md) for complete details on:**
- Dual storage (pickle + database)
- Message table schema
- Pagination with `before_index`
- CRUD operations

### Quick Summary

**Backend Storage**:
1. **Pickle file**: Full ModelMessage objects for agent
2. **Database**: Simplified {role, content, timestamp} for frontend

**Pagination Endpoint**:
```python
GET /api/messages/{session_id}?page_size=50&before_index=100
```

**Frontend Loading**:
```javascript
// Initial load (most recent 50)
const response = await fetch(`/api/messages/${sessionId}?page_size=50`);

// Load more (scroll up)
if (hasMore) {
    const response = await fetch(
        `/api/messages/${sessionId}?page_size=50&before_index=${oldestIndex}`
    );
}
```

---

## 8. Key Differences for Strudel Agent

### Architecture Changes

| Aspect | Tooler Example | Strudel Agent |
|--------|----------------|---------------|
| **Sessions** | Multiple concurrent chat sessions | Single session per item (clip/song/playlist) |
| **UI** | Chat interface | Carousel interface |
| **Message input** | Global chat input | Per-panel input |
| **History** | Single conversation thread | Per-item session history |
| **Agent context** | Project-based | Item-based (clip, song, playlist) |
| **Real-time updates** | Chat messages | Code updates, player state |

### Backend Adaptations

**Session metadata** (see [database_architecture.md](./database_architecture.md)):
```python
class SessionCreate(BaseModel):
    agent_name: str = 'strudel'
    session_type: str  # 'clip', 'song', 'playlist', 'pack'
    item_id: str       # Clip ID, song ID, etc.
    project_id: str    # Strudel project
```

**WebSocket context**:
```python
# Include item context in every message
context = {
    'session_type': 'clip',
    'item_id': 'kick',
    'project_id': 'house_project',
    'current_code': 'sound("bd*4")...',
    'loaded_panels': ['kick', 'bass', 'hats'],
}
```

**Update events**:
```python
# Send code updates to frontend
await manager.send_message(session_id, {
    'type': 'clip_updated',
    'clip_id': 'kick',
    'new_code': 'sound("bd*4").gain(1.0)',
}, target='pwa')
```

### Frontend Adaptations

**Carousel state**:
```javascript
class StrudelPWA {
    constructor() {
        this.panels = [];  // Loaded carousel panels
        this.currentPanelIndex = 0;
        this.sessions = new Map();  // panel_id -> session
    }
    
    async loadPanel(type, itemId) {
        // Create session for this item
        const sessionId = await this.createItemSession(type, itemId);
        
        // Create panel with code editor
        const panel = {
            id: `${type}:${itemId}`,
            type,
            itemId,
            sessionId,
            ws: new WSClient(sessionId),
            editor: new CodeMirror(...),
        };
        
        this.panels.push(panel);
    }
}
```

**Update handling**:
```javascript
wsClient.on('clip_updated', (message) => {
    const panel = this.findPanel('clip', message.clip_id);
    if (panel) {
        panel.editor.setValue(message.new_code);
    }
});
```

---

## 9. Implementation Checklist for Strudel Agent

### Backend

- [ ] **Create `backend/` folder**
  - [ ] `server.py` - FastAPI app with WebSocket
  - [ ] `agent_factory.py` - Agent creation (OpenRouter only)
  - [ ] `session_manager.py` - Session lifecycle
  - [ ] `manager.py` - WebSocket connection manager
  - [ ] `models.py` - Pydantic message models
  - [ ] `mcp_server.py` - Strudel-specific MCP tools

- [ ] **Database setup** (see [database_architecture.md](./database_architecture.md))
  - [ ] Create `src/db/` folder
  - [ ] Define SQLModel models
  - [ ] Implement CRUD operations
  - [ ] Add Strudel-specific tables (clips, songs, playlists)

- [ ] **Session metadata**
  - [ ] Add `session_type` field (clip/song/playlist/pack)
  - [ ] Add `item_id` field
  - [ ] Add `project_id` field

- [ ] **WebSocket protocol**
  - [ ] Handshake with session_id
  - [ ] Message routing (pwa/mcp)
  - [ ] Tool request/response protocol
  - [ ] Update events (clip_updated, song_updated, etc.)

- [ ] **MCP tools**
  - [ ] Clip CRUD (create, read, update, delete)
  - [ ] Song CRUD
  - [ ] Playlist CRUD
  - [ ] Sample pack search
  - [ ] Strudel player controls
  - [ ] PWA tools (notifications, forms, etc.)

- [ ] **API endpoints**
  - [ ] `/api/clips` - List/create clips
  - [ ] `/api/clips/{clip_id}` - Get/update/delete clip
  - [ ] `/api/songs` - List/create songs
  - [ ] `/api/songs/{song_id}` - Get/update/delete song
  - [ ] `/api/playlists` - List/create playlists
  - [ ] `/api/sessions` - Session management
  - [ ] `/api/messages/{session_id}` - Message history

### Frontend

- [ ] **Create `ui/` folder** (Svelte + shadcn-svelte)
  - [ ] Carousel component (Embla)
  - [ ] Panel components (Clip, Song, Playlist, Pack)
  - [ ] Left drawer (item browser)
  - [ ] Right drawer (chat history)
  - [ ] Player controls
  - [ ] Message input (per-panel)

- [ ] **WebSocket client**
  - [ ] Connection management
  - [ ] Event handling
  - [ ] PWA tool handlers
  - [ ] Message queueing
  - [ ] Reconnection logic

- [ ] **State management** (Zustand)
  - [ ] Carousel state (panels, currentIndex)
  - [ ] Session state (per-panel)
  - [ ] Player state (isPlaying, loaded clips)
  - [ ] UI state (drawers, filters)

- [ ] **Strudel integration**
  - [ ] @strudel/web initialization
  - [ ] Clip playback (stack() combination)
  - [ ] Code evaluation
  - [ ] Player controls (play, stop, update)

---

## 10. Next Steps

**For backend developer**:
1. Review this document + [database_architecture.md](./database_architecture.md)
2. Set up FastAPI project structure
3. Copy relevant code from tooler_example
4. Adapt for Strudel-specific needs
5. Create MCP server for Strudel tools

**For frontend developer**:
1. Review this document
2. Review UI specification (`ui_specification.md`)
3. Set up Svelte + shadcn-svelte project
4. Implement WebSocket client (copy from tooler_example)
5. Build carousel interface
6. Integrate @strudel/web

**Collaboration points**:
- WebSocket message protocol (agree on message types)
- Tool request/response format
- Update event structure
- API endpoint contracts

---

## End of Analysis

This document provides a complete technical overview of the tooler_example architecture. Use this as a reference for implementing the Strudel Agent backend and frontend.

**Key takeaway**: The tooler_example provides a solid foundation for WebSocket communication, session management, and PWA integration. Adapt the multi-session chat architecture to a per-item carousel architecture for Strudel Agent.

**Also see**: [database_architecture.md](./database_architecture.md) for complete database documentation.
