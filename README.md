# Strudel Agent

AI-powered music creation system for Strudel live coding. Create, organize, and perform with intelligent code generation and project management.

## What is this?

Strudel Agent is an MCP (Model Context Protocol) server that gives AI assistants the ability to work with Strudel live coding projects. Think of it as giving Claude or any MCP-compatible AI the power to write Strudel code, manage music projects, search sample packs, and help you create music faster.

The system includes:
- **MCP Server** - 29 tools for Strudel project management
- **LiveStrudler Agent** - Real-time code generator optimized for live performance
- **Knowledge Base** - Curated Strudel reference documentation
- **Sample Pack Database** - Searchable catalog of known sample packs
- **Surface Templates** - Parameterized code generation with validation

## Quick Start

### Installation

```bash
git clone https://github.com/yourusername/strudel_agent.git
cd strudel_agent
pip install -r requirements.txt
```

### Using with Claude Desktop

Add this to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "strudel": {
      "command": "python",
      "args": [
        "/absolute/path/to/strudel_agent/mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop and you're ready to go.

## What Can It Do?

The MCP server provides 29 tools organized into these categories:

### Knowledge & Discovery (5 tools)
- Search Strudel documentation
- List available knowledge docs
- Read full documentation files
- Search sample packs by genre/type
- Get detailed pack information

### Project Management (2 tools)
- List all projects
- Create/update project index files

### Clips (5 tools)
- List clips with metadata filtering
- Search clip code with regex
- Get full clip content
- Save new clips with versioned metadata
- Update existing clips (auto-bumps version)

### Songs (4 tools)
- List songs in a project
- Get full song content
- Create new songs with structure
- Update existing songs

### Playlists (4 tools)
- List playlists
- Get playlist content
- Create new playlists
- Update playlists

### Surface Templates (5 tools)
- Create parameterized code templates
- List templates by category/tags
- Get template schema
- Generate code from templates with validation
- Update existing templates

### Sample Packs (2 tools)
- Search known packs database
- Get detailed pack documentation

## Project Structure

```
strudel_agent/
├── projects/                   # Your music projects
│   └── {project_name}/
│       ├── index.md           # Project info
│       ├── clips/             # Reusable code snippets (.js)
│       ├── songs/             # Complete compositions (.md)
│       ├── playlists/         # Performance sets (.md)
│       └── surfaces/          # Code templates (.yaml)
│
├── knowledge/                  # Strudel reference docs
│   ├── patterns.md
│   ├── effects.md
│   └── ...
│
├── known_packs/               # Sample pack database
│   ├── dirt_samples.md
│   ├── garden.md
│   └── ...
│
├── agents/                    # Agent system prompts
│   ├── LiveStrudler.md       # Real-time code generator
│   ├── StrudelMusicAssistant.md
│   └── StrudelCoder.md
│
├── mcp_server.py             # MCP server implementation
├── agent.py                  # CLI test agent
└── requirements.txt
```

## Key Features

### Clip Versioning

Clips use semantic versioning and track metadata in the first line:

```javascript
// {"name": "Techno Kick", "tags": ["drums", "kick", "techno"], "tempo": 128, "description": "Four-on-floor with sidechain", "author": "you", "version": "1.2.0", "date": "2025-12-26"}
$: sound("bd*4").gain(0.9)
```

Updating a clip automatically bumps the version and updates the date.

### Surface Templates

Create reusable, parameterized patterns with schema validation:

```yaml
metadata:
  name: "Techno Kick Pattern"
  category: "drums"
  tags: ["kick", "techno"]

template: |
  $: sound("bd*{pattern}").gain({gain}).lpf({cutoff})

schema:
  pattern:
    type: integer
    default: 4
    min: 1
    max: 16
  gain:
    type: float
    default: 0.8
    min: 0.0
    max: 1.0
  cutoff:
    type: integer
    default: 800
    min: 100
    max: 20000
```

Generate validated code:

```javascript
// generate_from_template with {pattern: 8, gain: 0.9, cutoff: 600}
$: sound("bd*8").gain(0.9).lpf(600)
```

### Sample Pack Discovery

Searchable database of known sample packs with usage examples, licenses, and tags. Search by genre, instrument type, or characteristics.

## LiveStrudler Agent

The included LiveStrudler agent is optimized for real-time code generation:

- **Code-first output** - No explanations, just working JavaScript
- **Knowledge integration** - Automatically searches docs before coding
- **Musical translation** - Converts intent ("make it darker") to parameters
- **Live performance focus** - Fast iteration, minimal friction
- **Canvas awareness** - Builds on previous output

Perfect for live coding sessions where speed matters.

## Roadmap

The project is actively developing these features:

1. **Sample Discovery** - Intelligent sample search and recommendations
2. **Song Structuring** - Better arrangement and composition tools
3. **Streaming MIDI** - Real-time MIDI output capture
4. **MCP Toolset Review** - Full backend audit and testing
5. **Frontend Testing** - Comprehensive UI test suite
6. **Error Mitigation** - Autonomous debug loop for runtime errors
7. **Output Awareness** - Real-time audio/MIDI analysis for mixing and mastering

See `notes/roadmap.md` for detailed plans.

## Web UI (Coming Soon)

A full web interface with Strudel integration is in development. It will include:
- Real-time code editing with agent assistance
- Error feedback loops with autonomous debugging
- MIDI and audio output analysis
- Project browser and clip management
- Live performance mode

Stay tuned.

## Contributing

Contributions are welcome, especially in these areas:

### Knowledge Base

The `knowledge/` folder needs more high-quality Strudel documentation. If you know Strudel well, please contribute:
- Pattern techniques
- Effect usage examples
- Musical concepts and translations
- Common workflows
- Tips and tricks

The better the knowledge base, the better the agent performs.

### Sample Pack Database

Add entries to `known_packs/` for sample packs you use:
- Pack name and GitHub URL
- Sound categories available
- Usage examples
- License information
- Tags for searchability

Help build a comprehensive catalog.

### Example Projects

Create example projects in `projects/` that showcase:
- Different genres and styles
- Advanced techniques
- Template usage patterns
- Song structuring approaches

Finished examples help the agent learn better patterns.

## Testing

### MCP Server

Test the server directly:

```bash
python mcp_server.py
```

### CLI Agent

Run the test agent:

```bash
python agent.py
```

Optionally specify a model:

```bash
python agent.py --model anthropic/claude-3.7-sonnet
```

## Technical Details

### Storage

Filesystem-based (no database required):
- Projects stored in `projects/`
- Clips are `.js` files with JSON metadata
- Songs and playlists are markdown
- Templates are YAML

### Search

Regex-based search across:
- Clip metadata and code
- Song and playlist content
- Knowledge documentation
- Sample pack information

No embeddings or vector search (yet).

### Validation

Surface templates include schema validation:
- Type checking (string, integer, float, boolean, array)
- Range constraints (min, max)
- Enum options
- Pattern matching (regex)
- Array constraints (min/max items, item types)

## Thanks

Thanks to the Strudel community for building an amazing live coding environment. This project wouldn't exist without your work.

Special thanks to contributors who help improve the knowledge base and sample pack database. The more complete these resources are, the more useful the agent becomes.

## License

MIT
