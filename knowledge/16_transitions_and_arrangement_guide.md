# Transitions and Arrangement Guide for Strudel

**Research Date**: 2025-12-23  
**Purpose**: Comprehensive guide to creating smooth, professional transitions between sections in Strudel  
**Sources**: Tidal Cycles transitions, EDM production techniques, community practices

---

## Overview

Transitions are the glue that holds your arrangement together. They:
- **Create anticipation** for upcoming sections
- **Build or release energy** to manage track dynamics
- **Guide the listener** smoothly between musical ideas
- **Add professional polish** to arrangements

This guide covers both **Strudel/Tidal-specific transition functions** and **production techniques** that can be implemented in Strudel.

---

## Part 1: Strudel Transition Techniques

### 1. Using `arrange()` with Transition Patterns

**Concept**: Create dedicated transition patterns to insert between sections.

**Basic Example**:
```javascript
setcpm(130/4)

// Main sections
const intro = s("bd*4").gain(0.8)
const verse = stack(
  s("bd*4"),
  s("hh*8").gain(0.3),
  note("c2*4").s("sawtooth").lpf(400).gain(0.6)
)
const chorus = stack(
  s("bd*4"),
  s("hh*8, ~ oh ~ oh").gain("0.3 0.4"),
  note("c2!3 [c2 eb2]").s("sawtooth").lpf(600).gain(0.7),
  note("c4 e4 g4 b4").s("square").lpf(2000).gain(0.5)
)

// Transition patterns
const buildupFill = stack(
  s("bd*4"),
  s("sd*8").gain("0.4!3 0.6"),  // Accelerating snare roll
  s("white").lpf(sine.range(1000, 8000).slow(2)).gain(sine.range(0.2, 0.6).slow(2))  // Riser
)

const breakdownTransition = stack(
  s("~ ~ ~ cr"),  // Crash on beat 4
  note("c4*8").s("sine").gain(sine.range(0.5, 0).slow(1))  // Fade out tone
)

// Arrangement with transitions
$: arrange(
  [8, intro],
  [16, verse],
  [2, buildupFill],      // 2-cycle buildup
  [16, chorus],
  [1, breakdownTransition],  // 1-cycle breakdown
  [8, verse]
)
```

### 2. Pattern Modifiers for Transitions

**Using `lastOf()` for Final Bar Changes**:
```javascript
const verse = stack(
  s("bd*4"),
  s("hh*8").gain(0.3),
  s("~ cp ~ cp")
).lastOf(8, x => stack(
  x,
  s("sd*16").gain("0.3!3 0.5")  // Add snare roll in last cycle of 8
))

$: arrange(
  [16, verse],  // Last 2 cycles (of 16) will have snare roll
  [16, chorus]
)
```

**Using `firstOf()` for Intro Effects**:
```javascript
const chorus = stack(
  s("bd*4"),
  note("c4 e4 g4 b4").s("square").lpf(2000).gain(0.5)
).firstOf(16, x => stack(
  x,
  s("cr").gain(0.8)  // Crash on first cycle only
))

$: chorus
```

**Using `slow()` for Gradual Introduction**:
```javascript
// Gradually speed up over 8 cycles
const accel = s("bd*4")
  .slow("8 7 6 5 4 3 2 1")

$: accel.slow(8)
```

### 3. Crossfading with `cat()` and `stack()`

**Sequential Crossfade**:
```javascript
// Fade out first pattern while fading in second
const crossfade = cat(
  verse.gain(1),
  verse.gain(0.75).layer(chorus.gain(0.25)),
  verse.gain(0.5).layer(chorus.gain(0.5)),
  verse.gain(0.25).layer(chorus.gain(0.75)),
  chorus.gain(1)
)

$: crossfade
```

**Using `fadeIn()` and `fadeOut()`** (Tidal functions, check if available in Strudel):
```javascript
// Fade out over 4 cycles
const fadeOutVerse = verse.segment(32, (x, i) => 
  x.gain(1 - (i / 32))
)

// Fade in over 4 cycles
const fadeInChorus = chorus.segment(32, (x, i) => 
  x.gain(i / 32)
)

$: cat(
  verse.slow(12),
  fadeOutVerse.slow(4),
  fadeInChorus.slow(4),
  chorus.slow(12)
)
```

### 4. Filter Sweeps with Automation

