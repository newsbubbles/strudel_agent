# Strudel MIDI Output Guide

**Date:** 2025-12-25  
**Purpose:** How to get MIDI output from Strudel patterns

---

## Executive Summary

**YES! Strudel has full MIDI output support** 🎹

You can:
- ✅ Send MIDI notes to external hardware/software
- ✅ Send MIDI CC (control change) messages
- ✅ Send program changes, pitch bend, aftertouch
- ✅ Send NRPN, SysEx messages
- ✅ Use multiple MIDI channels
- ✅ Map Strudel controls to MIDI CC automatically
- ✅ Receive MIDI input for control

**Two implementations:**
1. **Browser (WebMIDI)** - `@strudel/midi` package (most common)
2. **Desktop App** - `@strudel/desktopbridge` (for Tauri app)

---

## Quick Start

### Basic MIDI Output

```javascript
// Send notes to MIDI device
note("c a f e").midi('IAC Driver Bus 1')

// With MIDI channel
note("c a f e").midichan(2).midi('IAC Driver Bus 1')

// Multiple patterns to different devices
stack(
  note("c3 e3 g3").midichan(1).midi('Device A'),
  note("c4 e4 g4").midichan(2).midi('Device B')
)
```

### MIDI CC (Control Change)

```javascript
// Send CC messages
ccn(74).ccv(sine.slow(4)).midi('IAC Driver Bus 1')

// Map Strudel controls to CC automatically
defaultmidimap({ lpf: 74, resonance: 71 })
note("c a f e")
  .lpf(sine.slow(4).range(200, 2000))
  .resonance(0.5)
  .midi()
```

---

## Architecture

### Browser Implementation (`@strudel/midi`)

```
Strudel Pattern
    ↓
.midi() method
    ↓
Web MIDI API (browser)
    ↓
MIDI Device (hardware/software)
```

