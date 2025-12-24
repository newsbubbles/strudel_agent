# Strudel Synthesizers Reference

**Research Date**: 2025-12-22  
**Updated**: 2025-12-23  
**Source**: https://strudel.cc/learn/synths/

---

## Overview

This guide covers Strudel's synthesis capabilities: waveforms, noise generators, additive synthesis, vibrato, FM synthesis, wavetable synthesis, and the ZZFX synth engine.

**Note**: Filters, ADSR envelopes, and modulation effects are covered in `04_effects_reference.md` as they are part of the audio effects chain, not the oscillator generation stage.

---

## Basic Waveforms

Strudel provides four basic oscillator waveforms:

### Waveform Types

| Waveform | Character | Harmonics | Use Case |
|----------|-----------|-----------|----------|
| `sine` | Smooth, pure tone | None (fundamental only) | Bass, pads, smooth leads, sub-bass |
| `sawtooth` | Bright, harsh, buzzy | All harmonics | Leads, bass, aggressive sounds, pads |
| `square` | Hollow, mid-range, woody | Odd harmonics only | Retro sounds, leads, bass |
| `triangle` | Soft, mellow | Few odd harmonics | Pads, soft leads (default) |

### Using Waveforms

**Basic Usage**:
```javascript
// Specify waveform with sound() or s()
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("<sawtooth square triangle sine>")

// Default is triangle when using note() without sound()
note("c e g")  // Uses triangle waveform

// Short form
note("c2 eb2 f2 g2").s("sawtooth")
```

**Combining Waveforms** (Layering):
```javascript
// Stack multiple waveforms for richer sound
note("c2 eb2 f2 g2")
  .sound("sawtooth,triangle")  // Both play simultaneously

// Layer with different octaves
note("c2 eb2 f2 g2")
  .sound("sine,sine")  // Will need different tuning
  .note(add("0,12"))   // Second voice one octave up
```

**Patterned Waveforms**:
```javascript
// Cycle through waveforms
note("c3*8").s("<sine saw square tri>")

// Random waveform selection
note("c3*8").s("[sine|saw|square|tri]")
```

---

## Noise Generators

Noise generators create non-pitched sounds useful for percussion, texture, and atmosphere.

### Noise Types

| Type | Character | Frequency Spectrum | Use Case |
|------|-----------|-------------------|----------|
| `white` | Hardest, brightest | Full spectrum (equal energy per Hz) | Hi-hats, snares, bright textures |
| `pink` | Medium, balanced | Balanced (1/f falloff, equal per octave) | Natural sounds, softer hats |
| `brown` | Softest, darkest | Lower frequencies emphasized (1/f² falloff) | Wind, rumble, dark textures |

### Using Noise

**As Sound Source**:
```javascript
// Basic noise
sound("<white pink brown>")

// Noise as hi-hats
sound("bd*2, <white pink brown>*8")
  .decay(.04).sustain(0)

// Filtered noise percussion
sound("white*4")
  .lpf(8000)
  .hpf(4000)
  .decay(.08)
  .sustain(0)
```

**Adding Noise to Oscillators**:
```javascript
// Add texture to any oscillator
note("c3").s("sawtooth").noise("<0.1 0.25 0.5>")

// Subtle noise on pads
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("sine")
  .noise(0.05)  // Just a hint of texture

// Heavy noise for grit
note("c2*4").s("square").noise(0.8)
```

**Parameter**:
- `noise(amount)`: Range 0 (no noise) to 1 (full noise)

### Crackle

Subtle noise crackles for vinyl-like texture.

**Usage**:
```javascript
// Basic crackle
s("crackle*4").density("<0.01 0.04 0.2 0.5>".slow(2))

// Layer crackle with music
$: note("c3 eb3 g3").s("piano")
$: s("crackle*8").density(0.02).gain(0.1)
```