**High-Pass Buildup** (Classic EDM transition):
```javascript
setcpm(130/4)

const verse = stack(
  s("bd*4"),
  s("hh*8").gain(0.3),
  note("c2*4").s("sawtooth").lpf(400).gain(0.6)
)

// Last 4 cycles: apply rising high-pass filter
const buildupVerse = verse
  .hpf(sine.range(20, 8000).slow(4))  // 4-cycle sweep

const chorus = stack(
  s("bd*4"),
  s("hh*8, ~ oh ~ oh"),
  note("c2!3 [c2 eb2]").s("sawtooth").lpf(600).gain(0.7),
  note("c4 e4 g4 b4").s("square").lpf(2000).gain(0.5)
)

$: arrange(
  [12, verse],
  [4, buildupVerse],  // Filter sweep over last 4 cycles
  [16, chorus]
)
```

**Low-Pass Breakdown**:
```javascript
// Transition from chorus to breakdown
const chorusToBreakdown = chorus
  .lpf(sine.range(12000, 400).slow(4))  // Close filter over 4 cycles
  .gain(sine.range(1, 0.5).slow(4))     // Reduce volume

const breakdown = note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("sine")
  .attack(1)
  .release(2)
  .room(0.9)
  .gain(0.4)

$: arrange(
  [16, chorus],
  [4, chorusToBreakdown],
  [8, breakdown.slow(2)]
)
```

### 5. Silence and Dropouts

**Full Silence Before Drop**:
```javascript
const buildup = stack(
  s("bd*4"),
  s("sd*8").gain("0.4!3 0.6"),
  s("white").lpf(sine.range(1000, 12000).slow(4)).gain(sine.range(0.2, 0.7).slow(4))
)

const silence = s("~")  // One cycle of silence

const drop = stack(
  s("bd*4").gain(0.9),
  s("hh*8, ~ oh ~ oh"),
  note("c2*4").s("sawtooth").lpf(600).gain(0.7),
  note("c4 e4 g4 b4").s("square").lpf(2000).gain(0.5)
)

$: arrange(
  [4, buildup],
  [1, silence],  // 1 cycle of silence
  [16, drop]
)
```

**Kick Removal** (Last beat before drop):
```javascript
const buildup = s("bd*4")
  .mask("t t t ~")  // Remove last kick
  .layer(
    s("sd*16").gain("0.3!3 0.5"),
    s("white").lpf(sine.range(2000, 12000).slow(2)).gain(sine.range(0.3, 0.7).slow(2))
  )

$: buildup
```

**Dropout with Reverb Tail**:
```javascript
const verseEnd = verse
  .lastOf(4, x => 
    x.room(0.9).roomsize(8).gain(sine.range(1, 0).slow(1))  // Fade out with reverb
  )

$: arrange(
  [12, verse],
  [4, verseEnd],
  [16, chorus]
)
```

### 6. Using `pick()` and `pickRestart()` for Section Control

**Manual Section Switching**:
```javascript
const sections = {
  intro: s("bd*4").gain(0.8),
  verse: stack(
    s("bd*4"),
    s("hh*8").gain(0.3),
    note("c2*4").s("sawtooth").lpf(400).gain(0.6)
  ),
  buildup: stack(
    s("bd*4"),
    s("sd*16").gain("0.4!3 0.6"),
    s("white").lpf(sine.range(1000, 12000).slow(4)).gain(sine.range(0.2, 0.7).slow(4))
  ),
  chorus: stack(
    s("bd*4"),
    s("hh*8, ~ oh ~ oh"),
    note("c2!3 [c2 eb2]").s("sawtooth").lpf(600).gain(0.7),
    note("c4 e4 g4 b4").s("square").lpf(2000).gain(0.5)
  )
}

// Use pick() to select sections
$: pick("intro verse buildup chorus", sections)
```

**Using `pickRestart()` for Clean Section Changes**:
```javascript
// Restart pattern timing on section change
$: pickRestart("<intro*8 verse*16 buildup*4 chorus*16>", sections)
```

---

## Part 2: Production Techniques in Strudel

### 1. Drum Fills

**Classic Snare Roll** (Accelerating):
```javascript
const snareRoll = cat(
  s("sd*4").gain(0.4),   // Quarter notes (1 cycle)
  s("sd*8").gain(0.45),  // Eighth notes (1 cycle)
  s("sd*16").gain("0.4!3 0.6")  // Sixteenth notes with accent (1 cycle)
)

$: snareRoll.slow(3)
```

