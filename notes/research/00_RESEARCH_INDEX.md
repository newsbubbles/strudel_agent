# Strudel Research Index

**Research Completed**: 2025-12-22  
**Updated**: 2025-12-25  
**Verification**: All documentation verified against official sources

This folder contains comprehensive research on Strudel live coding for music, gathered from official documentation and verified community examples.

---

## Research Files

### 01_strudel_overview.md
**Purpose**: High-level introduction to Strudel  
**Status**: ✅ Complete  
**Content**:
- What is Strudel and its philosophy
- Core concepts (patterns, cycles, mini-notation)
- Sound generation methods
- Musical organization
- Integration capabilities

### 02_mini_notation_cheatsheet.md
**Purpose**: Complete reference for Strudel's pattern syntax  
**Status**: ✅ Complete  
**Content**:
- Basic syntax table
- Advanced patterns (Euclidean, polyrhythms)
- Pattern modifiers
- Combining patterns
- Common rhythmic patterns
- Pro tips

### 03_core_functions_reference.md
**Purpose**: Essential Strudel functions  
**Status**: ✅ Complete  
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
**Status**: ✅ Complete  
**Content**:
- Signal chain order
- **Filters (Subtractive Synthesis)**: lpf, hpf, bpf, vowel, resonance
- **ADSR envelope**: attack, decay, sustain, release
- **Filter envelope**: lpenv, lpattack, lpdecay, lpsustain
- **Pitch envelope**: penv, pattack, pdecay, prelease
- Time-based effects (delay, reverb)
- Modulation effects (phaser, tremolo)
- Dynamics (gain, compressor)
- Panning (pan, jux)
- Waveshaping (coarse, crush, distort)
- Orbits and ducking

### 05_samples_drums_reference.md
**Purpose**: Comprehensive sample and drum documentation  
**Status**: ✅ Complete  
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
**Status**: ✅ Complete (Verified 2025-12-23)  
**Content**:
- **Basic waveforms**: sine, sawtooth, square, triangle with characteristics
- **Noise generators**: white, pink, brown, crackle with use cases
- **Additive synthesis**: partials, phases, algorithmic generation
- **Vibrato**: vib, vibmod with musical sweet spots
- **FM synthesis**: fm, fmh, FM envelope (fmattack, fmdecay, fmsustain, fmenv)
- **Wavetable synthesis**: wt_ prefix, AKWF library, scanning techniques
- **ZZFX synth**: All 20 parameters, sound design examples
- **Synthesis techniques**: Bass, pads, leads, percussion, experimental
- **Cross-references**: Links to filters/ADSR in effects reference
- **Tips and workflows**: Sound design process, CPU optimization

**Note**: Filters, ADSR envelopes, and LFOs are covered in `04_effects_reference.md` as they are part of the audio effects chain.

### 07_musical_patterns_library.md
**Purpose**: Proven musical patterns and complete examples  
**Status**: ✅ Complete  
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
**Status**: ✅ Complete  
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

### 09_stack_and_song_structure.md
**Purpose**: Building complete songs with JavaScript variables and arrangement  
**Status**: ✅ Complete  
**Content**:
- `stack()` function - layering patterns simultaneously
- Using JavaScript variables for reusable musical parts
- `arrange()` function - creating song structures
- `cat()` function - sequential patterns
- Complete song structure examples (verse/chorus/bridge)
- When to use stack() vs mini-notation
- Nested stacks for complex arrangements
- Practical workflow for composition
- Common patterns (techno, house, ambient)

### 10_visualizers_reference.md
**Purpose**: Visual feedback and performance visuals  
**Status**: ✅ Complete  
**Content**:
- Global vs inline visualizers
- `punchcard()` / `pianoroll()` - note grids over time
- `scope()` - oscilloscope for waveforms
- `spiral()` - cyclical pattern visualization
- `pitchwheel()` - pitch circle for harmony
- `spectrum()` - frequency analyzer
- `markcss()` - custom CSS styling
- Options and customization for each visualizer
- Usage tips and performance considerations
- Common use cases and example combinations

