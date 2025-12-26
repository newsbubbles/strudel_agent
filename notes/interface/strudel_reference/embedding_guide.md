# Strudel Embedding Guide - Complete Control

**Date:** 2025-12-25  
**Purpose:** How to embed Strudel in your app with full programmatic control

---

## Overview

You have **4 main options** for embedding Strudel, ranked from "most UI" to "headless":

1. **Full REPL with Editor** - `<strudel-editor>` component (CodeMirror editor + controls)
2. **Iframe Embed** - `<strudel-repl>` via `@strudel/embed` (loads strudel.cc in iframe)
3. **Headless with Custom UI** - `@strudel/web` (no editor, full control)
4. **Manual Integration** - Import individual packages via npm

---

## Option 1: Full REPL Component (Most UI)

### What You Get
- ✅ Full CodeMirror editor
- ✅ Built-in play/stop controls
- ✅ Syntax highlighting
- ✅ Pattern visualization
- ✅ Can hide/customize controls

### Basic Usage

```html
<!DOCTYPE html>
<html>
<head>
  <title>Strudel Embedded</title>
</head>
<body>
  <!-- Load the REPL component -->
  <script src="https://unpkg.com/@strudel/repl@latest"></script>
  
  <!-- Embed the editor -->
  <strudel-editor id="myEditor">
    <!--
    note("c e g b").s("piano")
    -->
  </strudel-editor>

  <script>
    // Get reference to the editor
    const editor = document.getElementById('myEditor');
    
    // Listen for state changes
    editor.addEventListener('update', (event) => {
      console.log('REPL state:', event.detail);
      console.log('Playing:', event.detail.started);
    });
  </script>
</body>
</html>
```

### Programmatic Control

```javascript
// Wait for editor to be ready
const editor = document.getElementById('myEditor');

// Access the StrudelMirror instance
const strudelMirror = editor.editor;  // This is the StrudelMirror class instance!

// Now you have FULL control:

// 1. Update code
strudelMirror.setCode('note("<c e g b>").s("piano")');

// 2. Trigger evaluation
strudelMirror.evaluate();

// 3. Stop playback
strudelMirror.stop();

// 4. Toggle play/stop
strudelMirror.toggle();

// 5. Append code
strudelMirror.appendCode('.slow(2)');

// 6. Get current code
const currentCode = strudelMirror.code;

// 7. Check if playing
const isPlaying = strudelMirror.repl.scheduler.started;
```

### Alternative: Using Custom Events

```javascript
// You can also control via DOM events (from anywhere)

// Set code via attribute
const editor = document.getElementById('myEditor');
editor.setAttribute('code', 'note("c a f e").s("piano")');

// Trigger evaluation via custom event
document.dispatchEvent(new CustomEvent('repl-evaluate'));

// Stop via custom event
document.dispatchEvent(new CustomEvent('repl-stop'));
```

### Styling & Customization

```html
<style>
  /* Hide the editor UI, keep only the controls */
  strudel-editor .cm-editor {
    display: none;
  }
  
  /* Or hide everything and control programmatically */
  strudel-editor {
    display: none;
  }
  
  /* Custom size */
  strudel-editor {
    width: 800px;
    height: 400px;
  }
</style>

<!-- Your custom UI -->
<div id="customControls">
  <button onclick="playPattern()">Play</button>
  <button onclick="stopPattern()">Stop</button>
  <select id="patternSelect" onchange="changePattern()">
    <option value="pattern1">Pattern 1</option>
    <option value="pattern2">Pattern 2</option>
  </select>
</div>

<!-- Hidden Strudel editor (audio engine only) -->
<strudel-editor id="myEditor" style="display: none;">
  <!-- Initial code -->
</strudel-editor>

<script>
  const patterns = {
    pattern1: 'note("c e g").s("piano")',
    pattern2: 'note("<c e g b>").s("sawtooth").lpf(1000)'
  };
  
  function playPattern() {
    const editor = document.getElementById('myEditor').editor;
    editor.evaluate();
  }
  
  function stopPattern() {
    const editor = document.getElementById('myEditor').editor;
    editor.stop();
  }
  
  function changePattern() {
    const select = document.getElementById('patternSelect');
    const patternCode = patterns[select.value];
    
    const editor = document.getElementById('myEditor').editor;
    editor.setCode(patternCode);
    editor.evaluate();
  }
</script>
```

