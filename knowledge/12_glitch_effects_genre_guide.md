# Glitch Effects and Genre-Specific Techniques

**Research Date**: 2025-12-23  
**Sources**: Official Strudel documentation, community examples, verified code from GitHub

---

## Overview

This guide compiles verified examples of glitch-style effects, experimental sound design, and genre-specific techniques in Strudel. All code examples use proper `$:` notation or `const` variable declarations and have been tested or sourced from the official documentation and community.

---

## Core Glitch Effects

### 1. Bitcrushing (`crush`)

**What it does**: Reduces bit depth to create digital distortion artifacts.

**Parameters**: Bit depth (16 = nearly original, 1 = extreme reduction)

**Basic Example**:
```javascript
$: s("<bd sd>,hh*3").fast(2).crush("<16 8 7 6 5 4 3 2>")
```

**Explanation**: Gradually decreases bit depth from 16-bit (clean) to 2-bit (heavily degraded), creating increasingly severe digital distortion.

**Advanced Example - Patterned Bitcrushing**:
```javascript
$: s("bd*4 hh*8")
  .crush("<4 8 [2 16]>")
  .gain("<0.8 1 0.9>")
```

**Use Cases**:
- Lo-fi hip-hop textures
- Industrial/glitch hop degradation
- Retro 8-bit game sounds
- IDM digital artifacts

---

### 2. Sample Rate Reduction (`coarse`)

**What it does**: Fake-resampling by lowering sample rate, creating lo-fi digital artifacts.

**Parameters**: Factor (1 = original, 2 = half rate, 3 = one-third, etc.)

**Basic Example**:
```javascript
$: s("bd sd [~ bd] sd,hh*8").coarse("<1 4 8 16 32>")
```

**Explanation**: Progressively lowers the sample rate, creating aliasing and digital degradation.

**Note**: This effect currently only works in Chromium-based browsers.

**Advanced Example - Rhythmic Sample Rate Reduction**:
```javascript
$: s("hh*16")
  .coarse("<1!4 [4 8]!4 [16 32]!8>")
  .gain(0.7)
```

**Use Cases**:
- Telephone/radio effect
- Vintage sampler emulation
- Glitch transitions
- Experimental textures

---

### 3. Waveshape Distortion (`distort`)

**What it does**: Applies waveshaping distortion to alter the sound's character.

**Parameters**: `amount:postgain:type`
- `amount`: 0-10 typical (higher = more extreme)
- `postgain`: Optional volume control after distortion
- `type`: Optional distortion algorithm (e.g., "diode")

**Basic Example**:
```javascript
$: s("bd sd [~ bd] sd,hh*8").distort("<0 2 3 10:.5>")
```

**Synth Distortion Example**:
```javascript
$: note("d1!8")
  .penv(36).pdecay(.12)
  .decay(.23)
  .distort("8:.4")
```

**Specific Distortion Type**:
```javascript
$: s("bd:4*4").bank("tr808")
  .distort("3:0.5:diode")
```

**Advanced Example - From Community (disto.js)**:
```javascript
$: n("<[[0,4]]*3>")
  .scale("c#2:minor").s("supersaw")
  .transpose("<0 2 [3 1]>/8")
  .lpa(0).lpe(10).lpd(0.2).lpr(1)
  .lpf("<[10 10 100]>")
  .dist("8:0.18")
```

**Use Cases**:
- Heavy bass distortion
- Aggressive lead synths
- Industrial drums
- Experimental noise textures

---

## Sample Chopping and Stuttering

### 4. Break Chopping (`chop`, `slice`, `splice`)

**What they do**:
- `chop(n)`: Chops sample into n pieces (order not specified)
- `slice(n, pattern)`: Chops into n pieces, plays specific slices by index
- `splice(n, pattern)`: Like slice, but adjusts speed to event duration

**Basic Chop Example**:
```javascript
samples('github:yaxu/clean-breaks')

setcpm(120/4)
$: s("amen/4").fit().chop(32)
```

**Chop with Randomization**:
```javascript
samples('github:yaxu/clean-breaks')

setcpm(120/4)
$: s("amen/4").fit().chop(16).cut(1)
  .sometimesBy(.5, ply("2"))
  .sometimesBy(.25, mul(speed("-1")))
```

