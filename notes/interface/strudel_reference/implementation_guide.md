# Strudel External Control - Implementation Guide

## Quick Start: Three Practical Approaches

---

## Approach 1: Puppeteer (Zero Strudel Modifications)

### Setup

```bash
npm install puppeteer
```

### Implementation

**File:** `strudel-controller.js`

```javascript
const puppeteer = require('puppeteer');

class StrudelController {
  constructor() {
    this.browser = null;
    this.page = null;
  }

  async connect(url = 'http://localhost:3000') {
    this.browser = await puppeteer.launch({
      headless: false,  // Set to true for headless operation
      args: ['--autoplay-policy=no-user-gesture-required']  // Allow audio
    });
    
    this.page = await this.browser.newPage();
    await this.page.goto(url);
    
    // Wait for Strudel to load
    await this.page.waitForSelector('strudel-editor', { timeout: 10000 });
    console.log('Connected to Strudel REPL');
  }

  async setCode(code) {
    await this.page.evaluate((code) => {
      const editor = document.querySelector('strudel-editor');
      if (editor) {
        editor.setAttribute('code', code);
      } else {
        throw new Error('strudel-editor element not found');
      }
    }, code);
  }

  async evaluate() {
    await this.page.evaluate(() => {
      const event = new CustomEvent('repl-evaluate', {
        detail: { source: 'external' },
        cancelable: true
      });
      document.dispatchEvent(event);
    });
  }

  async stop() {
    await this.page.evaluate(() => {
      const event = new CustomEvent('repl-stop', {
        detail: { source: 'external' },
        cancelable: true
      });
      document.dispatchEvent(event);
    });
  }

  async setCodeAndEvaluate(code) {
    await this.setCode(code);
    await new Promise(resolve => setTimeout(resolve, 100));  // Small delay
    await this.evaluate();
  }

  async getState() {
    return await this.page.evaluate(() => {
      const editor = document.querySelector('strudel-editor');
      return {
        code: editor?.getAttribute('code') || '',
        // Add more state extraction as needed
      };
    });
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }
}

// Usage example
async function main() {
  const strudel = new StrudelController();
  
  try {
    await strudel.connect('https://strudel.cc');
    
    // Play a simple pattern
    await strudel.setCodeAndEvaluate('note("c e g").s("piano")');
    
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Change pattern
    await strudel.setCodeAndEvaluate('note("<c e g b>").s("sawtooth").lpf(2000)');
    
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Stop
    await strudel.stop();
    
  } catch (err) {
    console.error('Error:', err);
  } finally {
    await strudel.close();
  }
}

main();
```

### HTTP API Wrapper

**File:** `strudel-api-server.js`

```javascript
const express = require('express');
const { StrudelController } = require('./strudel-controller');

const app = express();
app.use(express.json());

let strudel = null;

app.post('/connect', async (req, res) => {
  try {
    strudel = new StrudelController();
    await strudel.connect(req.body.url || 'https://strudel.cc');
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/code', async (req, res) => {
  try {
    if (!strudel) throw new Error('Not connected');
    await strudel.setCode(req.body.code);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/evaluate', async (req, res) => {
  try {
    if (!strudel) throw new Error('Not connected');
    
    if (req.body.code) {
      await strudel.setCodeAndEvaluate(req.body.code);
    } else {
      await strudel.evaluate();
    }
    
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/stop', async (req, res) => {
  try {
    if (!strudel) throw new Error('Not connected');
    await strudel.stop();
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/state', async (req, res) => {
  try {
    if (!strudel) throw new Error('Not connected');
    const state = await strudel.getState();
    res.json(state);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Strudel API server running on port ${PORT}`);
});
```

### Usage from Python

```python
import requests
import time

class StrudelClient:
    def __init__(self, api_url='http://localhost:3001'):
        self.api_url = api_url
    
    def connect(self, strudel_url='https://strudel.cc'):
        response = requests.post(f'{self.api_url}/connect', 
                                json={'url': strudel_url})
        return response.json()
    
    def set_code(self, code):
        response = requests.post(f'{self.api_url}/code', 
                                json={'code': code})
        return response.json()
    
    def evaluate(self, code=None):
        payload = {'code': code} if code else {}
        response = requests.post(f'{self.api_url}/evaluate', json=payload)
        return response.json()
    
    def stop(self):
        response = requests.post(f'{self.api_url}/stop')
        return response.json()
    
    def get_state(self):
        response = requests.get(f'{self.api_url}/state')
        return response.json()

# Usage
strudel = StrudelClient()
strudel.connect()