**Parameters**:
- `density(amount)`: Controls noise amount (0-1)
  - 0.01-0.05: Subtle vinyl texture
  - 0.1-0.3: Noticeable crackle
  - 0.5+: Heavy static

---

## Additive Synthesis

Control over individual harmonics that compose waveforms. Build custom timbres by specifying the amplitude and phase of each harmonic.

### partials()

Controls the magnitude (amplitude) of each harmonic.

**Concept**: Each element in the array represents a harmonic:
- Index 0 = fundamental frequency
- Index 1 = 2nd harmonic (1 octave up)
- Index 2 = 3rd harmonic (1 octave + perfect 5th up)
- etc.

**Spectral Filtering** (Remove high harmonics):
```javascript
// Gradually remove harmonics from sawtooth
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("sawtooth")
  .partials([1, 1, "<1 0>", "<1 0>", "<1 0>", "<1 0>", "<1 0>"])
```

**Create Custom Waveform**:
```javascript
// Build from scratch with sound("user")
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("user")
  .partials([1, 0, 0.3, 0, 0.1, 0, 0, 0.3])  // Custom harmonic recipe
```

**Algorithmic Harmonics**:
```javascript
// Generate many harmonics programmatically
const numHarmonics = 22
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("saw")
  .partials(new Array(numHarmonics).fill(1))  // All harmonics equal

// Recreate sawtooth wave mathematically
const sawPartials = new Array(100).fill(0).map((_, i) => 1 / (i + 1))
note("c2").sound("user").partials(sawPartials)
```

**Tips**:
- First value (index 0) controls fundamental, not DC offset
- Use 0 to remove a harmonic
- Values > 1 boost harmonics
- Odd harmonics only = square-ish sound
- Even harmonics only = hollow sound

### phases()

Controls the starting phase of each harmonic for depth and complexity.

**Usage**:
```javascript
// Add phase variation for richness
s("saw").seg(16).n(irand(12)).scale("F1:minor")
  .penv(48).panchor(0).pdec(0.05)
  .delay(0.25).room(0.25)
  .partials(randL(200))   // Random amplitudes
  .phases(randL(200))     // Random phases
```

**Effect**:
- Same partials + different phases = different timbre
- Adds "movement" and "depth" to static waveforms
- Useful for creating unique, evolving textures

**Tips**:
- Combine with `partials()` for maximum control
- Random phases create unpredictable, organic sounds
- Systematic phases can create phasing effects

---

## Vibrato

Frequency modulation for pulsating, expressive pitch effects.

### vib() / vibrato() / v()

Applies vibrato to oscillator frequency.

**Format**: `"frequency"` or `"frequency:depth"`

**Parameters**:
- `frequency`: Speed in Hz (cycles per second)
- `depth`: Amount in semitones (optional)

**Basic Vibrato**:
```javascript
// Varying speed
note("a e").vib("<.5 1 2 4 8 16>")

// With depth (12 semitones = 1 octave)
note("a e").vib("<.5 1 2 4 8 16>:12")
```

**Subtle Vibrato** (Musical):
```javascript
// Gentle vibrato for realism
note("c4 e4 g4").s("sine")
  .vib("5:0.5")  // 5Hz, half semitone

// Varying depth
note("c4 e4 g4").s("sine")
  .vib("6:<0.2 0.5 0.8>")  // Increasing depth
```

**Extreme Vibrato** (Effects):
```javascript
// Siren effect
note("c3").vib("1:12")  // 1Hz, 1 octave

// Rapid warble
note("c3").vib("16:2")  // 16Hz, 2 semitones
```

### vibmod() / vmod()

Sets vibrato depth in semitones (alternative to colon syntax).

**Format**: `"depth"` or `"depth:frequency"`

**Usage**:
```javascript
// Set depth separately
note("a e").vib(4).vibmod("<.25 .5 1 2 12>")

// With frequency
note("a e").vibmod("<.25 .5 1 2 12>:8")
```