**Explanation**: 
- Fits the break into cycles
- Chops into 16 pieces
- `.cut(1)` prevents overlapping
- 50% chance of doubling playback speed
- 25% chance of reversing

**Slice with Pattern Control**:
```javascript
samples('github:yaxu/clean-breaks')

setcpm(120/4)
$: s("amen/4").fit()
  .slice(8, "<0 1 2 3 4*2 5 6 [6 7]>*2")
  .cut(1).rarely(ply("2"))
```

**Splice with Speed Adjustment**:
```javascript
samples('github:yaxu/clean-breaks')

setcpm(120/4)
$: s("amen")
  .splice(8, "<0 1 2 3 4*2 5 6 [6 7]>*2")
  .cut(1).rarely(ply("2"))
```

**Note**: `splice` automatically fits the sample, no need for `.fit()`

### 5. Arranging Multiple Chop and Stutter Effects

When building structured longer loops, arrange effect patterns over a sample.

```javascript
samples('github:yaxu/clean-breaks')

setcpm(120/4)

// Set Sample Here
const sample = "amen/4"

// Effects Patterns
const chop32 = s(sample).fit().chop(32)

const chopRand16 = s(sample).fit().chop(16).cut(1)
  .sometimesBy(.5, ply("2"))
  .sometimesBy(.25, mul(speed("-1")))

const patternControl = s(sample).fit()
  .slice(8, "<0 1 2 3 4*2 5 6 [6 7]>*2")
  .cut(1).rarely(ply("2"))

const speedAdjust = s(sample)
  .splice(8, "<0 1 2 3 4*2 5 6 [6 7]>*2")
  .cut(1).rarely(ply("2"))

// Output a 20 bar loop arrangement with scope visualizer
$: arrange(
  [8, chop32],
  [4, chopRand16],
  [4, patternControl],
  [4, speedAdjust]
)._scope()
```

**Use Cases**:
- Breakcore/jungle breaks
- Glitch hop stutters
- IDM sample manipulation
- Drum & bass resequencing

---

### 5. Sample Rushing (`run`)

**What it does**: Rushes through a sample bank sequentially.

**Basic Example**:
```javascript
samples('bubo:fox')

$: n(run(8)).s("ftabla")
```

**With Timing Adjustment**:
```javascript
samples('bubo:fox')

$: n(run(8)).s("ftabla").early(2/8)
```

**With Randomization**:
```javascript
samples('bubo:fox')

$: n(run(8)).s("ftabla").early(2/8)
  .sometimes(mul(speed("1.5")))
```

**Use Cases**:
- Rapid sample cycling
- Tabla/percussion rushes
- Glitch transitions
- Sound design textures

---

### 6. Wavetable Synthesis (Looped Samples)

**What it does**: Loops tiny portions of samples to create synth-like tones.

**Basic Wavetable from Drum Sample**:
```javascript
$: note("<c eb g f>").s("bd")
  .loop(1).loopEnd(.05)
  .gain(.2)
```

**Explanation**: Loops the first 5% of a bass drum to create a synth tone.

**Dedicated Wavetable Samples**:
```javascript
samples('github:bubobubobubobubo/dough-waveforms')

$: note("c eb g bb").s("wt_dbass").clip(2).fast(3)
```

**Note**: Samples starting with `wt_` are automatically looped.

**Running Through Wavetables**:
```javascript
samples('github:bubobubobubobubo/dough-waveforms')

$: note("c2*8").s("wt_dbass").n(run(8)).fast(2)
```

**With Filter Envelope and a beat**:
```javascript
samples('github:bubobubobubobubo/dough-waveforms')

setcpm(140/4)

$: s("- bd - - bd - - bd - - bd -").bank("RolandTR909")
  .lpf(130).clip(.22)
  .gain(.3)

$: note("[c2,eb2]*8").s("wt_dbass").n(run(8))
  .lpf(perlin.range(100,1000).slow(8))
  .lpenv(-3).lpa(.1).room(.5).fast(2)
```

