# Frontend Build & Debug Guide 🚀

**Date**: 2025-12-25  
**Purpose**: Build, launch, and debug the Svelte frontend  
**Status**: Ready to test (backend not hooked up yet)  

---

## Quick Start (TL;DR)

```bash
# Navigate to UI directory
cd ui

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev

# Open browser
# http://localhost:5173
```

---

## Prerequisites

### **Required**:
- ✅ Node.js (v18+ recommended)
- ✅ npm (comes with Node.js)

### **Check Versions**:
```bash
node --version   # Should be v18.x or higher
npm --version    # Should be 9.x or higher
```

### **Install Node.js** (if needed):
- **macOS**: `brew install node`
- **Linux**: `curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs`
- **Windows**: Download from https://nodejs.org/

---

## Step-by-Step Guide

### **1. Navigate to UI Directory**

```bash
cd /path/to/strudel_agent/ui

# Or from project root:
cd ui
```

---

### **2. Install Dependencies** (First Time Only)

```bash
npm install
```

**What This Does**:
- Installs Svelte, SvelteKit, TypeScript
- Installs ShadCN UI components
- Installs Tailwind CSS
- Installs development tools

**Expected Output**:
```
added 500+ packages in 30s
```

**Troubleshooting**:
- If you get permission errors: `sudo npm install`
- If you get network errors: Check internet connection
- If you get version conflicts: Delete `node_modules/` and `package-lock.json`, then retry

---

### **3. Start Development Server**

```bash
npm run dev
```

**Expected Output**:
```
  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**What This Does**:
- Starts Vite dev server on port 5173
- Enables hot module replacement (HMR)
- Watches for file changes
- Compiles TypeScript on the fly

---

### **4. Open in Browser**

**Option 1: Auto-open**
```bash
npm run dev -- --open
```

**Option 2: Manual**
1. Open browser
2. Navigate to: `http://localhost:5173`

**Expected**: You should see the Strudel Agent UI!

---

## What You Should See

### **Main Layout**:

```
┌───────────────────────────────────────────────────────────────┐
│  [☰]  Strudel Agent                                    [💬]  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                    < Carousel Panels >                        │
│                                                               │
│                  [Empty State / Test Panels]                  │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│  🎵 No clip selected      [▶️ Play]  [🔄 Update]      Ready  │
└───────────────────────────────────────────────────────────────┘
```

**Components**:
- **Top Bar**: Logo, drawer toggles
- **Carousel**: Panel navigation (may be empty without backend)
- **Bottom Player**: Play/Stop/Update controls
- **Left Drawer**: Browse items (toggle with ☰)
- **Right Drawer**: Chat history (toggle with 💬)

---

## Expected Behavior (Without Backend)

### **✅ What Works**:
- UI renders correctly
- Layout is responsive
- Drawers toggle open/close
- Buttons are styled correctly
- Dark mode theme applied
- TypeScript compilation succeeds

### **⚠️ What Doesn't Work Yet**:
- WebSocket connection (no backend)
- API calls (no backend)
- Loading real clips/songs/playlists
- Playing audio (Strudel may fail to init)
- Chat messages
- Browse items list

### **Expected Errors in Console**:
```
[WebSocket] Failed to connect: Connection refused
[API] Failed to fetch: Network error
[Strudel] Failed to initialize: CDN not loaded
```

**This is normal!** The backend isn't running yet.

---

## Development Commands

### **Start Dev Server**:
```bash
npm run dev
```

### **Build for Production**:
```bash
npm run build
```

### **Preview Production Build**:
```bash
npm run preview
```

### **Type Check**:
```bash
npm run check
```

### **Lint**:
```bash
npm run lint
```

### **Format**:
```bash
npm run format
```

---

## Browser DevTools

### **Open DevTools**:
- **Chrome/Edge**: `F12` or `Cmd+Opt+I` (Mac) / `Ctrl+Shift+I` (Windows/Linux)
- **Firefox**: `F12` or `Cmd+Opt+K` (Mac) / `Ctrl+Shift+K` (Windows/Linux)
- **Safari**: `Cmd+Opt+I` (enable Developer menu first)

### **Useful Tabs**:

#### **1. Console**
See logs, errors, warnings:
```javascript
[GlobalPlayer] Initializing Strudel...
[WebSocket] Connecting to ws://localhost:8000/ws
[API] Fetching clips...
```