---

## Option 2: Iframe Embed (Easiest)

### What You Get
- ✅ Full strudel.cc experience
- ✅ Zero configuration
- ✅ Automatic updates
- ❌ Limited control (iframe sandbox)

### Basic Usage

```html
<!-- Option A: Direct iframe -->
<iframe 
  src="https://strudel.cc/?xwWRfuCE8TAR" 
  width="800" 
  height="600"
></iframe>

<!-- Option B: Using @strudel/embed -->
<script src="https://unpkg.com/@strudel/embed@latest"></script>
<strudel-repl>
  <!--
  note("c e g b").s("piano")
  -->
</strudel-repl>
```

### Controlling via postMessage

You can control an iframe using `postMessage`:

```javascript
const iframe = document.querySelector('iframe');

// Send code to iframe
iframe.contentWindow.postMessage({
  type: 'strudel-code',
  code: 'note("c a f e").s("piano")'
}, '*');

// Listen for events from iframe
window.addEventListener('message', (event) => {
  if (event.data.type === 'strudel-state') {
    console.log('Strudel state:', event.data);
  }
});
```

**Note:** This requires the iframe content to support postMessage (may need custom implementation).

---

## Option 3: Headless with Custom UI (Recommended for Full Control)

### What You Get
- ✅ No editor UI
- ✅ Full programmatic control
- ✅ Custom UI completely separate
- ✅ Lightweight
- ❌ No syntax highlighting (unless you add it)

### Basic Setup

```html
<!DOCTYPE html>
<html>
<head>
  <title>Headless Strudel</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    button {
      padding: 10px 20px;
      margin: 5px;
      font-size: 16px;
    }
    textarea {
      width: 100%;
      height: 200px;
      font-family: monospace;
      padding: 10px;
    }
  </style>
</head>
<body>
  <h1>Custom Strudel Controller</h1>
  
  <textarea id="codeInput">
note("c e g b").s("piano")
  </textarea>
  
  <div>
    <button id="playBtn">Play</button>
    <button id="stopBtn">Stop</button>
    <button id="evaluateBtn">Evaluate Code</button>
  </div>
  
  <div id="status">Status: Stopped</div>

  <!-- Load Strudel -->
  <script src="https://unpkg.com/@strudel/web@latest"></script>
  
  <script>
    // Initialize Strudel
    initStrudel({
      prebake: () => samples('github:tidalcycles/dirt-samples'),
    });
    
    let currentPattern = null;
    
    // Play button
    document.getElementById('playBtn').addEventListener('click', () => {
      const code = document.getElementById('codeInput').value;
      
      // Evaluate and play
      evaluate(code);
      
      document.getElementById('status').textContent = 'Status: Playing';
    });
    
    // Stop button
    document.getElementById('stopBtn').addEventListener('click', () => {
      hush();  // Stop all patterns
      document.getElementById('status').textContent = 'Status: Stopped';
    });
    
    // Evaluate button (parse without playing)
    document.getElementById('evaluateBtn').addEventListener('click', () => {
      const code = document.getElementById('codeInput').value;
      try {
        evaluate(code, false);  // Don't autostart
        alert('Code is valid!');
      } catch (err) {
        alert('Error: ' + err.message);
      }
    });
  </script>
</body>
</html>
```

### Advanced: Pattern Management

```javascript
initStrudel();

class PatternManager {
  constructor() {
    this.patterns = {};
    this.currentPattern = null;
  }
  
  // Store a pattern
  store(name, code) {
    this.patterns[name] = code;
  }
  
  // Play a stored pattern
  play(name) {
    if (!this.patterns[name]) {
      throw new Error(`Pattern "${name}" not found`);
    }
    
    this.stop();  // Stop current pattern
    evaluate(this.patterns[name]);
    this.currentPattern = name;
  }
  
  // Stop current pattern
  stop() {
    hush();
    this.currentPattern = null;
  }
  
  // List all patterns
  list() {
    return Object.keys(this.patterns);
  }
  
  // Get pattern code
  get(name) {
    return this.patterns[name];
  }
}

// Usage
const manager = new PatternManager();

manager.store('drums', 's("bd sd hh sd").fast(2)');
manager.store('bass', 'note("c2 e2 g2 a2").s("sawtooth").lpf(500)');
manager.store('melody', 'note("<c4 e4 g4 b4>").s("piano")');

// Play patterns
manager.play('drums');

setTimeout(() => {
  manager.play('bass');
}, 4000);

setTimeout(() => {
  manager.stop();
}, 8000);
```

