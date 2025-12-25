# Mastering and Mixing in Strudel

**Research Date**: 2025-12-23  
**Sources**: Official Strudel documentation, community examples, verified working code

---

## Overview

This guide covers professional mixing and mastering techniques in Strudel, including gain staging, dynamics processing, spatial effects, orbits, ducking, and final output control. While Strudel doesn't have a traditional "master bus limiter," it provides powerful tools for creating polished, professional-sounding mixes.

---

## Signal Chain in Strudel

Understanding the signal flow is essential for effective mixing:

```
1. Sound Generation (samples/oscillators)
   ↓
2. Effects Processing (in order):
   - gain (main volume control)
   - Filters (lpf, hpf, bpf)
   - Distortion/bit crushing
   - compressor (dynamics control)
   - Panning
   - Phaser
   - postgain (makeup gain)
   ↓
3. Signal Routing:
   - Dry output
   - Delay send
   - Reverb send
   ↓
4. Combined into "orbit"
   ↓
5. Ducking effects (orbit level)
   ↓
6. Final output to mixer
   ↓
7. Global effects via all()
```

---

## Core Mixing Tools

### 1. Gain Staging with `gain`

**What it does**: Controls the overall volume of a sound with exponential scaling.

**Parameters**:
- `amount` (number|Pattern): Gain multiplier

**Basic Example**:
```javascript
$: s("hh*8").gain(".4!2 1 .4!2 1 .4 1").fast(2)
```

**Patterned Gain for Dynamics**:
```javascript
$: s("bd*4").gain("<0.8 1 0.9 0.85>")
```

**Gain Hierarchy Example**:
```javascript
// Clear mix hierarchy
const kick = s("bd*4").gain(0.8)      // Loudest
const snare = s("~ sd ~ sd").gain(0.6) // Medium
const hats = s("hh*8").gain(0.3)      // Quieter
const bass = note("c1*4").s("sawtooth").gain(0.5)

$: stack(kick, snare, hats, bass)
```