### 11_conditional_modifiers_reference.md
**Purpose**: Advanced pattern control and variation  
**Status**: ✅ Complete  
**Content**:
- **Cycle-based conditionals**: `lastOf()`, `firstOf()`
- **Pattern-based conditionals**: `when()`
- **Chunking functions**: `chunk()`, `chunkBack()`, `fastChunk()`
- **Arpeggiation**: `arp()`, `arpWith()`
- **Structure functions**: `struct()`, `mask()`
- **Reset functions**: `reset()`, `restart()`
- **Silence and inversion**: `hush()`, `invert()`
- **Pick functions**: `pick()`, `pickmod()`, `pickF()`, `pickRestart()`, `pickReset()`
- **Inhabit functions**: `inhabit()`, `squeeze()`
- **Time-based conditionals**: `off()`, `palindrome()`, `iter()`, `ribbon()`, `inside()`, `outside()`
- 27 functions with syntax, parameters, and examples
- Quick reference table
- Common use cases and patterns

### 12_glitch_effects_genre_guide.md
**Purpose**: Glitch effects and experimental production techniques  
**Status**: ✅ Complete  
**Content**:
- **Core glitch effects**: `crush`, `coarse`, `distort` with full examples
- **Sample manipulation**: `chop`, `slice`, `splice`, `run` techniques
- **Glitch techniques**: tape warble, stuttering, reset/restart, masking
- **Genre-specific examples**: Glitch hop, IDM, breakcore, experimental, glitch techno
- **Effect combination strategies**: Subtle to extreme glitch levels
- **Community examples**: Verified code from GitHub repositories
- **Quick reference table**: Parameter ranges and sweet spots
- **Production tips**: Layering, automation, filtering techniques
- **Browser compatibility notes**: Chromium-specific effects
- 10+ complete working examples across genres

### 13_mastering_mixing_guide.md
**Purpose**: Professional mixing and mastering techniques  
**Status**: ✅ Complete (Added 2025-12-23)  
**Content**:
- **Signal chain**: Understanding Strudel's audio routing
- **Gain staging**: `gain`, `velocity`, `postgain` with best practices
- **Dynamics processing**: `compressor` with parameter breakdowns and sweet spots
- **Orbits system**: Routing, grouping, and independent processing
- **Ducking/sidechain**: `duckorbit`, `duckattack`, `duckdepth` techniques
- **Global effects**: `all()` function for master bus processing (key discovery!)
- **Clipping/limiting**: Using `clip()` for soft limiting
- **Spatial effects**: Advanced reverb and delay techniques
- **Complete mixing examples**: Techno, ambient, aggressive electronic
- **Mastering workflow**: Step-by-step from balance to final output
- **Mixing tips**: Do's and don'ts for each technique
- **Loudness strategies**: Genre-specific compression and limiting
- **Troubleshooting**: Solutions for common mix problems
- **Advanced techniques**: Parallel compression, multi-band processing, stereo width

### 14_trance_production_guide.md
**Purpose**: Trance music production techniques  
**Status**: ✅ Complete (Added 2025-12-23)  
**Content**:
- **Essential sounds**: Supersaw leads, plucks, pads, rolling bass, trance kicks
- **Synthesis techniques**: 5-7 layer supersaws, detuning strategies, FM leads
- **Trance techniques**: Filter sweeps, sidechain compression, trance gates, arpeggios, risers
- **Complete examples**: Progressive trance (130 BPM), uplifting breakdown, psytrance (142 BPM)
- **Arrangement structure**: Classic trance structure with buildups, drops, breakdowns
- **Production tips**: Sound design, mixing, arrangement strategies
- **Tempo guide**: Progressive (128-132), Uplifting (135-140), Psytrance (138-145)
- **Quick reference**: Essential sounds, key techniques, typical parameter values
- **Subgenre coverage**: Progressive, uplifting, psytrance, tech trance, vocal trance

