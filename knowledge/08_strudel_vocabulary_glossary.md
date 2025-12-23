# Strudel Vocabulary & Glossary

**Research Date**: 2025-12-22

A comprehensive glossary of Strudel-specific terminology for translating musical intent into code.

## Core Concepts

### Pattern
The fundamental unit in Strudel. A pattern is a time-based sequence of events that repeats cyclically.

### Cycle
A unit of time (default 2 seconds). All patterns repeat based on cycles. Can be changed with `setcpm()` or `setcps()`.

### Mini-Notation
Strudel's compact syntax for representing patterns using special characters like `[]`, `<>`, `*`, `/`, etc.

### Stack
Layering multiple patterns to play simultaneously (using `,` or `stack()`).

## Musical Intent → Strudel Translation

### Rhythm Terms

| Musical Intent | Strudel Code | Explanation |
|---------------|--------------|-------------|
| "Play faster" | `.fast(2)` or `*2` | Double the speed |
| "Play slower" | `.slow(2)` or `/2` | Half the speed |
| "Add shuffle" | `.late("[0 .01]*4")` | Delay alternate notes |
| "Swing feel" | `note("c@2 e")` | Elongate first note |
| "Syncopated" | `sound("bd ~ ~ bd ~ bd ~ ~")` | Off-beat accents |
| "Four on the floor" | `sound("bd*4")` | Kick on every beat |
| "Breakbeat" | Complex pattern with varied hits | See pattern library |
| "Polyrhythm" | `sound("{bd bd bd, cp cp cp cp}")` | Multiple rhythms |
| "Euclidean" | `sound("bd(5,8)")` | Evenly distributed |

### Melodic Terms

| Musical Intent | Strudel Code | Explanation |
|---------------|--------------|-------------|
| "Play a melody" | `note("c e g b")` | Sequence of notes |
| "Arpeggio" | `n("0 2 4 7").scale("C:minor")` | Chord notes in sequence |
| "Ascending" | `n(run(8))` | Going up |
| "Descending" | `n(run(8)).rev()` | Going down |
| "Octave jump" | `note("c2 c3")` | Same note, different octave |
| "Transpose" | `.add(7)` | Shift pitch up |
| "Random notes" | `n(irand(8))` | Randomized |
| "Pentatonic" | `.scale("C:minor:pentatonic")` | 5-note scale |
| "Chromatic" | All 12 notes | Use MIDI numbers |

### Harmonic Terms

| Musical Intent | Strudel Code | Explanation |
|---------------|--------------|-------------|
| "Play a chord" | `note("[c,e,g]")` | Notes together |
| "Chord progression" | `chord("<C F G>")` | Sequence of chords |
| "Major" | `.scale("C:major")` | Happy sound |
| "Minor" | `.scale("C:minor")` | Sad sound |
| "Jazz chords" | `chord("Dm7 G7 C^7")` | Extended harmonies |
| "Power chord" | `note("[c2,g2]")` | Root + fifth |
| "Voicing" | `.voicing()` | Chord arrangement |

### Timbre Terms

| Musical Intent | Strudel Code | Explanation |
|---------------|--------------|-------------|
| "Bright sound" | `.lpf(8000)` or `.s("sawtooth")` | High frequencies |
| "Dark sound" | `.lpf(400)` | Low frequencies |
| "Warm" | `.s("triangle")` | Soft waveform |
| "Harsh" | `.s("sawtooth")` or `.distort(2)` | Aggressive |
| "Clean" | `.s("sine")` | Pure tone |
| "Dirty" | `.distort(4)` | Distorted |
| "Filtered" | `.lpf(1000).lpq(10)` | Resonant filter |
| "Bell-like" | `.fm(8)` | FM synthesis |
| "Noisy" | `.noise(0.5)` or `.s("white")` | Added noise |

### Dynamic Terms

