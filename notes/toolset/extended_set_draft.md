# Strudel MCP Toolset - Extended Knowledge Access Tools

**Date**: 2025-12-22  
**Status**: Extension to proposed_set_draft.md  
**Purpose**: Define knowledge access tools that extend agent capabilities beyond system prompt

---

## Motivation

Even with a comprehensive system prompt, the agent needs access to **deep reference knowledge** about Strudel:
- Mini-notation syntax details
- Core function parameters and usage
- Effects reference with ranges and synonyms
- Musical pattern examples
- Vocabulary mapping (musical intent → code)
- Sample/drum sound catalogs
- Synthesis techniques

**Problem**: System prompts have token limits and can't contain all this detail.

**Solution**: Knowledge access tools that let the agent **look up instructions on-demand** using regex queries.

**Benefits**:
1. Agent output becomes more **controlled** and **accurate**
2. Agent is **aware** it's using a tool to get instructions (metacognitive)
3. System prompt can focus on **when to use** these tools, not cramming all the knowledge
4. Knowledge can be **updated** without changing agent code
5. Agent can **cite sources** when explaining to user

---

## Knowledge Organization

Create a curated `knowledge/` folder with structured reference files:

```
knowledge/
  notation.md          # Mini-notation syntax reference
  core_functions.md    # Core functions with parameters
  effects.md           # Effects with ranges, synonyms, examples
  patterns.md          # Musical pattern library
  vocabulary.md        # Musical intent → Strudel code mapping
  samples.md           # Sample/drum sound catalog
  synths.md            # Synthesis techniques
  best_practices.md    # Coding conventions, tips, gotchas
```

**Source**: Curated from `notes/research/` with structure optimized for agent lookup.

---

## Extended Tool Set

### 6. Knowledge Access Tools

**Why These Tools?**

The agent needs to:
- Look up syntax when user asks for specific notation
- Find function parameters when composing code
- Discover musical patterns for specific genres/feels
- Translate musical intent to code
- Understand effect ranges to avoid invalid values
- Learn best practices for specific scenarios

---

### `lookup_notation`

**Purpose**: Look up mini-notation syntax and usage.

**Why**: User says "how do I make a polyrhythm?" or agent needs to know euclidean syntax.

**Functionality**:
- Search `knowledge/notation.md` by regex
- Find syntax patterns, examples, explanations
- Return relevant sections with context

**Input**:
```python
query: str  # Regex pattern to search for
context_lines: int = 3  # Lines of context around match
```

**Output**:
```python
{
  "matches": list[{
    "section": str,  # Section heading where match found
    "content": str,  # Matched content with context
    "line_number": int,
    "example": str | None  # Code example if available
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# User: "How do I create a polyrhythm?"
# Agent calls:
lookup_notation(query="polyrhythm|\\{.*,.*\\}")

# Returns:
{
  "matches": [
    {
      "section": "Polyrhythms",
      "content": "Different time signatures\nsound(\"{bd sd hh, cp cp cp cp}\")  // 3 against 4",
      "line_number": 35,
      "example": "sound(\"{bd sd hh, cp cp cp cp}\")"
    }
  ]
}
```

**Use Cases**:
- "How do I make euclidean rhythms?"
- "What's the syntax for alternation?"
- "How do I nest patterns?"
- Agent needs to verify syntax before generating code

---

### `lookup_function`

**Purpose**: Look up Strudel function details (parameters, usage, examples).

**Why**: Agent needs to know function signatures, parameter ranges, return types.

**Functionality**:
- Search `knowledge/core_functions.md` by function name or concept
- Return function signature, parameters, examples
- Include related functions

**Input**:
```python
query: str  # Function name or regex pattern
include_examples: bool = True
```