**When to Use**:
- Use `vib(freq:depth)` for concise syntax
- Use `vib(freq).vibmod(depth)` when patterning depth separately

**Vibrato Sweet Spots**:

| Use Case | Frequency (Hz) | Depth (semitones) |
|----------|----------------|-------------------|
| Subtle realism | 4-6 | 0.1-0.5 |
| Expressive | 5-7 | 0.5-1.0 |
| Dramatic | 3-8 | 1.0-2.0 |
| Siren/wobble | 0.5-2 | 6-12 |
| Tremolo-like | 8-16 | 0.5-2.0 |

---

## FM Synthesis

Frequency Modulation synthesis for complex, metallic, and bell-like timbres.

**Concept**: One oscillator (modulator) rapidly changes the frequency of another (carrier), creating additional harmonics.

### fm() / fmi()

Sets the **Modulation Index** (brightness/harmonic content).

**Range**: 0 (no FM) to 32+ (extreme)

**Usage**:
```javascript
// Increasing brightness
note("c e g b g e").fm("<0 1 2 8 32>")

// Patterned FM
note("c3*8").s("sine").fm("<0 2 4 8>")
```

**FM Index Guide**:
- 0: Pure carrier (no modulation)
- 1-2: Subtle harmonics, warm
- 4-8: Rich, complex timbres
- 16-32: Bright, metallic, aggressive
- 32+: Extreme, noisy

### fmh()

Sets the **Harmonicity Ratio** between carrier and modulator frequencies.

**Range**: Any number (decimals create inharmonic timbres)

**Usage**:
```javascript
// Simple ratios = harmonic sounds
note("c e g b g e")
  .fm(4)
  .fmh("<1 2 1.5 1.61>")

// Complex ratios = metallic sounds
note("c3").fm(8).fmh("<1.414 2.718 3.141>")
```

**Harmonicity Guide**:

| Ratio | Character | Use Case |
|-------|-----------|----------|
| 1 | Harmonic, warm | Bass, pads |
| 2 | Bright, clear | Bells, leads |
| 0.5 | Sub-harmonic | Deep bass |
| 1.5 | Musical, sweet | Mallets, keys |
| 1.414, π, e | Metallic, inharmonic | FX, experimental |
| Decimals | Clangorous | Bells, percussion |

### FM Envelope

Controls how FM amount changes over time.

#### fmattack()

Time to reach maximum modulation.

```javascript
note("c e g b g e")
  .fm(4)
  .fmattack("<0 .05 .1 .2>")
```

#### fmdecay()

Time to reach sustain level after attack.

```javascript
note("c e g b g e")
  .fm(4)
  .fmdecay("<.01 .05 .1 .2>")
  .fmsustain(.4)
```

#### fmsustain()

Level of modulation during sustain phase.

```javascript
note("c e g b g e")
  .fm(4)
  .fmdecay(.1)
  .fmsustain("<1 .75 .5 0>")  // 0 = no sustain
```

#### fmenv()

Sets envelope ramp type: `lin` (linear) or `exp` (exponential).

**Note**: Exponential may be buggy in current version.

```javascript
note("c e g b g e")
  .fm(4)
  .fmdecay(.2)
  .fmsustain(0)
  .fmenv("<exp lin>")
```

### FM Synthesis Examples

**Bell Sound**:
```javascript
note("c4 e4 g4")
  .s("sine")
  .fm(8)
  .fmh(1.414)  // Inharmonic ratio
  .fmattack(0)
  .fmdecay(0.3)
  .fmsustain(0)
  .release(1)
  .room(0.5)
```

**FM Bass**:
```javascript
note("c1 eb1 f1 g1")
  .s("sine")
  .fm(4)
  .fmh(2)
  .fmdecay(.1)
  .fmsustain(0)
  .lpf(400)
```

**FM Lead**:
```javascript
note("c4 e4 g4 b4")
  .s("sine")
  .fm(8)
  .fmh(1.5)
  .fmattack(0)
  .fmdecay(.2)
  .fmsustain(0)
  .delay(.25)
```

