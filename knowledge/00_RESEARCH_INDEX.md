# Strudel Research Index

**Research Completed**: 2025-12-22

This folder contains comprehensive research on Strudel live coding for music, gathered from official documentation.

## Research Files

### 01_strudel_overview.md
**Purpose**: High-level introduction to Strudel  
**Content**:
- What is Strudel and its philosophy
- Core concepts (patterns, cycles, mini-notation)
- Sound generation methods
- Musical organization
- Integration capabilities

### 02_mini_notation_cheatsheet.md
**Purpose**: Complete reference for Strudel's pattern syntax  
**Content**:
- Basic syntax table
- Advanced patterns (Euclidean, polyrhythms)
- Pattern modifiers
- Combining patterns
- Common rhythmic patterns
- Pro tips

### 03_core_functions_reference.md
**Purpose**: Essential Strudel functions  
**Content**:
- Sound generation (`sound`, `note`, `n`)
- Tempo control (`setcpm`, `setcps`)
- Pattern manipulation (`fast`, `slow`, `rev`, `jux`, `add`, `ply`, `off`)
- Scales and harmony (`scale`, `chord`, `voicing`)
- Sample banks (`bank`, `samples`)
- Pattern structure (`stack`, `struct`, `mask`)
- Time manipulation (`early`, `late`, `offset`)
- Randomization and modulation signals
- Utility functions

### 04_effects_reference.md
**Purpose**: Complete audio effects documentation  
**Content**:
- Signal chain order
- Filters (lpf, hpf, bpf, vowel)
- ADSR envelope
- Filter envelope
- Pitch envelope
- Time-based effects (delay, reverb)
- Modulation effects (phaser, tremolo)
- Dynamics (gain, compressor)
- Panning (pan, jux)
- Waveshaping (coarse, crush, distort)
- Orbits and ducking

### 05_samples_drums_reference.md
**Purpose**: Comprehensive sample and drum documentation  
**Content**:
- Default drum sounds and abbreviations
- Drum machine banks
- Sample selection techniques
- Loading custom samples (GitHub, URL, Shabda)
- Pitched samples
- Sample manipulation (begin, end, loop, speed)
- Advanced techniques (chop, slice, splice, scrub)
- Classic drum patterns
- Utility functions

### 06_synths_reference.md
**Purpose**: Synthesis engine documentation  
**Content**:
- Basic waveforms (sine, saw, square, triangle)
- Noise generators (white, pink, brown)
- Additive synthesis (partials, phases)
- Vibrato
- FM synthesis (fm, fmh, FM envelope)
- Wavetable synthesis
- ZZFX synth
- Synthesis techniques and examples

### 07_musical_patterns_library.md
**Purpose**: Proven musical patterns and complete examples  
**Content**:
- Drum patterns (basic beats, advanced, polyrhythmic, Euclidean)
- Basslines (simple, funky, walking)
- Melodic patterns (arpeggios, sequences, generative)
- Chord progressions
- Rhythmic techniques (polymeters, phasing, swing)
- Pattern transformations
- Complete genre examples (techno, ambient, jazz, dub, breakcore)
- Tips for creating patterns

### 08_strudel_vocabulary_glossary.md
**Purpose**: Translation guide from musical intent to Strudel code  
**Content**:
- Core concepts definitions
- Musical intent → Strudel code mappings
- Rhythm, melodic, harmonic, timbre, dynamic, spatial terms
- Drum sound vocabulary
- Genre-specific patterns
- Effect descriptions
- Common musical requests
- Pattern complexity levels
- Synthesis vocabulary
- Time signature concepts
- Musical concepts in code

## Key Findings for Agent Development

### 1. Pattern-Based Thinking
Strudel is fundamentally about patterns that repeat in cycles. Everything is a pattern that can be:
- Layered (stacked)
- Transformed (reversed, sped up, slowed down)
- Combined (parallel, sequential)
- Modulated (with signals like sine, saw, rand)

### 2. Mini-Notation is Core
The mini-notation syntax is Strudel's most powerful feature:
- Compact and expressive
- Can be nested infinitely
- Combines rhythmic and melodic information
- Essential for live coding workflow

### 3. Functional Composition
Strudel uses method chaining:
```javascript
note("c e g b")
  .s("sawtooth")
  .lpf(1000)
  .room(.5)
  .delay(.25)
```
Each function returns a pattern that can be further modified.

### 4. Time is Relative
Everything operates in "cycles" not absolute time:
- Tempo changes affect all patterns proportionally
- Patterns can be sped up/slowed down independently
- Time-based effects use cycle fractions

### 5. Randomness is Constrained
Strudel provides tools for controlled randomness:
- `rand`: Pure random (0-1)
- `irand(n)`: Random integer (0 to n-1)
- `choose([...])`: Pick from array
- `perlin`: Smooth random (Perlin noise)
- Can be combined with scales to stay musical

### 6. Live Coding Workflow
Code is meant to be:
- Written quickly
- Modified in real-time
- Experimented with
- Layered incrementally

Use `$:` for multiple concurrent patterns, `_$:` to mute.

### 7. Effects are Patternable
Almost any parameter can accept a pattern:
```javascript
.lpf("<400 800 1600 3200>")  // Filter sweeps
.gain("1 .8 .9 .7")           // Dynamic accents
.pan(sine)                    // Animated panning
```

## Agent Design Implications

### For Understanding User Intent
The agent needs to:
1. **Recognize musical terminology** ("groovy", "bright", "punchy", etc.)
2. **Map to Strudel code** using vocabulary glossary
3. **Understand context** (genre, mood, energy level)
4. **Ask clarifying questions** when intent is ambiguous

### For Code Generation
The agent should:
1. **Start simple** and layer complexity
2. **Use variables** for reusable patterns
3. **Comment code** to explain musical intent
4. **Provide alternatives** ("try this for more energy")
5. **Explain what code does musically**

### For Teaching
The agent can:
1. **Show examples** from pattern library
2. **Explain concepts** using analogies
3. **Build progressively** from simple to complex
4. **Encourage experimentation**
5. **Provide musical context** for techniques

## Next Steps

1. ✅ Research complete
2. ⏳ Create `agents/StrudelCoder.md` agent blueprint
3. ⏳ Design snippet storage system
4. ⏳ Build MCP server for tool access
5. ⏳ Test agent with various musical requests

## Sources

- https://strudel.cc/workshop/getting-started/
- https://strudel.cc/workshop/first-sounds/
- https://strudel.cc/workshop/first-notes/
- https://strudel.cc/workshop/first-effects/
- https://strudel.cc/workshop/pattern-effects/
- https://strudel.cc/learn/samples/
- https://strudel.cc/learn/synths/
- https://strudel.cc/learn/effects/

## Research Statistics

- **Pages Scraped**: 8 comprehensive documentation pages
- **Functions Documented**: 100+ core functions and effects
- **Patterns Catalogued**: 50+ musical patterns across genres
- **Vocabulary Terms**: 200+ musical intent → code mappings
- **Code Examples**: 150+ working examples
- **Drum Machines**: 9 classic drum machine banks
- **Synthesis Types**: 5 synthesis methods documented