**Output**:
```python
{
  "functions": list[{
    "name": str,
    "aliases": list[str],  # Alternative names (e.g., s() for sound())
    "description": str,
    "parameters": list[{
      "name": str,
      "type": str,
      "description": str,
      "default": any | None,
      "range": str | None  # e.g., "0-1", "0-20000 Hz"
    }],
    "examples": list[str],
    "related_functions": list[str],
    "category": str  # "sound_generation" | "tempo" | "pattern_manipulation" | etc.
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# User: "Make it faster"
# Agent calls:
lookup_function(query="fast|speed")

# Returns:
{
  "functions": [
    {
      "name": "fast",
      "aliases": [],
      "description": "Speeds up a pattern by a given factor",
      "parameters": [
        {
          "name": "factor",
          "type": "number",
          "description": "Speed multiplier",
          "default": null,
          "range": "> 0"
        }
      ],
      "examples": [
        "sound(\"bd sd\").fast(2)",
        "note(\"c e g\").fast(\"<1 2 4>\")"
      ],
      "related_functions": ["slow", "hurry"],
      "category": "pattern_manipulation"
    }
  ]
}
```

**Use Cases**:
- "How do I use the scale() function?"
- "What parameters does lpf() accept?"
- Agent needs to verify function exists before using it
- Agent wants to find alternative functions

---

### `lookup_effect`

**Purpose**: Look up audio effect details (parameters, ranges, synonyms).

**Why**: Agent needs to know effect parameter ranges to generate valid code.

**Functionality**:
- Search `knowledge/effects.md` by effect name or musical intent
- Return effect details with parameter ranges
- Include synonyms and related effects

**Input**:
```python
query: str  # Effect name or regex pattern
include_examples: bool = True
```

**Output**:
```python
{
  "effects": list[{
    "name": str,
    "synonyms": list[str],  # Alternative names
    "category": str,  # "filter" | "envelope" | "spatial" | "distortion" | etc.
    "description": str,
    "parameters": list[{
      "name": str,
      "type": str,
      "range": str,  # e.g., "0-20000 Hz", "0-1"
      "default": any | None,
      "description": str
    }],
    "examples": list[str],
    "related_effects": list[str],
    "signal_chain_position": int | None  # Order in signal chain
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# User: "Make it darker"
# Agent calls:
lookup_effect(query="dark|low.*pass|lpf")

# Returns:
{
  "effects": [
    {
      "name": "lpf",
      "synonyms": ["cutoff", "ctf", "lp"],
      "category": "filter",
      "description": "Low-pass filter - removes high frequencies",
      "parameters": [
        {
          "name": "frequency",
          "type": "number",
          "range": "0-20000 Hz",
          "default": null,
          "description": "Cutoff frequency"
        }
      ],
      "examples": [
        "sound(\"bd\").lpf(400)",
        "sound(\"sawtooth\").lpf(sine.range(400, 4000))"
      ],
      "related_effects": ["lpq", "hpf", "bpf"],
      "signal_chain_position": 3
    }
  ]
}
```

**Use Cases**:
- "What's the range for reverb room size?"
- "How do I make something sound distant?"
- Agent needs to validate effect parameters
- Agent wants to find similar effects

---

### `lookup_pattern`

**Purpose**: Look up proven musical patterns by genre, technique, or element.

**Why**: Agent can find example patterns for specific musical contexts.

**Functionality**:
- Search `knowledge/patterns.md` by genre, technique, element
- Return complete pattern examples with explanations
- Include variations and related patterns

**Input**:
```python
query: str  # Regex pattern for genre/technique/element
element_filter: str | None = None  # "drums" | "bass" | "melody" | "chords" | etc.
```