| Musical Intent | Strudel Code | Explanation |
|---------------|--------------|-------------|
| "Louder" | `.gain(1.5)` | Increase volume |
| "Quieter" | `.gain(0.5)` | Decrease volume |
| "Accent" | `.gain("1 .7 .8 .7")` | Emphasize beats |
| "Fade in" | `.attack(2)` | Slow attack |
| "Fade out" | `.release(2)` | Slow release |
| "Punchy" | `.attack(.01).decay(.1).sustain(0)` | Short envelope |
| "Sustained" | `.sustain(1).release(1)` | Held notes |

### Spatial Terms

| Musical Intent | Strudel Code | Explanation |
|---------------|--------------|-------------|
| "Left/Right" | `.pan(0)` / `.pan(1)` | Stereo position |
| "Moving" | `.pan(sine)` | Animated panning |
| "Wide" | `.jux(rev)` | Stereo width |
| "Centered" | `.pan(0.5)` | Middle |
| "Spacious" | `.room(.8)` | Reverb |
| "Intimate" | `.room(0)` | Dry |
| "Distant" | `.room(.9).lpf(2000)` | Far away |

### Temporal Effects

| Musical Intent | Strudel Code | Explanation |
|---------------|--------------|-------------|
| "Echo" | `.delay(.5)` | Delay effect |
| "Reverb" | `.room(.5)` | Room ambience |
| "Slapback" | `.delay(.8:.125:.3)` | Short echo |
| "Long decay" | `.room(.8).size(4)` | Cathedral |
| "Tight" | `.room(.2).size(1)` | Small room |

## Drum Sound Vocabulary

### Drum Types

| Term | Code | Description |
|------|------|-------------|
| Kick / Bass drum | `bd` | Low thump |
| Snare | `sd` | Sharp crack |
| Hi-hat closed | `hh` | Tight click |
| Hi-hat open | `oh` | Sustained sizzle |
| Clap | `cp` | Hand clap |
| Rimshot | `rim` | Stick on rim |
| Crash | `cr` | Cymbal crash |
| Ride | `rd` | Ride cymbal |
| Tom (high/mid/low) | `ht`, `mt`, `lt` | Toms |
| Cowbell | `cb` | Cowbell |
| Shaker | `sh` | Shaker |

### Drum Machine Character

| Character | Code | Era/Style |
|-----------|------|----------|
| "808 sound" | `.bank("RolandTR808")` | Classic hip-hop |
| "909 sound" | `.bank("RolandTR909")` | House/techno |
| "Vintage" | `.bank("RhythmAce")` | 70s |
| "80s digital" | `.bank("RolandTR707")` | 80s pop |

## Genre-Specific Patterns

### House
- Four-on-the-floor kick: `sound("bd*4")`
- Offbeat claps: `sound("[~ cp]*2")`
- Steady hi-hats: `sound("hh*8")`

### Techno
- Driving kick: `sound("bd*4")`
- Minimal percussion: `sound("~ cp ~ cp, hh*8")`
- Filtered bass: `note("c2*4").s("sawtooth").lpf(800)`

### Hip-Hop
- Boom bap: `sound("bd ~ ~ ~ bd ~ ~ ~, ~ ~ sd ~ ~ ~ sd ~")`
- Swing: Use `.late("[0 .01]*4")`
- Sample chops: `.slice(8, "0 1 2 3")`

### Ambient
- Long attack: `.attack(2)`
- Lots of reverb: `.room(.9)`
- Slow movement: `.slow(4)`
- Layered pads: Stack multiple sounds

### Drum & Bass
- Fast tempo: `setcpm(170/4)`
- Breakbeats: Use `.slice()` on breaks
- Sub bass: `note("c1").s("sine")`

## Effect Descriptions

### Filter Characteristics

| Description | Implementation |
|-------------|----------------|
| "Muffled" | `.lpf(200)` |
| "Bright" | `.lpf(8000)` |
| "Thin" | `.hpf(1000)` |
| "Full" | `.hpf(100)` |
| "Resonant" | `.lpq(20)` |
| "Sweeping" | `.lpf(sine.range(200,4000))` |
| "Vowel-like" | `.vowel("a e i o u")` |

### Modulation Descriptions