**Tom Fill**:
```javascript
const tomFill = s("lt ht mt lt ht mt lt [ht mt]")
  .gain("0.5 0.6 0.7 0.5 0.6 0.7 0.5 [0.6 0.8]")
  .room(0.3)

$: tomFill
```

**Layered Fill** (Snare + Toms + Cymbals):
```javascript
const complexFill = stack(
  s("sd*8").gain("0.4!3 0.5"),
  s("lt ~ ht ~ mt ~ ht ~").gain(0.6),
  s("~ ~ ~ [~ cr]").gain(0.7)  // Crash on last beat
)

$: complexFill
```

**Euclidean Fill** (Polyrhythmic):
```javascript
const euclideanFill = stack(
  s("sd").struct("t(13,16)").gain(0.5),
  s("ht").struct("t(7,16)").gain(0.6),
  s("lt").struct("t(5,16)").gain(0.6)
)

$: euclideanFill
```

### 2. Risers and Sweeps

**White Noise Riser** (Classic buildup):
```javascript
const noiseRiser = s("white")
  .lpf(sine.range(400, 12000).slow(8))  // 8-cycle sweep
  .hpf(sine.range(100, 4000).slow(8))   // Band-pass effect
  .gain(sine.range(0.1, 0.7).slow(8))   // Rising volume
  .room(0.5)

$: noiseRiser
```

**Pitched Riser** (Synth):
```javascript
const pitchedRiser = note(sine.range(36, 60).slow(8))  // 2 octave rise
  .s("sawtooth")
  .lpf(sine.range(800, 4000).slow(8))
  .gain(sine.range(0.2, 0.6).slow(8))
  .room(0.6)

$: pitchedRiser
```

**Layered Riser** (White noise + Synth + Cymbal):
```javascript
const megaRiser = stack(
  // White noise layer
  s("white")
    .lpf(sine.range(1000, 12000).slow(8))
    .hpf(sine.range(200, 4000).slow(8))
    .gain(sine.range(0.15, 0.5).slow(8)),
  
  // Synth layer
  note(sine.range(48, 72).slow(8))
    .s("sawtooth")
    .lpf(sine.range(1000, 5000).slow(8))
    .gain(sine.range(0.2, 0.4).slow(8)),
  
  // Reverse cymbal layer
  s("cr")
    .speed(-1)
    .begin(0.5)
    .gain(sine.range(0.2, 0.7).slow(8))
).room(0.7)

$: megaRiser
```

**Rhythmic Riser** (Plucked pattern rising):
```javascript
const rhythmicRiser = note("c4 e4 g4 b4")
  .s("square")
  .add(sine.range(0, 12).slow(8))  // Pitch rises over 8 cycles
  .attack(0.001)
  .decay(0.1)
  .sustain(0)
  .lpf(2000)
  .gain(sine.range(0.3, 0.6).slow(8))

$: rhythmicRiser.fast(4)
```

### 3. Reverse Cymbals

**Basic Reverse Cymbal**:
```javascript
const reverseCymbal = s("cr")
  .speed(-1)        // Reverse playback
  .begin(0.5)       // Start halfway through
  .gain(0.6)
  .room(0.5)

$: reverseCymbal
```

**Reverse Cymbal with Filter**:
```javascript
const filteredReverse = s("cr")
  .speed(-1)
  .begin(0.5)
  .lpf(sine.range(2000, 12000).slow(2))  // Opening filter
  .gain(sine.range(0.3, 0.7).slow(2))
  .room(0.6)

$: filteredReverse.slow(2)
```

**Layered Reverse Effects**:
```javascript
const reverseStack = stack(
  // Reverse cymbal
  s("cr").speed(-1).begin(0.5).gain(0.6),
  // Reverse snare
  s("sd").speed(-1).begin(0.7).gain(0.4).delay(0.25),
  // Reverse white noise
  s("white").speed(-1).begin(0.6)
    .lpf(sine.range(1000, 8000).slow(2))
    .gain(sine.range(0.2, 0.5).slow(2))
).room(0.7)

$: reverseStack.slow(2)
```

### 4. Impacts

**Layered Impact** (Sub + Mid + High):
```javascript
const impact = stack(
  // Sub layer (low boom)
  note("c1").s("sine").decay(0.3).sustain(0).lpf(150).gain(0.9),
  // Mid layer (punch)
  s("bd:8").gain(0.8).distort(1),
  // High layer (crash)
  s("cr").gain(0.7).hpf(4000)
)

$: impact
```

