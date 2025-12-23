# Strudel Mini-Notation Cheatsheet

**Research Date**: 2025-12-22  
**Sources**: 
- https://strudel.cc/workshop/first-sounds/
- https://strudel.cc/workshop/first-notes/

## Basic Syntax

| Concept | Syntax | Example | Description |
|---------|--------|---------|-------------|
| **Sequence** | space | `sound("bd bd sd hh")` | Play sounds in order |
| **Sample Number** | `:x` | `sound("hh:0 hh:1 hh:2 hh:3")` | Select specific sample variant |
| **Rests** | `-` or `~` | `sound("metal - jazz jazz:1")` | Silence/rest |
| **Alternate** | `<>` | `sound("<bd hh rim oh bd rim>")` | Play one per cycle |
| **Sub-Sequences** | `[]` | `sound("bd wind [metal jazz] hh")` | Group events |
| **Sub-Sub-Sequences** | `[[]]` | `sound("bd [metal [jazz [sd cp]]]")` | Nested groups |
| **Speed up** | `*` | `sound("bd sd*2 cp*3")` | Multiply events |
| **Slow down** | `/` | `note("[c a f e]/2")` | Divide over cycles |
| **Parallel** | `,` | `sound("bd*2, hh*2 [hh oh]")` | Stack patterns |
| **Elongate** | `@` | `note("c@3 e")` | Make event longer |
| **Replicate** | `!` | `note("c!3 e")` | Repeat event |

## Advanced Patterns

### Euclidean Rhythms
```javascript
// Distribute events evenly
sound("bd(3,8)")  // 3 bass drums in 8 steps
sound("hh(5,8)")  // 5 hi-hats in 8 steps
```

### Polyrhythms
```javascript
// Different time signatures
sound("{bd sd hh, cp cp cp cp}")  // 3 against 4
```

### Alternation with Angle Brackets
```javascript
note("<36 34 41 39>")  // One note per cycle
note("60 <63 62 65 63>")  // First note always, second alternates
```

### Nested Alternation
```javascript
sound("bd <sd <cp rim>>")  // Nested alternation
```

## Pattern Modifiers

### Multiplication (Speed Up)
```javascript
sound("bd*2")           // Play bd twice per cycle
sound("bd*4")           // Play bd four times
sound("<bd*2 bd*4>")    // Alternate between 2 and 4
```

### Division (Slow Down)
```javascript
note("[c e g]/2")       // Pattern takes 2 cycles
note("[c e g]/4")       // Pattern takes 4 cycles
```

### Elongation with @
```javascript
note("c@3 eb")          // c is 3 units long, eb is 1
note("c@2 eb@2 g")      // c and eb are 2 units, g is 1
```

### Replication with !
```javascript
note("c!2 [eb,<g a bb a>]")  // c repeated twice
sound("bd!4")                 // bd repeated 4 times
```

## Combining Patterns

### Parallel Patterns (Comma)
```javascript
sound("bd*4, hh*8")                    // Drums + hi-hat
sound("bd*4, [~ cp]*2, [~ hh]*4")      // Three layers
```

### Multi-line Patterns (Backticks)
```javascript
sound(`
bd*2, 
- cp, 
- - - oh, 
hh*4,
[- casio]*2
`)
```

### Using $: for Multiple Patterns
```javascript
$: sound("bd*4, [~ cp]*2")  // Pattern 1
$: note("c eb g").s("piano")  // Pattern 2
$: s("hh*6")  // Pattern 3

_$: sound("bd*4")  // Muted pattern (underscore prefix)
```

## Sample Selection Patterns

### Direct Selection
```javascript
sound("jazz:0 jazz:1 [jazz:4 jazz:2] jazz:3*2")
```

### Using n() Function
```javascript
n("0 1 [4 2] 3*2").sound("jazz")  // Cleaner syntax
```

### Pattern Sample Numbers
```javascript
n("<0 1 2 3>").sound("hh")        // Cycle through samples
n("[0 1]*2").sound("bd")          // Alternate quickly
```

## Rhythmic Patterns

### Basic Drum Patterns
```javascript
// Four-on-the-floor
sound("bd*4, [~ cp]*2, hh*8")

// Rock beat
sound("[bd sd]*2, hh*8")

// Breakbeat
sound("bd*2 [~ bd] bd, ~ sd ~ sd, hh*8")
```

### 16-Step Sequencer Style
```javascript
setcpm(90/4)
sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  -  - ] [-  -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  hh - ],
[-  -  -  - ] [cp -  -  - ] [-  -  -  - ] [cp -  -  - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd]
`)
```

## Note Patterns

### Letter Notation
```javascript
note("c e g b")              // C E G B
note("c# d# f# g# a#")       // Sharps
note("db eb gb ab bb")       // Flats
```

### Octave Specification
```javascript
note("c2 e3 g4 b5")         // Different octaves
note("c2 c3 c4 c5")         // Ascending octaves
```

### Scale Degrees
```javascript
n("0 2 4 6").scale("C:minor")           // Scale degrees
n("0 2 4 <[6,8] [7,9]>").scale("C:minor")  // With chords
```

## Common Patterns

### Shuffle/Swing Rhythm
```javascript
n("<[4@2 4] [5@2 5] [6@2 6] [5@2 5]>*2")
.scale("C2:mixolydian")
```

### Alternating Patterns
```javascript
sound("bd <sd cp>")              // bd, then sd, then bd, then cp
sound("<bd sd> <hh oh>")         // Combinations alternate
```

### Nested Subdivisions
```javascript
sound("bd [hh hh] sd [hh bd]")     // Subdivided beats
sound("bd [[rim rim] hh] bd cp")   // Nested subdivisions
```

## Pro Tips

1. **Spaces matter**: `bd sd` is different from `bdsd`
2. **Commas stack**: Use for layering simultaneous patterns
3. **Brackets group**: Use to create subdivisions
4. **Angle brackets alternate**: One element per cycle
5. **Combine freely**: All syntax can be nested and combined
6. **Use variables**: Store patterns in variables for reuse

```javascript
let drums = "bd*4, [~ sd]*2, hh*8"
let bass = note("c2 eb2 f2 g2")

$: sound(drums)
$: bass.s("sawtooth").lpf(800)
```