**Use Cases**:
- Experimental synth tones
- Bass design from drums
- Glitchy textures
- Evolving pads

---

## Glitch Techniques

### 7. Tape Warble (Pitch Modulation)

**What it does**: Emulates analog tape warble/wow & flutter.

**Example**:
```javascript
$: note("<c4 bb f eb>*8")
  .add(note(perlin.range(0,.5)))
  .clip(2).s("gm_electric_guitar_clean")
```

**Explanation**: Uses Perlin noise to add smooth random pitch variation (0 to 0.5 semitones).

**Use Cases**:
- Lo-fi tape effects
- Vintage emulation
- Experimental pitch drift
- Ambient textures

---

### 8. Stutter Effects (Using Conditional Modifiers)

**Using `ply()` for Stuttering**:
```javascript
$: s("bd sd hh cp")
  .sometimesBy(.3, ply("2"))
```

**Explanation**: 30% chance of playing each event twice in quick succession.

**Controlled Stutter Pattern**:
```javascript
$: s("bd sd hh cp")
  .when("0 0 1 0", x=>x.ply("<2 3 4>"))
```

**Explanation**: Only stutters on the third beat, with varying repetitions.

**Extreme Stutter with `fast()`**:
```javascript
$: s("bd ~ sd ~")
  .lastOf(4, x=>x.fast(8))
```

**Explanation**: Every 4th cycle, speeds up the pattern 8x creating a rapid stutter.

**Use Cases**:
- Glitch hop stutters
- Breakcore fills
- Transition effects
- Rhythmic variation

---

### 9. Reset and Restart (Pattern Interruption)

**Using `reset()`**:
```javascript
$: s("[<bd lt> sd]*2, hh*8")
  .reset("<x@3 x(5,8)>")
```

**Explanation**: Resets pattern to start of current cycle when triggered.

**Using `restart()`**:
```javascript
$: s("[<bd lt> sd]*2, hh*8")
  .restart("<x@3 x(5,8)>")
```

**Explanation**: Restarts pattern from cycle 0 when triggered (more dramatic).

**Use Cases**:
- Glitch interruptions
- Pattern resets
- Build-up breaks
- Live coding transitions

---

### 10. Masking (Selective Silencing)

**Basic Mask**:
```javascript
$: s("hh*16").mask("1 1 1 0")
```

**Gradual Reveal**:
```javascript
$: s("hh*16")
  .mask("<1!1 [1 0]!1 [1 0 0]!1 [1 0 0 0]!1>")
```

**Explanation**: Progressively thins out the hi-hat pattern over time.

**Conditional Masking**:
```javascript
$: note("c [eb,g] d [eb,g]")
  .mask("<1 [0 1]>")
```

**Use Cases**:
- Gating effects
- Pattern thinning
- Build-ups/breakdowns
- Rhythmic variation

---

## Genre-Specific Examples

### Glitch Hop

**Full Glitch Hop Pattern**:
```javascript
setcpm(85)

const kick = s("bd:4*4")
  .gain("<1 0.8 1 0.9>")
  .distort("2:0.6")

const snare = s("~ sd ~ sd")
  .sometimesBy(0.3, ply("2"))
  .crush("<8 4>")

const hats = s("hh*8")
  .coarse("<1 4 8 1>")
  .gain(0.6)

const bass = note("<c1 eb1 f1 g1>")
  .s("sawtooth")
  .lpf("<400 800>")
  .distort("3:0.5")
  .room(0.2)

$: stack(kick, snare, hats, bass)
```

---

### IDM (Intelligent Dance Music)

**Full IDM Pattern**:
```javascript
setcpm(120)

samples('github:yaxu/clean-breaks')

const breaks = s("amen")
  .splice(16, "<[0 2 4 6] [1 3 5 7] [8 10 12 14] [9 11 13 15]>")
  .cut(1)
  .sometimesBy(0.2, mul(speed("-1")))
  .crush("<16 8 4>")

const melody = note("<[c5 e5 g5] [d5 f5 a5]>")
  .s("sine")
  .add(note(perlin.range(0, 0.3)))
  .lpf(perlin.range(400, 2000).slow(4))
  .room(0.5)

const bass = note("<c2 eb2 f2 g2>")
  .s("sawtooth")
  .lpf(300)
  .distort("4:0.4")

$: stack(breaks, melody, bass)
```

