# Strudel Control Flow Diagrams

## 1. Current Event Flow (Built-in)

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant StrudelEditor as strudel-editor<br/>(Web Component)
    participant StrudelMirror as StrudelMirror<br/>(Editor Instance)
    participant REPL as REPL Engine
    participant WebAudio as Web Audio API
    
    User->>Browser: Press Ctrl+Enter
    Browser->>StrudelMirror: keymap triggers onEvaluate()
    StrudelMirror->>StrudelMirror: evaluate()
    StrudelMirror->>REPL: repl.evaluate(code)
    REPL->>REPL: Transpile & parse code
    REPL->>WebAudio: Schedule audio events
    WebAudio-->>User: 🎵 Sound output
    
    Note over Browser,StrudelMirror: Alternative: Via Custom Event
    User->>Browser: External script
    Browser->>Browser: document.dispatchEvent(<br/>'repl-evaluate')
    Browser->>StrudelMirror: onEvaluateRequest()
    StrudelMirror->>StrudelMirror: evaluate()
    StrudelMirror->>REPL: repl.evaluate(code)
```

---

## 2. External Control via Puppeteer

```mermaid
sequenceDiagram
    participant External as External Process<br/>(Python/Node)
    participant Puppeteer
    participant Browser as Chrome Browser
    participant Strudel as Strudel REPL
    participant Audio as Web Audio
    
    External->>Puppeteer: Launch browser
    Puppeteer->>Browser: Open strudel.cc
    Browser->>Strudel: Load REPL
    
    External->>Puppeteer: setCode("note('c e g')")
    Puppeteer->>Browser: page.evaluate()
    Browser->>Strudel: editor.setAttribute('code', ...)
    
    External->>Puppeteer: evaluate()
    Puppeteer->>Browser: page.evaluate()
    Browser->>Browser: dispatchEvent('repl-evaluate')
    Browser->>Strudel: Trigger evaluation
    Strudel->>Audio: Play pattern
    Audio-->>External: 🎵 Audio output
```

---

## 3. Proposed WebSocket Control (Custom Implementation)

```mermaid
sequenceDiagram
    participant External as External Process<br/>(Your App)
    participant WSServer as WebSocket Server<br/>(Node.js)
    participant Browser as Browser
    participant Strudel as Strudel REPL
    participant Audio as Web Audio
    
    Browser->>WSServer: Connect ws://localhost:9999
    WSServer-->>Browser: Connection established
    
    Note over External,WSServer: Send control command
    External->>WSServer: HTTP POST /send-code<br/>{code: "note('c')"}
    WSServer->>Browser: WebSocket message<br/>{action: "setCode", code: ...}
    Browser->>Strudel: strudelEditor.setCode(code)
    
    External->>WSServer: HTTP POST /evaluate
    WSServer->>Browser: {action: "evaluate"}
    Browser->>Browser: dispatchEvent('repl-evaluate')
    Browser->>Strudel: Trigger evaluation
    Strudel->>Audio: Play pattern
    
    Note over Browser,WSServer: Send state updates
    Strudel->>Browser: onUpdateState(state)
    Browser->>WSServer: WebSocket message<br/>{type: "state", playing: true}
    WSServer->>External: Broadcast state change
```

---

## 4. Proposed MQTT Bidirectional Control

```mermaid
sequenceDiagram
    participant External as External Process
    participant Broker as MQTT Broker<br/>(Mosquitto)
    participant Browser as Browser
    participant Strudel as Strudel REPL
    participant Audio as Web Audio
    
    Browser->>Broker: Connect (WSS)
    Browser->>Broker: Subscribe to /strudel/control
    External->>Broker: Connect
    External->>Broker: Subscribe to /strudel/state
    
    Note over External,Broker: Send control command
    External->>Broker: Publish /strudel/control<br/>{action: "setCode", code: ...}
    Broker->>Browser: Message received
    Browser->>Strudel: strudelEditor.setCode(code)
    
    External->>Broker: Publish /strudel/control<br/>{action: "evaluate"}
    Broker->>Browser: Message received
    Browser->>Browser: dispatchEvent('repl-evaluate')
    Browser->>Strudel: Trigger evaluation
    Strudel->>Audio: Play pattern
    
    Note over Browser,Broker: Publish state updates
    Strudel->>Browser: onUpdateState(state)
    Browser->>Broker: Publish /strudel/state<br/>{playing: true, code: ...}
    Broker->>External: Message received
    External->>External: Update UI / Log state