**Impact with Reverse Reverb**:
```javascript
// This would typically be done in a DAW, but we can simulate:
const impactWithReverb = stack(
  // Reverse cymbal leading in
  s("cr").speed(-1).begin(0.5).room(0.8).early(0.5),
  // Main impact
  stack(
    note("c1").s("sine").decay(0.3).sustain(0).lpf(150).gain(0.9),
    s("bd:8").gain(0.8),
    s("cr").gain(0.7)
  )
)

$: impactWithReverb
```

### 5. Downlifters

**Pitch Drop**:
```javascript
const downlifter = note(sine.range(60, 36).slow(4))  // Drop 2 octaves
  .s("sine")
  .lpf(sine.range(2000, 400).slow(4))  // Closing filter
  .gain(sine.range(0.5, 0.2).slow(4))
  .distort(1.5)  // Add harmonics

$: downlifter
```

**Reverse Impact Downlifter**:
```javascript
const reverseDownlifter = s("cr")
  .speed(-1)
  .begin(0)
  .end(0.5)
  .lpf(sine.range(12000, 800).slow(2))
  .gain(sine.range(0.6, 0.2).slow(2))

$: reverseDownlifter.slow(2)
```

### 6. Volume Automation

**Crescendo** (Rising volume):
```javascript
const crescendo = verse
  .gain(sine.range(0.7, 1).slow(8))  // Gradual volume increase

$: crescendo
```

**Pre-Drop Dip**:
```javascript
const buildupWithDip = buildup
  .lastOf(4, x => 
    x.gain("1 1 1 0.5")  // Dip on last beat
  )

$: buildupWithDip
```

**Logarithmic Volume Curve** (More natural):
```javascript
// Simulate logarithmic curve with stepped values
const logCrescendo = verse
  .gain("0.5 0.6 0.7 0.75 0.8 0.85 0.9 0.95")

$: logCrescendo.slow(8)
```

### 7. Vocal Risers

**Vocal Sample Riser**:
```javascript
// Using a vocal sample (if available)
const vocalRiser = s("vocal:2*8")
  .add(sine.range(0, 12).slow(4))  // Pitch rises
  .lpf(sine.range(800, 4000).slow(4))
  .gain(sine.range(0.3, 0.6).slow(4))
  .room(0.4)

$: vocalRiser
```

**Formant-Shifted Riser** (Simulated):
```javascript
// Simulate formant shift with layered pitches
const formantRiser = note("c4*8")
  .s("sine")
  .layer(
    x => x.add(0),
    x => x.add(7),   // Fifth above
    x => x.add(12)   // Octave above
  )
  .add(sine.range(0, 12).slow(4))
  .lpf(sine.range(1000, 5000).slow(4))
  .gain(sine.range(0.2, 0.5).slow(4))
  .room(0.5)

$: formantRiser
```

### 8. Glitch Transitions

**Stutter Effect**:
```javascript
const stutter = verse
  .lastOf(4, x => 
    x.ply(4)  // Repeat 4x in last cycle
  )

$: stutter
```

**Glitchy Buildup**:
```javascript
const glitchBuild = stack(
  s("bd*4").sometimes(ply(2)),
  s("hh*8").crush("<8 6 4 2>"),  // Decreasing bit depth
  note("c4*8").s("square")
    .coarse("<1 2 4 8>")  // Decreasing sample rate
    .gain(0.5)
)

$: glitchBuild
```

**Reset/Restart Glitch**:
```javascript
const resetGlitch = verse
  .sometimes(reset())  // Random resets create glitchy feel

$: resetGlitch
```

### 9. Harmonic Transitions

**Rising Chord Progression**:
```javascript
const risingChords = note("<[c3,e3,g3] [d3,f3,a3] [e3,g3,b3] [f3,a3,c4]>")
  .s("sawtooth")
  .attack(0.5)
  .release(1)
  .lpf(2000)
  .room(0.7)
  .gain(sine.range(0.3, 0.6).slow(4))

$: risingChords
```

**Arpeggio Buildup**:
```javascript
const arpBuild = note("<[c3,e3,g3] [d3,f3,a3] [e3,g3,b3] [g3,b3,d4]>")
  .arp("up")
  .s("square")
  .attack(0.001)
  .decay(0.1)
  .sustain(0)
  .lpf(3000)
  .delay(0.25)
  .gain(sine.range(0.4, 0.7).slow(4))

$: arpBuild.fast(4)
```

---

## Part 3: Complete Transition Examples

### Example 1: Classic EDM Buildup to Drop