**Evolving FM Pad**:
```javascript
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("sine")
  .fm(sine.range(2, 8).slow(4))  // Modulated FM
  .fmh(perlin.range(1, 2))       // Evolving harmonicity
  .room(0.7)
  .attack(0.5)
```

---

## Wavetable Synthesis

Custom waveforms loaded as single-cycle samples (wavetables).

### Using Wavetables

**Key Concepts**:
- Prefix sample names with `wt_`
- Automatically loops the single cycle
- Use `loopBegin` and `loopEnd` to scan through wavetable
- Default set includes 1000+ wavetables from AKWF library

**Basic Usage**:
```javascript
// Load wavetable sample bank
samples('bubo:waveforms')

// Use wavetable
note("c3 eb3 g3 bb3").s('wt_flute')
```

**Complete Example**:
```javascript
samples('bubo:waveforms')

note("<[g3,b3,e4]!2 [a3,c3,e4] [b3,d3,f#4]>")
  .n("<1 2 3 4 5 6 7 8 9 10>/2")  // Cycle through variations
  .s('wt_flute')
  .room(0.5).size(0.9)
  .velocity(0.25)
  .often(n => n.ply(2))
  .release(0.125)
  .decay("<0.1 0.25 0.3 0.4>")
  .sustain(0)
  .cutoff("<1000 2000 4000>")
  .fast(4)
```

**Wavetable Scanning**:
```javascript
// Scan through wavetable positions
note("c3").s('wt_saw')
  .loopBegin(sine.range(0, 0.5).slow(2))  // Animate through table
```

**Available Wavetables** (AKWF library):
- `wt_flute`, `wt_saw`, `wt_square`, `wt_sine`
- 1000+ more in the AKWF collection
- Can import custom wavetables

**Tips**:
- Wavetables are more CPU-efficient than additive synthesis
- Great for unique timbres not possible with basic waveforms
- Combine with filters and effects for rich sounds

---

## ZZFX Synth

"Zuper Zmall Zound Zynth" - a compact synth and FX engine with extensive parameters.

**Concept**: Designed for small code size but packed with features. Includes synthesis and effects in one engine.

### ZZFX Sound Types

Use `z_` prefix:

- `z_sawtooth`
- `z_tan`
- `z_noise`
- `z_sine`
- `z_square`

**Usage**:
```javascript
note("c2 eb2 f2 g2")
  .s("z_sawtooth")
```

### ZZFX Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `zrand` | 0-1 | Randomization amount |
| `attack` | seconds | Envelope attack time |
| `decay` | seconds | Envelope decay time |
| `sustain` | 0-1 | Envelope sustain level |
| `release` | seconds | Envelope release time |
| `curve` | 1-3 | Waveshape distortion |
| `slide` | +/- | Pitch slide (positive = up, negative = down) |
| `deltaSlide` | number | Pitch slide variation |
| `noise` | 0-1 | Noise/dirt amount |
| `zmod` | number | FM modulation speed |
| `zcrush` | 0-1 | Bit crush amount |
| `zdelay` | 0-1 | Simple delay effect |
| `pitchJump` | semitones | Pitch change after pitchJumpTime |
| `pitchJumpTime` | seconds | Time before pitchJump occurs |
| `lfo` | Hz | LFO speed (resets slide + pitchJump) |
| `tremolo` | 0-1 | LFO volume modulation depth |

### ZZFX Example (Kitchen Sink)

```javascript
note("c2 eb2 f2 g2")
  .s("{z_sawtooth z_tan z_noise z_sine z_square}%4")
  .zrand(0)
  .attack(0.001)
  .decay(0.1)
  .sustain(.8)
  .release(.1)
  .curve(1)
  .slide(0)
  .deltaSlide(0)
  .noise(0)
  .zmod(0)
  .zcrush(0)
  .zdelay(0)
  .pitchJump(0)
  .pitchJumpTime(0)
  .lfo(0)
  .tremolo(0.5)
```