#### **2. Network**
Inspect API calls:
- Filter by `WS` to see WebSocket attempts
- Filter by `Fetch/XHR` to see API calls
- Check status codes (expect 404/connection errors without backend)

#### **3. Elements/Inspector**
Inspect DOM:
- Check if components rendered
- Verify Tailwind classes applied
- Inspect component structure

#### **4. Sources/Debugger**
Debug TypeScript:
- Set breakpoints in `.svelte` files
- Step through component logic
- Inspect reactive variables

---

## Hot Module Replacement (HMR)

**What is HMR?**
Vite automatically reloads components when you edit files.

**Try It**:
1. Open `ui/src/lib/components/layout/MainLayout.svelte`
2. Change something (e.g., add a console.log)
3. Save file
4. Browser updates automatically (no full reload!)

**Example**:
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  
  onMount(() => {
    console.log('🎉 Component mounted! HMR works!');
  });
</script>
```

Save → Check console → See new log!

---

## Testing Components in Isolation

### **Test Individual Components**:

Create a test route in `ui/src/routes/test/+page.svelte`:

```svelte
<script lang="ts">
  import { GlobalPlayer } from '$lib/components/player';
  import { ClipPanel } from '$lib/components/panels';
</script>

<div class="p-8">
  <h1 class="text-2xl font-bold mb-4">Component Testing</h1>
  
  <!-- Test GlobalPlayer -->
  <div class="border rounded p-4 mb-4">
    <h2 class="text-lg font-semibold mb-2">GlobalPlayer</h2>
    <GlobalPlayer />
  </div>
  
  <!-- Test ClipPanel -->
  <div class="border rounded p-4">
    <h2 class="text-lg font-semibold mb-2">ClipPanel</h2>
    <ClipPanel panel={{
      id: 'test-1',
      type: 'clip',
      itemId: 'test-clip',
      data: {
        filename: 'test.js',
        code: 'sound("bd").fast(2)',
        created: new Date(),
        modified: new Date()
      },
      createdAt: new Date(),
      lastModified: new Date()
    }} />
  </div>
</div>
```

Navigate to: `http://localhost:5173/test`

---

## Debugging Tips

### **1. Check TypeScript Errors**

```bash
npm run check
```

**Look for**:
- Type mismatches
- Missing imports
- Invalid prop types

---

### **2. Check Console Logs**

All components have debug logs:
```javascript
console.log('[ComponentName] Action happening...');
```

**Useful logs**:
- `[GlobalPlayer]` - Player initialization, play/stop
- `[WebSocket]` - Connection status
- `[API]` - API calls
- `[Carousel]` - Panel navigation
- `[Strudel]` - Audio engine

---

### **3. Inspect Svelte Stores**

Add this to any component:

```svelte
<script lang="ts">
  import { carousel } from '$lib/stores/carousel';
  import { player } from '$lib/stores/player';
  
  // Log store changes
  $: console.log('Carousel:', $carousel);
  $: console.log('Player:', $player);
</script>
```

---

### **4. Check Network Tab**

**WebSocket**:
- Look for `ws://localhost:8000/ws`
- Status: `(pending)` or `101 Switching Protocols` (success) or `failed` (no backend)

**API Calls**:
- Look for `http://localhost:8000/api/*`
- Status: `200 OK` (success) or `404 Not Found` (no backend)

---

### **5. Svelte DevTools** (Optional)