```javascript
setcpm(128/4)

// Main sections
const verse = stack(
  s("bd*4"),
  s("hh*8").gain(0.3),
  s("~ cp ~ cp").gain(0.5),
  note("c2*4").s("sawtooth").lpf(400).gain(0.6)
)

const drop = stack(
  s("bd*4").gain(0.9),
  s("hh*8, ~ oh ~ oh").gain("0.3 0.4"),
  s("~ cp ~ cp").gain(0.6),
  note("c2!3 [c2 eb2]").s("sawtooth").lpf(600).gain(0.7),
  note("c4 e4 g4 b4").s("square").lpf(2500).gain(0.5)
)

// 4-cycle buildup transition
const buildup = stack(
  // Drums with snare roll
  s("bd*4"),
  s("sd*16").gain("0.3!3 0.5"),
  
  // Layered riser
  s("white")
    .lpf(sine.range(1000, 12000).slow(4))
    .hpf(sine.range(200, 4000).slow(4))
    .gain(sine.range(0.15, 0.6).slow(4)),
  
  note(sine.range(48, 72).slow(4))
    .s("sawtooth")
    .lpf(sine.range(1000, 5000).slow(4))
    .gain(sine.range(0.2, 0.4).slow(4)),
  
  // Reverse cymbal
  s("cr")
    .speed(-1)
    .begin(0.5)
    .gain(sine.range(0.2, 0.7).slow(4))
  
).room(0.5)
  .hpf(sine.range(30, 300).slow(4))  // Rising high-pass on everything

// Silence before drop
const silence = s("~")

// Arrangement
$: arrange(
  [16, verse],
  [4, buildup],
  [1, silence],
  [16, drop]
)

// Master compression
all(x => x
  .compressor("-12:4:5:0.01:0.15")
  .postgain(1.2)
)
```

### Example 2: Breakdown Transition

```javascript
setcpm(130/4)

const chorus = stack(
  s("bd*4").gain(0.9),
  s("hh*8, ~ oh ~ oh"),
  note("c2!3 [c2 eb2]").s("sawtooth").lpf(600).gain(0.7),
  note("c4 e4 g4 b4").s("square").lpf(2500).gain(0.5)
)

const breakdown = stack(
  note("<[c3,e3,g3] [d3,f3,a3]>")
    .s("sine,square")
    .attack(1)
    .release(2)
    .room(0.9)
    .gain(0.4),
  
  note("c4 e4 g4 b4")
    .s("square")
    .attack(0.001)
    .decay(0.15)
    .sustain(0)
    .delay(0.375)
    .room(0.6)
    .gain(0.5)
)

// 4-cycle transition to breakdown
const toBreakdown = chorus
  .lpf(sine.range(12000, 600).slow(4))  // Closing filter
  .gain(sine.range(1, 0.5).slow(4))     // Reducing volume
  .lastOf(4, x => stack(
    x,
    // Add downlifter
    note(sine.range(60, 36).slow(1))
      .s("sine")
      .lpf(sine.range(2000, 400).slow(1))
      .gain(sine.range(0.5, 0.2).slow(1))
      .distort(1.5)
  ))

$: arrange(
  [16, chorus],
  [4, toBreakdown],
  [8, breakdown.slow(2)]
)
```

### Example 3: Section Changes with Fills

```javascript
setcpm(132/4)

const intro = s("bd*4").gain(0.8)

const verse = stack(
  s("bd*4"),
  s("hh*8").gain(0.3),
  note("c2*4").s("sawtooth").lpf(400).gain(0.6)
)

const chorus = stack(
  s("bd*4"),
  s("hh*8, ~ oh ~ oh"),
  note("c2!3 [c2 eb2]").s("sawtooth").lpf(600).gain(0.7),
  note("c4 e4 g4 b4").s("square").lpf(2500).gain(0.5)
)

// Transition fills
const introFill = stack(
  s("bd*4"),
  s("sd*8").gain("0.4!3 0.5"),
  s("~ ~ ~ cr").gain(0.7)
)

const verseFill = stack(
  s("bd*4"),
  s("lt ht mt lt ht mt lt [ht mt]").gain("0.5 0.6 0.7 0.5 0.6 0.7 0.5 [0.6 0.8]"),
  s("~ ~ ~ [~ cr]").gain(0.7)
)

const chorusFill = stack(
  s("bd*4"),
  s("sd*16").gain("0.4!3 0.6"),
  s("white").lpf(sine.range(2000, 10000).slow(2)).gain(sine.range(0.3, 0.6).slow(2))
)

// Arrangement
$: arrange(
  [7, intro],
  [1, introFill],
  [15, verse],
  [1, verseFill],
  [15, chorus],
  [1, chorusFill],
  [8, verse]
)
```

