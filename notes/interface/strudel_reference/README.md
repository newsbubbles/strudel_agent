# Strudel External Control Research

**Research Date:** 2025-12-25  
**Project:** Strudel (https://strudel.cc)  
**Goal:** Understand how to control Strudel REPL from external processes over network

---

## Executive Summary

### Question
> How can I control the Strudel REPL code editor and trigger evaluation from an external process over the network?

### Answer

**Strudel DOES have programmatic control APIs**, but **NO built-in network exposure** for incoming control.

**What exists:**
- ✅ JavaScript API: `StrudelMirror` class with `setCode()`, `evaluate()`, `stop()` methods
- ✅ DOM Custom Events: `repl-evaluate`, `repl-stop` for triggering actions
- ✅ Web Component: `<strudel-editor>` with `code` attribute
- ✅ Network OUTPUT: OSC and MQTT for sending audio events OUT to external systems
- ✅ **MIDI OUTPUT: Full MIDI support for sending notes/CC to external devices** 🎹
- ❌ Network INPUT: No built-in API for receiving control commands FROM external systems

**Solution:** Add a bridge layer using one of three approaches:

1. **Puppeteer** - Browser automation (zero code changes)
2. **UserScript + WebSocket** - Browser extension + server (works on strudel.cc)
3. **Fork + Native WebSocket** - Modify Strudel source (best performance)

### UPDATE: Embedding Solution

**For embedding in your own app**, you don't need network bridges! Just embed Strudel directly:

1. **`@strudel/web`** - Headless (no UI, perfect for custom controls) ⭐ **RECOMMENDED**
2. **`<strudel-editor>`** - Full editor (can hide/style)
3. **`@strudel/embed`** - Iframe embed (easiest)
4. **npm packages** - Manual integration (maximum control)

See **[embedding_guide.md](./embedding_guide.md)** for complete details!

### UPDATE: MIDI Output

**Strudel has full MIDI output support!** Send notes, CC, program changes, and more to external MIDI devices.

See **[midi_output_guide.md](./midi_output_guide.md)** for complete MIDI documentation!

---

## Quick Reference

### Key Files

| File | Purpose |
|------|--------|
| `packages/codemirror/codemirror.mjs` | StrudelMirror class - main control API |
| `packages/repl/repl-component.mjs` | Web Component wrapper |
| `packages/web/` | Headless bundle for custom UI |
| `packages/midi/midi.mjs` | MIDI output (WebMIDI) |
| `packages/desktopbridge/midibridge.mjs` | MIDI output (desktop app) |
| `packages/osc/osc.mjs` | OSC output client (WebSocket) |
| `packages/osc/server.js` | OSC bridge server (Node.js) |
| `packages/mqtt/mqtt.mjs` | MQTT output integration |

### Control Methods

#### Option 1: Embed with `@strudel/web` (Headless)

```html
<script src="https://unpkg.com/@strudel/web@latest"></script>
<button id="play">Play</button>
<button id="stop">Stop</button>

<script>
  initStrudel();
  
  document.getElementById('play').onclick = () => {
    evaluate('note("c e g").s("piano")');
  };
  
  document.getElementById('stop').onclick = () => {
    hush();
  };
</script>
```

#### Option 2: Embed with `<strudel-editor>`

```html
<script src="https://unpkg.com/@strudel/repl@latest"></script>
<strudel-editor id="myEditor">
  <!-- note("c e g").s("piano") -->
</strudel-editor>

<script>
  const editor = document.getElementById('myEditor').editor;
  editor.setCode('note("c a f e").s("piano")');
  editor.evaluate();
</script>
```

#### Option 3: MIDI Output

```javascript
// Send to MIDI device
note("c a f e").midi('IAC Driver Bus 1')

// With CC control
defaultmidimap({ lpf: 74 })
note("c e g").lpf(sine.slow(4).range(200, 2000)).midi()
```

#### Option 4: Remote Control (Network)

```javascript
// Method 1: Set code via Web Component
const editor = document.querySelector('strudel-editor');
editor.setAttribute('code', 'note("c e g").s("piano")');

// Method 2: Direct API call (if instance accessible)
window.strudelEditor.setCode('note("c e g").s("piano")');
window.strudelEditor.evaluate();

// Method 3: Custom Events (works from anywhere in DOM)
document.dispatchEvent(new CustomEvent('repl-evaluate'));
document.dispatchEvent(new CustomEvent('repl-stop'));
```

### Available Custom Events

- `repl-evaluate` - Triggers code evaluation
- `repl-stop` - Stops playback
- `repl-toggle-comment` - Toggles line comments
- `start-repl` - Internal event when REPL starts

---

## Documentation Files

### ⭐ [embedding_guide.md](./embedding_guide.md)

**Complete guide for embedding Strudel in your app:**
- 4 embedding methods compared
- Full code examples for each
- Custom UI patterns
- React integration
- Complete playlist player example
- API reference

**Use this if:** You want to embed Strudel in your own application

---

### ⭐ [midi_output_guide.md](./midi_output_guide.md) - NEW! 🎹

**Complete MIDI output documentation:**
- MIDI output capabilities (notes, CC, program change, etc.)
- Control mapping (midimap)
- MIDI input for control
- Recording MIDI to file (via DAW)
- Virtual MIDI setup (macOS/Windows/Linux)
- Complete examples

**Use this if:** You want to send MIDI from Strudel to external devices/software

---

### [embedding_quick_reference.md](./embedding_quick_reference.md)

**Quick decision tree and cheat sheet:**
- Decision flowchart
- Side-by-side comparison
- Common patterns
- API cheat sheet
- Troubleshooting

**Use this if:** You need a quick reference while coding

---

### [architecture_analysis.md](./architecture_analysis.md)

Comprehensive analysis of Strudel's architecture including:
- Project overview and structure
- Component breakdown
- Existing network features (OSC, MQTT, MIDI)
- External control strategies
- Code locations reference

**Key Diagrams:**
- Architecture overview
- Network exposure strategies
- Component interaction map

**Use this if:** You want to understand Strudel's internals

---

### [control_flow_diagrams.md](./control_flow_diagrams.md)

Visual diagrams showing:
- Current event flow
- External control via Puppeteer
- Proposed WebSocket control
- Proposed MQTT bidirectional control
- UserScript + WebSocket bridge
- Data flow from code update to audio output
- Architecture layers
- OSC bridge architecture
- Component interaction map
- State management flow

**Use this if:** You want visual architecture diagrams

---

### [implementation_guide.md](./implementation_guide.md)

Practical implementation examples for **remote network control**:
- **Approach 1:** Puppeteer (zero modifications)
- **Approach 2:** UserScript + WebSocket bridge
- **Approach 3:** Fork Strudel + native WebSocket
- Complete code examples for each approach
- HTTP API wrappers
- Python client examples
- Testing scripts

**Use this if:** You need to control Strudel over the network (e.g., from Python/Node.js)

---

## Decision Matrix

### For Embedding in Your App

| Use Case | Recommended Approach | File |
|----------|---------------------|------|
| Custom UI, no editor | `@strudel/web` | [embedding_guide.md](./embedding_guide.md) |
| Hide editor, keep audio | `<strudel-editor>` + CSS | [embedding_guide.md](./embedding_guide.md) |
| Full editor experience | `<strudel-editor>` | [embedding_guide.md](./embedding_guide.md) |
| Quick iframe embed | `@strudel/embed` | [embedding_guide.md](./embedding_guide.md) |
| Maximum control | npm packages | [embedding_guide.md](./embedding_guide.md) |

### For MIDI Output

| Use Case | Recommended Approach | File |
|----------|---------------------|------|
| Send MIDI notes | `.midi()` method | [midi_output_guide.md](./midi_output_guide.md) |
| Control external synth | MIDI CC + midimap | [midi_output_guide.md](./midi_output_guide.md) |
| Record MIDI patterns | Route to DAW | [midi_output_guide.md](./midi_output_guide.md) |
| MIDI input control | `midin()` function | [midi_output_guide.md](./midi_output_guide.md) |

### For Remote Network Control

| Use Case | Recommended Approach | File |
|----------|---------------------|------|
| Quick experimentation | Puppeteer | [implementation_guide.md](./implementation_guide.md) |
| Personal automation | UserScript + WebSocket | [implementation_guide.md](./implementation_guide.md) |
| Building a tool/product | Fork Strudel | [implementation_guide.md](./implementation_guide.md) |
| One-off script | Puppeteer | [implementation_guide.md](./implementation_guide.md) |
| Long-term integration | Fork or UserScript | [implementation_guide.md](./implementation_guide.md) |
| Production system | Fork Strudel | [implementation_guide.md](./implementation_guide.md) |

---

## Architecture Highlights

### Strudel is Modular

```
@strudel/core          → Pattern engine
@strudel/repl          → REPL logic  
@strudel/codemirror    → Editor (StrudelMirror)
@strudel/transpiler    → Code → AST
@strudel/webaudio      → Audio output (default)
@strudel/midi          → MIDI output (WebMIDI)
@strudel/web           → Headless bundle (no UI)
@strudel/embed         → Iframe embed helper
@strudel/osc           → OSC output (SuperDirt)
@strudel/mqtt          → MQTT output (IoT)
```

### Control Flow (Embedded)

```
Your App UI
    ↓
initStrudel() / <strudel-editor>
    ↓
evaluate(code) / editor.evaluate()
    ↓
REPL Engine
    ↓
Web Audio API / MIDI Output
    ↓
🔊 Sound Output / 🎹 MIDI Device
```

### Control Flow (Remote)

```
External Process
    ↓
[Bridge Layer] ← YOU NEED TO ADD THIS
    ↓
Browser (JavaScript)
    ↓
StrudelMirror.setCode() / evaluate()
    ↓
REPL Engine
    ↓
Web Audio API / MIDI Output
    ↓
🔊 Sound Output / 🎹 MIDI Device
```

---

## Existing Network Features

### MIDI Output (packages/midi/)

**Direction:** Strudel → External (MIDI devices/software)  
**Protocol:** WebMIDI API (browser) or native MIDI (desktop)  
**Purpose:** Send MIDI notes, CC, program changes, etc.  
**Use case:** Control external synths, drum machines, DAWs

**Quick example:**
```javascript
note("c a f e").midi('IAC Driver Bus 1')
```

**Recording:** Route to DAW via virtual MIDI, record there, export as .mid

---

### OSC Output (packages/osc/)

**Direction:** Strudel → External (SuperCollider/SuperDirt)  
**Protocol:** WebSocket (browser) → UDP OSC (server)  
**Purpose:** Send audio events to external audio engines  
**Cannot be used for:** Controlling the REPL

**Architecture:**
```
Browser (Strudel) 
    ↓ WebSocket (ws://localhost:8080)
Node.js Bridge Server
    ↓ UDP OSC (port 57120)
SuperCollider/SuperDirt
```

### MQTT Output (packages/mqtt/)

**Direction:** Strudel → External (IoT devices)  
**Protocol:** MQTT over WebSocket (WSS)  
**Purpose:** Send pattern events to MQTT broker  
**Potential:** Could be extended for bidirectional control

---

## Implementation Complexity

### Embedding (Easiest)

```html
<script src="https://unpkg.com/@strudel/web@latest"></script>
<button onclick="evaluate('note(\"c\")').play()">Play</button>
```

**Lines of code:** ~10  
**Setup time:** 2 minutes  
**Maintenance:** Easy

### MIDI Output (Easy)

```javascript
note("c e g b").midi('IAC Driver Bus 1')
```

**Lines of code:** 1 line!  
**Setup time:** 5 minutes (virtual MIDI setup)  
**Maintenance:** Easy

### Puppeteer (Easy)

```javascript
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto('https://strudel.cc');

// Control it!
await page.evaluate(() => {
  document.querySelector('strudel-editor').setAttribute('code', 'note("c")');
  document.dispatchEvent(new CustomEvent('repl-evaluate'));
});
```

**Lines of code:** ~50  
**Setup time:** 10 minutes  
**Maintenance:** Easy

### UserScript + WebSocket (Medium)

**Components:**
1. WebSocket server (Node.js) - ~100 lines
2. Tampermonkey script - ~50 lines
3. HTTP API wrapper - ~50 lines

**Lines of code:** ~200  
**Setup time:** 30 minutes  
**Maintenance:** Medium

### Fork Strudel (Advanced)

**Components:**
1. WebSocket client in Strudel - ~150 lines
2. Control API module - ~100 lines
3. Integration in REPL component - ~50 lines
4. Server (optional) - ~100 lines

**Lines of code:** ~400  
**Setup time:** 2-4 hours  
**Maintenance:** Requires keeping fork updated

---

## Next Steps

### For Embedding in Your App

1. Read **[embedding_guide.md](./embedding_guide.md)**
2. Choose your approach (likely `@strudel/web`)
3. Copy the example code
4. Customize your UI
5. Start live coding! 🎵

### For MIDI Output

1. Read **[midi_output_guide.md](./midi_output_guide.md)**
2. Set up virtual MIDI (IAC/loopMIDI)
3. Try basic MIDI output
4. Connect to your synth/DAW
5. Record your patterns! 🎹

### For Remote Network Control

1. Read **[implementation_guide.md](./implementation_guide.md)**
2. Decide on approach (see Decision Matrix)
3. Follow implementation guide for chosen approach
4. Test with simple patterns
5. Build your integration
6. Consider contributing back to Strudel if useful!

---

## Key Insights

1. **Strudel is browser-based** - runs entirely in browser using Web Audio API
2. **Easy to embed** - Multiple packages for different use cases
3. **Full MIDI support** - Send MIDI to external devices/software (real-time only)
4. **No built-in remote control** - designed for interactive use, not automation
5. **Good separation of concerns** - REPL logic is separate from UI
6. **Event-driven architecture** - uses CustomEvents for loose coupling
7. **Extensible via packages** - modular design makes it easy to add features
8. **Network features exist** - but only for OUTPUT (OSC, MQTT, MIDI)

---

## Potential Contributions to Strudel

If you implement a clean solution, consider contributing:

1. **Native WebSocket control API** - Add to core packages
2. **Bidirectional MQTT** - Extend existing MQTT package
3. **HTTP REST API** - Optional server for remote control
4. **MIDI file export** - Write patterns to .mid files
5. **Documentation** - How to control Strudel programmatically

**Repository:** https://codeberg.org/uzu/strudel  
**License:** AGPL-3.0-or-later (requires open source contributions)

---

## Resources

- **Strudel Website:** https://strudel.cc
- **Documentation:** https://strudel.cc/learn
- **MIDI Tutorial:** https://strudel.cc/learn/input-output/
- **Embedding Guide:** https://strudel.cc/technical-manual/project-start
- **npm Packages:** https://www.npmjs.com/search?q=%40strudel
- **Repository:** https://codeberg.org/uzu/strudel
- **Discord:** https://discord.com/invite/HGEdXmRkzT (TidalCycles)
- **Forum:** https://club.tidalcycles.org/

---

## Research Notes

All code examples in this research are MIT licensed and free to use.  
Strudel itself is AGPL-3.0-or-later - be aware of licensing if forking.

For questions or updates to this research, see the project repository.
