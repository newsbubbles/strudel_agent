# Strudel MCP Toolset - Extended Set (Final)

**Date**: 2025-12-22  
**Status**: Final design for knowledge access  
**Purpose**: Simplified knowledge access tool for agent reference lookup

---

## Overview

This extends the proposed toolset with a **single, simple knowledge access tool** that lets the agent search curated reference files in the `knowledge/` folder.

**Philosophy**: 
- Agent has limited context window - can't memorize all Strudel syntax/functions/patterns
- Knowledge files contain detailed reference material with full examples
- Agent uses regex search to find relevant instructions on-demand
- Single tool with flexible parameters keeps it simple and powerful

---

## Extended Tool Category

### 6. Knowledge Access

**Why This Tool?**

The agent needs to:
- Look up syntax when user asks about notation
- Find function details when composing code
- Discover patterns for specific genres/techniques
- Translate musical concepts to code
- Learn from full contextual examples

Instead of cramming everything into the system prompt, the agent **looks up** what it needs **when it needs it**.

---

### `search_knowledge`

**Purpose**: Search curated knowledge files using regex patterns.

**Why**: Agent can find syntax, functions, effects, patterns, vocabulary, samples, and techniques by searching markdown reference files with context-rich examples.

**Functionality**:
- Search markdown files in `knowledge/` directory
- Use regex patterns for flexible matching
- Optionally filter to specific knowledge category
- Return matches with surrounding context
- Include full code examples from knowledge files

**Input**:
```python
query: str  # Regex pattern to search for
category: str | None = None  # Optional: filter to specific file
context_lines: int = 3  # Lines of context around matches
max_results: int = 10  # Limit results
```

**Category Options**:
- `"notation"` - Mini-notation syntax reference
- `"core_functions"` - Core Strudel functions
- `"effects"` - Audio effects reference
- `"patterns"` - Musical pattern examples
- `"vocabulary"` - Musical intent → code translation
- `"samples"` - Sample/drum catalog
- `"synths"` - Synthesis techniques
- `"best_practices"` - Coding conventions and tips
- `None` - Search all files

**Output**:
```python
{
  "matches": list[{
    "file": str,  # Which knowledge file
    "section": str,  # Markdown section header
    "line_number": int,
    "content": str,  # Matched content with context lines
    "code_example": str | None  # Extracted code block if nearby
  }],
  "total_matches": int,
  "query": str,  # Echo back the query
  "category_searched": str | None  # Which category was searched
}
```

**Example Usage 1: User asks "How do I make a polyrhythm?"**

```python
# Agent calls:
search_knowledge(
  query="polyrhythm|\\{.*,.*\\}",
  category="notation"
)

# Returns:
{
  "matches": [
    {
      "file": "notation.md",
      "section": "Polyrhythms",
      "line_number": 35,
      "content": "### Polyrhythms\n\nDifferent time signatures layered together:\n\n```javascript\nsound(\"{bd sd hh, cp cp cp cp}\")  // 3 against 4\n```\n",
      "code_example": "sound(\"{bd sd hh, cp cp cp cp}\")  // 3 against 4"
    }
  ],
  "total_matches": 1,
  "query": "polyrhythm|\\{.*,.*\\}",
  "category_searched": "notation"
}
```

**Example Usage 2: User says "Make it groovy"**

```python
# Agent calls:
search_knowledge(
  query="groov.*|swing|shuffle",
  category="vocabulary"
)

# Returns:
{
  "matches": [
    {
      "file": "vocabulary.md",
      "section": "Rhythm Terms",
      "line_number": 28,
      "content": "| \"Add shuffle\" | `.late(\"[0 .01]*4\")` | Delay alternate notes |\n| \"Swing feel\" | `note(\"c@2 e\")` | Elongate first note |\n",
      "code_example": null
    },
    {
      "file": "patterns.md",
      "section": "Swing/Shuffle",
      "line_number": 286,
      "content": "### Swing/Shuffle\n\nAdd groove with timing offsets:\n\n```javascript\n// Swing hi-hats\nsound(\"hh*8\").late(\"[0 .01]*4\")\n\n// Shuffle drums\nstack(\n  sound(\"bd*4\"),\n  sound(\"[~ cp]*2\").late(\"[0 .02]*2\"),\n  sound(\"hh*8\").late(\"[0 .01]*4\")\n)\n```\n",
      "code_example": "// Swing hi-hats\nsound(\"hh*8\").late(\"[0 .01]*4\")\n\n// Shuffle drums\nstack(\n  sound(\"bd*4\"),\n  sound(\"[~ cp]*2\").late(\"[0 .02]*2\"),\n  sound(\"hh*8\").late(\"[0 .01]*4\")\n)"
    }
  ],
  "total_matches": 2,
  "query": "groov.*|swing|shuffle",
  "category_searched": "vocabulary"
}
```

**Example Usage 3: Agent needs to verify lpf() range**

```python
# Agent calls:
search_knowledge(
  query="lpf.*range|low.*pass.*filter",
  category="effects"
)