### Example 4: Using Your Example Code Enhanced

```javascript
// {"name": "Wavey Base Enhanced", "tags": ["trance", "transitions", "professional"], "tempo": 130}

samples('github:bubobubobubobubo/dough-waveforms')

setcpm(130/4)

// Drum Set
const bd4 = s("bd:1*4").lpf(300).gain(.7)
const hh8 = s("<- hh>*8").gain(.13).sometimesBy(.05, ply(3))
const sd2 = s("sd - sd -").gain(.3)

// Droning Orbiting Bass
const droneBass = note("c2*8").s("wt_dbass").n(run(8))
  .lpf(perlin.range(100,1000).slow(8))
  .lpenv(sine.range(-3.0, 4.0).slow(16)).lpa(.1).room(.5).fast(2)

// Drone Hi (matching bass)
const droneHi = note("c4*8").s("sawtooth")
  .n(run(8))
  .lpf(900).lpenv(sine.range(-3.0, 4.0).slow(16)).lpa(.2)
  .room(.9).size(20)
  .gain(.1)

// === TRANSITION ELEMENTS ===

// Snare roll buildup (2 cycles)
const snareRoll = stack(
  bd4,
  s("sd*16").gain("0.3!3 0.5"),
  hh8
)

// White noise riser (4 cycles)
const riser = s("white")
  .lpf(sine.range(1000, 12000).slow(4))
  .hpf(sine.range(200, 4000).slow(4))
  .gain(sine.range(0.15, 0.6).slow(4))
  .room(0.5)

// Reverse cymbal (1 cycle)
const reverseCrash = s("cr")
  .speed(-1)
  .begin(0.5)
  .gain(sine.range(0.3, 0.7).slow(1))
  .room(0.6)

// Impact on drop
const dropImpact = stack(
  note("c1").s("sine").decay(0.3).sustain(0).lpf(150).gain(0.9),
  s("bd:1").gain(0.9),
  s("cr").gain(0.7)
)

// Breakdown transition (4 cycles)
const breakdownTrans = stack(
  droneHi,
  note(sine.range(60, 36).slow(4))
    .s("sine")
    .lpf(sine.range(2000, 400).slow(4))
    .gain(sine.range(0.5, 0.2).slow(4))
    .distort(1.5)
).lpf(sine.range(12000, 800).slow(4))

// === PATTERNS ===
const pat = {
  intro: droneBass,
  drive: stack(droneBass, bd4),
  foreshadow: stack(droneBass, bd4, hh8, droneHi),
  buildupSnare: stack(droneBass, snareRoll, droneHi),
  buildupRiser: stack(droneBass, bd4, snareRoll, riser, droneHi)
    .hpf(sine.range(30, 300).slow(4)),  // Rising high-pass
  reverseCrash: stack(droneBass, reverseCrash),
  dropWithImpact: stack(dropImpact, droneBass, bd4, hh8, sd2, droneHi),
  fullOn: stack(droneBass, bd4, hh8, sd2, droneHi),
  breakdownTrans: breakdownTrans,
  fakeSilence: droneHi,
  silence: s("~")
}

// === ARRANGEMENT ===
$: arrange(
  [16, pat.intro],
  [8, pat.drive],
  [14, pat.foreshadow],
  [2, pat.buildupSnare],      // Add snare roll
  [2, pat.buildupRiser],      // Add riser and filter sweep
  [1, pat.reverseCrash],      // Reverse cymbal
  [1, pat.silence],           // Silence before drop
  [1, pat.dropWithImpact],    // Drop with impact
  [15, pat.fullOn],           // Continue drop
  [4, pat.breakdownTrans],    // Transition to breakdown
  [8, pat.fakeSilence]
)

// Master compression
all(x => x
  .compressor("-12:4:5:0.01:0.15")
  .postgain(1.2)
  .clip(0.95)
)
```

---

## Part 4: Transition Timing Guide

### Typical Transition Lengths

