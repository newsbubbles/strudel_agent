# Conditional Modifiers Reference

**Research Date**: 2025-12-23  
**Source**: https://strudel.cc/learn/conditional-modifiers/

---

## Overview

Conditional modifiers allow you to control patterns based on specific conditions, structures, or time-based rules. They're essential for creating variation, building complexity, and adding musical interest to your patterns.

---

## Cycle-Based Conditionals

### lastOf()

**What it does**: Applies a function every n cycles, starting from the **last** cycle.

**Syntax**: `pattern.lastOf(n, func)`

**Parameters**:
- `n` (number): How many cycles to wait
- `func` (function): The function to apply

**Example**:
```javascript
// Reverses the note pattern every 4 cycles, starting from the last (4th) cycle
note("c3 d3 e3 g3").lastOf(4, x=>x.rev())
```

**Use Case**: Add variation at the end of musical phrases.

---

### firstOf()

**What it does**: Applies a function every n cycles, starting from the **first** cycle.

**Syntax**: `pattern.firstOf(n, func)`

**Parameters**:
- `n` (number): How many cycles to wait
- `func` (function): The function to apply

**Example**:
```javascript
// Reverses the note pattern every 4 cycles, starting from the first cycle
note("c3 d3 e3 g3").firstOf(4, x=>x.rev())
```

**Use Case**: Add variation at the beginning of musical phrases.

---

## Pattern-Based Conditionals

### when()

**What it does**: Applies a function **whenever** a given pattern is in a true state (non-zero).

**Syntax**: `pattern.when(binary_pat, func)`

