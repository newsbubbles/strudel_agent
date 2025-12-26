# Strudel Agent UI

Frontend interface for the Strudel Agent - a conversational AI assistant for live coding with Strudel.

## Tech Stack

- **Framework**: SvelteKit 2.0 + TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn-svelte (to be installed)
- **Code Editor**: CodeMirror 6
- **Audio Engine**: @strudel/web (loaded via CDN)
- **State Management**: Svelte Stores

## Project Structure

```
ui/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── ui/           # shadcn-svelte components
│   │   │   ├── panels/       # Panel types (Clip, Song, etc.)
│   │   │   ├── drawers/      # Left/Right drawer content
│   │   │   ├── player/       # Global player controls
│   │   │   └── layout/       # Layout components
│   │   ├── stores/           # Svelte stores (state management)
│   │   ├── services/         # External integrations (WebSocket, API, Strudel)
│   │   ├── types/            # TypeScript definitions
│   │   └── utils/            # Helper functions
│   ├── routes/               # SvelteKit routes
│   └── app.css               # Global styles + Tailwind
├── static/                   # Static assets
├── package.json
├── svelte.config.js
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd ui
npm install
```

### Install shadcn-svelte Components

After initial setup, install shadcn-svelte components:

```bash
# Initialize shadcn-svelte (if not already done)
npx shadcn-svelte@latest init

# Install required components
npx shadcn-svelte@latest add carousel
npx shadcn-svelte@latest add drawer
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add input
npx shadcn-svelte@latest add textarea
npx shadcn-svelte@latest add scroll-area
npx shadcn-svelte@latest add separator
npx shadcn-svelte@latest add badge
```

### Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Development Workflow

This project is being built in phases:

- ✅ **Phase 1**: Project Setup (COMPLETE)
- ⏳ **Phase 2**: Type Definitions
- ⏳ **Phase 3**: Store Architecture
- ⏳ **Phase 4**: WebSocket Service
- ⏳ **Phase 5**: API Service
- ⏳ **Phase 6**: Strudel Player Integration
- ⏳ **Phase 7**: UI Components - Layout
- ⏳ **Phase 8**: Panel Components
- ⏳ **Phase 9**: Drawer Components
- ⏳ **Phase 10**: Global Player Controls
- ⏳ **Phase 11**: Main App Integration

See `../notes/interface/ui_implementation.md` for complete implementation plan.

## Architecture

### State Management

Using native Svelte stores:

- `carouselStore` - Loaded panels and current index
- `sessionStore` - Active sessions per panel
- `webSocketStore` - Connection state and message queue
- `historyStore` - Chat history per session
- `playerStore` - Global player state
- `recentStore` - Recently closed items (LocalStorage)

### API Integration

- **REST API**: `http://localhost:8000/api` (proxied via Vite)
- **WebSocket**: `ws://localhost:8000/ws` (proxied via Vite)

### Strudel Integration

- Loaded via CDN: `https://unpkg.com/@strudel/web@latest`
- Headless mode (no built-in editor)
- Custom controls via global player
- Multiple clips combined with `stack()`

## Key Features

### Carousel-Based Interface

- Each panel = one session with the agent
- Swipe between panels
- Per-panel message input and chat history

### Panel Types

- **Clip**: CodeMirror editor for Strudel patterns
- **Song**: Markdown viewer with clip references
- **Playlist**: List view with song references
- **Pack**: Read-only documentation viewer

### Real-Time Updates

- Agent can update any loaded panel
- WebSocket-based bidirectional communication
- Live code updates reflected in editor

### Global Player

- Combines all loaded clips with `stack()`
- Play/Stop/Update controls
- Works across all panels

## Configuration

### Backend Proxy

Vite is configured to proxy API and WebSocket requests to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws': { target: 'ws://localhost:8000', ws: true }
  }
}
```

To change the backend URL, edit `vite.config.ts`.

## Troubleshooting

### Strudel not loading

- Check browser console for errors
- Verify CDN script tag in `src/app.html`
- Check network connection

### Backend connection failed

- Ensure backend is running on `http://localhost:8000`
- Check Vite proxy configuration
- Verify CORS settings on backend

### TypeScript errors

```bash
npm run check
```

### Styling issues

- Ensure Tailwind is processing CSS: `npm run dev`
- Check `tailwind.config.js` content paths
- Verify `app.css` is imported in `+layout.svelte`

## Resources

- **SvelteKit Docs**: https://kit.svelte.dev/docs
- **shadcn-svelte**: https://www.shadcn-svelte.com
- **Strudel Docs**: https://strudel.cc/learn
- **Implementation Plan**: `../notes/interface/ui_implementation.md`
- **Phase 6 Details**: `../notes/interface/ui_phase6_implementation.md`

## License

Same as parent project.