**Output**:
```python
{
  "patterns": list[{
    "name": str,
    "description": str,
    "element": str,  # "drums" | "bass" | "melody" | "chords" | "rhythm" | etc.
    "genre": list[str],  # ["techno", "house", etc.]
    "technique": list[str],  # ["euclidean", "polyrhythm", etc.]
    "code": str,  # Complete pattern code
    "explanation": str,  # What makes this pattern work
    "variations": list[str],  # Alternative versions
    "related_patterns": list[str]
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# User: "Add a techno bassline"
# Agent calls:
lookup_pattern(query="techno.*bass|bass.*techno", element_filter="bass")

# Returns:
{
  "patterns": [
    {
      "name": "Minimal Techno Bass",
      "description": "Driving bass pattern with filter modulation",
      "element": "bass",
      "genre": ["techno", "minimal"],
      "technique": ["filter-modulation", "repetitive"],
      "code": "note(\"c2*4\").s(\"sawtooth\").lpf(sine.range(200, 800).slow(4))",
      "explanation": "Repetitive root note with slow filter sweep creates hypnotic movement",
      "variations": [
        "note(\"<c2 c2 eb2 f2>*4\").s(\"sawtooth\").lpf(400)",
        "note(\"c2!3 eb2\").s(\"sawtooth\").lpf(600).resonance(10)"
      ],
      "related_patterns": ["acid_bassline", "deep_house_bass"]
    }
  ]
}
```

**Use Cases**:
- "Show me a house drum pattern"
- "I need an arpeggio example"
- "What's a good breakbeat pattern?"
- Agent wants to suggest patterns to user

---

### `lookup_vocabulary`

**Purpose**: Translate musical intent to Strudel code.

**Why**: User speaks in musical terms ("make it groovy"), agent needs code.

**Functionality**:
- Search `knowledge/vocabulary.md` by musical term
- Return Strudel code equivalents
- Include multiple interpretations when ambiguous

**Input**:
```python
musical_intent: str  # Regex pattern for musical term
category: str | None = None  # "rhythm" | "melody" | "harmony" | "timbre" | "dynamics" | "spatial"
```

**Output**:
```python
{
  "translations": list[{
    "musical_term": str,
    "category": str,
    "strudel_code": str,
    "explanation": str,
    "context": str,  # When to use this interpretation
    "examples": list[str],
    "related_terms": list[str]
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# User: "Make it groovy"
# Agent calls:
lookup_vocabulary(musical_intent="groov.*|swing|shuffle")

# Returns:
{
  "translations": [
    {
      "musical_term": "groovy",
      "category": "rhythm",
      "strudel_code": ".late('[0 .01]*4')",
      "explanation": "Add swing feel by delaying alternating notes",
      "context": "Works best on hi-hats and percussion",
      "examples": [
        "sound(\"hh*8\").late('[0 .01]*4')",
        "sound(\"~ cp*2\").late('[0 .02]*2')"
      ],
      "related_terms": ["swing", "shuffle", "laid-back"]
    },
    {
      "musical_term": "groovy",
      "category": "rhythm",
      "strudel_code": ".off(1/8, x => x.gain(0.6))",
      "explanation": "Add ghost notes for groove",
      "context": "Works on snares and kicks",
      "examples": [
        "sound(\"sd*2\").off(1/8, x => x.gain(0.6))"
      ],
      "related_terms": ["ghost-notes", "funky"]
    }
  ]
}
```

**Use Cases**:
- "What does 'bright' mean in code?"
- "How do I make something sound 'distant'?"
- "User said 'punchy', what should I do?"
- Agent disambiguates vague musical terms

---

### `lookup_samples`

**Purpose**: Look up available samples/drums and their characteristics.

**Why**: Agent needs to know what samples exist and how to use them.

**Functionality**:
- Search `knowledge/samples.md` by sample name, type, or character
- Return sample details with usage examples
- Include bank information for drum machines

**Input**:
```python
query: str  # Regex pattern for sample name or type
sample_type: str | None = None  # "drums" | "melodic" | "fx" | "percussion"
```