**Parameters**:
- `binary_pat` (Pattern): A pattern that determines when to apply the function (0 = don't apply, 1 = apply)
- `func` (function): The function to apply

**Examples**:
```javascript
// Apply transformation only when pattern is 1 (every other half-cycle)
"c3 eb3 g3".when("<0 1>/2", x=>x.sub("5")).note()

// Apply distortion only on specific beats
s("bd sd hh cp").when("0 1 0 1", x=>x.distort(0.5))

// Conditional reverb
note("c e g b").when("<0 0 1>", x=>x.room(0.9))
```

**Use Case**: Conditionally apply effects or transformations based on a pattern.

---

## Chunking Functions

### chunk()

**What it does**: Divides a pattern into a given number of parts, then cycles through those parts in turn, applying the function to each part (one part per cycle).

**Synonyms**: `slowChunk`, `slowchunk`

**Syntax**: `pattern.chunk(n, func)`

**Parameters**:
- `n` (number): Number of parts to divide the pattern into
- `func` (function): The function to apply to each part

**Examples**:
```javascript
// Divides into 4 parts, adds 7 to each part in sequence (one part per cycle)
"0 1 2 3".chunk(4, x=>x.add(7)).scale("A:minor").note()

// Apply different effects to different chunks
s("bd sd hh cp").chunk(2, x=>x.room(0.5))
```

**Use Case**: Create evolving patterns that change part-by-part over time.

---

### chunkBack()

**What it does**: Like `chunk()`, but cycles through the parts in **reverse** order.

**Synonyms**: `chunkback`

**Syntax**: `pattern.chunkBack(n, func)`

**Parameters**:
- `n` (number): Number of parts to divide the pattern into
- `func` (function): The function to apply to each part

**Example**:
```javascript
// Divides into 4 parts, adds 7 to each part in reverse sequence
"0 1 2 3".chunkBack(4, x=>x.add(7)).scale("A:minor").note()
```

**Use Case**: Create reverse-evolving patterns.

---

### fastChunk()

**What it does**: Like `chunk()`, but the cycles of the source pattern **aren't repeated** for each set of chunks.

**Synonyms**: `fastchunk`

**Syntax**: `pattern.fastChunk(n, func)`

**Parameters**:
- `n` (number): Number of parts to divide the pattern into
- `func` (function): The function to apply to each part

**Example**:
```javascript
// Applies color transformation to chunks without repeating cycles
"<0 8> 1 2 3 4 5 6 7"
  .scale("C2:major").note()
  .fastChunk(4, x => x.color('red'))
  .slow(2)
```

**Use Case**: Apply transformations to chunks while maintaining pattern flow.

---

## Arpeggiation Functions

### arp()

**What it does**: Selects indices in stacked notes to create arpeggios.

**Syntax**: `pattern.arp(indices_pattern)`

**Parameters**:
- `indices_pattern` (Pattern): A pattern of indices to select from the stacked notes

**Examples**:
```javascript
// Create arpeggios by selecting different notes from chords
note("<[c,eb,g]!2 [c,f,ab] [d,f,ab]>").arp("0 [0,2] 1 [0,2]")

// Simple up-down arpeggio
note("[c,e,g]").arp("0 1 2 1")

// Random arpeggio pattern
note("[c,e,g,b]").arp("<0 1 2 3>")
```

**Index Reference**:
- `0` = bottom note
- `1` = second note
- `2` = third note, etc.

**Use Case**: Turn chords into arpeggios with custom patterns.

---

### arpWith()

**What it does**: Selects indices in stacked notes using a **custom function**.

**Status**: 🧪 Experimental

**Syntax**: `pattern.arpWith(function)`

**Parameters**:
- `function`: A function that selects the indices (receives array of notes)

**Example**:
```javascript
// Always select the third note (index 2) from each chord
note("<[c,eb,g]!2 [c,f,ab] [d,f,ab]>").arpWith(haps => haps[2])

// Select first and last note
note("[c,e,g,b]").arpWith(haps => [haps[0], haps[haps.length-1]])
```

**Use Case**: Advanced arpeggio patterns with custom logic.

---

## Structure Functions

### struct()

**What it does**: Applies a given **rhythm structure** to a pattern.

**Syntax**: `pattern.struct(structure_pattern)`

**Parameters**:
- `structure_pattern` (Pattern): A pattern that defines the rhythm structure (`x` = trigger, `~` = rest)

**Examples**:
```javascript
// Apply rhythm structure to chord notes
note("c,eb,g").struct("x ~ x ~ ~ x ~ x ~ ~ ~ x ~ x ~ ~").slow(2)

// Simple kick pattern with structure
s("bd").struct("x ~ ~ x ~ ~ x ~")

// Complex polyrhythm structure
n("0 2 4").struct("x(3,8)").scale("C:minor")
```

**Use Case**: Define rhythmic patterns independently from note/sound content.

---

### mask()

**What it does**: Returns **silence** when the mask pattern is `0` or `~`. Lets sound through when `1`.

**Syntax**: `pattern.mask(mask_pattern)`

**Parameters**:
- `mask_pattern` (Pattern): A binary pattern that determines when to silence (`0` = silence, `1` = play)

**Examples**:
```javascript
// Silence parts of the pattern based on mask
note("c [eb,g] d [eb,g]").mask("<1 [0 1]>")

// Create gated effect
s("bd*8").mask("1 0 1 0")

// Gradually reveal pattern
s("hh*16").mask("<1!4 [1 0]!4 [1 0 0]!4 [1 0 0 0]!4>")
```

**Use Case**: Selectively mute parts of a pattern, create gating effects.

---

## Reset and Restart Functions

### reset()

**What it does**: Resets the pattern to the **start of the current cycle** for each onset of the reset pattern.

**Syntax**: `pattern.reset(reset_pattern)`

**Parameters**:
- `reset_pattern` (Pattern): A pattern that triggers the reset

**Examples**:
```javascript
// Reset drum pattern at specific points
s("[<bd lt> sd]*2, hh*8").reset("<x@3 x(5,8)>")

// Reset melody on kick hits
note("c d e f g").reset(s("bd ~ ~ ~"))
```

**Use Case**: Create stuttering effects, sync patterns to triggers.

---

### restart()

**What it does**: Restarts the pattern from the **very beginning (cycle 0)** for each onset of the restart pattern.

**Difference from reset()**: `reset()` only resets to the start of the current cycle, while `restart()` goes back to cycle 0.

**Syntax**: `pattern.restart(restart_pattern)`

**Parameters**:
- `restart_pattern` (Pattern): A pattern that triggers the restart

**Examples**:
```javascript
// Restart drum pattern from the beginning at specific points
s("[<bd lt> sd]*2, hh*8").restart("<x@3 x(5,8)>")

// Restart melody from beginning on downbeat
note("c d e f g a b c5").restart("x ~ ~ ~")
```

**Use Case**: Create looping sections that restart from the beginning.

---

## Silence and Inversion

### hush()

**What it does**: Silences a pattern completely.

**Syntax**: `pattern.hush()`

**Parameters**: None

**Example**:
```javascript
// Only the hi-hat plays because bass drum is hushed
stack(
  s("bd").hush(),
  s("hh*3")
)

// Conditionally hush
s("bd*4").when("0 0 1 0", x=>x.hush())
```

**Use Case**: Mute specific layers in a stack, create dropouts.

---

### invert()

**What it does**: Swaps `1`s and `0`s in a binary pattern.

**Synonyms**: `inv`

**Syntax**: `pattern.invert()`

**Parameters**: None

**Examples**:
```javascript
// Invert binary pattern every 4 cycles
s("bd").struct("1 0 0 1 0 0 1 0".lastOf(4, invert))

// Create complementary rhythm
const rhythm = "1 0 1 0 1 1 0 0";
stack(
  s("bd").struct(rhythm),
  s("sd").struct(rhythm.invert())
)
```

**Use Case**: Create complementary rhythms, flip patterns.

---

## Pick Functions (Pattern Selection)

### pick()

**What it does**: Picks patterns or values from a **list** (by index) or a **lookup table** (by name). Maintains the structure of the original patterns.

**Syntax**: `pattern.pick(array_or_object)`

**Parameters**:
- `array_or_object`: A list or lookup table of patterns or values

**Examples**:
```javascript
// Using a list of note patterns
note("<0 1 2!2 3>".pick(["g a", "e f", "f g f g", "g c d"]))

// Using a list of sound patterns
sound("<0 1 [2,0]>".pick(["bd sd", "cp cp", "hh hh"]))

// Using a named lookup table
s("<a!2 [a,b] b>".pick({a: "bd(3,8)", b: "sd sd"}))

// Pick drum patterns
"<0 1 2>".pick([
  s("bd*4"),
  s("bd sd"),
  s("bd ~ sd ~")
])
```

**Use Case**: Create pattern variations, switch between different musical ideas.

---

### pickmod()

**What it does**: Same as `pick()`, but if you pick a number **greater than the list size**, it **wraps around** instead of sticking at the maximum.

**Syntax**: `pattern.pickmod(array_or_object)`

**Example**:
```javascript
// If you have 3 items and pick index 5, it wraps to index 2 (5 % 3 = 2)
note("<0 1 2!2 5>".pickmod(["g a", "e f", "f g f g"]))

// Safe indexing with wrapping
"<0 1 2 3 4 5 6 7>".pickmod(["bd", "sd", "hh"]) // Cycles through 3 items
```

**Use Case**: Safe pattern picking with automatic wrapping.

---

### pickF()

**What it does**: Uses a pattern of numbers to pick which **function** to apply to another pattern.

**Syntax**: `pattern.pickF(lookup_pattern, functions_array)`

**Parameters**:
- `lookup_pattern` (Pattern): A pattern of indices
- `functions_array` (Array<function>): An array of functions to choose from

**Examples**:
```javascript
// Apply different transformations to sound pattern
s("bd [rim hh]").pickF("<0 1 2>", [rev, jux(rev), fast(2)])

// Apply different transformations to note pattern
note("<c2 d2>(3,8)").s("square")
  .pickF("<0 2> 1", [
    jux(rev), 
    fast(2), 
    x=>x.lpf(800)
  ])

// Cycle through effect combinations
s("hh*8").pickF("<0 1 2 3>", [
  x=>x.gain(0.5),
  x=>x.lpf(1000),
  x=>x.room(0.5),
  x=>x.delay(0.25)
])
```

**Use Case**: Programmatically apply different effects or transformations.

---

### pickmodF()

**What it does**: Same as `pickF()`, but with **wrapping** for out-of-range indices.

**Syntax**: `pattern.pickmodF(lookup_pattern, functions_array)`

**Example**:
```javascript
// If you have 3 functions and pick index 5, it wraps to index 2
s("bd [rim hh]").pickmodF("<0 1 5>", [rev, jux(rev), fast(2)])
```

---

### pickRestart()

**What it does**: Similar to `pick()`, but the chosen pattern is **restarted from the beginning** when its index is triggered.

**Syntax**: `pattern.pickRestart(array_or_object)`

**Example**:
```javascript
// Each pattern restarts when its letter is triggered
"<a@2 b@2 c@2 d@2>".pickRestart({
  a: n("0 1 2 0"),
  b: n("2 3 4 ~"),
  c: n("[4 5] [4 3] 2 0"),
  d: n("0 -3 0 ~")
}).scale("C:major").s("piano")
```

**Use Case**: Create sections that always start from the beginning when triggered.

---

### pickmodRestart()

**What it does**: Same as `pickRestart()`, but with **wrapping** for out-of-range indices.

**Syntax**: `pattern.pickmodRestart(array_or_object)`

---

### pickReset()

**What it does**: Similar to `pick()`, but the chosen pattern is **reset to the start of the current cycle** when its index is triggered.

**Syntax**: `pattern.pickReset(array_or_object)`

**Use Case**: Create sections that reset to current cycle start.

---

### pickmodReset()

**What it does**: Same as `pickReset()`, but with **wrapping** for out-of-range indices.

**Syntax**: `pattern.pickmodReset(array_or_object)`

---

## Inhabit Functions (Squeezed Pattern Selection)

### inhabit()

**What it does**: Picks patterns or values from a list (by index) or lookup table (by name). Similar to `pick()`, but **cycles are squeezed** into the target ('inhabited') pattern.

**Synonyms**: `pickSqueeze`

**Syntax**: `pattern.inhabit(array_or_object)`

**Parameters**:
- `array_or_object`: A list or lookup table of patterns or values

**Examples**:
```javascript
// Using a lookup table with named patterns
"<a b [a,b]>".inhabit({
  a: s("bd(3,8)"),
  b: s("cp sd")
})

// With a slower tempo
s("a@2 [a b] a".inhabit({
  a: "bd(3,8)", 
  b: "sd sd"
})).slow(4)
```

**Difference from pick()**: `inhabit()` squeezes the selected pattern to fit the duration of the selecting event.

**Use Case**: Fit patterns into specific time windows.

---

### inhabitmod()

**What it does**: Same as `inhabit()`, but with **wrapping** for out-of-range indices.

**Synonyms**: `pickmodSqueeze`

**Syntax**: `pattern.inhabitmod(array_or_object)`

---

### squeeze()

**What it does**: Picks from a list using a pattern of integers as indices. The selected pattern is **compressed to fit** the duration of the selecting event.

**Syntax**: `squeeze(index_pattern, patterns_array)`

**Parameters**:
- `index_pattern` (Pattern): A pattern of indices
- `patterns_array`: A list of values or patterns

**Example**:
```javascript
// Squeezes selected patterns to fit the duration of each index event
note(squeeze("<0@2 [1!2] 2>", ["g a", "f g f g", "g a c d"]))

// Squeeze drum patterns
squeeze("<0 1 [0 1]>", [
  s("bd*4"),
  s("hh*8")
])
```

**Use Case**: Fit different patterns into specific time slots.

---

## Time-Based Conditionals

### off()

**What it does**: Creates a **copy** of the pattern, **shifts it in time**, and applies modifications to the copy. Both original and modified copy play together.

**Syntax**: `pattern.off(timeOffset, function)`

**Parameters**:
- `timeOffset` (number): Time shift in fractions of a cycle (e.g., `1/8`, `1/16`)
- `function` (function): Modification function to apply to the copy

**Examples**:
```javascript
// Create echo effect by adding transposed copy 1/16th cycle later
n("0 [4 <3 2>] <2 3> [~ 1]")
  .off(1/16, x => x.add(4))
  .scale("C5:minor")

// Speed-shifted echo
s("bd sd").off(1/8, x => x.speed(1.5))

// Layered delay with different effects
note("c e g")
  .off(1/8, x => x.add(7))
  .off(1/4, x => x.add(12).gain(0.5))

// Stereo delay
s("hh*4").off(1/16, x => x.pan(1)).pan(0)
```

**Use Case**: Create delays, echoes, layered harmonies, rhythmic doubling.

---

### palindrome()

**What it does**: Applies `rev()` to a pattern **every other cycle**, causing the pattern to alternate between forwards and backwards.

**Syntax**: `pattern.palindrome()`

**Parameters**: None

**Example**:
```javascript
// Plays "c d e g" forward, then "g e d c" backward, alternating
note("c d e g").palindrome()

// Palindrome drums
s("bd sd hh cp").palindrome()
```

**Use Case**: Create back-and-forth musical phrases.

---

### iter()

**What it does**: Divides a pattern into `n` subdivisions, plays them in order, and **increments the starting subdivision each cycle**. After reaching the last subdivision, it wraps back to the first.

**Syntax**: `pattern.iter(n)`

**Parameters**:
- `n` (number): The number of subdivisions

**Example**:
```javascript
// Divides into 4 parts, rotates starting position each cycle
note("0 1 2 3".scale('A minor')).iter(4)

// Cycle 1: 0 1 2 3
// Cycle 2: 1 2 3 0
// Cycle 3: 2 3 0 1
// Cycle 4: 3 0 1 2
// Cycle 5: 0 1 2 3 (wraps)
```

**Use Case**: Create rotating patterns, phasing effects.

---

### iterBack()

**What it does**: Similar to `iter()`, but plays the subdivisions in **reverse order**.

**Synonyms**: `iterback`

**Syntax**: `pattern.iterBack(n)`

**Parameters**:
- `n` (number): The number of subdivisions

**Example**:
```javascript
// Rotates in reverse
note("0 1 2 3".scale('A minor')).iterBack(4)
```

**Use Case**: Reverse rotation effects.

---

### ribbon()

**What it does**: Loops a **specific portion** of a pattern defined by an offset and duration. Like cutting a piece from a time ribbon and looping it.

**Syntax**: `pattern.ribbon(offset, cycles)`

**Parameters**:
- `offset` (number): Start point of the loop in cycles
- `cycles` (number): Loop length in cycles

**Examples**:
```javascript
// Loop cycles 1-3 of the pattern
note("<c d e f>").ribbon(1, 2)

// Loop a portion of randomness (use specific seed)
n(irand(8).segment(4)).scale("c:pentatonic").ribbon(1337, 2)

// Rhythm generator
s("bd!16?").ribbon(29, 0.5)
```

**Use Case**: Lock in interesting random variations, create frozen sections.

---

### inside()

**What it does**: Carries out an operation **'inside'** a cycle. Applies a transformation to a pattern **slowed down** by a factor, then **sped back up**.

**Syntax**: `pattern.inside(n, function)`

**Parameters**:
- `n` (number): The factor to slow down and speed up
- `function`: The transformation function to apply

**Example**:
```javascript
"0 1 2 3 4 3 2 1".inside(4, rev).scale('C major').note()

// Equivalent to:
// "0 1 2 3 4 3 2 1".slow(4).rev().fast(4).scale('C major').note()
```

**Use Case**: Apply transformations at a different time scale.

---

### outside()

**What it does**: Carries out an operation **'outside'** a cycle. Applies a transformation to a pattern **sped up** by a factor, then **slowed back down**.

**Syntax**: `pattern.outside(n, function)`

**Parameters**:
- `n` (number): The factor to speed up and slow down
- `function`: The transformation function to apply

**Example**:
```javascript
"<[0 1] 2 [3 4] 5>".outside(4, rev).scale('C major').note()

// Equivalent to:
// "<[0 1] 2 [3 4] 5>".fast(4).rev().slow(4).scale('C major').note()
```

**Use Case**: Apply transformations at a faster time scale.

---

## Quick Reference Table

| Function | Category | Purpose |
|----------|----------|----------|
| `lastOf()` | Cycle-based | Apply function every n cycles (starting last) |
| `firstOf()` | Cycle-based | Apply function every n cycles (starting first) |
| `when()` | Pattern-based | Apply function when condition is true |
| `chunk()` | Chunking | Divide and apply function to each part sequentially |
| `chunkBack()` | Chunking | Like chunk but in reverse |
| `fastChunk()` | Chunking | Chunk without repeating cycles |
| `arp()` | Arpeggiation | Select indices from stacked notes |
| `arpWith()` | Arpeggiation | Custom arpeggio function |
| `struct()` | Structure | Apply rhythm structure |
| `mask()` | Structure | Silence when mask is 0 |
| `reset()` | Reset | Reset to start of current cycle |
| `restart()` | Reset | Restart from cycle 0 |
| `hush()` | Silence | Silence pattern completely |
| `invert()` | Inversion | Swap 1s and 0s |
| `pick()` | Selection | Pick patterns by index/name |
| `pickmod()` | Selection | Pick with wrapping |
| `pickF()` | Selection | Pick functions to apply |
| `pickRestart()` | Selection | Pick with restart behavior |
| `pickReset()` | Selection | Pick with reset behavior |
| `inhabit()` | Selection | Pick and squeeze patterns |
| `squeeze()` | Selection | Compress patterns to fit |
| `off()` | Time-based | Create time-shifted copy |
| `palindrome()` | Time-based | Alternate forward/backward |
| `iter()` | Time-based | Rotate pattern each cycle |
| `iterBack()` | Time-based | Rotate backward each cycle |
| `ribbon()` | Time-based | Loop specific portion |
| `inside()` | Time-based | Transform at slower scale |
| `outside()` | Time-based | Transform at faster scale |

---

## Common Use Cases

### Creating Variation

```javascript
// Add variation every 4 cycles
s("bd sd hh cp").lastOf(4, x=>x.rev())

// Conditional effects
note("c e g b").when("<0 1>", x=>x.room(0.9))

// Rotating patterns
n("0 2 4 6").scale("C:minor").iter(4)
```

### Building Complexity

```javascript
// Layered delays
note("c e g")
  .off(1/8, x => x.add(7))
  .off(1/4, x => x.add(12).gain(0.5))

// Multiple transformations
s("bd sd").pickF("<0 1 2>", [
  rev,
  fast(2),
  x=>x.room(0.5)
])
```

### Rhythmic Interest

```javascript
// Euclidean structure
n("0 2 4").struct("x(5,8)").scale("C:minor")

// Masked patterns
s("hh*16").mask("1 1 1 0")

// Complementary rhythms
const r = "1 0 1 0 1 1 0 0";
stack(
  s("bd").struct(r),
  s("sd").struct(r.invert())
)
```

### Pattern Selection

```javascript
// Switch between drum patterns
"<0 1 2>".pick([
  s("bd*4"),
  s("bd sd"),
  s("bd ~ sd ~")
])

// Named pattern switching
"<verse chorus>".pick({
  verse: stack(kick, bass),
  chorus: stack(kick, bass, synth)
})
```

---

## Tips

1. **Combine conditionals** for complex behavior:
   ```javascript
   s("bd sd hh cp")
     .when("<0 1>", x=>x.room(0.5))
     .lastOf(4, x=>x.rev())
   ```

2. **Use pick() for song structure**:
   ```javascript
   "<intro!4 verse!8 chorus!8 verse!8>".pick({
     intro: s("bd hh"),
     verse: stack(s("bd sd"), s("hh*8")),
     chorus: stack(s("bd sd"), s("hh*8"), note("c e g"))
   })
   ```

3. **mask() for gradual reveals**:
   ```javascript
   s("hh*16").mask("<1!16 [1 0]!8 [1 0 0]!8 [1 0 0 0]!8>")
   ```

4. **off() for instant depth**:
   ```javascript
   note("c e g")
     .off(1/16, x=>x.add(7))
     .off(1/8, x=>x.add(12).gain(0.6))
   ```

5. **struct() separates rhythm from content**:
   ```javascript
   const rhythm = "x ~ x ~ x x ~ x";
   note("c e g b").struct(rhythm)
   ```