**Package:** `packages/midi/midi.mjs`  
**Uses:** [WebMIDI.js](https://github.com/djipco/webmidi) library  
**Browser Support:** Chrome, Edge, Opera (requires MIDI access permission)

### Desktop Implementation (`@strudel/desktopbridge`)

```
Strudel Pattern
    ↓
.midi() method
    ↓
Tauri IPC (Invoke)
    ↓
Rust Backend
    ↓
Native MIDI (CoreMIDI/ALSA/Windows MIDI)
```

**Package:** `packages/desktopbridge/midibridge.mjs`  
**Uses:** Tauri IPC to Rust backend  
**Platform:** Desktop app only (macOS, Linux, Windows)

---

## Complete API Reference

### `.midi(device, options)`

Sends pattern events as MIDI messages.

**Parameters:**
- `device` (string | number) - MIDI device name or index (default: 0)
- `options` (object) - Configuration options

**Options:**
```javascript
{
  isController: false,     // Disable note messages (for MIDI controllers)
  noteOffsetMs: 10,        // Note-off offset to prevent glitching
  midichannel: 1,          // Default MIDI channel
  velocity: 0.9,           // Default velocity (0-1)
  gain: 1,                 // Default gain multiplier
  midimap: 'default'       // MIDI control mapping name
}
```

**Example:**
```javascript
note("c e g b").midi('IAC Driver Bus 1', {
  midichannel: 2,
  velocity: 0.8,
  noteOffsetMs: 5
})
```

---

## MIDI Message Types

### 1. Note Messages

```javascript
// Basic notes
note("c4 e4 g4").midi()

// With velocity
note("c4 e4 g4").velocity(0.7).midi()

// With gain (multiplies velocity)
note("c4 e4 g4").gain(0.5).velocity(0.8).midi() // effective velocity: 0.4

// MIDI note numbers directly
n("60 64 67").midi()

// On specific channel
note("c4 e4 g4").midichan(3).midi()
```

**Hap Value Fields:**
- `note` - Note name ("c4") or MIDI number (60)
- `velocity` - Note velocity (0-1, default 0.9)
- `gain` - Gain multiplier (0-1, default 1)
- `midichan` - MIDI channel (1-16, default 1)

---

### 2. Control Change (CC)

```javascript
// Direct CC messages
ccn(74).ccv(sine.slow(4)).midi()

// Multiple CCs
stack(
  ccn(74).ccv(sine.slow(4)),      // Filter cutoff
  ccn(71).ccv(cosine.slow(3))     // Resonance
).midi()

// CC with notes
note("c e g").ccn(74).ccv(0.5).midi()
```

**Hap Value Fields:**
- `ccn` - CC number (0-127)
- `ccv` - CC value (0-1, scaled to 0-127)

---

### 3. Program Change

```javascript
// Change MIDI program/patch
progNum("<0 10 20 30>").slow(4).midi()

// With notes
note("c e g").progNum(5).midi()
```

**Hap Value Fields:**
- `progNum` - Program number (0-127)

---

### 4. Pitch Bend

```javascript
// Pitch bend
midibend(sine.slow(2)).midi()

// With notes
note("c4").midibend(0.5).midi()
```

**Hap Value Fields:**
- `midibend` - Bend amount (-1 to 1)

---

### 5. Channel Aftertouch

```javascript
// Aftertouch
miditouch(sine.slow(3)).midi()

// With notes
note("c4").miditouch(0.7).midi()
```

**Hap Value Fields:**
- `miditouch` - Aftertouch amount (0-1)

---

### 6. NRPN (Non-Registered Parameter Number)

```javascript
// NRPN messages
nrpnn(100).nrpv(64).midi()
```

**Hap Value Fields:**
- `nrpnn` - NRPN number (0-255 or array)
- `nrpv` - NRPN value (0-255)

---

### 7. SysEx (System Exclusive)

```javascript
// SysEx messages
sysexid(0x41).sysexdata([0x10, 0x42, 0x12]).midi()

// Manufacturer ID as array (3 bytes)
sysexid([0x00, 0x01, 0x02]).sysexdata([0x10, 0x20]).midi()
```

**Hap Value Fields:**
- `sysexid` - Manufacturer ID (0-255 or array of 3 bytes)
- `sysexdata` - Data bytes (array of 0-255)

**Manufacturer IDs:** https://midi.org/sysexidtable

---

### 8. MIDI Clock/Transport

```javascript
// MIDI clock
midicmd("clock").midi()

// Start/Stop/Continue
midicmd("start").midi()
midicmd("stop").midi()
midicmd("continue").midi()
```

**Hap Value Fields:**
- `midicmd` - Command: "clock", "start", "stop", "continue"

---

## MIDI Control Mapping (midimap)

### Concept

Instead of manually sending CC messages, you can map Strudel controls (like `lpf`, `resonance`) to MIDI CC numbers. Strudel will automatically send CC messages when these controls change.

### Default Mapping

```javascript
// Define default mapping
defaultmidimap({
  lpf: 74,        // Map lpf to CC 74
  resonance: 71,  // Map resonance to CC 71
  pan: 10         // Map pan to CC 10
})

// Now these controls automatically send CC
note("c a f e")
  .lpf(sine.slow(4).range(200, 2000))  // Sends CC 74
  .resonance(0.5)                       // Sends CC 71
  .pan(0.7)                             // Sends CC 10
  .midi()
```

### Advanced Mapping (with scaling)

```javascript
defaultmidimap({
  lpf: {
    ccn: 74,           // CC number
    min: 0,            // Minimum input value
    max: 20000,        // Maximum input value
    exp: 0.5           // Exponential curve (1 = linear)
  },
  resonance: {
    ccn: 71,
    min: 0,
    max: 10,
    exp: 1
  }
})

note("c a f e")
  .lpf(sine.slow(2).range(400, 2000))  // Scaled from 400-2000 to 0-127
  .resonance(5)                         // Scaled from 0-10 to 0-127
  .midi()
```

**Scaling formula:**
```javascript
normalized = ((value - min) / (max - min)) ** exp
cc_value = Math.round(normalized * 127)
```

### Named Mappings

```javascript
// Define multiple mappings
midimaps({
  mysynth: {
    lpf: 74,
    resonance: 71,
    attack: 73
  },
  mydrum: {
    decay: 80,
    tone: 81
  }
})

// Use specific mapping
note("c e g").lpf(1000).midimap('mysynth').midi()
note("bd sd").decay(0.3).midimap('mydrum').midi()
```

### Load Mappings from URL

```javascript
// Load from GitHub
await midimaps('github:user/repo/branch')
// Expects midimap.json at root

// Load from URL
await midimaps('https://example.com/mymaps.json')

// Format:
// {
//   "mapping1": { "lpf": 74, "resonance": 71 },
//   "mapping2": { "attack": 73, "decay": 75 }
// }
```

---

## MIDI Input (`midin`)

Receive MIDI CC messages and use them to control patterns.

```javascript
// Get MIDI input function
const cc = await midin('IAC Driver Bus 1')

// Use CC values in patterns
note("c a f e")
  .lpf(cc(74).range(200, 2000))   // CC 74 controls filter
  .resonance(cc(71).range(0, 10)) // CC 71 controls resonance
  .sound("sawtooth")

// Specific MIDI channel
const cc = await midin('IAC Driver Bus 1')
const cc2 = (ccNum) => cc(ccNum, 2) // Only channel 2

note("c e g").lpf(cc2(74).range(200, 2000))

// Conditional logic based on CC
note("c a f e")
  .sound("sawtooth")
  .when(cc(64).gt(0.5), x => x.lpf(500)) // When CC 64 > 0.5
```

**Returns:** Function `(ccNum, channel?) => Pattern`
- `ccNum` - CC number to query (0-127)
- `channel` - Optional MIDI channel (1-16)
- Returns a Pattern that produces the most recent CC value (0-1)

---

## Device Selection

### By Name

```javascript
// Exact match (case-sensitive, partial match)
note("c e g").midi('IAC Driver Bus 1')
note("c e g").midi('IAC')  // Matches first device with "IAC" in name
```

### By Index

```javascript
// First device (default)
note("c e g").midi(0)

// Second device
note("c e g").midi(1)
```

### List Available Devices

Check browser console after enabling WebMIDI:

```javascript
import { enableWebMidi } from '@strudel/midi'

await enableWebMidi({
  onEnabled: ({ outputs, inputs }) => {
    console.log('Outputs:', outputs.map(o => o.name))
    console.log('Inputs:', inputs.map(i => i.name))
  }
})
```

### Default Device

If no device specified:
1. Tries to find first device with "IAC" in name
2. Falls back to first available device

---

## Complete Examples

### Example 1: Drum Machine to MIDI

```javascript
// Map drum sounds to MIDI notes
stack(
  s("bd").n(36).midichan(10).midi(),      // Kick on note 36, channel 10
  s("sd").n(38).midichan(10).midi(),      // Snare on note 38, channel 10
  s("hh").n(42).midichan(10).midi(),      // Hi-hat on note 42, channel 10
)
```

### Example 2: Generative Synth with CC

```javascript
defaultmidimap({
  lpf: 74,
  resonance: 71,
  attack: 73,
  release: 72
})

stack(
  // Melody
  note("<c4 e4 g4 b4>")
    .lpf(sine.slow(4).range(200, 2000))
    .resonance(cosine.slow(3).range(0, 10))
    .attack(0.1)
    .release(0.5)
    .midichan(1),
  
  // Bass
  note("c2 e2 g2 a2")
    .lpf(500)
    .attack(0.01)
    .release(0.3)
    .midichan(2)
).midi('My Synth')
```

### Example 3: MIDI Controller Mode

```javascript
// Send only CC messages, no notes
defaultmidimap({
  lpf: 74,
  resonance: 71,
  pan: 10
})

stack(
  lpf(sine.slow(4).range(200, 2000)),
  resonance(cosine.slow(3).range(0, 10)),
  pan(saw.slow(2).range(0, 1))
).midi('My Device', { isController: true })
```

### Example 4: Multiple Devices

```javascript
// Send to different devices
stack(
  note("c4 e4 g4").midichan(1).midi('Synth A'),
  note("c3 e3 g3").midichan(1).midi('Synth B'),
  s("bd sd hh").n("<36 38 42>").midichan(10).midi('Drum Machine')
)
```

### Example 5: MIDI Input Control

```javascript
const cc = await midin('My MIDI Controller')

// Use hardware knobs to control synthesis
note("c a f e")
  .sound("sawtooth")
  .lpf(cc(1).range(200, 5000))      // Knob 1 -> Filter
  .resonance(cc(2).range(0, 20))    // Knob 2 -> Resonance
  .gain(cc(7).range(0, 1))          // Knob 7 -> Volume
  .pan(cc(10).range(0, 1))          // Knob 10 -> Pan
```

### Example 6: Program Changes

```javascript
// Change synth patches every 4 beats
stack(
  progNum("<0 10 20 30>").slow(4).midi(),
  note("c4 e4 g4 b4").midi()
)
```

### Example 7: Pitch Bend

```javascript
// Smooth pitch bends
stack(
  note("c4").sustain(4).midi(),
  midibend(sine.slow(4).range(-1, 1)).midi()
)
```

---

## Recording MIDI to File

**Important:** Strudel sends MIDI in real-time only. To record MIDI to a file:

### Option 1: Use DAW/Software

1. Route Strudel MIDI output to a DAW (Ableton, Logic, Reaper, etc.)
2. Record MIDI in the DAW
3. Export as .mid file

**Setup:**
```javascript
// macOS: Use IAC Driver
note("c a f e").midi('IAC Driver Bus 1')
// In DAW: Set MIDI input to "IAC Driver Bus 1"

// Windows: Use loopMIDI or similar
// Linux: Use JACK MIDI
```

### Option 2: MIDI Recording Software

Use dedicated MIDI recording software:
- **macOS:** MIDI Monitor, MidiPipe
- **Windows:** MIDI-OX, MidiView
- **Linux:** QMidiRoute, Mididings
- **Cross-platform:** MidiEditor

### Option 3: Custom Solution (Advanced)

Capture MIDI messages in JavaScript and write to .mid file:

```javascript
import { enableWebMidi } from '@strudel/midi'
import { MidiWriter } from 'midi-writer-js' // External library

const track = new MidiWriter.Track()
const events = []

// Intercept MIDI messages
const originalMidi = Pattern.prototype.midi
Pattern.prototype.midi = function(...args) {
  return this.onTrigger((hap, ct, cps, tt) => {
    // Capture MIDI data
    const { note, velocity, duration } = hap.value
    events.push({
      time: tt,
      note,
      velocity,
      duration: (hap.duration.valueOf() / cps) * 1000
    })
  }).fmap(originalMidi.bind(this)(...args))
}

// After recording, write to file
function saveMidi() {
  events.forEach(e => {
    track.addEvent(new MidiWriter.NoteEvent({
      pitch: e.note,
      duration: `T${Math.round(e.duration)}`,
      velocity: Math.round(e.velocity * 127)
    }))
  })
  
  const write = new MidiWriter.Writer(track)
  const blob = new Blob([write.buildFile()], { type: 'audio/midi' })
  const url = URL.createObjectURL(blob)
  
  // Download
  const a = document.createElement('a')
  a.href = url
  a.download = 'strudel.mid'
  a.click()
}
```

**Note:** This is a simplified example. Real implementation would need:
- Proper timing quantization
- Multiple track support
- CC/program change handling
- Tempo mapping

---

## Browser MIDI Permissions

### First-Time Setup

1. Browser will prompt for MIDI access permission
2. User must allow access
3. Permission is remembered for the domain

### Troubleshooting

**"MIDI not enabled" error:**
```javascript
import { enableWebMidi } from '@strudel/midi'

// Explicitly enable (returns promise)
await enableWebMidi()

// Or with callbacks
await enableWebMidi({
  onEnabled: (webmidi) => console.log('MIDI ready!'),
  onConnected: (webmidi) => console.log('Device connected'),
  onDisconnected: (webmidi, event) => console.log('Device disconnected')
})
```

**Browser compatibility:**
- ✅ Chrome/Chromium
- ✅ Edge
- ✅ Opera
- ❌ Firefox (no WebMIDI support)
- ❌ Safari (no WebMIDI support)

**Firefox/Safari workaround:**
- Use [Web MIDI API Polyfill](https://github.com/cwilso/WebMIDIAPIShim)
- Or use desktop app version

---

## Virtual MIDI Setup

### macOS

**IAC Driver (built-in):**

1. Open **Audio MIDI Setup** (Applications > Utilities)
2. Window menu > Show MIDI Studio
3. Double-click "IAC Driver"
4. Check "Device is online"
5. Add ports if needed

Now use:
```javascript
note("c a f e").midi('IAC Driver Bus 1')
```

### Windows

**loopMIDI (free):**

1. Download [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Install and run
3. Create a virtual port (e.g., "Strudel")

Now use:
```javascript
note("c a f e").midi('Strudel')
```

### Linux

**ALSA (built-in):**

```bash
# Create virtual port
sudo modprobe snd-virmidi

# List ports
aconnect -l
```

Or use **JACK MIDI**:

```bash
# Start JACK
jackd -d alsa

# Create MIDI bridge
a2jmidid -e
```

---

## API Summary

### Pattern Methods

| Method | Purpose | Example |
|--------|---------|----------|
| `.midi(device, options)` | Send MIDI output | `.midi('IAC')` |
| `.midichan(n)` | Set MIDI channel | `.midichan(2)` |
| `.velocity(v)` | Set note velocity | `.velocity(0.8)` |
| `.gain(g)` | Multiply velocity | `.gain(0.5)` |
| `.ccn(n)` | CC number | `.ccn(74)` |
| `.ccv(v)` | CC value | `.ccv(0.5)` |
| `.progNum(n)` | Program change | `.progNum(10)` |
| `.midibend(v)` | Pitch bend | `.midibend(0.5)` |
| `.miditouch(v)` | Aftertouch | `.miditouch(0.7)` |
| `.nrpnn(n)` | NRPN number | `.nrpnn(100)` |
| `.nrpv(v)` | NRPN value | `.nrpv(64)` |
| `.sysexid(id)` | SysEx ID | `.sysexid(0x41)` |
| `.sysexdata(data)` | SysEx data | `.sysexdata([0x10])` |
| `.midicmd(cmd)` | MIDI command | `.midicmd('clock')` |
| `.midimap(name)` | Use named mapping | `.midimap('mysynth')` |

### Global Functions

| Function | Purpose | Example |
|----------|---------|----------|
| `enableWebMidi(options)` | Enable MIDI | `await enableWebMidi()` |
| `defaultmidimap(mapping)` | Set default CC map | `defaultmidimap({lpf: 74})` |
| `midimaps(maps)` | Add named CC maps | `midimaps({mymap: {...}})` |
| `midin(device)` | Get MIDI input | `const cc = await midin('IAC')` |

---

## Key Insights from Architecture

1. **Real-time only** - MIDI is sent during playback, not pre-rendered
2. **WebMIDI based** - Uses browser's native MIDI API (Chrome/Edge only)
3. **Flexible mapping** - Can map any Strudel control to MIDI CC
4. **Multiple devices** - Can send to multiple MIDI devices simultaneously
5. **Full MIDI spec** - Supports notes, CC, program change, SysEx, etc.
6. **Bidirectional** - Can both send and receive MIDI

---

## Recording MIDI - Best Practices

### Recommended Workflow

1. **Compose in Strudel** - Use live coding to create patterns
2. **Route to DAW** - Use virtual MIDI (IAC/loopMIDI)
3. **Record in DAW** - Capture MIDI in real-time
4. **Export .mid** - Save as MIDI file from DAW
5. **Edit if needed** - Quantize, clean up in MIDI editor

### Why not export directly from Strudel?

- Strudel is designed for live performance
- Patterns are infinite/generative
- Timing is relative to playback
- No built-in MIDI file writer

### Alternative: Render to Audio

If you just need audio (not MIDI):
```javascript
// Use Strudel's audio output instead
note("c a f e").sound("piano")
// Record audio with browser's MediaRecorder API
```

---

## Resources

- **WebMIDI.js Docs:** https://webmidijs.org/
- **MIDI Specification:** https://www.midi.org/specifications
- **Strudel MIDI Tutorial:** https://strudel.cc/learn/input-output/
- **MIDI CC List:** https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2
- **General MIDI:** https://www.midi.org/specifications-old/item/gm-level-1-sound-set

---

## Next Steps

1. Enable MIDI in your browser
2. Set up virtual MIDI (IAC/loopMIDI)
3. Try basic note output
4. Experiment with CC mappings
5. Connect to your DAW/synth
6. Record your patterns!

🎹 Happy MIDI coding!
