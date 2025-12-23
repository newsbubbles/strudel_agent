# Strudel Core Functions Reference

**Research Date**: 2025-12-22

## Sound Generation

### sound() / s()
Plays the sound of the given name.

**Parameters**: `sound_name` (string|Pattern)

**Examples**:
```javascript
sound("bd sd [~ bd] sd")
s("bd sd [~ bd] sd")  // Short form
s("bd sd, hh*8")      // With layering
```

### note()
Sets pitch as number (MIDI) or letter notation.

**Parameters**: `pitch` (number|string|Pattern)

**Examples**:
```javascript
note("48 52 55 59").sound("piano")  // MIDI numbers
note("c e g b").sound("piano")      // Letter notation
note("c2 e3 g4 b5").sound("piano")  // With octaves
note("c# d# f# g# a#")               // Sharps
note("db eb gb ab bb")               // Flats
```

### n()
Selects sample number or scale degree.

**Parameters**: `number` (number|Pattern)

**Examples**:
```javascript
// Sample selection
n("0 1 2 3").sound("hh")

// Scale degrees
n("0 2 4 6").scale("C:minor").sound("piano")
```

## Tempo Control

### setcpm()
Sets the tempo in cycles per minute.

**Parameters**: `cpm` (number)

**Examples**:
```javascript
setcpm(90/4)  // 90 BPM with 4 beats per cycle
setcpm(120/4) // 120 BPM
setcpm(60)    // 60 cycles per minute
```

### setcps()
Sets the tempo in cycles per second.

**Parameters**: `cps` (number)

**Examples**:
```javascript
setcps(0.5)  // 2 seconds per cycle
setcps(1)    // 1 second per cycle
setcps(0.75) // 1.33 seconds per cycle
```

## Pattern Manipulation

### fast()
Speeds up a pattern by a given factor.

**Parameters**: `factor` (number|Pattern)

**Examples**:
```javascript
sound("bd sd").fast(2)           // Twice as fast
sound("bd sd").fast("<1 2 4>")   // Variable speed
```

### slow()
Slows down a pattern by a given factor.

**Parameters**: `factor` (number|Pattern)

**Examples**:
```javascript
sound("bd sd").slow(2)           // Half speed
sound("bd sd").slow("<1 2 4>")   // Variable speed
```

### rev()
Reverses the order of events in a pattern.

**Examples**:
```javascript
n("0 1 [4 3] 2 0 2 [~ 3] 4").sound("jazz").rev()
sound("bd sd hh cp").rev()
```

### jux()
Splits pattern between left/right channels, applying modification to right.

**Parameters**: `function` (function)

**Examples**:
```javascript
n("0 1 [4 3] 2").sound("jazz").jux(rev)
sound("bd sd hh").jux(fast(2))
```

### add()
Adds a number or note pattern to existing notes (transposition).

**Parameters**: `value` (number|Pattern)

**Examples**:
```javascript
note("c2 [eb3,g3]").add("<0 <1 -1>>")
n("0 [2 4] <3 5>").add("<0 [0,2,4]>").scale("C5:minor")
```

### ply()
Repeats each event in a pattern n times.

**Parameters**: `n` (number|Pattern)

**Examples**:
```javascript
sound("bd sd").ply(2)              // Each event twice
sound("bd sd").ply("<1 2 3>")      // Variable repetition
```

### off()
Creates a copy of pattern, shifts it in time, and applies modifications.

**Parameters**: 
- `timeOffset` (number): Time shift (fractions of a cycle)
- `function` (function): Modification function

**Examples**:
```javascript
n("0 [4 <3 2>] <2 3> [~ 1]")
  .off(1/16, x => x.add(4))
  .scale("C5:minor")

s("bd sd").off(1/8, x => x.speed(1.5))
```

## Scales and Harmony

### scale()
Interprets `n()` values as scale degrees.

**Parameters**: `scale_name` (string|Pattern)

**Available Scales**:
- Major: `C:major`, `D:major`, etc.
- Minor: `A:minor`, `C:minor`, etc.
- Modes: `D:dorian`, `G:mixolydian`, `E:phrygian`, `F:lydian`
- Pentatonic: `C:major:pentatonic`, `A:minor:pentatonic`

**Examples**:
```javascript
n("0 2 4 6").scale("C:minor").sound("piano")
n("0 2 4 <[6,8] [7,9]>").scale("C:minor")
n("0 2 4").scale("<C:major D:mixolydian>/4")
```

### chord()
Generates chord progressions.

**Parameters**: `chord_pattern` (string|Pattern)

**Examples**:
```javascript
chord("<Bbm9 Fm9>/4")
chord("<C^7 Dm7 G7 C^7>")
```

### voicing()
Applies chord voicing to notes.

**Examples**:
```javascript
chord("<Bbm9 Fm9>/4").voicing().s("gm_epiano1")
```

## Sample Banks