**Output**:
```python
{
  "samples": list[{
    "name": str,
    "abbreviation": str | None,
    "type": str,  # "drums" | "melodic" | "fx" | "percussion"
    "description": str,
    "character": list[str],  # ["punchy", "vintage", "electronic", etc.]
    "banks": list[str] | None,  # Drum machine banks if applicable
    "usage_examples": list[str],
    "variations": int | None,  # Number of sample variations available
    "related_samples": list[str]
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# User: "Add a vintage kick"
# Agent calls:
lookup_samples(query="kick|bd", sample_type="drums")

# Returns:
{
  "samples": [
    {
      "name": "bd",
      "abbreviation": "bd",
      "type": "drums",
      "description": "Bass drum / kick drum",
      "character": ["punchy", "deep", "foundational"],
      "banks": ["RolandTR808", "RolandTR909", "RolandTR707"],
      "usage_examples": [
        "sound(\"bd*4\")",
        "sound(\"bd*4\").bank('RolandTR808')",
        "n(\"0 1 2\").sound(\"bd\")"
      ],
      "variations": 24,
      "related_samples": ["kick", "bassdrum"]
    }
  ]
}
```

**Use Cases**:
- "What hi-hat samples are available?"
- "Show me 808 drum sounds"
- "What's the difference between bd and kick?"
- Agent needs to select appropriate samples

---

### `lookup_synth_technique`

**Purpose**: Look up synthesis techniques and parameters.

**Why**: Agent needs to know how to create specific synth sounds.

**Functionality**:
- Search `knowledge/synths.md` by technique or desired sound
- Return synthesis approach with parameters
- Include waveform selection, modulation, etc.

**Input**:
```python
query: str  # Regex pattern for technique or sound description
sound_character: str | None = None  # "bright" | "warm" | "harsh" | "bell-like" | etc.
```

**Output**:
```python
{
  "techniques": list[{
    "name": str,
    "description": str,
    "sound_character": list[str],
    "approach": str,  # "additive" | "FM" | "wavetable" | "subtractive"
    "waveform": str | None,
    "parameters": dict,  # Key synthesis parameters
    "code_example": str,
    "use_cases": list[str],
    "related_techniques": list[str]
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# User: "Create a bell-like sound"
# Agent calls:
lookup_synth_technique(query="bell|metallic", sound_character="bright")

# Returns:
{
  "techniques": [
    {
      "name": "FM Bell Synthesis",
      "description": "Use FM synthesis with high modulation index for bell timbres",
      "sound_character": ["bright", "metallic", "bell-like", "percussive"],
      "approach": "FM",
      "waveform": "sine",
      "parameters": {
        "fm": "8-12 (high modulation index)",
        "fmh": "3-5 (harmonicity ratio)",
        "decay": "0.5-2 (long decay)"
      },
      "code_example": "note(\"c4 e4 g4\").s(\"sine\").fm(10).fmh(4).decay(1.5)",
      "use_cases": ["bells", "chimes", "metallic percussion"],
      "related_techniques": ["additive_synthesis", "wavetable_bells"]
    }
  ]
}
```

**Use Cases**:
- "How do I make a pad sound?"
- "What's the best way to create a bass synth?"
- "I want a harsh, aggressive sound"
- Agent needs synthesis guidance

---

### `lookup_best_practices`

**Purpose**: Look up coding conventions, tips, and common gotchas.

**Why**: Agent should follow best practices and avoid common mistakes.

**Functionality**:
- Search `knowledge/best_practices.md` by topic or scenario
- Return recommendations, warnings, tips
- Include do's and don'ts

**Input**:
```python
query: str  # Regex pattern for topic or scenario
topic: str | None = None  # "performance" | "composition" | "effects" | "live-coding" | etc.
```

**Output**:
```python
{
  "practices": list[{
    "topic": str,
    "title": str,
    "recommendation": str,
    "rationale": str,
    "examples": {
      "good": list[str],
      "bad": list[str]
    },
    "gotchas": list[str],  # Common mistakes
    "related_topics": list[str]
  }],
  "total_matches": int
}
```