### ZZFX Sound Design Examples

**Laser Zap**:
```javascript
note("c4").s("z_square")
  .slide(-12)       // Pitch drops
  .decay(0.3)
  .sustain(0)
  .zmod(10)         // FM modulation
  .curve(2)
```

**Coin Pickup**:
```javascript
note("c5").s("z_sine")
  .pitchJump(7)     // Jump up 7 semitones
  .pitchJumpTime(0.05)
  .decay(0.2)
  .sustain(0)
  .tremolo(0.3)
```

**8-bit Explosion**:
```javascript
note("c2").s("z_noise")
  .slide(-24)       // Pitch slides down 2 octaves
  .decay(0.5)
  .sustain(0)
  .zcrush(0.5)      // Bit crush
  .curve(3)
```

**Retro Bass**:
```javascript
note("c1 eb1 f1 g1").s("z_square")
  .attack(0.001)
  .decay(0.15)
  .sustain(0.4)
  .release(0.1)
  .curve(2)
  .noise(0.1)       // Slight grit
```

**Tremolo Pad**:
```javascript
note("<[c3,e3,g3] [d3,f3,a3]>").s("z_sawtooth")
  .attack(0.3)
  .release(0.5)
  .lfo(4)           // 4Hz LFO
  .tremolo(0.6)     // 60% depth
  .zdelay(0.3)      // Built-in delay
```

---

## Synthesis Techniques

### Bass Sounds

**Sawtooth Bass** (Classic):
```javascript
note("c2 eb2 f2 g2")
  .s("sawtooth")
  .lpf(800)
  .lpenv(4)         // Filter envelope
  .lpa(.01)
  .lpd(.1)
  .lps(.5)
  .gain(0.7)
```

**FM Bass** (Modern):
```javascript
note("c2 eb2 f2 g2")
  .s("sine")
  .fm(4)
  .fmh(2)
  .fmdecay(.1)
  .fmsustain(0)
  .lpf(400)
```

**Sub Bass** (Deep):
```javascript
note("c1 eb1 f1 g1")
  .s("sine")
  .attack(0.01)
  .decay(0.2)
  .sustain(0.8)
  .lpf(200)
  .gain(0.8)
```

**Reese Bass** (Layered):
```javascript
stack(
  note("c1").s("sawtooth").lpf(400),
  note("c1").s("sawtooth").note(add(0.1)).lpf(400)  // Detuned
).gain(0.6)
```

### Pad Sounds

**Soft Pad** (Ambient):
```javascript
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("triangle,sine")  // Layer waveforms
  .attack(.5)
  .release(1)
  .room(.8)
  .gain(.4)
```

**Bright Pad with Vibrato**:
```javascript
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("sawtooth")
  .lpf(2000)
  .vib(4)           // 4Hz vibrato
  .vibmod(0.5)      // 0.5 semitone depth
  .attack(.3)
  .release(.8)
  .room(.6)
```

**FM Pad** (Evolving):
```javascript
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("sine")
  .fm(sine.range(2, 8).slow(4))  // Evolving FM
  .fmh(1.5)
  .attack(0.5)
  .release(1)
  .room(0.7)
```

**Additive Pad** (Rich):
```javascript
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("user")
  .partials([1, 0.5, 0.3, 0.2, 0.1, 0.05])  // Custom harmonics
  .attack(0.4)
  .release(0.8)
  .room(0.8)
```

### Lead Sounds

**Square Lead** (Retro):
```javascript
note("c4 e4 g4 b4")
  .s("square")
  .lpf(1500)
  .lpq(5)           // Resonance
  .attack(.01)
  .decay(.1)
  .sustain(.3)
  .delay(0.25)
```