```

---

## 5. UserScript + WebSocket Bridge

```mermaid
sequenceDiagram
    participant External as External Process
    participant Bridge as WebSocket Bridge<br/>(Standalone Server)
    participant Browser as Browser<br/>(with UserScript)
    participant Strudel as Strudel REPL
    participant Audio as Web Audio
    
    Note over Browser: User loads strudel.cc
    Browser->>Browser: Tampermonkey injects script
    Browser->>Bridge: Connect ws://localhost:9999
    Bridge-->>Browser: Connection established
    
    External->>Bridge: HTTP API call<br/>POST /code {"code": "..."}
    Bridge->>Browser: WebSocket: {action: "setCode"}
    Browser->>Strudel: editor.setAttribute('code', ...)
    
    External->>Bridge: POST /evaluate
    Bridge->>Browser: WebSocket: {action: "evaluate"}
    Browser->>Browser: dispatchEvent('repl-evaluate')
    Browser->>Strudel: Trigger evaluation
    Strudel->>Audio: Play pattern
    
    Strudel->>Browser: State change event
    Browser->>Bridge: WebSocket: {type: "state", ...}
    Bridge->>External: WebHook / SSE / Polling
```

---

## 6. Data Flow: Code Update → Audio Output

```mermaid
graph TD
    START[External Code Update] --> METHOD{Control Method}
    
    METHOD -->|Puppeteer| PUPPET[page.evaluate]
    METHOD -->|WebSocket| WS[WebSocket Message]
    METHOD -->|MQTT| MQTT[MQTT Publish]
    METHOD -->|UserScript| SCRIPT[Injected Script]
    
    PUPPET --> SET_CODE[Set Code]
    WS --> SET_CODE
    MQTT --> SET_CODE
    SCRIPT --> SET_CODE
    
    SET_CODE --> DOM_ATTR["DOM: editor.setAttribute('code', ...)"]
    SET_CODE --> JS_API["JS: strudelEditor.setCode(...)"]
    
    DOM_ATTR --> EDITOR[StrudelMirror Instance]
    JS_API --> EDITOR
    
    EDITOR --> TRIGGER{Trigger Evaluation?}
    
    TRIGGER -->|Manual| EVENT["dispatchEvent('repl-evaluate')"]
    TRIGGER -->|Auto| EVAL[evaluate method]
    
    EVENT --> EVAL
    
    EVAL --> TRANSPILE[Transpile Code]
    TRANSPILE --> PARSE[Parse Pattern]
    PARSE --> SCHEDULE[Schedule Events]
    SCHEDULE --> WEBAUDIO[Web Audio API]
    WEBAUDIO --> OUTPUT[🎵 Audio Output]
    
    style SET_CODE fill:#e1f5ff
    style EVAL fill:#ffe1e1
    style OUTPUT fill:#e1ffe1
```

---

## 7. Architecture Layers

```mermaid
graph TB
    subgraph "Layer 1: External Control"
        EXT1[Python Script]
        EXT2[Node.js App]
        EXT3[HTTP API]
        EXT4[CLI Tool]
    end
    
    subgraph "Layer 2: Bridge/Transport"
        PUPPET[Puppeteer]
        WS[WebSocket Server]
        MQTT_B[MQTT Broker]
        HTTP[HTTP Server]
    end
    
    subgraph "Layer 3: Browser Integration"
        SCRIPT[UserScript]
        NATIVE[Native WS Client]
        MQTT_C[MQTT Client]
        INJECT[Injected Code]
    end
    
    subgraph "Layer 4: Strudel API"
        COMPONENT["Web Component<br/>&lt;strudel-editor&gt;"]
        MIRROR["StrudelMirror<br/>(Editor API)"]
        EVENTS["Custom Events<br/>(repl-evaluate)"]
    end
    
    subgraph "Layer 5: Core Engine"
        REPL[REPL Engine]
        TRANS[Transpiler]
        CORE[Core Pattern Engine]
    end
    
    subgraph "Layer 6: Output"
        AUDIO[Web Audio API]
        OSC_OUT[OSC Output]
        MIDI[MIDI Output]
    end
    
    EXT1 --> PUPPET
    EXT2 --> WS
    EXT3 --> HTTP
    EXT4 --> MQTT_B
    
    PUPPET --> INJECT
    WS --> NATIVE
    MQTT_B --> MQTT_C
    HTTP --> SCRIPT
    
    INJECT --> COMPONENT
    NATIVE --> COMPONENT
    MQTT_C --> COMPONENT
    SCRIPT --> COMPONENT
    
    COMPONENT --> MIRROR
    MIRROR --> EVENTS
    EVENTS --> MIRROR
    
    MIRROR --> REPL
    REPL --> TRANS
    TRANS --> CORE
    
    CORE --> AUDIO
    CORE --> OSC_OUT
    CORE --> MIDI
    
    style COMPONENT fill:#e1f5ff
    style MIRROR fill:#ffe1e1
    style EVENTS fill:#fff4e1