**Example Usage**:
```python
# Agent is about to generate code with many effects
# Agent calls:
lookup_best_practices(query="effect.*chain|signal.*order", topic="effects")

# Returns:
{
  "practices": [
    {
      "topic": "effects",
      "title": "Signal Chain Order",
      "recommendation": "Apply effects in proper order: filters before reverb, distortion before delay",
      "rationale": "Signal chain order affects final sound. Reverb after filter sounds more natural.",
      "examples": {
        "good": [
          "sound(\"bd\").lpf(800).room(0.5)",
          "sound(\"sawtooth\").shape(0.4).delay(0.25)"
        ],
        "bad": [
          "sound(\"bd\").room(0.5).lpf(800)  // Filter after reverb sounds unnatural"
        ]
      },
      "gotchas": [
        "Reverb before filter can sound muddy",
        "Too many effects can cause performance issues"
      ],
      "related_topics": ["performance_optimization", "effect_parameters"]
    }
  ]
}
```

**Use Cases**:
- "What's the best way to structure a song?"
- "How many effects is too many?"
- "Should I use .fast() or *2?"
- Agent self-checks before generating code

---

### `search_knowledge`

**Purpose**: General-purpose search across all knowledge files.

**Why**: When agent doesn't know which specific knowledge tool to use.

**Functionality**:
- Search all files in `knowledge/` directory
- Return matches grouped by file/category
- Useful for exploratory queries

**Input**:
```python
query: str  # Regex pattern to search across all knowledge
max_results: int = 20
context_lines: int = 2
```

**Output**:
```python
{
  "results": list[{
    "file": str,  # Which knowledge file
    "category": str,  # Derived from filename
    "section": str,  # Section heading
    "content": str,  # Matched content with context
    "line_number": int,
    "relevance_score": float  # Based on match quality
  }],
  "total_matches": int,
  "files_searched": list[str]
}
```

**Example Usage**:
```python
# User: "How do I make a build-up?"
# Agent unsure which knowledge category, calls:
search_knowledge(query="build.*up|riser|tension")

# Returns matches from multiple files:
{
  "results": [
    {
      "file": "patterns.md",
      "category": "patterns",
      "section": "Transitions",
      "content": "Build-up with increasing density: sound(\"hh*<4 8 16 32>\")",
      "line_number": 245,
      "relevance_score": 0.92
    },
    {
      "file": "effects.md",
      "category": "effects",
      "section": "Filter Sweeps",
      "content": "Rising filter for tension: .hpf(sine.range(100, 8000).slow(8))",
      "line_number": 178,
      "relevance_score": 0.85
    },
    {
      "file": "vocabulary.md",
      "category": "vocabulary",
      "section": "Temporal Effects",
      "content": "Build-up: Increasing intensity over time",
      "line_number": 103,
      "relevance_score": 0.78
    }
  ],
  "total_matches": 3,
  "files_searched": ["notation.md", "core_functions.md", "effects.md", "patterns.md", "vocabulary.md", "samples.md", "synths.md", "best_practices.md"]
}
```

**Use Cases**:
- Agent doesn't know which specific tool to use
- User asks broad question
- Agent wants to explore related concepts
- Fallback when specific lookups return nothing

---

## Integration with Agent System Prompt

### System Prompt Strategy

**Don't**: Cram all Strudel knowledge into system prompt  
**Do**: Teach agent **when and how** to use knowledge tools

**System Prompt Should Include**:

1. **Tool Usage Triggers**:
   ```
   When user asks about:
   - Syntax → use lookup_notation()
   - Functions → use lookup_function()
   - Effects → use lookup_effect()
   - Musical intent → use lookup_vocabulary()
   - Patterns/examples → use lookup_pattern()
   - Samples → use lookup_samples()
   - Synthesis → use lookup_synth_technique()
   - Best practices → use lookup_best_practices()
   - Unsure → use search_knowledge()
   ```

2. **Workflow Integration**:
   ```
   Before generating code:
   1. If unsure about syntax → lookup_notation()
   2. If unsure about function parameters → lookup_function()
   3. If using effects → lookup_effect() to verify ranges
   4. If need example pattern → lookup_pattern()
   
   After generating code:
   1. Check against best_practices
   2. Verify all functions exist
   3. Validate parameter ranges
   ```