# Play pattern
strudel.evaluate('note("c e g").s("piano")')
time.sleep(5)

# Change pattern
strudel.evaluate('note("<c e g b>").s("sawtooth").lpf(2000)')
time.sleep(5)

# Stop
strudel.stop()
```

---

## Approach 2: UserScript + WebSocket Bridge

### Part A: WebSocket Bridge Server

**File:** `websocket-bridge.js`

```javascript
const WebSocket = require('ws');
const express = require('express');

const app = express();
app.use(express.json());

const wss = new WebSocket.Server({ port: 9999 });
const clients = new Set();

wss.on('connection', (ws) => {
  console.log('Browser connected');
  clients.add(ws);
  
  ws.on('close', () => {
    clients.delete(ws);
    console.log('Browser disconnected');
  });
  
  ws.on('message', (data) => {
    // Handle messages from browser (state updates, etc.)
    console.log('From browser:', data.toString());
  });
});

function broadcast(message) {
  const payload = JSON.stringify(message);
  clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(payload);
    }
  });
}

// HTTP API for external control
app.post('/code', (req, res) => {
  broadcast({
    action: 'setCode',
    code: req.body.code
  });
  res.json({ success: true });
});

app.post('/evaluate', (req, res) => {
  if (req.body.code) {
    broadcast({ action: 'setCode', code: req.body.code });
    setTimeout(() => {
      broadcast({ action: 'evaluate' });
    }, 100);
  } else {
    broadcast({ action: 'evaluate' });
  }
  res.json({ success: true });
});

app.post('/stop', (req, res) => {
  broadcast({ action: 'stop' });
  res.json({ success: true });
});

const HTTP_PORT = 3002;
app.listen(HTTP_PORT, () => {
  console.log(`HTTP API listening on port ${HTTP_PORT}`);
  console.log(`WebSocket server listening on port 9999`);
});
```

### Part B: Tampermonkey UserScript

**File:** `strudel-control.user.js`

```javascript
// ==UserScript==
// @name         Strudel External Control
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Allow external control of Strudel REPL via WebSocket
// @author       You
// @match        https://strudel.cc/*
// @match        http://localhost:3000/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    console.log('[Strudel Control] Initializing...');

    let ws = null;
    let reconnectInterval = null;

    function connect() {
        try {
            ws = new WebSocket('ws://localhost:9999');

            ws.onopen = () => {
                console.log('[Strudel Control] Connected to control server');
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('[Strudel Control] Received:', data);

                    switch(data.action) {
                        case 'setCode':
                            const editor = document.querySelector('strudel-editor');
                            if (editor) {
                                editor.setAttribute('code', data.code);
                                console.log('[Strudel Control] Code updated');
                            } else {
                                console.error('[Strudel Control] Editor not found');
                            }
                            break;

                        case 'evaluate':
                            document.dispatchEvent(new CustomEvent('repl-evaluate', {
                                detail: { source: 'external' },
                                cancelable: true
                            }));
                            console.log('[Strudel Control] Evaluation triggered');
                            break;

                        case 'stop':
                            document.dispatchEvent(new CustomEvent('repl-stop', {
                                detail: { source: 'external' },
                                cancelable: true
                            }));
                            console.log('[Strudel Control] Stopped');
                            break;

                        default:
                            console.warn('[Strudel Control] Unknown action:', data.action);
                    }
                } catch (err) {
                    console.error('[Strudel Control] Error processing message:', err);
                }
            };

            ws.onerror = (error) => {
                console.error('[Strudel Control] WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('[Strudel Control] Disconnected, will retry...');
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(() => {
                        console.log('[Strudel Control] Attempting reconnect...');
                        connect();
                    }, 5000);
                }
            };
        } catch (err) {
            console.error('[Strudel Control] Connection error:', err);
        }
    }

    // Wait for page to load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', connect);
    } else {
        connect();
    }
})();
```

### Installation Steps

1. Install Tampermonkey browser extension
2. Create new script with the code above
3. Run the WebSocket bridge: `node websocket-bridge.js`
4. Open strudel.cc in browser
5. Control from external process:

```bash
# Set code
curl -X POST http://localhost:3002/code \
  -H "Content-Type: application/json" \
  -d '{"code": "note(\"c e g\").s(\"piano\")"}

# Evaluate
curl -X POST http://localhost:3002/evaluate

# Set code and evaluate in one call
curl -X POST http://localhost:3002/evaluate \
  -H "Content-Type: application/json" \
  -d '{"code": "note(\"<c e g b>\").s(\"sawtooth\")"}