---

### Breakcore

**Full Breakcore Pattern**:
```javascript
setcpm(180)

samples('github:yaxu/clean-breaks')

const fastBreaks = s("amen")
  .splice(32, run(32).fast("<1 2 4 8>"))
  .cut(1)
  .fast("<1 2 [4 2] [8 4]>")
  .crush("<16 8 4 2>")
  .gain(0.8)

const kick = s("bd:5*4")
  .distort("5:0.5")
  .gain(1.2)

const stabs = note("<[c4 eb4 g4]!3 [d4 f4 ab4]>")
  .s("square")
  .lpf("<800 1600>")
  .crush(4)
  .room(0.3)
  .fast("<1 [2 4]>")

$: stack(fastBreaks, kick, stabs)
```

---

### Experimental/Noise

**Full Experimental Pattern**:
```javascript
setcpm(60)

samples('github:bubobubobubobubo/dough-waveforms')

const noise = note(rand.range(20, 80))
  .s("wt_dbass")
  .n(irand(8))
  .coarse(irand(32).segment(8))
  .crush(irand(16).segment(4))
  .lpf(perlin.range(100, 5000))
  .distort(perlin.range(0, 10))
  .pan(rand)
  .gain(0.5)

const texture = s("hh*16")
  .speed(perlin.range(0.5, 2))
  .mask(rand.segment(16))
  .room(0.9)
  .delay(0.5)

const drone = note("<c1 eb1 f#1 ab1>")
  .s("sawtooth")
  .lpf(200)
  .distort("8:0.3")
  .slow(4)

$: stack(noise, texture, drone)
  .room(0.8)
```

---

### Glitch Techno

**Full Glitch Techno Pattern**:
```javascript
setcpm(130)

const kick = s("bd:8*4")
  .gain("<1 0.8 1 0.9>")
  .distort("1:0.8")

const glitchHats = s("hh*16")
  .coarse("<1 1 4 8>")
  .crush("<16 8 4 8>")
  .mask("<1!12 [1 0]!4>")
  .gain(0.5)

const bass = note("<c1!3 [c1 g1]>")
  .s("sawtooth")
  .lpf("<300 400 300 500>")
  .distort("3:0.5")
  .room(0.1)

const stutter = s("sd")
  .at("<0.5 0.75>")
  .ply("<1 [2 3 4]>")
  .crush(4)

$: stack(kick, glitchHats, bass, stutter)
```

---

## Effect Combination Strategies

### Subtle Glitch (Lo-Fi)
```javascript
$: s("bd sd hh cp")
  .coarse(2)
  .crush(12)
  .distort("1:0.8")
```

### Medium Glitch (Experimental)
```javascript
$: s("bd sd hh cp")
  .coarse("<4 8>")
  .crush("<8 4>")
  .distort("<3 5>:0.6")
  .sometimesBy(0.3, ply("2"))
```

### Extreme Glitch (Noise)
```javascript
$: s("bd sd hh cp")
  .coarse("<16 32 [8 24]>")
  .crush("<2 3 4 [1 2]>")
  .distort("<8 10 12>:0.4")
  .sometimesBy(0.5, mul(speed("-1")))
  .mask(rand.segment(8))
```

---

## Glitch Effect Parameters Quick Reference

| Effect | Parameter Range | Sweet Spot | Use Case |
|--------|----------------|------------|----------|
| `crush` | 1-16 | 4-8 | Digital distortion, lo-fi |
| `coarse` | 1-32+ | 4-16 | Sample rate reduction, aliasing |
| `distort` | 0-10+ | 2-5 | Waveshaping, saturation |
| `ply` | 2-8 | 2-4 | Stuttering, repeats |
| `chop` | 8-32 | 16 | Break chopping |
| `slice` | 8-32 | 8-16 | Controlled slicing |

---

## Tips for Glitch Production