3. **Citation Behavior**:
   ```
   When using knowledge tools, cite the source:
   "According to the mini-notation reference, polyrhythms use {...} syntax."
   "The effects reference shows lpf() range is 0-20000 Hz."
   ```

4. **Metacognitive Awareness**:
   ```
   Agent should be aware when it's using a tool:
   "Let me look up the best pattern for techno bass..."
   "I'll check the effects reference for reverb parameters..."
   ```

---

## Knowledge File Structure

### Optimization for Regex Search

Knowledge files should be structured for easy regex lookup:

**Consistent Headings**:
```markdown
### Function: fast()
**Aliases**: None  
**Category**: Pattern Manipulation  
**Description**: Speeds up a pattern by a given factor

**Parameters**:
- `factor` (number): Speed multiplier, range: > 0

**Examples**:
```javascript
sound("bd sd").fast(2)
```

**Related**: slow(), hurry()
```

**Searchable Keywords**:
- Include synonyms: "speed up", "faster", "accelerate"
- Include musical terms: "tempo", "pace"
- Include use cases: "double time", "half time"

**Structured Data**:
- Use consistent formatting for ranges: "0-1", "0-20000 Hz"
- Use consistent formatting for examples: Always in code blocks
- Use consistent formatting for related items: Comma-separated lists

---

## Curation Process

### From Research Notes to Knowledge Files

**Steps**:

1. **Extract from `notes/research/`**:
   - 02_mini_notation_cheatsheet.md → `knowledge/notation.md`
   - 03_core_functions_reference.md → `knowledge/core_functions.md`
   - 04_effects_reference.md → `knowledge/effects.md`
   - 05_samples_drums_reference.md → `knowledge/samples.md`
   - 06_synths_reference.md → `knowledge/synths.md`
   - 07_musical_patterns_library.md → `knowledge/patterns.md`
   - 08_strudel_vocabulary_glossary.md → `knowledge/vocabulary.md`

2. **Restructure for Agent Lookup**:
   - Add consistent section headers
   - Add searchable keywords
   - Add parameter ranges in standard format
   - Add more examples where needed
   - Cross-reference related concepts

3. **Create `knowledge/best_practices.md`**:
   - Extract tips from research notes
   - Add common gotchas
   - Add performance considerations
   - Add composition guidelines

4. **Validate Structure**:
   - Test regex searches
   - Ensure all sections are findable
   - Check for consistency

---

## Tool Priority

### High Priority (MVP)

**Essential for agent to function**:

1. `lookup_function` - Agent must know function signatures
2. `lookup_effect` - Agent must know effect parameter ranges
3. `lookup_vocabulary` - Agent must translate musical intent
4. `search_knowledge` - Fallback for all queries

### Medium Priority (Enhanced)

**Improve agent quality**:

5. `lookup_notation` - Better syntax understanding
6. `lookup_pattern` - Provide proven examples
7. `lookup_samples` - Better sample selection

### Low Priority (Nice-to-Have)

**Polish and edge cases**:

8. `lookup_synth_technique` - Advanced synthesis
9. `lookup_best_practices` - Code quality

---

## Implementation Notes

### Technical Approach

**Simple File-Based Search**:
- Use Python's `re` module for regex search
- Read knowledge files on-demand (or cache in memory)
- Return structured results from markdown parsing

**No Database Needed**:
- Knowledge files are static reference material
- File-based search is fast enough for small corpus
- Easy to update by editing markdown files

**Markdown Parsing**:
- Extract section headers for context
- Parse code blocks for examples
- Extract lists for related items
- Use regex to find parameter ranges, descriptions

### Client Architecture Extension