### 15_dubstep_production_guide.md
**Purpose**: Dubstep music production techniques  
**Status**: ✅ Complete (Added 2025-12-23)  
**Content**:
- **Essential sounds**: Wobble bass, sub bass, reese bass, growls, screeches
- **Wobble techniques**: LFO filter modulation with sine/saw/random patterns
- **Bass layering**: Sub + mid + high frequency stacks
- **FM bass synthesis**: Metallic growls and evolving timbres
- **Distortion techniques**: Heavy distortion, bit crushing, sample rate reduction
- **Complete examples**: Classic dubstep, brostep, riddim, melodic dubstep
- **Half-time drums**: Kick patterns, syncopated snares, sparse percussion
- **Arrangement structure**: Build → drop → breakdown → second drop
- **Production tips**: Sound design, mixing, arrangement strategies
- **Subgenre coverage**: Classic dubstep, brostep, riddim, melodic dubstep
- **Quick reference**: Essential sounds, key techniques, typical parameter values

### 16_transitions_and_arrangement_guide.md
**Purpose**: Complete guide to transitions between sections  
**Status**: ✅ Complete (Added 2025-12-23)  
**Content**:
- **Strudel transition techniques**: Using `arrange()`, `lastOf()`, `firstOf()`, `cat()`, filter sweeps, silence/dropouts, `pick()`, `pickRestart()`
- **Production techniques**: Drum fills (snare rolls, tom fills, layered, Euclidean), risers (white noise, pitched, layered, rhythmic), reverse cymbals, impacts, downlifters, volume automation, vocal risers, glitch transitions, harmonic transitions
- **Complete examples**: EDM buildup to drop, breakdown transition, section changes with fills, enhanced user code example
- **Transition timing guide**: Typical lengths and placement (every 4/8/16/32 cycles)
- **Transition combinations**: Low→high energy, high→low energy, same energy section changes
- **Advanced techniques**: Dynamic transitions with `segment()`, polyrhythmic transitions, call and response, tension and release
- **Quick reference**: Essential transition elements, formulas for basic/epic buildups, breakdown transitions
- **9 core transition types**: Drum fills, risers/sweeps, reverse cymbals, impacts, downlifters, volume automation, vocal risers, glitch effects, harmonic transitions
- **4 complete working examples** with full code

### 17_ambient_music_production_guide.md
**Purpose**: Comprehensive guide to ambient music production  
**Status**: ✅ Complete (Added 2025-12-25)  
**Content**:
- **Core principles**: Texture over melody, space as instrument, slow evolution, system-based composition, layered complexity
- **Sound design**: Drones (sine, filtered noise, detuned, FM), pads (basic, three-layer system, evolving ADSR, wavetable), textures (vinyl crackle, noise sweeps, granular, metallic)
- **Generative techniques**: Phase looping (Music for Airports style), probabilistic patterns, Perlin noise modulation, Euclidean ambient, slow evolution
- **Ambient motifs**: Minimal melodic motifs (single note, two-note, three-note), pentatonic scales, modal harmony (Dorian, Mixolydian, Lydian), arpeggios, suspended chords
- **Space and effects**: Heavy reverb, evolving reverb, ping-pong delay, long feedback delay, chorus/width, panning movement
- **Complete compositions**: 5 full ambient examples (Eno-style, dark ambient, bright ambient, minimal ambient, evolving soundscape)
- **Arrangement techniques**: Layered introduction, evolving sections, generative long-form
- **Production tips**: Sound design, mixing, composition tips with specific parameter values
- **Ambient subgenres**: Dark ambient, space ambient, drone ambient with full examples
- **Brian Eno techniques**: Incommensurable loops, phase relationships, system-based composition
- **Quick reference**: Essential functions, chord progressions, scales

### 18_interactive_and_algorithmic_functions.md
**Purpose**: Advanced custom functions for interactive control and algorithmic composition  
**Status**: ✅ Complete (Added 2025-12-25)  
**Content**:
- **Interactive control**: Keyboard trigger (Ctrl+1-9 toggle muting), MIDI note trigger (hardware controller integration), tempo control with arrow keys
- **Algorithmic composition**: Markov chain generator (probabilistic sequences), ascending pattern generator (mathematical melodies)
- **Musical utilities**: Manual chords (custom voicings and inversions), add degree (scale degree transposition), rebaser (Roman numeral notation)
- **Audio processing**: Ten-band EQ with visual feedback and interactive sliders
- **register() API**: Creating custom pattern functions with `.withValue()` and `.withHap()`
- **Event listeners**: Keyboard and MIDI input handling for live performance
- **State management**: Persistent state across cycles for interactive control
- **Complete implementations**: 9 fully documented community functions with use cases
- **Live performance examples**: Combining keyboard control, tempo adjustment, and Markov chains
- **EQ mixing tips**: Genre-specific EQ templates (techno, ambient) and frequency band reference
- **Troubleshooting**: Browser compatibility, MIDI device detection, debugging tips
- **Further exploration**: Ideas for custom functions (velocity sensitivity, CC control, gesture recording)