### 1. Layer Clean and Glitched
```javascript
const clean = s("bd sd hh cp")
const glitched = s("bd sd hh cp").crush(4).coarse(8)

$: stack(clean.gain(0.7), glitched.gain(0.3))
```

### 2. Use Conditional Glitches
```javascript
$: s("bd sd hh cp")
  .sometimesBy(0.25, x=>x.crush(2).coarse(16))
```

### 3. Automate Effect Intensity
```javascript
$: s("bd*4")
  .crush("<16 12 8 4 2>")
  .slow(8)
```

### 4. Combine with Filters
```javascript
$: s("hh*16")
  .crush(4)
  .lpf("<2000 1000 500>")
```

### 5. Use Randomness Wisely
```javascript
$: s("bd sd hh cp")
  .crush(irand(8).segment(4).add(4))
```

**Explanation**: Random crush values between 4-12, updated every 4 events.

---

## Browser Compatibility Notes

- **`coarse` effect**: Currently only works in Chromium-based browsers (Chrome, Edge, Brave)
- **`crush` effect**: Works in all modern browsers
- **`distort` effect**: Works in all modern browsers

---

## Community Examples

These verified examples come from the [eefano/strudel-songs-collection](https://github.com/eefano/strudel-songs-collection) repository:

### "disto.js" - Distortion Showcase
```javascript
setcps(90/60)

$: n("<[[0,4]]*3>")
  .scale("c#2:minor").s("supersaw")
  .transpose("<0 2 [3 1]>/8")
  .lpa(0).lpe(10).lpd(0.2).lpr(1)
  .lpf("<[10 10 100]>")
  .dist("8:0.18")

$: n("<[[5 ~]*3] 4 4b 3 [1 2 1] 0 [4 5 2] 4 >")
  .scale("c#4:minor")
  .transpose("<0 2 [3 1]>/8")
  .s("supersaw")
  .lpf(500)
  .dist("10:0.12")
  .room(0.2)
  .mask("<0@3 1@4 >/8")

$: "[bd,sd,oh,mt,lt,cr]" .pickOut({
    bd:s("EmuDrumulator_bd").velocity(1).lpf(1000),
    sd:s("EmuDrumulator_sd").velocity(1),
    oh:s("EmuDrumulator_oh").pan(0.6).speed(0.7).velocity(0.2),
    mt:s("EmuDrumulator_mt").velocity(0.6),
    lt:s("EmuDrumulator_lt").velocity(0.6),
    cr:s("SequentialCircuitsDrumtracks_cr").speed(1.3).pan(0.4).velocity(0.5)
  })
  .room(0.9).gain(0.5)
  .mask("<0 1@5 0 1 >/8")
```

---

## Further Resources

### Official Documentation
- [Audio Effects Reference](https://strudel.cc/learn/effects/)
- [Recipes (Sample Chopping)](https://strudel.cc/recipes/recipes/)
- [Conditional Modifiers](https://strudel.cc/learn/conditional-modifiers/)
- [Time Modifiers](https://strudel.cc/learn/time-modifiers/)

### Community Resources
- [Strudel Community Bakery](https://strudel.cc/bakery/) - User-submitted patterns
- [eefano's Song Collection](https://github.com/eefano/strudel-songs-collection) - Verified working examples
- [Strudel Discord](https://discord.com/invite/HGEdXmRkzT) - Live community support

### Video Tutorials
- [Strudel Live Coding #15 - Glitch Effect](https://www.youtube.com/watch?v=5ivEVNZLDQs)
- [Chopping Breaks & Samples in STRUDEL](https://www.youtube.com/watch?v=dcmwqqzJubA)

---

## Summary

Glitch effects in Strudel are achieved through:

1. **Digital Degradation**: `crush`, `coarse`, `distort`
2. **Sample Manipulation**: `chop`, `slice`, `splice`, `run`
3. **Pattern Interruption**: `reset`, `restart`, `mask`
4. **Conditional Processing**: `sometimesBy`, `when`, `ply`
5. **Modulation**: `perlin`, `rand`, `irand`

Combine these techniques with proper gain staging, filtering, and reverb to create professional glitch productions across genres from lo-fi hip-hop to extreme breakcore.