### With React

```jsx
import { useEffect, useState } from 'react';
import { initStrudel, evaluate, hush } from '@strudel/web';

function StrudelPlayer() {
  const [code, setCode] = useState('note("c e g").s("piano")');
  const [isPlaying, setIsPlaying] = useState(false);
  
  useEffect(() => {
    // Initialize Strudel once
    initStrudel({
      prebake: () => samples('github:tidalcycles/dirt-samples'),
    });
  }, []);
  
  const play = () => {
    evaluate(code);
    setIsPlaying(true);
  };
  
  const stop = () => {
    hush();
    setIsPlaying(false);
  };
  
  return (
    <div>
      <textarea 
        value={code} 
        onChange={(e) => setCode(e.target.value)}
        rows={10}
        cols={50}
      />
      <div>
        <button onClick={play} disabled={isPlaying}>Play</button>
        <button onClick={stop} disabled={!isPlaying}>Stop</button>
      </div>
      <div>Status: {isPlaying ? 'Playing' : 'Stopped'}</div>
    </div>
  );
}

export default StrudelPlayer;
```

---

## Option 4: Manual Integration (npm packages)

### What You Get
- ✅ Maximum control
- ✅ Tree-shaking (smaller bundle)
- ✅ TypeScript support
- ✅ Custom build pipeline
- ❌ More complex setup

### Installation

```bash
npm install @strudel/core @strudel/webaudio @strudel/transpiler
```

### Usage

```javascript
import { repl } from '@strudel/core';
import { webaudioOutput, getAudioContext } from '@strudel/webaudio';
import { transpiler } from '@strudel/transpiler';

const replInstance = repl({
  defaultOutput: webaudioOutput,
  getTime: () => getAudioContext().currentTime,
  transpiler,
  onToggle: (started) => {
    console.log('Playing:', started);
  },
});

// Evaluate code
const code = 'note("c e g b").s("piano")';
replInstance.evaluate(code, true);

// Stop
replInstance.scheduler.stop();
```

---

## Comparison Table

| Feature | `<strudel-editor>` | `@strudel/embed` | `@strudel/web` | Manual npm |
|---------|-------------------|------------------|----------------|------------|
| **Editor UI** | ✅ Full | ✅ Full (iframe) | ❌ None | ❌ None |
| **Syntax Highlighting** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Programmatic Control** | ✅ Full | ⚠️ Limited | ✅ Full | ✅ Full |
| **Custom UI** | ✅ Can hide/style | ❌ Iframe | ✅ Complete | ✅ Complete |
| **Setup Complexity** | Low | Very Low | Low | Medium |
| **Bundle Size** | Medium | Small (iframe) | Small | Smallest |
| **Version Pinning** | ✅ Yes | ⚠️ No | ✅ Yes | ✅ Yes |
| **Offline Support** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |

---

## Complete Example: Custom Player with Playlist