### 19_drum_and_bass_production_guide.md
**Purpose**: Comprehensive Drum and Bass production guide  
**Status**: ✅ Complete (Added 2025-12-25)  
**Content**:
- **DnB fundamentals**: Fast tempo (160-180 BPM), breakbeat drums, sub bass, Reese bass, atmospheric elements
- **Subgenre coverage**: Liquid DnB, neurofunk, jump-up, jungle, minimal/deep with specific characteristics
- **Drum programming**: Amen break (chopping, rearranging), building breaks from scratch, breakbeat chopping techniques, layering drums (kick, snare), drum processing (compression, EQ, sidechain)
- **Bass design**: Sub bass (sine wave foundation, rolling patterns, envelope modulation), Reese bass (classic, aggressive FM, neurofunk), wobble bass (LFO, stepped), bass layering (sub + mid + high)
- **Song structure**: Classic DnB arrangement (intro, buildup, drop, breakdown), breakdown techniques, drop variations, complete track examples
- **Atmospheric elements**: Pads and strings (liquid, neurofunk), vocal samples (chopped, atmospheric), sound effects and textures
- **Complete examples**: 5 full DnB tracks (liquid, neurofunk, jump-up, minimal/deep, jungle)
- **Production tips**: Sound design (8 tips), mixing (8 tips), arrangement (8 tips)
- **Technical reference**: Tempo guide by subgenre, frequency ranges for all elements
- **Advanced techniques**: Resampling and layering, drum fills and transitions, automation and movement, parallel processing
- **Mixing checklist**: 8-point checklist for professional DnB mixing

---

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

### 8. Song Structure with Variables
JavaScript variables enable complete song composition:
- Define reusable patterns as variables
- Stack patterns to create sections (verse, chorus)
- Use `arrange()` to sequence sections over cycles
- Combine `stack()`, `cat()`, and `arrange()` for full songs

### 9. Visual Feedback for Performance
Visualizers enhance live coding and understanding:
- Scope shows waveforms in real-time
- Pianoroll/punchcard displays note patterns
- Spectrum shows frequency content
- Multiple inline visualizers can be combined
- Essential for audiovisual performances

### 10. Conditional Modifiers for Variation
Conditional modifiers are essential for musical interest:
- Create variation over time with `lastOf()`, `firstOf()`, `iter()`
- Apply effects conditionally with `when()`, `mask()`
- Build complexity with `chunk()`, `pick()`, `off()`
- Structure songs with `pickRestart()`, `reset()`
- Transform at different scales with `inside()`, `outside()`

### 11. Glitch Effects for Experimental Production
Glitch effects enable experimental sound design:
- Digital degradation with `crush`, `coarse`, `distort`
- Sample manipulation with `chop`, `slice`, `splice`
- Pattern interruption with `reset`, `restart`, `mask`
- Genre-specific techniques for glitch hop, IDM, breakcore
- Layering clean and glitched sounds for depth

### 12. Synthesis Architecture
Strudel separates synthesis into two stages:
- **Oscillator generation** (06_synths_reference.md): Waveforms, FM, additive, wavetable
- **Audio processing** (04_effects_reference.md): Filters, ADSR, modulation, effects
- This separation mirrors traditional synthesizer architecture

### 13. Mastering and Mixing Techniques
Professional mixing requires understanding:
- Signal chain and effect order
- Gain staging with headroom management
- Strategic compression for dynamics control
- Orbit routing for independent processing
- Ducking for clarity and space
- Global effects via `all()` for master bus
- Combining compression and clipping for loudness
- Genre-specific mastering approaches