# Returns:
{
  "matches": [
    {
      "file": "effects.md",
      "section": "Filters",
      "line_number": 30,
      "content": "### lpf() - Low-Pass Filter\n\n**Synonyms**: `cutoff`, `ctf`, `lp`  \n**Range**: 0-20000 Hz\n\nRemoves high frequencies above cutoff.\n\n```javascript\nsound(\"bd\").lpf(400)  // Darker kick\nsound(\"sawtooth\").lpf(sine.range(400, 4000))  // Sweeping filter\n```\n",
      "code_example": "sound(\"bd\").lpf(400)  // Darker kick\nsound(\"sawtooth\").lpf(sine.range(400, 4000))  // Sweeping filter"
    }
  ],
  "total_matches": 1,
  "query": "lpf.*range|low.*pass.*filter",
  "category_searched": "effects"
}
```

**Example Usage 4: Broad search across all knowledge**

```python
# Agent calls:
search_knowledge(
  query="build.*up|riser|tension",
  category=None,  # Search all files
  max_results=5
)

# Returns matches from multiple files:
{
  "matches": [
    {
      "file": "patterns.md",
      "section": "Transitions",
      "line_number": 245,
      "content": "Build-up with increasing density:\n\n```javascript\n// Escalating hi-hats\n$: sound(\"hh*<4 8 16 32>\")\n  .gain(\"<0.6 0.7 0.8 1>\")\n\n// Rising filter sweep\n$: sound(\"sawtooth\")\n  .note(\"c2\")\n  .hpf(sine.range(100, 8000).slow(8))\n```\n",
      "code_example": "// Escalating hi-hats\n$: sound(\"hh*<4 8 16 32>\")\n  .gain(\"<0.6 0.7 0.8 1>\")\n\n// Rising filter sweep\n$: sound(\"sawtooth\")\n  .note(\"c2\")\n  .hpf(sine.range(100, 8000).slow(8))"
    },
    {
      "file": "effects.md",
      "section": "Filter Sweeps",
      "line_number": 178,
      "content": "Create tension with rising filter:\n\n```javascript\n.hpf(sine.range(100, 8000).slow(8))  // 8-cycle sweep\n.lpf(saw.range(200, 8000).slow(4))   // Faster sweep\n```\n",
      "code_example": ".hpf(sine.range(100, 8000).slow(8))  // 8-cycle sweep\n.lpf(saw.range(200, 8000).slow(4))   // Faster sweep"
    },
    {
      "file": "vocabulary.md",
      "section": "Temporal Effects",
      "line_number": 103,
      "content": "| \"Build-up\" | Increasing intensity | `.gain(\"<0.5 0.7 0.9 1>\")` |\n| \"Drop\" | Sudden change | Pattern transition |\n",
      "code_example": null
    }
  ],
  "total_matches": 3,
  "query": "build.*up|riser|tension",
  "category_searched": null
}
```

**Error Cases**:
- Invalid category name → Return error with valid category list
- No matches found → Return empty matches list with helpful message
- Invalid regex pattern → Return error with regex syntax help

**Use Cases**:
- "How do I use the scale() function?" → `search_knowledge("scale\\(\\)", "core_functions")`
- "What's euclidean rhythm syntax?" → `search_knowledge("euclidean", "notation")`
- "Show me techno patterns" → `search_knowledge("techno", "patterns")`
- "What does 'bright' mean in code?" → `search_knowledge("bright", "vocabulary")`
- "What 808 drums are available?" → `search_knowledge("808|RolandTR808", "samples")`
- "How do I make a pad sound?" → `search_knowledge("pad|synth.*pad", "synths")`

---

## Knowledge File Structure

### Design Principles

**Each knowledge file should**:
1. **Be searchable** - Consistent headers, keywords, synonyms
2. **Include full examples** - Complete multi-line Strudel scripts with `$:` syntax
3. **Show context** - Not just isolated snippets, but how to use in real songs
4. **Cross-reference** - Link to related concepts
5. **Be practical** - Focus on what agent needs to help user

### File Descriptions

#### `knowledge/notation.md`
**Source**: Curated from `notes/research/02_mini_notation_cheatsheet.md`

**Content**:
- Basic syntax (sequence, rests, alternation, sub-sequences)
- Pattern modifiers (speed up `*`, slow down `/`, elongate `@`, replicate `!`)
- Advanced patterns (euclidean, polyrhythms, nested alternation)
- Full examples showing notation in context

**Example Section**:
```markdown
### Euclidean Rhythms