| Transition Type | Cycles | Use Case |
|----------------|--------|----------|
| **Drum fill** | 1 | Quick section change |
| **Snare roll** | 1-2 | Build energy before drop |
| **Short riser** | 2-4 | Moderate buildup |
| **Long riser** | 4-8 | Epic buildup (trance, progressive) |
| **Filter sweep** | 4-8 | Gradual energy change |
| **Breakdown** | 4-8 | Transition out of high energy |
| **Silence** | 0.5-1 | Dramatic pause before drop |
| **Crossfade** | 2-4 | Smooth blend between sections |
| **Glitch fill** | 0.5-1 | Quick, chaotic transition |
| **Impact** | 0.25 | Punctuate section start |

### Transition Placement

**Every 4 Cycles** (16 bars):
- Small fills or variations
- Subtle changes to maintain interest

**Every 8 Cycles** (32 bars):
- Medium transitions
- Section changes (verse to chorus)
- Drum fills with some buildup

**Every 16 Cycles** (64 bars):
- Major transitions
- Full buildups to drops
- Epic risers and filter sweeps
- Breakdowns

**Every 32 Cycles** (128 bars):
- Complete song structure changes
- Second drop buildups
- Major energy shifts

---

## Part 5: Transition Combinations

### Low Energy → High Energy

**Combine**:
1. Rising filter sweep (high-pass)
2. Snare roll (last 2 cycles)
3. White noise riser
4. Pitched synth riser
5. Reverse cymbal (last cycle)
6. Silence (last beat)
7. Impact (first beat of new section)

**Example**:
```javascript
const lowToHigh = stack(
  // Filter sweep on existing pattern
  verse.hpf(sine.range(30, 300).slow(8)),
  
  // Snare roll (last 2 cycles)
  s("~!6 [sd*16]").slow(8).gain("0.4!3 0.5"),
  
  // Layered riser
  s("white")
    .lpf(sine.range(1000, 12000).slow(8))
    .gain(sine.range(0.15, 0.6).slow(8)),
  
  note(sine.range(48, 72).slow(8))
    .s("sawtooth")
    .lpf(sine.range(1000, 5000).slow(8))
    .gain(sine.range(0.2, 0.4).slow(8)),
  
  // Reverse cymbal (last cycle)
  s("~!7 cr").slow(8)
    .speed(-1)
    .begin(0.5)
    .gain(0.6)
).room(0.6)

$: lowToHigh
```

### High Energy → Low Energy

**Combine**:
1. Closing filter sweep (low-pass)
2. Volume reduction
3. Downlifter
4. Drum removal
5. Reverb increase

**Example**:
```javascript
const highToLow = chorus
  .lpf(sine.range(12000, 600).slow(4))  // Closing filter
  .gain(sine.range(1, 0.5).slow(4))     // Volume reduction
  .room(sine.range(0.3, 0.9).slow(4))   // Reverb increase
  .lastOf(4, x => stack(
    x,
    // Downlifter
    note(sine.range(60, 36).slow(1))
      .s("sine")
      .lpf(sine.range(2000, 400).slow(1))
      .gain(sine.range(0.5, 0.2).slow(1))
  ))

$: highToLow
```

### Same Energy (Section Change)

**Combine**:
1. Short drum fill (1 cycle)
2. Crash cymbal on downbeat
3. Small filter or gain variation

**Example**:
```javascript
const sameEnergy = stack(
  // Drum fill (last cycle)
  verse.lastOf(8, x => stack(
    x,
    s("lt ht mt lt ht mt lt [ht mt]")
      .gain("0.5 0.6 0.7 0.5 0.6 0.7 0.5 [0.6 0.8]")
  )),
  
  // Crash on new section
  chorus.firstOf(16, x => stack(
    x,
    s("cr").gain(0.7)
  ))
)

$: sameEnergy
```

---

## Part 6: Advanced Techniques

### 1. Dynamic Transitions with `segment()`

**Create custom automation curves**:
```javascript
// Custom fade curve
const customFade = verse.segment(32, (x, i) => {
  const fade = Math.pow(i / 32, 2)  // Exponential curve
  return x.gain(1 - fade)
})

$: customFade.slow(4)
```

### 2. Polyrhythmic Transitions

**Different elements transition at different rates**:
```javascript
const polyTrans = stack(
  // Bass: slow filter sweep (8 cycles)
  droneBass.lpf(sine.range(200, 1000).slow(8)),
  
  // Drums: fast buildup (4 cycles)
  s("bd*4").layer(
    s("sd*16").gain(sine.range(0, 0.6).slow(4))
  ),
  
  // Hi: medium sweep (6 cycles)
  droneHi.lpf(sine.range(900, 3000).slow(6))
)

$: polyTrans
```