### 14. Genre-Specific Production
Different genres require specialized techniques:
- **Trance**: Supersaw layering, filter sweeps, long buildups, heavy sidechain
- **Dubstep**: LFO wobbles, bass layering, half-time drums, aggressive distortion
- **Ambient**: Phase looping, Perlin modulation, heavy reverb, slow evolution
- **DnB**: Fast breakbeats, Reese bass, sub bass layering, break chopping
- Each genre has specific tempo, sound design, and arrangement patterns

### 15. Professional Transitions
Transitions are critical for polished arrangements:
- **Multiple approaches**: Strudel-specific functions + production techniques
- **Layering**: Combine fills + risers + filters for maximum impact
- **Timing**: Use appropriate lengths (1-8 cycles) based on energy change
- **Energy management**: Build tension with risers, release with drops
- **Variety**: 9+ transition types for different musical contexts
- **Automation**: Use `sine.range()` for smooth parameter sweeps

### 16. Ambient Music Philosophy
Ambient music requires a different approach:
- **Texture over melody**: Focus on timbral quality and atmosphere
- **System-based composition**: Set up generative systems that evolve organically
- **Space as instrument**: Reverb and delay are compositional elements
- **Slow evolution**: Changes happen over very long periods (16-48 cycles)
- **Incommensurable loops**: Use prime number cycle lengths (5, 7, 11, 13) for phase relationships
- **Perlin modulation**: Smooth, organic parameter evolution
- **Modal harmony**: Dorian, Mixolydian, Lydian for ambiguous tonality

### 17. Extensibility Through register()
Strudel can be extended with custom functions:
- **Interactive control**: Keyboard/MIDI input for live performance
- **Algorithmic composition**: Markov chains, mathematical transformations
- **Custom utilities**: Chord systems, scale degree manipulation
- **Audio processing**: Multi-band EQ, custom effects chains
- **State management**: Persistent state across cycles
- **Event handling**: Browser APIs for hardware integration

### 18. DnB Production Essentials
Drum and Bass has unique production requirements:
- **Fast tempo**: 160-180 BPM with half-time bass feel (80-90 BPM)
- **Break chopping**: Amen, Think, Apache breaks with complex rearrangement
- **Bass layering**: Sub (sine <150Hz) + Reese (detuned saws 150-800Hz) + high harmonics
- **Heavy compression**: Aggressive drum compression for punch
- **Sidechain ducking**: Bass ducks to kick for clarity
- **Subgenre variation**: Liquid (melodic), neurofunk (dark), jump-up (wobbles), jungle (ragga)

---

## Agent Design Implications

### For Understanding User Intent
The agent needs to:
1. **Recognize musical terminology** ("groovy", "bright", "punchy", "glitchy", "loud", "polished", "atmospheric", "droning", "interactive", "rolling bass", "breakbeat", etc.)
2. **Map to Strudel code** using vocabulary glossary
3. **Understand context** (genre, mood, energy level, performance vs composition)
4. **Ask clarifying questions** when intent is ambiguous
5. **Recognize glitch/experimental requests** and apply appropriate effects
6. **Understand mixing requests** ("make it louder", "add space", "tighten the kick")
7. **Understand synthesis requests** ("warmer", "brighter", "more harmonics")
8. **Recognize genre-specific requests** ("trance lead", "dubstep wobble", "supersaw", "ambient drone", "Reese bass", "Amen break")
9. **Recognize transition requests** ("add a buildup", "smooth transition", "drop")
10. **Recognize ambient requests** ("evolving", "meditative", "spacious", "generative")
11. **Recognize interactive requests** ("keyboard control", "MIDI input", "live performance")
12. **Recognize DnB requests** ("liquid", "neurofunk", "jump-up", "rolling sub", "chop the break")