# Stop
curl -X POST http://localhost:3002/stop
```

---

## Approach 3: Fork Strudel + Native WebSocket

### Modify Strudel Website

**File:** `website/src/control-api.ts` (new file)

```typescript
import { StrudelMirror } from '@strudel/codemirror';

export class StrudelControlAPI {
  private ws: WebSocket | null = null;
  private editor: StrudelMirror | null = null;
  private reconnectInterval: number | null = null;

  constructor(private wsUrl: string = 'ws://localhost:9999') {}

  setEditor(editor: StrudelMirror) {
    this.editor = editor;
    this.connect();
  }

  private connect() {
    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log('[Control API] Connected');
        if (this.reconnectInterval) {
          clearInterval(this.reconnectInterval);
          this.reconnectInterval = null;
        }
        this.sendState();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };

      this.ws.onerror = (error) => {
        console.error('[Control API] Error:', error);
      };

      this.ws.onclose = () => {
        console.log('[Control API] Disconnected');
        this.scheduleReconnect();
      };
    } catch (err) {
      console.error('[Control API] Connection failed:', err);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (!this.reconnectInterval) {
      this.reconnectInterval = window.setInterval(() => {
        this.connect();
      }, 5000);
    }
  }

  private handleMessage(data: any) {
    if (!this.editor) return;

    switch(data.action) {
      case 'setCode':
        this.editor.setCode(data.code);
        this.sendState();
        break;

      case 'evaluate':
        this.editor.evaluate(data.autostart ?? true);
        this.sendState();
        break;

      case 'stop':
        this.editor.stop();
        this.sendState();
        break;

      case 'getState':
        this.sendState();
        break;

      default:
        console.warn('[Control API] Unknown action:', data.action);
    }
  }

  private sendState() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;

    const state = {
      type: 'state',
      code: this.editor?.code || '',
      playing: this.editor?.repl?.scheduler?.started || false,
      // Add more state as needed
    };

    this.ws.send(JSON.stringify(state));
  }

  disconnect() {
    if (this.reconnectInterval) {
      clearInterval(this.reconnectInterval);
    }
    this.ws?.close();
  }
}

// Expose globally
if (typeof window !== 'undefined') {
  (window as any).strudelControlAPI = new StrudelControlAPI();
}
```

**Integrate in main REPL component:**

```typescript
// In your main REPL component
import { StrudelControlAPI } from './control-api';

const controlAPI = new StrudelControlAPI();

// After creating StrudelMirror instance
const editor = new StrudelMirror({ /* options */ });
controlAPI.setEditor(editor);
```

---

## Comparison Table

| Feature | Puppeteer | UserScript | Fork Strudel |
|---------|-----------|------------|-------------|
| **Setup Complexity** | Low | Medium | High |
| **Strudel Modifications** | None | None | Required |
| **Latency** | Medium (~100ms) | Low (~10ms) | Lowest (~5ms) |
| **Resource Usage** | High (full browser) | Low | Low |
| **Maintenance** | Easy | Easy | Requires updates |
| **Production Ready** | No | Maybe | Yes |
| **State Monitoring** | Limited | Good | Excellent |
| **Bidirectional** | Yes | Yes | Yes |

---

## Recommended Path

### For Experimentation:
**Use Puppeteer** - Get started in 10 minutes, no browser extensions needed.

### For Personal Use:
**Use UserScript** - Clean separation, works on official strudel.cc, minimal setup.

### For Production/Integration:
**Fork Strudel** - Native integration, best performance, full control.

---

## Testing Your Setup

### Test Script (Node.js)

```javascript
const axios = require('axios');

async function testStrudelControl() {
  const api = 'http://localhost:3001';  // or 3002 for UserScript approach
  
  console.log('Testing Strudel control...');
  
  // Test 1: Simple pattern
  console.log('Test 1: Playing C major chord');
  await axios.post(`${api}/evaluate`, {
    code: 'note("c e g").s("piano")'
  });
  await sleep(3000);
  
  // Test 2: Pattern with effects
  console.log('Test 2: Pattern with filter');
  await axios.post(`${api}/evaluate`, {
    code: 'note("<c e g b>").s("sawtooth").lpf("<1000 2000 500>")'
  });
  await sleep(5000);
  
  // Test 3: Stop
  console.log('Test 3: Stopping');
  await axios.post(`${api}/stop`);
  
  console.log('Tests complete!');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

testStrudelControl().catch(console.error);
```

---

## Next Steps

1. Choose your approach based on use case
2. Set up the bridge/controller
3. Test with simple patterns
4. Build your integration (DAW control, AI generation, etc.)
5. Consider contributing back to Strudel project if you build something useful!
