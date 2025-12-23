# Strudel Overview

**Research Date**: 2025-12-22  
**Source**: https://strudel.cc/workshop/getting-started/

## What is Strudel?

Strudel is an official port of the Tidal Cycles pattern language to JavaScript, designed for:
- **Live coding music** in real-time
- **Algorithmic composition** using pattern manipulation
- **Teaching music and code** with a low barrier to entry
- **Integration** with existing music setups via MIDI or OSC

## Core Philosophy

### Pattern-Based Music Creation
- Music is organized in **cyclical patterns**
- Patterns can be **layered** (stacked) simultaneously
- Uses **mini-notation**: a compact syntax for representing rhythms, notes, and sequences

### Live Coding Workflow
1. Click into the text field
2. Press `ctrl`+`enter` to play
3. Change code and press `ctrl`+`enter` to update
4. Press `ctrl`+`.` to stop

## Key Concepts

### Cycles
- Music is organized in cyclical patterns
- Default cycle length is 2 seconds (can be changed with `setcpm` or `setcps`)
- Patterns repeat every cycle

### Mini-Notation
A compact syntax for representing musical patterns:
- **Spaces** = sequence events
- **Commas** = stack/parallel patterns
- **Brackets** `[]` = sub-sequences
- **Angle brackets** `<>` = alternate between values
- **Asterisk** `*` = speed up (multiply)
- **Slash** `/` = slow down (divide)
- **Tilde** `~` = rest/silence
- **At sign** `@` = elongate
- **Exclamation** `!` = replicate

### Pattern Transformations
- **Masking**: Selectively including or excluding events
- **Time Manipulation**: Shifting, stretching, or compressing patterns
- **Structural Changes**: Altering the fundamental organization of patterns

## Sound Generation Methods

### 1. Samples
- Most common way to make sound
- Short pieces of audio that serve as basis for sound generation
- Can load samples from any publicly available URL
- Supports wav, mp3, ogg formats

### 2. Synthesizers
- Generate sounds on the fly
- Basic waveforms: sine, sawtooth, square, triangle
- Advanced synthesis: FM, additive, wavetable
- ZZFX integration for compact synth engine

### 3. Effects Processing
- Filters (low-pass, high-pass, band-pass)
- Time-based effects (delay, reverb)
- Modulation (tremolo, phaser, vibrato)
- Dynamics (compression, gain)

## Musical Organization

### Chord Progressions
- Defined using standard chord notation
- Example: `chord("<Bbm9 Fm9>/4")`

### Scales
- Notes can be related to scale structures
- Example: `n("0 2 4 6").scale("C:minor")`

### Texture Layering
- Combine rhythmic, harmonic, and melodic elements
- Use `stack()` or `$:` for multiple simultaneous patterns

## Integration Capabilities

- **MIDI**: Send patterns to external MIDI devices
- **OSC**: Open Sound Control for communication with other software
- **Sample Loading**: From GitHub, URLs, or local files
- **Shabda**: Query samples from freesound.org or generate speech

## Typical Pattern Structure

```javascript
// Define chord progression
let chords = chord("<Bbm9 Fm9>/4").dict('ireal')

// Combine multiple layers
stack(
  stack( // DRUMS
    s("bd").struct("<[x*<1 2> [~@3 x]] x>"),
    s("~ [rim, sd:<2 3>]").room("<0 .2>"),
    n("[0 <1 3>]*<2!3 4>").s("hh")
  ),
  // CHORDS
  chords.offset(-1).voicing().s("gm_epiano1:1").phaser(4).room(.5),
  // MELODY
  n("<0!3 1*2>").set(chords).mode("root:g2").voicing().s("gm_acoustic_bass")
)
```

This structure demonstrates:
- Layered drum patterns with different rhythmic structures
- Chord voicings with effects
- Melodic elements related to chord progression
- Spatial effects (room, phaser) for depth