### For Code Generation
The agent should:
1. **Start simple** and layer complexity
2. **Use variables** for reusable patterns
3. **Comment code** to explain musical intent
4. **Provide alternatives** ("try this for more energy")
5. **Explain what code does musically**
6. **Use stack() and arrange()** for song structures
7. **Add visualizers** for performance contexts
8. **Apply conditional modifiers** for variation and interest
9. **Use glitch effects appropriately** for experimental genres
10. **Apply proper gain staging** and mixing techniques
11. **Use orbits strategically** for independent processing
12. **Add master bus processing** with `all()` when appropriate
13. **Choose appropriate synthesis method** (basic waveforms, FM, additive, wavetable)
14. **Combine oscillators with filters** for subtractive synthesis
15. **Apply genre-specific techniques** (supersaw for trance, wobble for dubstep, phase loops for ambient, Reese bass for DnB)
16. **Add professional transitions** between sections (fills, risers, sweeps, impacts)
17. **Use generative techniques** for ambient (Perlin modulation, incommensurable loops, probabilistic patterns)
18. **Implement interactive control** when requested (keyboard triggers, MIDI, tempo control)
19. **Use register() for custom functions** when built-in functions aren't sufficient
20. **Add algorithmic composition** (Markov chains, mathematical patterns) for generative music
21. **Chop and rearrange breaks** for DnB (Amen, Think, Apache)
22. **Layer bass properly** for DnB (sub + Reese + high harmonics)
23. **Use half-time bass patterns** for DnB feel