Install browser extension:
- **Chrome**: [Svelte DevTools](https://chrome.google.com/webstore/detail/svelte-devtools/ckolcbmkjpjmangdbmnkpjigpkddpogn)
- **Firefox**: [Svelte DevTools](https://addons.mozilla.org/en-US/firefox/addon/svelte-devtools/)

**Features**:
- Inspect component tree
- View component state
- Track reactive updates
- Time-travel debugging

---

## Common Issues & Solutions

### **Issue 1: Port Already in Use**

**Error**:
```
Error: Port 5173 is already in use
```

**Solution**:
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

---

### **Issue 2: Module Not Found**

**Error**:
```
Error: Cannot find module '@/lib/components/...'
```

**Solution**:
```bash
# Restart dev server
# Ctrl+C to stop
npm run dev
```

---

### **Issue 3: TypeScript Errors**

**Error**:
```
Type 'string' is not assignable to type 'number'
```

**Solution**:
1. Check `npm run check` output
2. Fix type mismatches
3. Add type annotations
4. Restart dev server if needed

---

### **Issue 4: Styles Not Applied**

**Error**:
Components look unstyled (no Tailwind)

**Solution**:
```bash
# Check Tailwind config
cat tailwind.config.js

# Restart dev server
npm run dev
```

---

### **Issue 5: WebSocket Connection Failed**

**Error**:
```
[WebSocket] Failed to connect: Connection refused
```

**Expected!** Backend isn't running yet.

**Temporary Fix** (to test UI):
Comment out WebSocket initialization in stores:

```typescript
// ui/src/lib/stores/websocket.ts
export function createWebSocketStore() {
  // ... existing code ...
  
  function connect() {
    // TEMPORARILY DISABLE FOR TESTING
    console.log('[WebSocket] Connection disabled for frontend testing');
    return;
    
    // ... rest of connect logic ...
  }
}
```

---

## Testing Checklist

### **Visual Testing**:

- [ ] Page loads without errors
- [ ] Layout renders correctly
- [ ] Top bar visible with logo
- [ ] Carousel area visible
- [ ] Bottom player visible
- [ ] Left drawer toggles
- [ ] Right drawer toggles
- [ ] Buttons styled correctly
- [ ] Dark mode applied
- [ ] Responsive on mobile (resize browser)

### **Interaction Testing**:

- [ ] Left drawer button toggles drawer
- [ ] Right drawer button toggles drawer
- [ ] Drawer overlay closes drawer
- [ ] Play button disabled (no clip)
- [ ] Update button disabled (no clip)
- [ ] Keyboard navigation works (Tab)
- [ ] Focus states visible

### **Console Testing**:

- [ ] No critical errors (WebSocket/API errors are expected)
- [ ] Component mount logs visible
- [ ] TypeScript compilation successful
- [ ] No infinite loops
- [ ] No memory leaks

---

## Performance Monitoring

### **Check Bundle Size**:

```bash
npm run build

# Output shows bundle sizes:
# dist/index.html                  0.50 kB
# dist/assets/index-abc123.js     50.00 kB
# dist/assets/index-abc123.css     5.00 kB
```

### **Lighthouse Audit**:

1. Open DevTools
2. Go to "Lighthouse" tab
3. Click "Generate report"
4. Check scores:
   - Performance: 90+
   - Accessibility: 95+
   - Best Practices: 90+
   - SEO: 90+

---

## Next Steps

### **After Frontend Testing**:

1. **Build Backend**: Follow backend setup guide
2. **Connect Services**: Wire up WebSocket + API
3. **Test Integration**: End-to-end testing
4. **Load Real Data**: Test with actual clips/songs
5. **Test Strudel**: Play audio

### **Development Workflow**:

```bash
# Terminal 1: Frontend
cd ui
npm run dev

# Terminal 2: Backend (when ready)
cd backend
python -m uvicorn main:app --reload

# Terminal 3: Agent (when ready)
cd agent
python agent.py
```

---

## Resources

### **Documentation**:
- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [Svelte Tutorial](https://svelte.dev/tutorial)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Docs](https://vitejs.dev/guide/)

### **Project Files**:
- **Main Layout**: `ui/src/lib/components/layout/MainLayout.svelte`
- **Global Player**: `ui/src/lib/components/player/GlobalPlayer.svelte`
- **Stores**: `ui/src/lib/stores/`
- **Services**: `ui/src/lib/services/`
- **Types**: `ui/src/lib/types/`

### **Config Files**:
- **Vite**: `ui/vite.config.ts`
- **TypeScript**: `ui/tsconfig.json`
- **Tailwind**: `ui/tailwind.config.js`
- **SvelteKit**: `ui/svelte.config.js`

---

## Quick Reference

### **Start Dev Server**:
```bash
cd ui && npm run dev
```

### **Open Browser**:
```
http://localhost:5173
```

### **Check Logs**:
```
F12 → Console tab
```

### **Test Component**:
```svelte
<!-- Add to any .svelte file -->
<script>
  console.log('🎉 Component loaded!');
</script>
```

### **Restart Server**:
```
Ctrl+C → npm run dev
```

---

## Success Criteria

✅ **Frontend is ready when**:
- Dev server starts without errors
- Page loads in browser
- UI renders correctly
- Components are interactive
- No critical console errors
- TypeScript compiles successfully

🎯 **You're ready to connect the backend!**

---

**Happy Testing!** 🚀✨
