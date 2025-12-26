# Strudel Agent Interface - Seed Ideas

## UI Vision

### Core Philosophy
UI is focused on the two modalities of music (live and production)
- Mobile first and desktop friendly
- Agent is the centerpiece of the UI and everything else revolves around it
- The player is also central - enabling both forced updates and agent-driven updates

### Main Content Area
- **Carousel-based code editor system**
  - User can swipe left and right to switch between code panes
  - Carousel buttons for navigation
  - Shows editable JavaScript code with syntax highlighting
  - Switching tabs/panes changes the code of the strudel player

### Global Controls
- **Play/Stop and Update buttons** (global level)
  - Mobile version: positioned at bottom of screen
  - Includes button to pull out the left drawer

### Left Drawer
- **Navigation tabs/sections:**
  - Project picker
  - Clips
  - Songs
  - Playlists
  - Knowledge
  - Packs
- **Challenge:** Need a good UI pattern to navigate through the massive data that could be in there

### Message/Agent Interface
- **Below the code area:**
  - Message input for interacting with the strudel agent
  - Send button
  - Mic button for voice input
    - Shows voice input waveform in message area during recording
    - Sends audio to backend for Whisper transcription

### Right Drawer
- Chat history
- Way to see other chats

## Backend Architecture

### Technology Stack
- **FastAPI** as the main framework
- Endpoints for chatting with the agent
- Agent and MCP server already work with filesystem
- Need API wrapping those processes (currently CLI-only)

### Key Integration Point
- Agent can cause player updates through internal call:
  - MCP server → Backend API → Player update

## Use Cases

### Asset Management & Studio Work
- Feel like doing professional studio work
- Manage clips, songs, playlists, packs, knowledge

### Live Music Creation
- Create music live with the agent
- Real-time code editing and playback
- Voice-driven interaction for hands-free flow

## Design Goals
- Seamless switching between production and live modes
- Agent-centric workflow
- Mobile-first but desktop-capable
- Voice and text interaction
- Professional feel with powerful asset management