```html
<!DOCTYPE html>
<html>
<head>
  <title>Strudel Playlist Player</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
    }
    .playlist {
      list-style: none;
      padding: 0;
    }
    .playlist li {
      padding: 10px;
      margin: 5px 0;
      background: #f0f0f0;
      cursor: pointer;
      border-radius: 5px;
    }
    .playlist li.active {
      background: #4CAF50;
      color: white;
    }
    .controls {
      margin: 20px 0;
    }
    button {
      padding: 10px 20px;
      margin: 5px;
      font-size: 16px;
      cursor: pointer;
    }
    #visualizer {
      width: 100%;
      height: 100px;
      background: #000;
      margin: 20px 0;
    }
  </style>
</head>
<body>
  <h1>🎵 Strudel Playlist Player</h1>
  
  <div class="controls">
    <button id="playBtn">▶️ Play</button>
    <button id="stopBtn">⏹️ Stop</button>
    <button id="nextBtn">⏭️ Next</button>
  </div>
  
  <div id="nowPlaying">Now Playing: None</div>
  
  <h2>Playlist</h2>
  <ul class="playlist" id="playlist"></ul>
  
  <canvas id="visualizer"></canvas>

  <script src="https://unpkg.com/@strudel/web@latest"></script>
  
  <script>
    // Initialize Strudel
    initStrudel({
      prebake: () => samples('github:tidalcycles/dirt-samples'),
    });
    
    // Playlist data
    const playlist = [
      {
        name: 'Piano Melody',
        code: 'note("<c e g b>").s("piano").slow(2)'
      },
      {
        name: 'Drum Beat',
        code: 's("bd sd hh sd").fast(2)'
      },
      {
        name: 'Bass Line',
        code: 'note("c2 e2 g2 a2").s("sawtooth").lpf(500)'
      },
      {
        name: 'Complex Pattern',
        code: 'stack(s("bd sd"), note("<c e g>").s("piano")).fast(1.5)'
      }
    ];
    
    let currentIndex = -1;
    let isPlaying = false;
    
    // Render playlist
    const playlistEl = document.getElementById('playlist');
    playlist.forEach((item, index) => {
      const li = document.createElement('li');
      li.textContent = item.name;
      li.onclick = () => playTrack(index);
      playlistEl.appendChild(li);
    });
    
    // Play track
    function playTrack(index) {
      currentIndex = index;
      const track = playlist[index];
      
      // Update UI
      document.querySelectorAll('.playlist li').forEach((li, i) => {
        li.classList.toggle('active', i === index);
      });
      document.getElementById('nowPlaying').textContent = `Now Playing: ${track.name}`;
      
      // Play
      evaluate(track.code);
      isPlaying = true;
    }
    
    // Controls
    document.getElementById('playBtn').addEventListener('click', () => {
      if (currentIndex === -1) {
        playTrack(0);
      } else {
        playTrack(currentIndex);
      }
    });
    
    document.getElementById('stopBtn').addEventListener('click', () => {
      hush();
      isPlaying = false;
      document.getElementById('nowPlaying').textContent = 'Now Playing: None';
    });
    
    document.getElementById('nextBtn').addEventListener('click', () => {
      const nextIndex = (currentIndex + 1) % playlist.length;
      playTrack(nextIndex);
    });
    
    // Simple visualizer
    const canvas = document.getElementById('visualizer');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = 100;
    
    function drawVisualizer() {
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      if (isPlaying) {
        ctx.fillStyle = '#4CAF50';
        const bars = 20;
        for (let i = 0; i < bars; i++) {
          const height = Math.random() * canvas.height;
          const x = (canvas.width / bars) * i;
          const width = canvas.width / bars - 2;
          ctx.fillRect(x, canvas.height - height, width, height);
        }
      }
      
      requestAnimationFrame(drawVisualizer);
    }
    
    drawVisualizer();
  </script>
</body>
</html>
```

---

## Key API Reference

### `<strudel-editor>` Component

```javascript
const editor = document.getElementById('myEditor');
const strudelMirror = editor.editor;

// Properties
strudelMirror.code                    // Current code
strudelMirror.repl                    // REPL instance
strudelMirror.repl.scheduler.started  // Is playing?

// Methods
strudelMirror.setCode(code)          // Set code
strudelMirror.evaluate(autostart)    // Evaluate (default autostart=true)
strudelMirror.stop()                 // Stop playback
strudelMirror.toggle()               // Toggle play/stop
strudelMirror.appendCode(code)       // Append code at cursor

// Events
editor.addEventListener('update', (e) => {
  console.log(e.detail);  // { started: bool, ... }
});
```

### `@strudel/web` Functions

```javascript
initStrudel(options)           // Initialize (call once)
evaluate(code, autostart)      // Evaluate code
hush()                         // Stop all patterns
note(pattern)                  // Create note pattern
s(pattern)                     // Create sound pattern
samples(url)                   // Load samples
// ... all Strudel pattern functions
```

---

## Recommended Approach for Your Use Case

### If you want:

**"Just play patterns with my own UI"**  
→ Use `@strudel/web` (Option 3)

**"Embed the editor but control it programmatically"**  
→ Use `<strudel-editor>` + hide/style it (Option 1)

**"Embed strudel.cc experience"**  
→ Use iframe or `@strudel/embed` (Option 2)

**"Maximum control, custom everything"**  
→ Use npm packages (Option 4)

---

## Next Steps

1. Choose your approach based on your needs
2. Copy the relevant example code
3. Customize the UI to match your app
4. Add your own controls, visualizations, etc.
5. Enjoy live coding! 🎵