Distribute events evenly across steps using `(pulses, steps)` syntax.

**Syntax**: `sound("sample(pulses, steps)")`

**Examples**:
```javascript
// 3 kicks in 8 steps - classic pattern
sound("bd(3,8)")

// 5 hi-hats in 8 steps - more complex
sound("hh(5,8)")

// Full beat with euclidean rhythms
$: sound("bd(3,8)")  // Kick
$: sound("sd(5,16)")  // Snare
$: sound("hh(7,8)")   // Hi-hat
```

**Related**: Polyrhythms, Pattern density
```

#### `knowledge/core_functions.md`
**Source**: Curated from `notes/research/03_core_functions_reference.md`

**Content**:
- Sound generation (sound, note, n)
- Tempo control (setcpm, setcps)
- Pattern manipulation (fast, slow, rev, jux, add, ply, off)
- Scales and harmony (scale, chord, voicing)
- Full examples showing functions in songs

**Example Section**:
```markdown
### scale()

Interpret `n()` values as scale degrees.

**Syntax**: `.scale("key:mode")` or `.scale("key:mode:variant")`

**Parameters**:
- `key` - Root note (C, D, Eb, F#, etc.)
- `mode` - Scale mode (major, minor, dorian, etc.)
- `variant` - Optional (pentatonic, blues, etc.)

**Examples**:
```javascript
// Simple C minor melody
$: n("0 2 4 7").scale("C:minor")
  .s("piano")
  .slow(2)

// Pentatonic melody for ambient feel
$: n("0 2 4 5 7 9").scale("D:minor:pentatonic")
  .s("sawtooth")
  .lpf(800)
  .room(0.5)

// Random notes in scale (always sounds good)
$: n(irand(8)).scale("A:minor")
  .s("glockenspiel")
  .fast(4)
```

**Related**: chord(), voicing(), add()
```

#### `knowledge/effects.md`
**Source**: Curated from `notes/research/04_effects_reference.md`

**Content**:
- Filters (lpf, hpf, bpf with ranges and resonance)
- ADSR envelope (attack, decay, sustain, release)
- Filter envelope (lpenv, lpattack, etc.)
- Spatial effects (room, delay, pan)
- Distortion (shape, crush)
- Full examples showing effect chains

**Example Section**:
```markdown
### lpf() - Low-Pass Filter

**Synonyms**: `cutoff`, `ctf`, `lp`  
**Range**: 0-20000 Hz  
**Default**: No filtering

Removes frequencies above the cutoff frequency. Lower values = darker sound.

**Examples**:
```javascript
// Dark, muffled kick
$: sound("bd").lpf(400)

// Sweeping filter on bassline
$: note("c2 eb2 f2 g2")
  .s("sawtooth")
  .lpf(sine.range(200, 800).slow(4))  // Slow sweep
  .resonance(10)  // Add resonance for character

// Progressive darkening over 8 cycles
$: sound("hh*8")
  .lpf("<8000 4000 2000 1000>")  // Gets darker each cycle
```

**Tips**:
- Combine with `resonance()` (lpq) for more pronounced effect
- Use modulation (sine, saw, rand) for movement
- Lower than 200 Hz can sound muddy on bass
- Signal chain: Apply before reverb for natural sound

**Related**: hpf(), bpf(), lpq(), lpenv()
```

#### `knowledge/patterns.md`
**Source**: Curated from `notes/research/07_musical_patterns_library.md`

**Content**:
- Drum patterns (house, techno, breakbeat, hip-hop)
- Basslines (simple, funky, walking, techno)
- Melodic patterns (arpeggios, sequences, generative)
- Chord progressions (basic, complex, jazz)
- Rhythmic techniques (polymeters, phasing, swing)
- Full multi-voice examples

**Example Section**:
```markdown
### Techno Bassline

**Character**: Driving, repetitive, hypnotic  
**Tempo**: 120-140 BPM  
**Technique**: Filter modulation, root note emphasis

**Simple Techno Bass**:
```javascript
setcpm(130)

// Kick
$: sound("bd*4")
  .gain(1.2)

// Minimal bass - just root note with filter sweep
$: note("c2*4")
  .s("sawtooth")
  .lpf(sine.range(200, 800).slow(4))
  .gain(0.8)

// Hi-hats for texture
$: sound("hh*8")
  .gain(0.6)
  .pan(sine.slow(8))  // Subtle movement
```

**Variation - With Progression**:
```javascript
setcpm(130)

$: sound("bd*4")

// Bass with 4-bar progression
$: note("<c2!3 eb2>*4")
  .s("sawtooth")
  .lpf(sine.range(200, 1200).slow(8))
  .resonance(8)
  .gain(0.8)

$: sound("hh*8").gain(0.6)
$: sound("[~ cp]*2").gain(0.7)
```

**Tips**:
- Keep it simple - techno bass is about groove, not complexity
- Filter modulation creates movement without changing notes
- Slight resonance adds character
- Layer with kick, don't fight it

**Related**: Acid Bassline, Deep House Bass, Minimal Patterns
```

#### `knowledge/vocabulary.md`
**Source**: Curated from `notes/research/08_strudel_vocabulary_glossary.md`

**Content**:
- Core concepts (pattern, cycle, mini-notation, stack)
- Musical intent → code translation tables
- Rhythm terms (faster, slower, swing, syncopated)
- Melodic terms (ascending, arpeggio, transpose)
- Harmonic terms (chord, progression, voicing)
- Timbre terms (bright, dark, warm, harsh)
- Dynamic terms (loud, quiet, punchy, sustained)
- Spatial terms (wide, narrow, distant)
- Temporal effects (delay, echo, reverb)
- Genre-specific patterns

**Example Section**:
```markdown
### Musical Intent → Strudel Translation

#### "Make it groovy" / "Add swing"

**Code**: `.late("[0 .01]*4")` or `.late("[0 .02]*2")`  
**Explanation**: Delay alternating notes to create swing feel  
**Best on**: Hi-hats, percussion, snares

**Examples**:
```javascript
// Swing hi-hats
$: sound("hh*8")
  .late("[0 .01]*4")  // Every other note delayed
  .gain(0.7)

// Groovy claps
$: sound("[~ cp]*2")
  .late("[0 .02]*2")  // Heavier swing
  .room(0.3)

// Full groove with swing
setcpm(100)

$: sound("bd*4")  // Kick stays straight
$: sound("[~ sd]*2").gain(0.8)  // Snare straight
$: sound("hh*8")
  .late("[0 .01]*4")  // Hi-hat swings
  .gain("0.5 0.7")  // Accent pattern
```

**Alternative - Ghost Notes**:
```javascript
// Add groove with ghost notes instead
$: sound("sd*2")
  .off(1/8, x => x.gain(0.4))  // Quiet ghost note
```

**Related**: Shuffle, Laid-back, Funky
```

#### `knowledge/samples.md`
**Source**: Curated from `notes/research/05_samples_drums_reference.md`

**Content**:
- Default drum sounds (bd, sd, hh, cp, etc.)
- Drum machine banks (808, 909, 707, etc.)
- Sample selection patterns
- Non-drum samples (piano, bass, casio, etc.)
- Loading custom samples (GitHub, URL, Shabda)
- Pitched samples
- Full examples using samples

**Example Section**:
```markdown
### Roland TR-808 Drum Machine

**Character**: Iconic 80s electronic drums, punchy and synthetic  
**Use for**: Hip-hop, trap, electro, synthwave

**Loading**:
```javascript
// Use .bank() to select 808 sounds
sound("bd").bank("RolandTR808")
```

**Full 808 Beat**:
```javascript
setcpm(90)

// 808 kick - deep and punchy
$: sound("bd*4")
  .bank("RolandTR808")
  .gain(1.2)

// 808 snare - iconic clap-snare hybrid
$: sound("[~ sd]*2")
  .bank("RolandTR808")
  .gain(0.9)

// 808 hi-hats - crisp and tight
$: sound("hh*8")
  .bank("RolandTR808")
  .gain("0.6 0.8")  // Accent pattern

// 808 cowbell - because why not
$: sound("~ ~ cb ~")
  .bank("RolandTR808")
  .gain(0.7)
```

**Sample Variations**:
```javascript
// 808 has multiple kick variations
$: n("0 1 2 3").sound("bd")
  .bank("RolandTR808")
  .slow(2)
```

**Related**: RolandTR909, RolandTR707, Drum Machines
```

#### `knowledge/synths.md`
**Source**: Curated from `notes/research/06_synths_reference.md`

**Content**:
- Basic waveforms (sine, sawtooth, square, triangle)
- Noise generators (white, pink, brown, crackle)
- Additive synthesis (partials, phases)
- Vibrato (vib, vibmod)
- FM synthesis (fm, fmh, fm envelope)
- Wavetable synthesis
- Full synth examples

**Example Section**:
```markdown
### FM Synthesis for Bell Sounds

**Character**: Bright, metallic, bell-like, percussive  
**Technique**: High FM index with moderate harmonicity

**Simple Bell**:
```javascript
$: note("c4 e4 g4 c5")
  .s("sine")  // Start with sine wave
  .fm(10)     // High modulation index = bright
  .fmh(4)     // Harmonicity ratio = timbre
  .decay(1.5) // Long decay for bell ring
  .gain(0.7)
  .room(0.4)  // Add space
```

**Complex Bell Pad**:
```javascript
setcpm(60)

// Layered bells with different harmonicities
$: note("<Cm7 Fm7 Gm7 Bb7>")
  .s("sine")
  .fm(12)
  .fmh("3 4 5")  // Different harmonics per note
  .fmattack(0.01)
  .fmdecay(0.5)
  .decay(2)
  .room(0.6)
  .delay(0.25)
  .delayfeedback(0.4)
  .gain(0.6)
```

**Detuned Bell Ensemble**:
```javascript
// Stack slightly detuned bells for richness
$: stack(
  note("c4 e4 g4").s("sine").fm(10).fmh(4),
  note("c4 e4 g4").s("sine").fm(10).fmh(4).add(0.05),  // Slightly sharp
  note("c4 e4 g4").s("sine").fm(10).fmh(4).add(-0.05)  // Slightly flat
).decay(2).room(0.5).gain(0.5)
```

**Tips**:
- FM index (fm) controls brightness: 5-8 = mellow, 10-15 = bright
- Harmonicity (fmh) controls timbre: integers = harmonic, decimals = inharmonic
- Long decay essential for bell character
- Add reverb and delay for space
- Layer multiple bells with slight detuning for richness

**Related**: Additive Synthesis, Metallic Sounds, Percussion Synths
```

#### `knowledge/best_practices.md`
**Source**: New, curated from research + experience

**Content**:
- Signal chain order (filters before reverb, etc.)
- Performance optimization (voice count, effect limits)
- Code organization (setup section, voice sections, comments)
- Common mistakes and how to avoid them
- Debugging tips
- Live coding workflow

**Example Section**:
```markdown
### Signal Chain Order

**Rule**: Effects are applied in the order you write them. Order matters!

**Good Practice**:
1. **Source** - sound() or note()
2. **Pitch/Tuning** - note(), add(), scale()
3. **Filters** - lpf(), hpf(), bpf()
4. **Distortion** - shape(), crush()
5. **Dynamics** - gain(), compress()
6. **Spatial** - room(), delay(), pan()

**Examples**:
```javascript
// GOOD - Filter before reverb sounds natural
$: sound("bd")
  .lpf(800)      // Filter first
  .room(0.5)     // Then reverb

// BAD - Reverb before filter sounds unnatural
$: sound("bd")
  .room(0.5)     // Reverb first
  .lpf(800)      // Then filter (cuts the reverb tail!)

// GOOD - Distortion before delay
$: note("c2")
  .s("sawtooth")
  .shape(0.6)    // Distort first
  .delay(0.25)   // Then delay
  .room(0.3)     // Then reverb

// GOOD - Complete chain
$: note("c3 eb3 g3")
  .s("sawtooth")     // 1. Source
  .lpf(1200)         // 2. Filter
  .resonance(8)      // 2b. Filter resonance
  .shape(0.3)        // 3. Distortion
  .gain(0.8)         // 4. Dynamics
  .pan(sine.slow(4)) // 5. Spatial (pan)
  .delay(0.125)      // 5b. Spatial (delay)
  .room(0.4)         // 5c. Spatial (reverb)
```

**Why This Matters**:
- Reverb after filter = natural (filtered sound in space)
- Reverb before filter = unnatural (cuts reverb tail)
- Distortion after delay = muddy (distorts the echoes)
- Distortion before delay = clean (echoes are clean)

**Related**: Effect Parameters, Performance Optimization
```

---

## Agent Workflow Integration

### System Prompt Guidance

The agent's system prompt should include:

**When to use `search_knowledge`**:
- User asks "how do I..." questions
- Agent is unsure about syntax
- Agent needs to verify function parameters
- Agent wants to find example patterns
- Agent needs to translate musical intent to code
- Agent is composing code and wants to check best practices

**How to use it effectively**:
```
1. Before generating code:
   - If unsure about syntax → search_knowledge(query, category="notation")
   - If need function details → search_knowledge(query, category="core_functions")
   - If using effects → search_knowledge(query, category="effects")
   - If need pattern example → search_knowledge(query, category="patterns")
   
2. When user uses musical terms:
   - "groovy", "bright", "punchy", etc. → search_knowledge(query, category="vocabulary")
   
3. When user asks about samples:
   - "808 drums", "what samples", etc. → search_knowledge(query, category="samples")
   
4. When unsure which category:
   - Use category=None to search all files
   
5. Use regex patterns:
   - Alternatives: "swing|shuffle|groov.*"
   - Wildcards: "lpf.*range", "build.*up"
   - Exact: "scale\\(\\)", "note\\(\\)"
```

**Citation behavior**:
```
When using search_knowledge results, cite the source:
- "According to the notation reference, euclidean rhythms use (pulses, steps) syntax."
- "The effects reference shows lpf() range is 0-20000 Hz."
- "I found this techno bassline pattern in the patterns library."
```

### Example Agent Flow

**User**: "Add a groovy techno bassline"

```
1. Agent thinks:
   - "groovy" = need to look up what that means in code
   - "techno bassline" = need pattern example

2. Agent calls search_knowledge:
   
   search_knowledge("groov.*|swing", category="vocabulary")
   → Returns: .late("[0 .01]*4") for swing
   
   search_knowledge("techno.*bass", category="patterns")
   → Returns: Full techno bass pattern with filter sweep

3. Agent composes:
   - Takes techno bass pattern from results
   - Adds swing technique from vocabulary
   - Validates it makes sense together

4. Agent generates patch:
   patch_instructions = {
     "action": "append",
     "new_content": "\n$: note(\"c2*4\")\n  .s(\"sawtooth\")\n  .lpf(sine.range(200, 800).slow(4))\n  .late(\"[0 .01]*4\")\n"
   }

5. Agent responds:
   "Added a groovy techno bassline with swing timing. 
    The pattern uses a repetitive root note with filter modulation 
    (from the patterns library) and swing timing via .late() 
    (from the vocabulary reference)."
```

---

## Implementation Notes

### Technical Approach

**Simple and Fast**:
- Read markdown files from `knowledge/` directory
- Use Python `re` module for regex search
- Parse markdown to extract sections and code blocks
- Return structured results
- No database, no indexing, just file I/O + regex

**Performance**:
- Knowledge files are small (< 100KB each)
- Regex search on 8 files is fast enough
- Can cache file contents in memory on startup
- No need for complex indexing

### Client Implementation

```python
# src/knowledge.py
import re
from pathlib import Path
from typing import List, Dict, Optional

class KnowledgeBase:
    """Search knowledge markdown files."""
    
    CATEGORIES = {
        'notation': 'notation.md',
        'core_functions': 'core_functions.md',
        'effects': 'effects.md',
        'patterns': 'patterns.md',
        'vocabulary': 'vocabulary.md',
        'samples': 'samples.md',
        'synths': 'synths.md',
        'best_practices': 'best_practices.md'
    }
    
    def __init__(self, knowledge_dir: str = "./knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self._cache = {}  # Cache file contents
        self._load_files()
    
    def _load_files(self):
        """Load all knowledge files into memory."""
        for category, filename in self.CATEGORIES.items():
            file_path = self.knowledge_dir / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self._cache[category] = f.read()
    
    def search(self, query: str, category: Optional[str] = None, 
              context_lines: int = 3, max_results: int = 10) -> Dict:
        """Search knowledge files with regex."""
        
        # Determine which files to search
        if category:
            if category not in self.CATEGORIES:
                raise ValueError(f"Invalid category. Valid: {list(self.CATEGORIES.keys())}")
            files_to_search = {category: self._cache[category]}
        else:
            files_to_search = self._cache
        
        matches = []
        
        for cat, content in files_to_search.items():
            file_matches = self._search_file(content, query, cat, context_lines)
            matches.extend(file_matches)
        
        # Limit results
        matches = matches[:max_results]
        
        return {
            'matches': matches,
            'total_matches': len(matches),
            'query': query,
            'category_searched': category
        }
    
    def _search_file(self, content: str, query: str, category: str, 
                    context_lines: int) -> List[Dict]:
        """Search single file content."""
        lines = content.splitlines()
        matches = []
        
        for i, line in enumerate(lines):
            if re.search(query, line, re.IGNORECASE):
                # Extract context
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = '\n'.join(lines[start:end])
                
                # Find section header
                section = self._find_section(lines, i)
                
                # Extract code example if nearby
                code_example = self._extract_code_block(lines, i)
                
                matches.append({
                    'file': self.CATEGORIES[category],
                    'section': section,
                    'line_number': i + 1,
                    'content': context,
                    'code_example': code_example
                })
        
        return matches
    
    def _find_section(self, lines: List[str], current_line: int) -> str:
        """Find markdown section header above current line."""
        for i in range(current_line, -1, -1):
            if lines[i].startswith('#'):
                return lines[i].lstrip('#').strip()
        return "Unknown"
    
    def _extract_code_block(self, lines: List[str], 
                           current_line: int, search_radius: int = 10) -> Optional[str]:
        """Extract code block near current line."""
        # Look for ```javascript blocks within search_radius
        start_line = max(0, current_line - search_radius)
        end_line = min(len(lines), current_line + search_radius)
        
        in_code_block = False
        code_lines = []
        
        for i in range(start_line, end_line):
            if lines[i].startswith('```'):
                if in_code_block:
                    # End of code block
                    return '\n'.join(code_lines)
                else:
                    # Start of code block
                    in_code_block = True
                    code_lines = []
            elif in_code_block:
                code_lines.append(lines[i])
        
        return None

# In src/client.py
class StrudelClient:
    def __init__(self, knowledge_dir: str = "./knowledge"):
        self.knowledge = KnowledgeBase(knowledge_dir)
    
    def search_knowledge(self, query: str, category: Optional[str] = None,
                        context_lines: int = 3, max_results: int = 10) -> Dict:
        """Search knowledge files."""
        return self.knowledge.search(query, category, context_lines, max_results)
```

---

## Updated Tool Count

### Total Toolset

**From proposed_set_draft.md**: 19 tools  
**New knowledge tool**: 1 tool (`search_knowledge`)  
**Total**: **20 tools**

### Tool Breakdown

1. **Canvas Tools** (3) - get_song, update_song, validate_script
2. **Project Tools** (5) - list, create, get_metadata, update_metadata, delete
3. **Clip Tools** (5) - search, get, save, update, delete
4. **Knowledge Tools** (4) - query_packs, query_vocab, identify_pattern, get_function_info
5. **Analysis Tools** (2) - analyze_song_structure, find_similar_clips
6. **Knowledge Access** (1) - **search_knowledge** ✨

---

## Priority

### High Priority (MVP)

**Essential tools**:
1. get_song
2. update_song
3. validate_script
4. search_clips
5. list_projects
6. query_packs
7. query_vocab
8. **search_knowledge** ✨ - **Critical for agent intelligence**

### Medium Priority

9-14. (Same as proposed_set_draft.md)

### Low Priority

15-19. (Same as proposed_set_draft.md)

---

## Next Steps

1. ✅ Simplify knowledge access to single tool
2. ⏭️ Curate `knowledge/` files from `notes/research/`
   - Add full multi-line examples with `$:` syntax
   - Add context and related concepts
   - Optimize for regex search
3. ⏭️ Implement `src/knowledge.py` (simple regex search)
4. ⏭️ Add `search_knowledge` to client and MCP server
5. ⏭️ Update agent system prompt with usage guidance
6. ⏭️ Test agent with knowledge lookups

---

**Status**: Extended set finalized. Single `search_knowledge` tool with flexible parameters. Ready to curate knowledge files.
