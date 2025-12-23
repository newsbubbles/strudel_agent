# Strudel Music Assistant

An AI agent for creating and organizing Strudel live coding music projects.

## Overview

Strudel Music Assistant helps you:
- Create reusable Strudel code snippets (clips)
- Organize clips into complete songs
- Build playlists for performances
- Search Strudel knowledge base
- Manage multiple music projects

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `LOGFIRE_API_KEY` - Your Logfire API key (optional)

### 3. Run the Agent

```bash
python agent.py
```

Optionally specify a different model:

```bash
python agent.py --model anthropic/claude-3.7-sonnet
```

## Project Structure

```
strudel_agent/
├── projects/                    # Your music projects
│   └── {project_name}/
│       ├── index.md            # Project description
│       ├── clips/              # Reusable code snippets
│       │   └── {clip_id}.js
│       ├── songs/              # Complete compositions
│       │   └── {song_id}.md
│       └── playlists/          # Performance sets
│           └── {playlist_id}.md
│
├── knowledge/                   # Strudel reference docs
│   ├── notation.md
│   ├── core_functions.md
│   └── ...
│
├── agents/                      # Agent system prompts
│   └── StrudelMusicAssistant.md
│
├── mcp_server.py                # MCP server implementation
├── agent.py                     # CLI agent for testing
├── requirements.txt
└── .env.example
```

## Usage Examples

### Creating a New Project

```
> I want to start a new house music project called "sunset_vibes"
```

The agent will create the project structure and help you build clips.

### Creating Clips

```
> Create a four-on-floor kick pattern for house music
```

The agent will generate Strudel code and save it as a clip.

### Building a Song

```
> Let's create a song using the kick, bass, and chord clips we made
```

The agent will help structure the song and save it as a markdown file.

### Searching Knowledge

```
> How do I add swing to a drum pattern?
```

The agent will search the knowledge base and explain the technique.

## File Formats

### Clip Files (`.js`)

First line contains JSON metadata as a comment:

```javascript
// {"name": "House Kick", "tags": ["drums", "kick", "house"], "tempo": 120, "description": "Four-on-floor kick pattern"}
sound("bd*4").bank("RolandTR909").gain(0.8)
```

### Song Files (`.md`)

Markdown with H1 title, description, and structure:

```markdown
# Sunset House Groove

Warm, groovy house track with filtered bass and jazzy chords.

## Structure

### Intro (0-16 bars)
- Start with [kick.js](../clips/kick.js)
- Add [hats.js](../clips/hats.js) at bar 8
```

### Playlist Files (`.md`)

Markdown with ordered song list:

```markdown
# Friday Night Set

## Tracklist

1. [Sunset House Groove](../songs/sunset_house_groove.md)
   - Transition: Fade out drums over 8 bars
```

## Available Tools

The agent has access to 16 tools:

**Knowledge**:
- `search_knowledge` - Search Strudel reference docs

**Projects**:
- `list_projects` - List all projects
- `write_project_index` - Create/update project description

**Clips**:
- `list_clips` - List clips in project
- `search_clips` - Search clip code
- `get_clips` - Get full clip content
- `save_new_clip` - Create new clip
- `update_clip` - Update existing clip

**Songs**:
- `list_songs` - List songs
- `get_songs` - Get full song content
- `save_new_song` - Create new song
- `update_song` - Update existing song

**Playlists**:
- `list_playlists` - List playlists
- `get_playlists` - Get full playlist content
- `save_new_playlist` - Create new playlist
- `update_playlist` - Update existing playlist

## Development

### Testing the MCP Server

Run the server directly:

```bash
python mcp_server.py
```

### Project Status

This is an MVP (Minimum Viable Product) implementation focusing on:
- Filesystem-based storage (no database)
- Regex-based search (no embeddings)
- Simple CRUD operations
- CLI agent for testing

**Planned enhancements**:
- PostgreSQL database for better querying
- pgvector embeddings for semantic search
- JavaScript syntax validation
- Async operations
- Web interface

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