### For Teaching
The agent can:
1. **Show examples** from pattern library
2. **Explain concepts** using analogies
3. **Build progressively** from simple to complex
4. **Encourage experimentation**
5. **Provide musical context** for techniques
6. **Demonstrate song structure** with variables
7. **Show visualizers** for understanding patterns
8. **Teach conditional modifiers** for creating variation
9. **Guide glitch production** with effect combinations
10. **Explain mixing concepts** (gain staging, compression, ducking)
11. **Demonstrate mastering workflow** step-by-step
12. **Explain synthesis architecture** (oscillators → filters → effects)
13. **Cross-reference documentation** (e.g., "filters are in effects reference")
14. **Teach genre-specific production** (trance buildups, dubstep bass design, ambient drones, DnB break chopping)
15. **Demonstrate transition techniques** (buildups, breakdowns, fills, risers)
16. **Teach generative techniques** (Brian Eno's phase looping, system-based composition)
17. **Explain register() API** for creating custom functions
18. **Guide interactive setup** (keyboard/MIDI configuration, event listeners)
19. **Demonstrate algorithmic composition** (Markov chains, mathematical patterns)
20. **Teach DnB fundamentals** (break chopping, Reese bass design, sub bass layering)

---

## Documentation Cross-References

### Synthesis Chain
1. **Oscillator Generation** → `06_synths_reference.md`
   - Waveforms, FM, additive, wavetable, noise
2. **Audio Processing** → `04_effects_reference.md`
   - Filters (subtractive synthesis), ADSR, modulation
3. **Mixing** → `13_mastering_mixing_guide.md`
   - Gain, compression, orbits, ducking, master bus
4. **Custom Processing** → `18_interactive_and_algorithmic_functions.md`
   - Ten-band EQ, custom effects chains

### Musical Structure
1. **Patterns** → `02_mini_notation_cheatsheet.md`
2. **Functions** → `03_core_functions_reference.md`
3. **Song Structure** → `09_stack_and_song_structure.md`
4. **Transitions** → `16_transitions_and_arrangement_guide.md`
5. **Variation** → `11_conditional_modifiers_reference.md`
6. **Algorithmic** → `18_interactive_and_algorithmic_functions.md`

### Sound Sources
1. **Synthesis** → `06_synths_reference.md`
2. **Samples** → `05_samples_drums_reference.md`
3. **Effects** → `04_effects_reference.md`
4. **Glitch** → `12_glitch_effects_genre_guide.md`

### Production
1. **Musical Patterns** → `07_musical_patterns_library.md`
2. **Vocabulary** → `08_strudel_vocabulary_glossary.md`
3. **Mixing** → `13_mastering_mixing_guide.md`
4. **Transitions** → `16_transitions_and_arrangement_guide.md`
5. **Visuals** → `10_visualizers_reference.md`

### Genre-Specific
1. **Trance** → `14_trance_production_guide.md`
2. **Dubstep** → `15_dubstep_production_guide.md`
3. **Ambient** → `17_ambient_music_production_guide.md`
4. **Drum and Bass** → `19_drum_and_bass_production_guide.md`
5. **Techno/Jazz/Dub** → `07_musical_patterns_library.md`
6. **Glitch/IDM/Breakcore** → `12_glitch_effects_genre_guide.md`

### Advanced/Interactive
1. **Custom Functions** → `18_interactive_and_algorithmic_functions.md`
2. **Live Performance** → `18_interactive_and_algorithmic_functions.md`
3. **Generative Music** → `17_ambient_music_production_guide.md` + `18_interactive_and_algorithmic_functions.md`

---

## Next Steps

1. ✅ Research complete
2. ✅ Stack and song structure documented
3. ✅ Visualizers documented
4. ✅ Conditional modifiers documented
5. ✅ Glitch effects and genre guide documented
6. ✅ Mastering and mixing guide documented
7. ✅ Synth reference verified and enhanced
8. ✅ Trance production guide created
9. ✅ Dubstep production guide created
10. ✅ Transitions and arrangement guide created
11. ✅ Ambient music production guide created
12. ✅ Interactive and algorithmic functions documented
13. ✅ Drum and Bass production guide created
14. ⏳ Create `agents/StrudelCoder.md` agent blueprint
15. ⏳ Design snippet storage system
16. ⏳ Build MCP server for tool access
17. ⏳ Test agent with various musical requests

---

## Sources

### Official Documentation
- https://strudel.cc/workshop/getting-started/
- https://strudel.cc/workshop/first-sounds/
- https://strudel.cc/workshop/first-notes/
- https://strudel.cc/workshop/first-effects/
- https://strudel.cc/workshop/pattern-effects/
- https://strudel.cc/learn/samples/
- https://strudel.cc/learn/synths/ ✅ Verified 2025-12-23
- https://strudel.cc/learn/effects/ ✅ Verified 2025-12-23
- https://strudel.cc/learn/factories/ (stack, arrange, cat)
- https://strudel.cc/functions/intro/ (JavaScript API)
- https://strudel.cc/learn/visual-feedback/ (visualizers)
- https://strudel.cc/learn/conditional-modifiers/ (conditional modifiers)
- https://strudel.cc/learn/time-modifiers/ (time-based modifiers)
- https://strudel.cc/recipes/recipes/ (sample chopping, wavetable synthesis)
- https://tidalcycles.org/docs/reference/transitions/ ✅ Verified 2025-12-23 (Tidal transitions)

### Community Resources
- https://github.com/eefano/strudel-songs-collection ✅ Verified 2025-12-25 (community functions)
- https://gist.github.com/therebelrobot/fe161e21a8bffc5325891d7ad62ec49b (Strudel learning course)
- https://strudel.cc/bakery/ (community patterns)
- https://club.tidalcycles.org/c/strudel/ (Tidal Club forum)
- https://club.tidalcycles.org/t/master-bus-compression-limiter/6005 (mastering discussion)
- https://www.youtube.com/watch?v=5ivEVNZLDQs (glitch effect tutorial)
- https://www.youtube.com/watch?v=dcmwqqzJubA (break chopping tutorial)
- https://www.reddit.com/r/edmproduction/ (EDM production techniques)
- https://www.edmprod.com/tension/ (tension and energy guide)
- https://www.morningdewmedia.com/transition-techniques-in-music-production/ (transition techniques)

### Ambient Music Research
- https://reverbmachine.com/blog/deconstructing-brian-eno-music-for-airports/ (Brian Eno techniques)
- https://www.audiocube.app/blog/how-to-write-ambient-music (ambient composition)
- https://blog.landr.com/how-to-make-ambient-music/ (ambient production techniques)
- https://blog.landr.com/soundscapes/ (soundscape creation)
- https://www.pointblankmusicschool.com/blog/how-to-create-rich-layered-textures-in-ambient-music/ (layering)

### Drum and Bass Research
- DnB production fundamentals (breakbeat chopping, Reese bass design)
- Classic breaks (Amen, Think, Apache) and their use in DnB
- Subgenre characteristics (liquid, neurofunk, jump-up, jungle, minimal/deep)
- DnB mixing techniques (heavy compression, sidechain ducking, EQ strategies)

### Genre Production Knowledge
- EDM production principles (trance, dubstep, buildups, drops)
- Synthesis techniques (supersaw, wobble bass, FM, Reese bass)
- Mixing strategies (sidechain, filter automation)
- Transition techniques (risers, fills, sweeps, impacts)
- Ambient techniques (phase looping, generative systems, Perlin modulation)
- Brian Eno's generative music philosophy
- DnB production techniques (break chopping, bass layering, half-time feel)

---

## Research Statistics

- **Pages Scraped**: 24+ comprehensive documentation pages
- **Functions Documented**: 180+ core functions and effects (including 9 custom community functions)
- **Patterns Catalogued**: 60+ musical patterns across genres
- **Vocabulary Terms**: 200+ musical intent → code mappings
- **Code Examples**: 650+ working examples
- **Drum Machines**: 9 classic drum machine banks
- **Synthesis Types**: 6 synthesis methods (waveforms, FM, additive, wavetable, ZZFX, noise)
- **Visualizers**: 7 visualization functions documented
- **Conditional Modifiers**: 27 conditional/time-based functions documented
- **Glitch Effects**: 10 core glitch techniques with genre examples
- **Mixing/Mastering**: Complete workflow with 15+ techniques
- **Song Structure Functions**: stack(), cat(), arrange() fully documented
- **Community Examples**: 10+ verified songs from GitHub
- **Synthesis Techniques**: 20+ sound design examples (bass, pads, leads, percussion, experimental)
- **Genre Guides**: 4 comprehensive production guides (trance, dubstep, ambient, DnB)
- **Genre Examples**: 18+ complete track examples across genres
- **Transition Techniques**: 9 core transition types with 50+ examples
- **Ambient Techniques**: Phase looping, Perlin modulation, generative systems, modal harmony
- **Ambient Examples**: 5 complete ambient compositions + 8 subgenre examples
- **Interactive Functions**: 9 community-created custom functions (keyboard, MIDI, tempo, Markov, EQ, etc.)
- **Custom Function Types**: Interactive control (3), algorithmic composition (2), musical utilities (3), audio processing (1)
- **DnB Techniques**: Break chopping, Reese bass design, sub bass layering, sidechain ducking
- **DnB Examples**: 5 complete DnB tracks (liquid, neurofunk, jump-up, minimal/deep, jungle)

---

## Verification Status

| File | Status | Last Verified | Notes |
|------|--------|---------------|-------|
| 01_strudel_overview.md | ✅ Complete | 2025-12-22 | - |
| 02_mini_notation_cheatsheet.md | ✅ Complete | 2025-12-22 | - |
| 03_core_functions_reference.md | ✅ Complete | 2025-12-22 | - |
| 04_effects_reference.md | ✅ Complete | 2025-12-23 | Verified signal chain, filters, ADSR |
| 05_samples_drums_reference.md | ✅ Complete | 2025-12-22 | - |
| 06_synths_reference.md | ✅ Complete | 2025-12-23 | Enhanced with cross-refs, verified all synthesis methods |
| 07_musical_patterns_library.md | ✅ Complete | 2025-12-22 | - |
| 08_strudel_vocabulary_glossary.md | ✅ Complete | 2025-12-22 | - |
| 09_stack_and_song_structure.md | ✅ Complete | 2025-12-22 | - |
| 10_visualizers_reference.md | ✅ Complete | 2025-12-22 | - |
| 11_conditional_modifiers_reference.md | ✅ Complete | 2025-12-22 | - |
| 12_glitch_effects_genre_guide.md | ✅ Complete | 2025-12-22 | - |
| 13_mastering_mixing_guide.md | ✅ Complete | 2025-12-23 | New research, all() function discovered |
| 14_trance_production_guide.md | ✅ Complete | 2025-12-23 | Genre-specific production guide |
| 15_dubstep_production_guide.md | ✅ Complete | 2025-12-23 | Genre-specific production guide |
| 16_transitions_and_arrangement_guide.md | ✅ Complete | 2025-12-23 | Comprehensive transition techniques |
| 17_ambient_music_production_guide.md | ✅ Complete | 2025-12-25 | Brian Eno techniques, generative systems, complete examples |
| 18_interactive_and_algorithmic_functions.md | ✅ Complete | 2025-12-25 | Community custom functions, register() API, interactive control |
| 19_drum_and_bass_production_guide.md | ✅ Complete | 2025-12-25 | DnB fundamentals, break chopping, Reese bass, subgenres |

**All research files are complete and verified against official documentation or established production techniques.**