### 3. Call and Response Transitions

**One element fades out while another fades in**:
```javascript
const callResponse = stack(
  // Call (fading out)
  verse.gain(sine.range(1, 0).slow(4)),
  
  // Response (fading in)
  chorus.gain(sine.range(0, 1).slow(4))
)

$: callResponse
```

### 4. Tension and Release

**Build maximum tension then release**:
```javascript
const tensionRelease = cat(
  // Build tension (4 cycles)
  verse
    .hpf(sine.range(30, 500).slow(4))
    .gain(sine.range(1, 0.7).slow(4))
    .layer(
      s("sd*16").gain(sine.range(0, 0.6).slow(4)),
      s("white").lpf(sine.range(1000, 12000).slow(4)).gain(sine.range(0.1, 0.6).slow(4))
    ),
  
  // Silence (1 cycle)
  s("~"),
  
  // Release (immediate full energy)
  drop
)

$: tensionRelease.slow(5)
```

---

## Quick Reference

### Essential Transition Elements

**Energy Builders**:
- Snare rolls: `s("sd*16").gain("0.4!3 0.6")`
- White noise risers: `s("white").lpf(sine.range(1000, 12000).slow(4))`
- Pitched risers: `note(sine.range(48, 72).slow(4)).s("sawtooth")`
- Filter sweeps: `.hpf(sine.range(30, 300).slow(4))`
- Volume crescendo: `.gain(sine.range(0.7, 1).slow(4))`

**Energy Reducers**:
- Downlifters: `note(sine.range(60, 36).slow(4)).s("sine")`
- Closing filters: `.lpf(sine.range(12000, 600).slow(4))`
- Volume reduction: `.gain(sine.range(1, 0.5).slow(4))`
- Reverb increase: `.room(sine.range(0.3, 0.9).slow(4))`

**Punctuation**:
- Drum fills: `s("lt ht mt lt ht mt lt [ht mt]")`
- Impacts: `stack(note("c1").s("sine"), s("bd:8"), s("cr"))`
- Reverse cymbals: `s("cr").speed(-1).begin(0.5)`
- Silence: `s("~")`
- Crashes: `s("cr").gain(0.7)`

### Transition Formulas

**Basic Buildup** (4 cycles):
```javascript
stack(
  existingPattern.hpf(sine.range(30, 200).slow(4)),
  s("sd*16").gain("0.4!3 0.5"),
  s("white").lpf(sine.range(1000, 12000).slow(4)).gain(sine.range(0.2, 0.6).slow(4))
)
```

**Epic Buildup** (8 cycles):
```javascript
stack(
  existingPattern.hpf(sine.range(30, 300).slow(8)),
  s("~!6 [sd*16]").slow(8).gain("0.4!3 0.6"),
  s("white").lpf(sine.range(800, 12000).slow(8)).gain(sine.range(0.15, 0.7).slow(8)),
  note(sine.range(48, 72).slow(8)).s("sawtooth").lpf(sine.range(1000, 5000).slow(8)).gain(sine.range(0.2, 0.4).slow(8)),
  s("cr").speed(-1).begin(0.5).gain(sine.range(0.2, 0.7).slow(8))
).room(0.6)
```

**Breakdown Transition** (4 cycles):
```javascript
existingPattern
  .lpf(sine.range(12000, 600).slow(4))
  .gain(sine.range(1, 0.5).slow(4))
  .room(sine.range(0.3, 0.9).slow(4))
```

---

## Summary

Effective transitions in Strudel require:

1. **Planning**: Know where your sections are and what energy level changes you need
2. **Layering**: Combine multiple transition elements (fills + risers + filters)
3. **Timing**: Use appropriate transition lengths (1-8 cycles depending on impact)
4. **Automation**: Use `sine.range()` and `slow()` for smooth parameter changes
5. **Contrast**: Make transitions noticeable but not jarring (unless intentional)
6. **Silence**: Don't underestimate the power of silence before a drop
7. **Experimentation**: Try unconventional combinations for unique results

**Key Functions**:
- `arrange()` - Structure your song with dedicated transition patterns
- `lastOf()` / `firstOf()` - Add elements at section boundaries
- `sine.range()` - Smooth automation curves
- `slow()` - Control transition duration
- `stack()` - Layer transition elements
- `cat()` - Sequential transitions

**Remember**: The best transitions serve the music. Sometimes a simple drum fill is more effective than an elaborate 8-cycle buildup. Let the energy and emotion of your track guide your transition choices.