**FM Lead** (Bright):
```javascript
note("c4 e4 g4 b4")
  .s("sine")
  .fm(8)
  .fmh(1.5)
  .fmattack(0)
  .fmdecay(.2)
  .fmsustain(0)
  .delay(.25)
```

**Saw Lead** (Aggressive):
```javascript
note("c4 e4 g4 b4")
  .s("sawtooth")
  .lpf(2000)
  .lpenv(8)         // Filter sweep
  .lpdecay(0.2)
  .vib(5)
  .vibmod(0.3)
  .distort(2)
```

### Percussive Sounds

**Kick Drum** (Synthesized):
```javascript
note("c1")
  .s("sine")
  .penv(24)         // Pitch envelope (drops 2 octaves)
  .pdecay(.05)
  .decay(.2)
  .sustain(0)
  .distort(1)
```

**Snare** (Noise-based):
```javascript
sound("white")
  .decay(.08)
  .sustain(0)
  .lpf(8000)
  .hpf(200)
  .distort(0.5)
```

**Hi-hat** (Filtered Noise):
```javascript
sound("white")
  .decay(.04)
  .sustain(0)
  .lpf(12000)
  .hpf(8000)
  .gain(0.3)
```

**Tom** (Pitched Noise):
```javascript
stack(
  note("c3 f3 g3").s("sine").penv(12).pdecay(0.05),
  sound("pink").lpf(2000)
).decay(0.3).sustain(0)
```

### Experimental Sounds

**Noise Sweep**:
```javascript
sound("white")
  .lpf(sine.range(200, 8000).slow(4))  // Sweeping filter
  .lpq(10)          // High resonance
  .room(.5)
```

**Granular Texture**:
```javascript
note("c2")
  .s("sawtooth")
  .partials(randL(50))   // Random harmonics
  .phases(randL(50))     // Random phases
  .room(.8)
  .gain(0.4)
```

**FM Chaos**:
```javascript
note("c2 e2 g2")
  .s("sine")
  .fm(sine.range(0, 32).slow(2))        // Chaotic FM
  .fmh(perlin.range(0.5, 4))            // Wandering harmonicity
  .room(0.6)
```

**Additive Bells**:
```javascript
note("c4 e4 g4")
  .s("user")
  .partials([1, 0, 0.7, 0, 0.3, 0, 0.1])  // Bell-like spectrum
  .decay(0.5)
  .sustain(0)
  .release(2)
  .room(0.7)
```

**Wavetable Morph**:
```javascript
samples('bubo:waveforms')

note("c3 eb3 g3")
  .s('wt_saw')
  .loopBegin(sine.range(0, 0.8).slow(4))  // Morph through table
  .lpf(perlin.range(500, 2000))
  .room(0.5)
```

---

## Tips for Synthesis

### General Synthesis

1. **Start Simple**: Begin with basic waveforms, add complexity gradually
2. **Layer Sounds**: Stack multiple oscillators with `.s("saw,triangle")`
3. **Use Envelopes**: Shape sounds with ADSR (see `04_effects_reference.md`)
4. **Filter Movement**: Animate filters with `lpenv`, `sine.range()`, etc.
5. **Add Space**: Use reverb and delay for depth
6. **Combine Techniques**: FM + filtering + effects = rich sounds

### Waveform Selection

- **Sine**: Pure, clean, great for sub-bass and FM
- **Sawtooth**: Bright, full spectrum, good starting point
- **Square**: Hollow, retro, use for leads and bass
- **Triangle**: Soft, mellow, good for pads (default)
- **Noise**: Texture, percussion, atmosphere

### FM Synthesis

- **Low FM index (1-4)**: Warm, subtle harmonics
- **Medium FM index (4-8)**: Rich, complex timbres
- **High FM index (16+)**: Bright, metallic, aggressive
- **Simple ratios (1, 2, 0.5)**: Musical, harmonic
- **Complex ratios (1.414, π)**: Inharmonic, metallic
- **Use FM envelope**: Create evolving timbres