```

---

## 8. OSC Bridge Architecture (Existing)

```mermaid
graph LR
    subgraph "Browser"
        PATTERN[Strudel Pattern]
        OSC_CLIENT[OSC Client<br/>packages/osc/osc.mjs]
    end
    
    subgraph "Bridge Server (Node.js)"
        WS_SERVER[WebSocket Server<br/>:8080]
        OSC_SERVER[OSC UDP Client<br/>:57120]
    end
    
    subgraph "SuperCollider"
        SUPERDIRT[SuperDirt<br/>Audio Engine]
    end
    
    PATTERN -->|"onTrigger(hap)"| OSC_CLIENT
    OSC_CLIENT -->|"WebSocket<br/>{address, args, timestamp}"| WS_SERVER
    WS_SERVER -->|"UDP OSC<br/>/dirt/play"| OSC_SERVER
    OSC_SERVER --> SUPERDIRT
    SUPERDIRT -->|Audio| SPEAKERS[🔊]
    
    style OSC_CLIENT fill:#ffe1e1
    style WS_SERVER fill:#e1f5ff
    style OSC_SERVER fill:#fff4e1
```

**Note:** This is OUTPUT only (Strudel → SuperDirt). Cannot be used for REPL control.

---

## 9. Component Interaction Map

```mermaid
graph TB
    subgraph "UI Layer"
        WEB_COMP["&lt;strudel-editor&gt;<br/>Web Component"]
        CODEMIRROR["CodeMirror<br/>Text Editor"]
    end
    
    subgraph "Control Layer"
        STRUDEL_MIRROR["StrudelMirror<br/>Main API Class"]
        REPL_CORE["repl()<br/>Core REPL Function"]
    end
    
    subgraph "Processing Layer"
        TRANSPILER["Transpiler<br/>Code → AST"]
        PATTERN_ENGINE["Pattern Engine<br/>Core Logic"]
        SCHEDULER["Scheduler<br/>Event Timing"]
    end
    
    subgraph "Output Layer"
        WEBAUDIO["Web Audio<br/>Default Output"]
        OSC["OSC Output<br/>SuperDirt"]
        MIDI_OUT["MIDI Output"]
        DRAW["Draw/Visuals<br/>Canvas"]
    end
    
    subgraph "External Events"
        CUSTOM_EVENTS["Custom Events<br/>repl-evaluate<br/>repl-stop"]
        KEYBOARD["Keyboard<br/>Ctrl+Enter"]
    end
    
    WEB_COMP -->|"contains"| CODEMIRROR
    WEB_COMP -->|"creates"| STRUDEL_MIRROR
    STRUDEL_MIRROR -->|"wraps"| CODEMIRROR
    STRUDEL_MIRROR -->|"uses"| REPL_CORE
    
    CUSTOM_EVENTS -->|"triggers"| STRUDEL_MIRROR
    KEYBOARD -->|"triggers"| STRUDEL_MIRROR
    
    STRUDEL_MIRROR -->|"setCode()"| CODEMIRROR
    STRUDEL_MIRROR -->|"evaluate()"| REPL_CORE
    
    REPL_CORE -->|"transpile"| TRANSPILER
    TRANSPILER -->|"parse"| PATTERN_ENGINE
    PATTERN_ENGINE -->|"schedule"| SCHEDULER
    
    SCHEDULER -->|"trigger events"| WEBAUDIO
    SCHEDULER -->|"trigger events"| OSC
    SCHEDULER -->|"trigger events"| MIDI_OUT
    SCHEDULER -->|"trigger events"| DRAW
    
    style STRUDEL_MIRROR fill:#ffe1e1
    style CUSTOM_EVENTS fill:#e1ffe1
    style REPL_CORE fill:#e1f5ff
```

---

## 10. State Management Flow

```mermaid
stateDiagram-v2
    [*] --> Idle: REPL Loaded
    
    Idle --> CodeChanged: setCode() / setAttribute('code')
    CodeChanged --> Idle: Code updated in editor
    
    Idle --> Evaluating: evaluate() / 'repl-evaluate' event
    CodeChanged --> Evaluating: evaluate() / 'repl-evaluate' event
    
    Evaluating --> TranspilingCode: Transpile JavaScript
    TranspilingCode --> ParsingPattern: Parse mini notation
    ParsingPattern --> SchedulingEvents: Build event timeline
    
    SchedulingEvents --> Playing: Scheduler.start()
    Playing --> Playing: Trigger audio events
    
    Playing --> Stopped: stop() / 'repl-stop' event
    Stopped --> Idle: Cleanup
    
    Playing --> Evaluating: Re-evaluate (new code)
    
    note right of Idle
        External control enters here:
        - setCode()
        - Custom events
    end note
    
    note right of Playing
        Audio output active
        Pattern running
    end note
```

---

## Summary

These diagrams illustrate:

1. **Built-in event flow** - How Strudel currently handles evaluation
2. **External control options** - Different architectural approaches
3. **Data flow** - From code update to audio output
4. **Layer architecture** - How components stack
5. **OSC bridge** - Existing network integration (output only)
6. **Component interactions** - How classes relate
7. **State management** - REPL lifecycle

The key insight: **Strudel has the API hooks (`setCode()`, custom events) but lacks built-in network exposure**. Any external control requires adding a bridge layer.