### bank()
Selects the sound bank (drum machine).

**Parameters**: `bank_name` (string|Pattern)

**Available Banks**:
- RolandTR808
- RolandTR909
- RolandTR707
- RolandTR505
- AkaiLinn
- RhythmAce
- ViscoSpaceDrum
- RolandCompurhythm1000
- CasioRZ1

**Examples**:
```javascript
sound("bd sd, hh*8").bank("RolandTR808")
sound("bd sd").bank("<RolandTR808 RolandTR909>")
```

### samples()
Loads custom sample maps.

**Parameters**: 
- `sampleMap` (object|string): Sample map or URL
- `basePath` (string): Optional base URL

**Examples**:
```javascript
// From GitHub
samples('github:tidalcycles/dirt-samples')

// From URL
samples('https://example.com/samples/strudel.json')

// Custom map
samples({
  bassdrum: 'bd/BT0AADA.wav',
  hihat: 'hh27/000_hh27closedhh.wav'
}, 'https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/')

// Shabda (freesound.org)
samples('shabda:bass:4,hihat:4,rimshot:2')

// Speech synthesis
samples('shabda/speech:hello,world')
```

## Pattern Structure

### stack()
Layers multiple patterns simultaneously.

**Parameters**: `...patterns` (Pattern[])

**Examples**:
```javascript
stack(
  s("bd*4"),
  s("~ sd ~ sd"),
  s("hh*8")
)

stack(
  note("c2 eb2 f2 g2").s("sawtooth"),
  note("c4 eb4 g4").s("piano"),
  s("bd sd [~ bd] sd")
)
```

### struct()
Defines rhythm structure for a pattern.

**Parameters**: `structure` (string|Pattern)

**Examples**:
```javascript
s("bd").struct("<[x*<1 2> [~@3 x]] x>")
n("0 2 4").struct("x ~ x x")
```

### mask()
Masks or filters events (1 = play, 0 = silence).

**Parameters**: `pattern` (string|Pattern)

**Examples**:
```javascript
s("bd sd hh cp").mask("<0 0 1 1>/16")
n("0 2 4 6").mask("1 0 1 0")
```

## Time Manipulation

### early()
Shifts events earlier in time.

**Parameters**: `amount` (number|Pattern)

**Examples**:
```javascript
sound("bd sd").early(0.5)
sound("hh*8").early(0.125)
```

### late()
Shifts events later in time.

**Parameters**: `amount` (number|Pattern)

**Examples**:
```javascript
sound("bd sd").late("[0 .01]*4")
sound("cp").late(0.125)
```

### offset()
Offsets events in time.

**Parameters**: `amount` (number|Pattern)

**Examples**:
```javascript
chord("<Bbm9 Fm9>/4").offset(-1)
sound("bd sd").offset(0.25)
```

## Randomization

### rand
Random value between 0 and 1.

**Examples**:
```javascript
sound("hh*8").gain(rand)
sound("bd*4").pan(rand)
```

### rand.range()
Random value in specified range.

**Parameters**: `min`, `max` (number)

**Examples**:
```javascript
sound("hh*8").lpf(rand.range(500, 2000))
sound("bd*4").speed(rand.range(0.9, 1.1))
```

### perlin
Perlin noise for smoother randomization (0-1).

**Examples**:
```javascript
sound("hh*8").gain(perlin)
```

### perlin.range()
Perlin noise in specified range.

**Parameters**: `min`, `max` (number)

**Examples**:
```javascript
sound("bd*4").gain(perlin.range(0.6, 0.9))
```

## Modulation Signals

### sine
Sine wave LFO (0-1).

**Examples**:
```javascript
sound("hh*16").gain(sine)
sound("bd*4").pan(sine)
```

### sine.range()
Sine wave in specified range.

**Parameters**: `min`, `max` (number)

**Examples**:
```javascript
sound("hh*16").lpf(sine.range(500, 2000))
note("c2").fm(sine.range(0, 8).slow(4))
```

### saw, square, tri
Other waveform LFOs (0-1).

**Examples**:
```javascript
sound("hh*16").gain(saw)
sound("bd*4").pan(square)
sound("sd*4").lpf(tri.range(200, 4000))
```

## Utility Functions

### run()
Generates ascending number sequence.

**Parameters**: `n` (number)

**Examples**:
```javascript
n(run(8)).scale("C:minor")  // 0 1 2 3 4 5 6 7
n(run(4)).sound("bd")       // Cycle through 4 samples
```

### irand()
Random integer.

**Parameters**: `max` (number)

**Examples**:
```javascript
n(irand(8)).scale("C:minor")
n(irand(4)).sound("hh")
```

### choose()
Randomly choose from array.

**Parameters**: `array` (array)

**Examples**:
```javascript
sound(choose(["bd", "sd", "hh", "cp"]))
n(choose([0, 2, 4, 7])).scale("C:minor")
```