### Additive Synthesis

- **Odd harmonics only**: Square-ish sound
- **Even harmonics only**: Hollow sound
- **All harmonics**: Sawtooth-ish sound
- **Random partials**: Unique, unpredictable timbres
- **Algorithmic generation**: Create complex spectra

### Vibrato

- **Subtle (0.1-0.5 semitones)**: Adds life and realism
- **Moderate (0.5-1.0 semitones)**: Expressive, emotional
- **Extreme (6-12 semitones)**: Siren, wobble effects
- **Frequency 4-6 Hz**: Natural, musical
- **Frequency 0.5-2 Hz**: Slow, dramatic

### Noise

- **White**: Bright, harsh, hi-hats
- **Pink**: Balanced, natural, softer percussion
- **Brown**: Dark, rumble, low-end texture
- **Add to oscillators**: Small amounts (0.05-0.2) add grit
- **Filter heavily**: Shape noise into musical sounds

### Sound Design Workflow

1. **Choose oscillator type** (waveform, FM, additive, wavetable)
2. **Set pitch/note** (fundamental frequency)
3. **Shape with envelope** (ADSR - see effects reference)
4. **Filter** (lpf, hpf, bpf - see effects reference)
5. **Add modulation** (vibrato, FM envelope, filter envelope)
6. **Layer** (stack multiple oscillators)
7. **Add effects** (reverb, delay, distortion)
8. **Mix** (gain, panning)

### CPU Optimization

- **Wavetables**: More efficient than many partials
- **Basic waveforms**: Lightest CPU load
- **FM synthesis**: Moderate CPU usage
- **Additive (many partials)**: Heavier CPU load
- **Layer sparingly**: Each layer adds CPU usage

---

## Cross-References

### Related Documentation

- **04_effects_reference.md**: Filters, ADSR, modulation, effects chain
- **03_core_functions_reference.md**: `note()`, `sound()`, `s()`, scales, chords
- **07_musical_patterns_library.md**: Complete synthesis examples by genre
- **13_mastering_mixing_guide.md**: Gain staging, compression, final mix

### Key Effects for Synthesis

**Filters** (Subtractive Synthesis):
- `lpf()` - Low-pass filter (remove highs)
- `hpf()` - High-pass filter (remove lows)
- `bpf()` - Band-pass filter (isolate range)
- `lpq()` - Resonance (emphasize cutoff frequency)
- `lpenv()` - Filter envelope (animate filter)

**Amplitude**:
- `attack()`, `decay()`, `sustain()`, `release()` - ADSR envelope
- `gain()` - Volume control
- `velocity()` - MIDI-style dynamics

**Modulation**:
- `tremolo()` - Amplitude modulation
- LFOs via `sine.range()`, `perlin.range()` - Modulate any parameter

**Spatial**:
- `room()` - Reverb
- `delay()` - Echo
- `pan()` - Stereo placement

**Distortion**:
- `distort()` - Waveshaping
- `crush()` - Bit reduction
- `coarse()` - Sample rate reduction

---

## Summary

Strudel provides multiple synthesis methods:

1. **Basic Waveforms**: Sine, saw, square, triangle
2. **Noise Generators**: White, pink, brown, crackle
3. **Additive Synthesis**: Custom harmonics with partials/phases
4. **FM Synthesis**: Complex timbres via frequency modulation
5. **Wavetable Synthesis**: Pre-rendered single-cycle waveforms
6. **ZZFX**: Compact synth with built-in effects

**Remember**:
- Combine synthesis with filters and effects for rich sounds
- Layer multiple oscillators for depth
- Use envelopes to shape sounds over time
- Experiment with FM and additive synthesis for unique timbres
- Start simple and add complexity gradually

**For complete synthesis**: Use this guide with `04_effects_reference.md` (filters, ADSR, modulation) and `07_musical_patterns_library.md` (genre examples).