**Best Practices**:
- Start with all elements at 0.5-0.8 gain
- Adjust relative to each other, not absolute levels
- Leave headroom (don't exceed 1.0 combined)
- Use lower gain for dense patterns

---

### 2. Velocity Control

**What it does**: Sets MIDI-style velocity (0-1), multiplied with gain.

**Parameters**:
- `amount` (number|Pattern): Velocity value between 0 and 1

**Example**:
```javascript
$: s("hh*8")
  .gain(".4!2 1 .4!2 1 .4 1")
  .velocity(".4 1")  // Adds additional dynamic variation
```

**Use Cases**:
- Humanizing drum patterns
- Creating accents and ghost notes
- Simulating MIDI velocity curves

---

### 3. Dynamics Processing with `compressor`

**What it does**: Reduces the volume of loud sounds to create consistent output levels.

**Parameters** (formatted as `threshold:ratio:knee:attack:release`):
- `threshold` (number): dB level where compression starts (negative values, e.g., -20)
- `ratio` (number): Compression amount (e.g., 4 = 4:1 ratio, 20 = 20:1)
- `knee` (number): dB range for smooth compression transition (0-40)
- `attack` (number): Time in seconds to reduce gain by 10dB (0.001-1)
- `release` (number): Time in seconds to increase gain by 10dB (0.01-2)

**Basic Example**:
```javascript
$: s("bd sd [~ bd] sd,hh*8")
  .compressor("-20:20:10:.002:.02")
```

**Breakdown**:
- `-20` = Threshold at -20dB
- `20` = 20:1 ratio (heavy compression)
- `10` = 10dB knee (smooth transition)
- `.002` = 2ms attack (fast)
- `.02` = 20ms release (moderate)

**Gentle Bus Compression**:
```javascript
$: s("bd sd hh cp")
  .compressor("-15:4:5:0.01:0.1")
  .postgain(1.2)
```

**Heavy Limiting**:
```javascript
$: s("bd*4")
  .compressor("-10:20:2:0.001:0.05")
  .postgain(1.5)
```

**Compression Sweet Spots**:

| Use Case | Threshold | Ratio | Knee | Attack | Release |
|----------|-----------|-------|------|--------|----------|
| **Gentle glue** | -15 to -10 | 2:1 to 4:1 | 5-10 | 0.01-0.02 | 0.1-0.2 |
| **Drum control** | -20 to -15 | 4:1 to 8:1 | 5-10 | 0.002-0.01 | 0.02-0.1 |
| **Heavy limiting** | -10 to -5 | 10:1 to 20:1 | 2-5 | 0.001-0.005 | 0.02-0.05 |
| **Pumping effect** | -20 to -10 | 8:1 to 20:1 | 0-5 | 0.001-0.005 | 0.2-0.5 |

---

### 4. Makeup Gain with `postgain`

**What it does**: Applies gain after all effects, perfect for makeup gain after compression.

**Parameters**:
- `amount` (number|Pattern): Gain multiplier

**Example**:
```javascript
$: s("bd sd [~ bd] sd,hh*8")
  .compressor("-20:20:10:.002:.02")
  .postgain(1.5)  // Bring level back up after compression
```

**Typical Workflow**:
```javascript
// 1. Set initial gain
$: s("bd*4").gain(0.8)
  // 2. Apply compression (reduces volume)
  .compressor("-15:4:5:0.01:0.1")
  // 3. Use postgain to compensate
  .postgain(1.3)
```

---

## Orbits: Routing and Grouping

### Understanding Orbits

**Orbits** are Strudel's routing system. Each orbit has its own:
- Delay effect
- Reverb effect
- Ducking capability
- Optional separate audio channel output

**Key Concepts**:
- Default orbit is 1
- Only ONE delay and ONE reverb per orbit
- Patterns in the same orbit share global effects
- Use different orbits to separate processing chains

### Basic Orbit Usage

```javascript
$: stack(
  s("hh*6").delay(.5).delaytime(.25).orbit(1),
  s("~ sd ~ sd").delay(.5).delaytime(.125).orbit(2)
)
```

**Explanation**: Hats and snare have different delay times because they're in different orbits.

### Sending to Multiple Orbits

```javascript
$: s("white").orbit("2,3,4").gain(0.2)
```

**Explanation**: Sends white noise to three orbits simultaneously.

### Orbit Mixing Strategy

```javascript
setcpm(120)

// Orbit 1: Drums (tight, minimal effects)
const drums = stack(
  s("bd*4").gain(0.8),
  s("~ sd ~ sd").gain(0.6),
  s("hh*8").gain(0.3)
).orbit(1).room(0.1)  // Just a touch of reverb

// Orbit 2: Bass (no reverb, some compression)
const bass = note("<c1 eb1 f1 g1>")
  .s("sawtooth")
  .lpf(300)
  .orbit(2)
  .compressor("-20:8:5:0.01:0.1")
  .postgain(1.2)

// Orbit 3: Pads/atmosphere (lots of reverb)
const pads = note("<c3 eb3 g3>")
  .orbit(3)
  .room(0.8)
  .roomsize(5)
  .gain(0.4)

$: stack(drums, bass, pads)
```

---

## Ducking (Sidechain Compression)

### Basic Ducking with `duckorbit`

**What it does**: Reduces the volume of one orbit when another plays (sidechain effect).

**Synonyms**: `duck`

**Parameters**:
- `orbit` (number|Pattern): Target orbit to be ducked

**Simple Example**:
```javascript
// Kick ducks the pad
$: note("c3 eb3 g3 bb3").s("sawtooth").orbit(2).gain(0.5)
$: s("bd*4").duckorbit(2).duckattack(0.2).duckdepth(1)
```

**Ducking Multiple Orbits**:
```javascript
// Kick ducks both pads and hats
$: note("c3 eb3 g3").s("sawtooth").orbit(2).gain(0.5)
$: s("hh*16").orbit(3).gain(0.3)
$: s("bd*4").duckorbit("2:3").duckattack(0.1).duckdepth(0.8)
```

### Ducking Parameters

#### `duckattack` (or `duckatt`)

**What it does**: Controls how quickly the ducked signal returns to normal volume.

**Parameters**:
- `time` (number|Pattern): Attack time in seconds

**Example**:
```javascript
$: note("c3*4").s("sawtooth").orbit(2)
$: s("bd*4").duckorbit(2)
  .duckattack("<0.05 0.1 0.2 0.4>")  // Varying recovery times
  .duckdepth(1)
```

**Different Attack Times per Orbit**:
```javascript
$: note("c3*4").s("sawtooth").orbit(2)
$: s("hh*16").orbit(3)
$: s("bd*4").duckorbit("2:3")
  .duckattack("0.4:0.1")  // Slow for pads, fast for hats
  .duckdepth("1:0.5")
```

#### `duckdepth`

**What it does**: Controls how much the target orbit's volume is reduced.

**Parameters**:
- `depth` (number|Pattern): Amount between 0 (no ducking) and 1 (full mute)

**Example**:
```javascript
$: note("c3*4").s("sawtooth").orbit(2)
$: s("bd*4").duckorbit(2)
  .duckattack(0.1)
  .duckdepth("<1 .9 .6 0>")  // Varying duck intensity
```

**Ducking Sweet Spots**:

| Style | Attack | Depth | Use Case |
|-------|--------|-------|----------|
| **Subtle pump** | 0.2-0.4s | 0.3-0.5 | Gentle breathing effect |
| **EDM sidechain** | 0.05-0.15s | 0.7-1.0 | Classic pumping bass |
| **Quick duck** | 0.01-0.05s | 0.5-0.8 | Tight kick clarity |
| **Slow swell** | 0.5-1.0s | 0.4-0.7 | Atmospheric breathing |

### Complete Ducking Example

```javascript
setcpm(128)

// Orbit 2: Pad that gets ducked
const pad = note("<c3 eb3 g3 bb3>")
  .s("sawtooth")
  .lpf(800)
  .room(0.6)
  .orbit(2)
  .gain(0.6)

// Orbit 3: Bass that gets ducked
const bass = note("<c1 eb1 g1 bb1>")
  .s("sawtooth")
  .lpf(300)
  .orbit(3)
  .gain(0.7)

// Kick that triggers ducking
const kick = s("bd*4")
  .duckorbit("2:3")     // Duck both orbits
  .duckattack("0.3:0.1") // Slow for pad, fast for bass
  .duckdepth("0.8:0.6")  // Heavy on pad, medium on bass
  .gain(0.9)

$: stack(pad, bass, kick)
```

---

## Global Effects with `all()`

### The `all()` Function

**What it does**: Applies effects to ALL patterns globally, like a master bus.

**Syntax**: `all(x => x.effectChain())`

**Basic Example**:
```javascript
$: s("bd sd hh cp")
$: note("c3 eb3 g3").s("sawtooth")

// Apply global reverb to everything
all(x => x.room(0.8))
```

### Global Compression (Mastering)

```javascript
setcpm(120)

$: s("bd*4, ~ sd ~ sd, hh*8")
$: note("<c2 eb2 g2 bb2>").s("sawtooth").lpf(400)

// Master bus compression
all(x => x
  .compressor("-12:4:5:0.01:0.15")
  .postgain(1.2)
)
```

### Global EQ and Limiting

```javascript
// Full mastering chain
all(x => x
  .lpf(18000)                           // High-end rolloff
  .hpf(20)                              // Low-end cleanup
  .compressor("-10:6:5:0.01:0.1")       // Glue compression
  .postgain(1.3)                        // Makeup gain
  .clip(0.95)                           // Soft limiting
)
```

### Global Spatial Effects

```javascript
// Cohesive reverb space
all(x => x
  .room(0.5)
  .roomsize(3)
  .roomlp(8000)  // Darker reverb
)
```

### Combining Global and Local Effects

```javascript
setcpm(130)

// Individual patterns with local effects
$: s("bd*4").gain(0.8).orbit(1)
$: s("~ sd ~ sd").gain(0.6).orbit(1)
$: s("hh*8").gain(0.3).room(0.3).orbit(2)
$: note("<c2 eb2 g2>").s("sawtooth").lpf(400).orbit(3).room(0.6)

// Global mastering
all(x => x
  .compressor("-12:4:5:0.01:0.15")  // Gentle glue
  .postgain(1.2)                    // Bring up level
  .hpf(30)                          // Remove sub-bass rumble
  .lpf(16000)                       // Gentle high rolloff
)
```

---

## Clipping and Soft Limiting

### `clip` Function

**What it does**: Hard clips the signal at a specified level (acts as a limiter).

**Parameters**:
- `level` (number): Maximum amplitude (0-2+)

**Soft Limiting Example**:
```javascript
$: s("bd*4").gain(1.2).clip(0.98)
```

**Explanation**: Allows the signal to go slightly over 1.0, then clips at 0.98 for a soft limiting effect.

**Aggressive Limiting**:
```javascript
$: note("c2*8").s("sawtooth")
  .gain(1.5)
  .clip(0.9)  // Heavy clipping for distortion
```

**Master Bus Limiting**:
```javascript
all(x => x
  .compressor("-10:10:3:0.001:0.05")  // Fast limiting compression
  .postgain(1.4)
  .clip(0.95)  // Final safety limiter
)
```

---

## Spatial Effects

### Delay

**Basic Delay**:
```javascript
$: s("bd bd").delay("<0 .25 .5 1>")
```

**With Time and Feedback** (format: `level:time:feedback`):
```javascript
$: s("bd bd").delay("0.65:0.25:0.9")
```

**Breakdown**:
- `0.65` = 65% wet/dry mix
- `0.25` = 250ms delay time
- `0.9` = 90% feedback (many repeats)

**Patterned Delay**:
```javascript
$: s("bd sd hh cp")
  .delay("0.5:0.125:0.7 0.3:0.25:0.5")
```

**Warning**: Feedback >= 1.0 causes infinite buildup!

### Reverb

**Basic Reverb**:
```javascript
$: s("bd sd [~ bd] sd").room("<0 .2 .4 .6 .8 1>")
```

**With Room Size** (format: `level:size`):
```javascript
$: s("bd sd [~ bd] sd").room("<0.9:1 0.9:4>")
```

**Advanced Reverb Control**:
```javascript
$: s("bd sd hh cp")
  .room(0.7)        // 70% wet
  .roomsize(5)      // Large hall
  .roomlp(8000)     // Dark reverb (low-pass at 8kHz)
  .roomfade(0.8)    // Longer decay
```

**Reverb Parameters**:
- `room` / `roomsize` / `rsize`: Size (0-10)
- `roomfade` / `rfade`: Decay time in seconds
- `roomlp` / `rlp`: Low-pass filter frequency (Hz)
- `roomdim` / `rdim`: Dimension/damping frequency (Hz)

**Impulse Response Reverb**:
```javascript
$: s("bd sd hh cp")
  .room(0.8)
  .ir("<shaker_large:0 shaker_large:2>")  // Use sample as IR
```

---

## Complete Mixing Examples

### Example 1: Minimal Techno Mix

```javascript
setcpm(128)

// Orbit 1: Drums (tight, minimal reverb)
const kick = s("bd:4*4")
  .orbit(1)
  .gain(0.85)
  .compressor("-15:4:5:0.01:0.1")

const snare = s("~ sd ~ sd")
  .orbit(1)
  .gain(0.6)

const hats = s("hh*16")
  .orbit(2)
  .gain(0.25)
  .room(0.3)
  .roomsize(1)

// Orbit 3: Bass (no reverb, heavy compression)
const bass = note("<c1 ~ eb1 ~>")
  .s("sawtooth")
  .lpf(350)
  .orbit(3)
  .gain(0.7)
  .compressor("-18:8:5:0.01:0.08")
  .postgain(1.3)

// Orbit 4: Pads (spacious)
const pads = note("<c3 eb3 g3 bb3>")
  .s("sine")
  .orbit(4)
  .room(0.7)
  .roomsize(4)
  .gain(0.4)

// Kick ducks bass and pads
const kickDuck = kick
  .duckorbit("3:4")
  .duckattack("0.05:0.2")
  .duckdepth("0.6:0.7")

$: stack(kickDuck, snare, hats, bass, pads)

// Master compression and limiting
all(x => x
  .compressor("-10:4:5:0.01:0.15")
  .postgain(1.2)
  .hpf(25)
  .lpf(18000)
  .clip(0.95)
)
```

### Example 2: Ambient Mix with Depth

```javascript
setcpm(60)

// Close/dry layer
const close = note("<c4 e4 g4 b4>")
  .s("sine")
  .orbit(1)
  .room(0.2)
  .gain(0.6)

// Mid-distance layer
const mid = note("<c3 e3 g3>")
  .s("square")
  .orbit(2)
  .room(0.5)
  .roomsize(3)
  .gain(0.5)

// Far/ambient layer
const far = note("<c2 e2 g2>")
  .s("sawtooth")
  .lpf(800)
  .orbit(3)
  .room(0.9)
  .roomsize(8)
  .gain(0.4)

// Texture layer
const texture = s("white")
  .orbit(4)
  .lpf(2000)
  .hpf(500)
  .room(0.7)
  .gain(0.15)

$: stack(close, mid, far, texture)

// Gentle master glue
all(x => x
  .compressor("-18:2:8:0.02:0.3")
  .postgain(1.1)
  .room(0.3)  // Additional global reverb for cohesion
)
```

### Example 3: Aggressive Electronic Mix

```javascript
setcpm(140)

// Heavy kick
const kick = s("bd:8*4")
  .orbit(1)
  .gain(1.0)
  .distort("2:0.7")
  .compressor("-10:10:2:0.001:0.05")
  .postgain(1.2)

// Distorted bass
const bass = note("<c1!3 [c1 g1]>")
  .s("sawtooth")
  .lpf(400)
  .distort("5:0.6")
  .orbit(2)
  .gain(0.8)
  .compressor("-12:8:3:0.01:0.08")
  .postgain(1.4)

// Glitchy hats
const hats = s("hh*16")
  .orbit(3)
  .coarse("<1 4 8>")
  .crush("<16 8 4>")
  .gain(0.4)
  .room(0.3)

// Lead stabs
const lead = note("<c4 eb4 g4>*2")
  .s("square")
  .lpf("<1200 2400>")
  .orbit(4)
  .room(0.4)
  .gain(0.6)

// Aggressive ducking
const kickDuck = kick
  .duckorbit("2:3:4")
  .duckattack("0.05:0.1:0.15")
  .duckdepth("0.9:0.7:0.5")

$: stack(kickDuck, bass, hats, lead)

// Heavy master limiting
all(x => x
  .compressor("-8:10:2:0.001:0.05")
  .postgain(1.5)
  .clip(0.92)
  .lpf(16000)
)
```

---

## Mastering Workflow

### Step 1: Balance (Gain Staging)

```javascript
// Get relative levels right first
const kick = s("bd*4").gain(0.8)
const snare = s("~ sd ~ sd").gain(0.6)
const hats = s("hh*8").gain(0.3)
const bass = note("c1*4").s("sawtooth").gain(0.5)

$: stack(kick, snare, hats, bass)
```

### Step 2: Separate Processing (Orbits)

```javascript
// Route to different orbits for independent processing
const kick = s("bd*4").orbit(1).gain(0.8)
const snare = s("~ sd ~ sd").orbit(1).gain(0.6)
const hats = s("hh*8").orbit(2).gain(0.3).room(0.3)
const bass = note("c1*4").s("sawtooth").orbit(3).gain(0.5).lpf(400)

$: stack(kick, snare, hats, bass)
```

### Step 3: Dynamics (Compression)

```javascript
// Add compression to control dynamics
const kick = s("bd*4").orbit(1).gain(0.8)
  .compressor("-15:4:5:0.01:0.1")
  
const bass = note("c1*4").s("sawtooth").orbit(3).gain(0.5)
  .lpf(400)
  .compressor("-18:6:5:0.01:0.08")
  .postgain(1.2)

$: stack(kick, snare, hats, bass)
```

### Step 4: Space (Reverb/Delay)

```javascript
// Add spatial effects
const hats = s("hh*8").orbit(2).gain(0.3)
  .room(0.4)
  .roomsize(2)
  
const pads = note("c3 eb3 g3").s("sine").orbit(4).gain(0.4)
  .room(0.7)
  .roomsize(5)
  .delay(0.3)

$: stack(kick, snare, hats, bass, pads)
```

### Step 5: Ducking (Clarity)

```javascript
// Make kick cut through
const kickDuck = kick
  .duckorbit("3:4")  // Duck bass and pads
  .duckattack("0.05:0.2")
  .duckdepth("0.7:0.6")

$: stack(kickDuck, snare, hats, bass, pads)
```

### Step 6: Master Processing (Global)

```javascript
// Final polish
all(x => x
  .hpf(30)                          // Remove rumble
  .lpf(18000)                       // Gentle high rolloff
  .compressor("-10:4:5:0.01:0.15")  // Glue compression
  .postgain(1.2)                    // Makeup gain
  .clip(0.95)                       // Safety limiter
)
```

---

## Mixing Tips and Best Practices

### 1. Gain Staging

**Do**:
- ✅ Start with all elements at moderate levels (0.5-0.8)
- ✅ Leave headroom (combined gain < 1.0)
- ✅ Use relative balancing, not absolute levels
- ✅ Lower gain for dense patterns

**Don't**:
- ❌ Mix everything at gain(1.0)
- ❌ Rely on clipping to control levels
- ❌ Ignore the combined output level

### 2. Compression

**Do**:
- ✅ Use gentle ratios (2:1 to 4:1) for glue
- ✅ Use fast attack for transient control
- ✅ Use slow release for pumping effects
- ✅ Always add makeup gain with `postgain`

**Don't**:
- ❌ Over-compress (>6dB reduction usually too much)
- ❌ Use compression on everything
- ❌ Forget to compensate with postgain

### 3. Orbits

**Do**:
- ✅ Group similar elements (drums in orbit 1, bass in orbit 2, etc.)
- ✅ Use separate orbits for different reverb/delay needs
- ✅ Keep effects-heavy elements in their own orbit

**Don't**:
- ❌ Put everything in the same orbit
- ❌ Use too many orbits (3-5 is usually enough)
- ❌ Forget that orbits share global effects

### 4. Ducking

**Do**:
- ✅ Duck pads/bass with kick for clarity
- ✅ Use faster attack for tight ducking
- ✅ Use slower attack for gentle breathing
- ✅ Vary depth by orbit (more on pads, less on bass)

**Don't**:
- ❌ Duck everything (kills dynamics)
- ❌ Use extreme depth on all elements
- ❌ Forget to adjust attack time

### 5. Reverb

**Do**:
- ✅ Use less reverb on low-frequency elements
- ✅ Use `roomlp` to darken reverb tails
- ✅ Match reverb size to genre (small for tight, large for ambient)
- ✅ Layer dry and wet signals

**Don't**:
- ❌ Drown the mix in reverb
- ❌ Use the same reverb settings for everything
- ❌ Forget to filter reverb tails

### 6. Global Effects

**Do**:
- ✅ Use `all()` for master bus processing
- ✅ Apply gentle compression for glue
- ✅ Use high-pass filter to remove rumble
- ✅ Use `clip()` as a safety limiter

**Don't**:
- ❌ Over-process with `all()` (subtle is better)
- ❌ Forget to leave headroom before global compression
- ❌ Use extreme limiting (clip < 0.9)

---

## Loudness and Limiting

### Understanding Loudness in Strudel

Strudel doesn't have traditional LUFS metering, but you can achieve competitive loudness:

**Method 1: Compression + Clipping**
```javascript
all(x => x
  .compressor("-10:6:3:0.001:0.05")  // Heavy compression
  .postgain(1.5)                     // Push level up
  .clip(0.93)                        // Catch peaks
)
```

**Method 2: Multi-Stage Limiting**
```javascript
all(x => x
  .compressor("-15:4:5:0.01:0.1")    // Gentle glue
  .postgain(1.2)
  .compressor("-8:10:2:0.001:0.05")  // Aggressive limiting
  .postgain(1.3)
  .clip(0.95)                        // Final safety
)
```

**Method 3: Saturation + Limiting**
```javascript
all(x => x
  .distort("1:0.8")                  // Subtle saturation
  .compressor("-10:8:3:0.001:0.05")  // Heavy limiting
  .postgain(1.4)
  .clip(0.92)
)
```

### Loudness by Genre

| Genre | Compression | Postgain | Clip Level | Notes |
|-------|-------------|----------|------------|-------|
| **Ambient** | -18:2:8:0.02:0.3 | 1.1 | 0.98 | Gentle, dynamic |
| **Techno** | -12:4:5:0.01:0.15 | 1.2-1.3 | 0.95 | Moderate limiting |
| **EDM** | -10:8:3:0.001:0.05 | 1.4-1.5 | 0.92 | Aggressive limiting |
| **Experimental** | -15:3:6:0.02:0.2 | 1.1-1.2 | 0.97 | Preserve dynamics |
| **Breakcore** | -8:10:2:0.001:0.05 | 1.5-1.6 | 0.90 | Maximum loudness |

---

## Troubleshooting

### Problem: Mix sounds muddy

**Solutions**:
```javascript
// 1. High-pass everything except kick/bass
all(x => x.hpf(100))

// 2. Reduce reverb on low frequencies
$: note("c1*4").s("sawtooth")
  .lpf(400)
  .room(0.1)  // Minimal reverb on bass

// 3. Use ducking for clarity
$: s("bd*4").duckorbit(2).duckdepth(0.7)
```

### Problem: Mix sounds thin

**Solutions**:
```javascript
// 1. Layer bass frequencies
const sub = note("c1*4").s("sine").gain(0.4)
const bass = note("c2*4").s("sawtooth").lpf(400).gain(0.5)

// 2. Add warmth with saturation
all(x => x.distort("1:0.9"))

// 3. Boost low-mids
const bass = note("c1*4").s("sawtooth")
  .bpf(200)  // Boost around 200Hz
  .bpq(2)
```

### Problem: Mix sounds harsh

**Solutions**:
```javascript
// 1. Roll off highs
all(x => x.lpf(14000))

// 2. Darken reverb
$: s("hh*8").room(0.5).roomlp(6000)

// 3. Reduce high-frequency elements
$: s("hh*8").gain(0.2).lpf(8000)
```

### Problem: Mix is too quiet

**Solutions**:
```javascript
// 1. Increase individual gains
const kick = s("bd*4").gain(0.9)
const snare = s("~ sd ~ sd").gain(0.7)

// 2. Add master compression
all(x => x
  .compressor("-12:6:5:0.01:0.1")
  .postgain(1.4)
)

// 3. Use aggressive limiting
all(x => x
  .compressor("-8:10:2:0.001:0.05")
  .postgain(1.5)
  .clip(0.92)
)
```

### Problem: Mix is clipping/distorting

**Solutions**:
```javascript
// 1. Reduce individual gains
const kick = s("bd*4").gain(0.7)
const bass = note("c1*4").s("sawtooth").gain(0.5)

// 2. Use compression before clipping
all(x => x
  .compressor("-15:4:5:0.01:0.1")
  .postgain(1.1)  // Gentle makeup
  .clip(0.98)     // Higher clip threshold
)

// 3. Reduce combined orbit levels
$: stack(
  s("bd*4").orbit(1).gain(0.6),
  s("hh*8").orbit(2).gain(0.3)
)
```

---

## Advanced Techniques

### Parallel Compression

```javascript
const dry = s("bd*4").gain(0.7)
const compressed = s("bd*4")
  .compressor("-20:20:5:0.001:0.05")
  .postgain(2.0)
  .gain(0.3)

$: stack(dry, compressed)  // Blend for punch + sustain
```

### Multi-Band Processing (Workaround)

```javascript
// Split into frequency bands using filters
const lows = note("c1*4").s("sawtooth")
  .lpf(200)
  .orbit(1)
  .compressor("-18:8:5:0.01:0.1")
  .gain(0.6)

const mids = note("c2*4").s("sawtooth")
  .bpf(1000)
  .bpq(1)
  .orbit(2)
  .compressor("-15:4:5:0.01:0.1")
  .gain(0.5)

const highs = note("c3*4").s("sawtooth")
  .hpf(4000)
  .orbit(3)
  .gain(0.4)

$: stack(lows, mids, highs)
```

### Dynamic EQ (Using Patterns)

```javascript
$: note("c2*8").s("sawtooth")
  .lpf(sine.range(400, 1200).slow(4))  // Sweeping filter
  .gain(0.6)
```

### Stereo Width Control

```javascript
// Narrow the stereo field
$: note("c3 eb3 g3").s("sawtooth")
  .pan(sine.range(0.4, 0.6))  // Subtle stereo movement

// Wide stereo with jux
$: note("c3 eb3 g3").s("sawtooth")
  .jux(rev)  // One side reversed
  .gain(0.5)
```

---

## Quick Reference

### Gain Staging
- `gain(amount)` - Main volume control
- `velocity(amount)` - MIDI-style velocity (0-1)
- `postgain(amount)` - Makeup gain after effects

### Dynamics
- `compressor("threshold:ratio:knee:attack:release")` - Dynamics processor
- `clip(level)` - Hard limiting/clipping

### Routing
- `orbit(number)` - Assign to processing group
- `duckorbit(orbit)` - Sidechain ducking
- `duckattack(time)` - Duck recovery time
- `duckdepth(amount)` - Duck intensity (0-1)

### Spatial
- `room(level)` - Reverb amount
- `roomsize(size)` - Reverb size (0-10)
- `roomlp(freq)` - Reverb low-pass filter
- `delay(level)` - Delay amount
- `delayfeedback(amount)` - Delay repeats

### Global
- `all(x => x.effects())` - Apply to all patterns

### Typical Values
- Gain: 0.3-0.9 (leave headroom)
- Compression ratio: 2:1 to 10:1
- Reverb: 0.2-0.8 (genre dependent)
- Clip threshold: 0.9-0.98

---

## Further Resources

### Official Documentation
- [Audio Effects Reference](https://strudel.cc/learn/effects/)
- [Conditional Modifiers](https://strudel.cc/learn/conditional-modifiers/)
- [Creating Patterns (stack, arrange)](https://strudel.cc/learn/factories/)

### Community
- [Tidal Club - Strudel Forum](https://club.tidalcycles.org/c/strudel/)
- [Strudel Discord](https://discord.com/invite/HGEdXmRkzT)

### Related Research Files
- `04_effects_reference.md` - Complete effects documentation
- `07_musical_patterns_library.md` - Genre-specific patterns
- `12_glitch_effects_genre_guide.md` - Experimental sound design

---

## Summary

Mastering in Strudel requires:

1. **Proper gain staging** - Balance elements first
2. **Strategic compression** - Control dynamics without over-processing
3. **Smart orbit routing** - Separate processing chains
4. **Effective ducking** - Create space and clarity
5. **Global processing** - Use `all()` for master bus effects
6. **Gentle limiting** - Use compression + clipping for loudness

Remember: **Strudel doesn't have a traditional master limiter**, but you can achieve professional results by combining compression, postgain, and clipping. The `all()` function is your master bus.

**Start with good balancing, add compression strategically, and use global effects sparingly for the best results.**
