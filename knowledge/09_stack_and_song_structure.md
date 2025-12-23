# Stack and Song Structure in Strudel

**Research Date**: 2025-12-23  
**Sources**: 
- https://strudel.cc/learn/factories/
- https://strudel.cc/functions/intro/

---

## Overview

The `stack()` function is fundamental to building complex musical structures in Strudel. It allows you to layer multiple patterns on top of each other, playing them simultaneously. Combined with JavaScript variables and the `arrange()` function, you can create complete song structures with verses, choruses, and other sections.

---

## The stack() Function

### What It Does

`stack()` takes multiple patterns as arguments and plays them at the same time. Each pattern is stretched or squeezed to fit into the same duration (one cycle by default). This is the primary way to create polyrhythms and complex musical textures by combining simpler patterns.

**Synonyms**: `polyrhythm`, `pr`  
**Mini-notation equivalent**: `"x,y"`

### Syntax

```javascript
stack(pattern1, pattern2, pattern3, ...)
```

Can also be chained on an existing pattern:

```javascript
existingPattern.stack(newPatternLayer)
```

---

## Basic Examples

### Example 1: Stacking Notes

Layers three different note patterns into a single chordal pattern:

```javascript
stack("g3", "b3", ["e4", "d4"]).note()
// Equivalent mini-notation: "g3,b3,[e4 d4]".note()
```

### Example 2: Adding a Layer to Existing Pattern

Hi-hat pattern with a note pattern layered on top:

```javascript
s("hh*4").stack(
  note("c4(5,8)")
)
```

### Example 3: Stacking Different Sound Types

When you have different types of sounds (note-based synth + drum samples), `stack()` is necessary because mini-notation `,` cannot be used:

```javascript
stack(
  note("c2 eb2(3,8)").s('sawtooth').cutoff(800),
  s("bd(5,8), hh*8")
)
```

---

## Using JavaScript Variables for Song Structure

### Building Reusable Musical Parts

Define individual musical components as variables, then combine them with `stack()` to create sections:

```javascript
// Define individual musical parts
const bassline = note("c2 g2 c2 g2").sound("bass").decay(0.3);
const chords = note("[c4maj7 f5maj7]*2").sound("piano").lpf(1500);
const melody = note("e5 g5 g5 e5 d5 f5 f5 d5").sound("sine").delay(0.25);

// Stack the parts together to create a full musical section
stack(bassline, chords, melody)
```

### Creating Song Sections

Build distinct sections (verse, chorus) by stacking different combinations:

```javascript
// --- Define individual patterns ---
const drums = s("bd sd hh hh");
const bass = note("c1 c1 g1 g1").sound("fm").decay(0.2);
const pad = note("[c4,e4,g4] [g4,b4,d5]").sound("saw").lpf(800).decay(1);

// --- Create song sections by stacking patterns ---
const verse = stack(drums, bass);
const chorus = stack(drums, bass, pad);
```

---

## The arrange() Function

### What It Does

`arrange()` is a higher-level tool for creating song structures. It allows you to specify how many cycles a given pattern should play before moving to the next one.

### Syntax

```javascript
arrange(
  [cycles, pattern],
  [cycles, pattern],
  ...
)
```

Takes an array of `[cycles, pattern]` pairs and plays them in sequence.

### Basic Example

```javascript
arrange(
  [4, "<c a f e>(3,8)"],
  [2, "<g a>(5,8)"]
).note()
```

This plays the chord progression `<c a f e>(3,8)` for 4 cycles, then plays `<g a>(5,8)` for 2 cycles.

---

## Complete Song Structure Example

### A/B/A Form with Verse and Chorus

```javascript
// --- Define individual patterns ---
const drums = s("bd sd hh hh");
const bass = note("c1 c1 g1 g1").sound("fm").decay(0.2);
const pad = note("[c4,e4,g4] [g4,b4,d5]").sound("saw").lpf(800).decay(1);

// --- Create song sections by stacking patterns ---
const verse = stack(drums, bass);
const chorus = stack(drums, bass, pad);

// --- Arrange the sections into a song structure ---
// Play the 'verse' for 4 cycles, then the 'chorus' for 4 cycles, then the 'verse' again for 4 cycles.
arrange(
  [4, verse],
  [4, chorus],
  [4, verse]
)
```

---

## Advanced Pattern: Nested Stacks

You can stack groups of patterns for more complex arrangements:

```javascript
stack(
  stack( // DRUMS
    s("bd").struct("<[x*<1 2> [~@3 x]] x>"),
    s("~ [rim, sd:<2 3>]").room("<0 .2>"),
    n("[0 <1 3>]*<2!3 4>").s("hh")
  ),
  // CHORDS
  chord("<Bbm9 Fm9>/4").dict('ireal').offset(-1).voicing().s("gm_epiano1:1").phaser(4).room(.5),
  // MELODY
  n("<0!3 1*2>").set(chord("<Bbm9 Fm9>/4")).mode("root:g2").voicing().s("gm_acoustic_bass")
)
```

---

## Related Functions

### cat() (or slowcat)

**Purpose**: Play patterns one after another (sequential, not simultaneous)

**Mini-notation equivalent**: `"<x y>"`

```javascript
cat("e5", "b4", ["d5", "c5"]).note()
// Equivalent mini-notation: "<e5 b4 [d5 c5]>".note()
```

This plays "e5" for one cycle, "b4" for the next cycle, then `["d5", "c5"]` for the third cycle.

### Combining cat() and stack()

Use `cat()` to create chord progressions with `stack()`:

```javascript
cat(
  stack("g3","b3","e4"),
  stack("a3","c3","e4"),
  stack("b3","d3","fs4"),
  stack("b3","e4","g4")
).note()
```

Equivalent mini-notation:

```javascript
cat(
  "g3,b3,e4",
  "a3,c3,e4",
  "b3,d3,f#4",
  "b3,e4,g4"
).note()
```

---

## When to Use stack() vs Mini-Notation

### Use Mini-Notation (`,`) When:
- Working with simple rhythms
- All patterns are the same type (all notes, or all samples)
- You want compact, readable code
- Patterns fit on one line

### Use stack() Function When:
- Combining different types of sounds (notes + samples)
- Building complex song structures with variables
- Need more flexibility beyond mini-notation modifiers (`* / ! @`)
- Creating reusable sections for arrangement
- Working with larger contexts and multiple layers

---

## Practical Workflow

### 1. Define Individual Patterns

```javascript
const kick = s("bd*4");
const snare = s("~ sd");
const hats = s("hh*8");
const bass = note("c2 ~ eb2 ~").s("sawtooth").lpf(400);
const lead = note("c4 eb4 g4 bb4").s("sine").delay(0.25);
```

### 2. Create Sections by Stacking

```javascript
const intro = stack(kick, hats);
const verse = stack(kick, snare, hats, bass);
const chorus = stack(kick, snare, hats, bass, lead);
const outro = stack(kick, hats).slow(2);
```

### 3. Arrange into Song Structure

```javascript
arrange(
  [4, intro],
  [8, verse],
  [8, chorus],
  [8, verse],
  [8, chorus],
  [4, outro]
)
```

---

## Key Principles

1. **stack() = Simultaneous** - All patterns play at the same time
2. **cat() = Sequential** - Patterns play one after another
3. **arrange() = Song Structure** - Control how many cycles each section plays
4. **Variables = Organization** - Store patterns for reuse and clarity
5. **Nesting = Complexity** - Stack groups of stacks for rich textures

---

## Common Patterns

### Minimal Techno

```javascript
const kick = s("bd*4").gain(0.9);
const hats = s("hh*8").lpf(800).gain(0.4);
const bass = note("c2 ~ c2 ~").s("sawtooth").lpf(400);

stack(kick, hats, bass)
```

### House Groove

```javascript
const drums = stack(
  s("bd*4"),
  s("~ sd"),
  s("hh*8")
);
const chords = note("[c4maj7 f4maj7]*2").s("piano").room(0.5);

stack(drums, chords)
```

### Ambient Texture

```javascript
const pad1 = note("<c3 eb3 f3 g3>").s("sawtooth").lpf(600).room(0.9).slow(4);
const pad2 = note("<g3 bb3 c4 d4>").s("sine").lpf(800).room(0.8).slow(5);
const texture = s("hh/4").gain(0.2).delay(0.5);

stack(pad1, pad2, texture)
```

---

## Summary

- Use `stack()` to layer patterns simultaneously
- Use JavaScript variables to organize musical parts
- Use `arrange()` to create song structures with multiple sections
- Combine `stack()`, `cat()`, and `arrange()` for complete compositions
- Mini-notation is great for simple patterns, functions are better for complex structures