| Description | Implementation |
|-------------|----------------|
| "Wobbling" | `.lpf(sine.range(200,2000).fast(4))` |
| "Vibrato" | `.vib(6).vibmod(0.5)` |
| "Tremolo" | `.tremsync(4)` |
| "Phasing" | `.phaser(4)` |
| "Chorus" | `.delay(.01).delayfeedback(.3)` |

## Common Musical Requests

### "Make it groovy"
- Add syncopation: `sound("bd ~ [~ bd] ~ bd ~ ~ bd")`
- Add swing: `.late("[0 .01]*4")`
- Vary velocity: `.gain(".8 1 .7 .9")`

### "Make it interesting"
- Add variation: Use `<>` for alternation
- Add randomness: `n(irand(4))`
- Add effects: `.delay(.5).room(.4)`

### "Make it more energetic"
- Increase tempo: `.fast(2)`
- Add more hi-hats: `sound("hh*16")`
- Increase filter: `.lpf(4000)`
- Add distortion: `.distort(2)`

### "Make it calmer"
- Decrease tempo: `.slow(2)`
- Lower filter: `.lpf(800)`
- Add reverb: `.room(.7)`
- Softer attack: `.attack(.5)`

### "Make it darker"
- Lower filter: `.lpf(400)`
- Minor scale: `.scale("C:minor")`
- Less brightness: `.s("triangle")`

### "Make it brighter"
- Higher filter: `.lpf(8000)`
- Major scale: `.scale("C:major")`
- Brighter waveform: `.s("sawtooth")`

## Pattern Complexity Levels

### Beginner
- Simple sequences: `sound("bd sd hh cp")`
- Basic repetition: `sound("bd*4")`
- Simple layering: `sound("bd*4, hh*8")`

### Intermediate
- Sub-sequences: `sound("bd [hh hh] sd [hh bd]")`
- Alternation: `sound("bd <sd cp>")`
- Pattern effects: `.rev()`, `.jux()`, `.fast()`

### Advanced
- Complex mini-notation: `sound("{bd [sd cp]*2, hh*<4 8>}")`
- Pattern transformations: `.off()`, `.every()`, `.sometimes()`
- Generative: Using `rand`, `irand`, `choose()`
- Euclidean: `sound("bd(5,8,2)")`

## Synthesis Vocabulary

### Oscillator Types
- **Sine**: Pure, fundamental tone
- **Sawtooth**: Bright, all harmonics
- **Square**: Hollow, odd harmonics
- **Triangle**: Soft, few harmonics

### Synthesis Techniques
- **Subtractive**: Start bright, filter down (`.s("sawtooth").lpf(800)`)
- **Additive**: Build from harmonics (`.partials([1,0,0.3,0,0.1])`)
- **FM**: Frequency modulation (`.fm(8).fmh(2)`)
- **Wavetable**: Custom waveforms (`.s("wt_flute")`)

## Time Signature Concepts

Strudel works in cycles, not traditional time signatures, but you can think of it as:
- 1 cycle = 1 bar
- `*4` = 4 notes per bar (quarter notes in 4/4)
- `*8` = 8 notes per bar (eighth notes in 4/4)
- `*16` = 16 notes per bar (sixteenth notes in 4/4)
- `/2` = Pattern takes 2 bars
- `/4` = Pattern takes 4 bars

## Musical Concepts in Code

### Call and Response
```javascript
$: note("c e g c").s("piano")  // Call
$: note("~ ~ ~ ~ e g b e").s("piano")  // Response
```

### Question and Answer
```javascript
note("c e g b, ~ ~ ~ ~ c e g c").s("piano")
```

### Tension and Release
```javascript
// Tension: dissonant, high filter
note("[c,db,g]").s("sawtooth").lpf(4000)
// Release: consonant, lower filter  
note("[c,e,g]").s("sawtooth").lpf(1000)
```

### Build-up
```javascript
sound("bd*<1 2 4 8>")
  .lpf(sine.range(200, 8000).slow(4))
  .gain("<.5 .6 .8 1>")
```

### Drop
```javascript
// Before drop: minimal
sound("bd ~ ~ ~")
// Drop: full energy
sound("bd*4, [~ cp]*2, hh*8")
```