```python
# src/knowledge.py
class KnowledgeBase:
    def __init__(self, knowledge_dir: Path):
        self.knowledge_dir = knowledge_dir
        self.files = {
            'notation': 'notation.md',
            'functions': 'core_functions.md',
            'effects': 'effects.md',
            'patterns': 'patterns.md',
            'vocabulary': 'vocabulary.md',
            'samples': 'samples.md',
            'synths': 'synths.md',
            'best_practices': 'best_practices.md'
        }
    
    def search(self, file_key: str, pattern: str, context_lines: int = 3):
        # Regex search in specific file
        # Return structured results
        pass
    
    def search_all(self, pattern: str, max_results: int = 20):
        # Search across all knowledge files
        pass
    
    def parse_section(self, content: str):
        # Parse markdown section into structured data
        pass
```

---

## Example Agent Workflow with Knowledge Tools

### Scenario: User says "Add a groovy techno bassline"

```
1. Agent interprets:
   - "groovy" = needs rhythm feel (lookup_vocabulary)
   - "techno bassline" = needs pattern example (lookup_pattern)

2. Agent calls tools:
   lookup_vocabulary(musical_intent="groov.*")
   → Returns: .late('[0 .01]*4') for swing
   
   lookup_pattern(query="techno.*bass", element_filter="bass")
   → Returns: note("c2*4").s("sawtooth").lpf(sine.range(200, 800).slow(4))

3. Agent composes:
   - Combines pattern with groove technique
   - Creates: note("c2*4").s("sawtooth").lpf(sine.range(200, 800).slow(4)).late('[0 .01]*4')

4. Agent validates:
   lookup_function(query="late")
   → Confirms .late() exists and usage is correct
   
   lookup_effect(query="lpf")
   → Confirms lpf range (0-20000 Hz), sine.range(200, 800) is valid

5. Agent applies:
   update_song(project, patch_instructions)

6. Agent responds:
   "Added a groovy techno bassline with swing timing (.late()) and 
    filter modulation (.lpf() with sine wave). The pattern uses a 
    repetitive root note (c2) which is typical for minimal techno."
```

**Benefits**:
- Agent **looked up** what "groovy" means (didn't guess)
- Agent **found** a proven techno bass pattern (didn't invent)
- Agent **validated** functions and parameters (didn't assume)
- Agent **cited** knowledge sources in response (transparent)

---

## Summary

### 8 New Knowledge Tools

| Tool | Purpose | Priority |
|------|---------|----------|
| `lookup_notation` | Mini-notation syntax lookup | MEDIUM |
| `lookup_function` | Function signatures and usage | HIGH |
| `lookup_effect` | Effect parameters and ranges | HIGH |
| `lookup_pattern` | Musical pattern examples | MEDIUM |
| `lookup_vocabulary` | Musical intent → code translation | HIGH |
| `lookup_samples` | Sample catalog and usage | MEDIUM |
| `lookup_synth_technique` | Synthesis techniques | LOW |
| `lookup_best_practices` | Coding guidelines and gotchas | LOW |
| `search_knowledge` | General-purpose search | HIGH |

### Total Toolset Now

**From proposed_set_draft.md**: 19 tools  
**New knowledge tools**: 9 tools  
**Total**: 28 tools

### Knowledge Files to Create

```
knowledge/
  notation.md          # From 02_mini_notation_cheatsheet.md
  core_functions.md    # From 03_core_functions_reference.md
  effects.md           # From 04_effects_reference.md
  patterns.md          # From 07_musical_patterns_library.md
  vocabulary.md        # From 08_strudel_vocabulary_glossary.md
  samples.md           # From 05_samples_drums_reference.md
  synths.md            # From 06_synths_reference.md
  best_practices.md    # New, curated from research + experience
```

### Next Steps

1. ✅ Document extended toolset (this file)
2. ⏭️ Curate `knowledge/` files from `notes/research/`
3. ⏭️ Implement `src/knowledge.py` module
4. ⏭️ Add knowledge tools to MCP server
5. ⏭️ Update agent system prompt with tool usage triggers
6. ⏭️ Test agent with knowledge tools

---

**Status**: Extended toolset defined. Ready to curate knowledge files and implement.
