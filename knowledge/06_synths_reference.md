# Strudel Synthesizers Reference

**Research Date**: 2025-12-22  
**Source**: https://strudel.cc/learn/synths/

## Basic Waveforms

Strudel provides four basic oscillator waveforms:

### Waveform Types

| Waveform | Character | Use Case |
|----------|-----------|----------|
| `sine` | Smooth, pure tone | Bass, pads, smooth leads |
| `sawtooth` | Bright, harsh | Leads, bass, aggressive sounds |
| `square` | Hollow, mid-range | Retro sounds, leads |
| `triangle` | Soft, mellow | Pads, soft leads (default) |

### Using Waveforms

```javascript
// Specify waveform
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("<sawtooth square triangle sine>")

// Default is triangle when using note() without sound()
note("c e g")

// Combining waveforms
note("c2 eb2 f2 g2")
  .sound("sawtooth,triangle")  // Stack waveforms
```

## Noise Generators

### Noise Types

| Type | Character | Frequency Spectrum |
|------|-----------|-------------------|
| `white` | Hardest | Full spectrum (equal energy) |
| `pink` | Medium | Balanced (1/f falloff) |
| `brown` | Softest | Lower frequencies emphasized |

### Using Noise

```javascript
// Basic noise
sound("<white pink brown>")

// Noise as hi-hats
sound("bd*2, <white pink brown>*8")
  .decay(.04).sustain(0)

// Add noise to oscillator
note("c3").noise("<0.1 0.25 0.5>")
```

### Crackle

Subtle noise crackles for texture:

```javascript
s("crackle*4").density("<0.01 0.04 0.2 0.5>".slow(2))
```

**Parameters**:
- `density`: Controls noise amount (0-1)

## Additive Synthesis

Control over harmonics that compose waveforms.

### partials()
Controls magnitude of each harmonic.

```javascript
// Spectral filtering (remove high harmonics)
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("sawtooth")
  .partials([1, 1, "<1 0>", "<1 0>", "<1 0>", "<1 0>", "<1 0>"])

// Create custom waveform
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("user")
  .partials([1, 0, 0.3, 0, 0.1, 0, 0, 0.3])

// Algorithmic harmonics
const numHarmonics = 22
note("c2 <eb2 <g2 g1>>".fast(2))
  .sound("saw")
  .partials(new Array(numHarmonics).fill(1))
```

### phases()
Controls phase of each harmonic for depth.

```javascript
s("saw").seg(16).n(irand(12)).scale("F1:minor")
  .penv(48).panchor(0).pdec(0.05)
  .delay(0.25).room(0.25)
  .partials(randL(200))
  .phases(randL(200))  // Add phase variation
```

## Vibrato

Frequency modulation for pulsating effect.

### vib() / vibrato() / v()
Applies vibrato to oscillator frequency.

**Format**: `"frequency"` or `"frequency:depth"`

```javascript
// Basic vibrato
note("a e").vib("<.5 1 2 4 8 16>")

// With depth (in semitones)
note("a e").vib("<.5 1 2 4 8 16>:12")
```

### vibmod() / vmod()
Sets vibrato depth in semitones.

**Format**: `"depth"` or `"depth:frequency"`

```javascript
// Set depth
note("a e").vib(4).vibmod("<.25 .5 1 2 12>")

// With frequency
note("a e").vibmod("<.25 .5 1 2 12>:8")
```

## FM Synthesis

Frequency Modulation for complex timbres.

### fm() / fmi()
Sets FM index (brightness).

```javascript
note("c e g b g e").fm("<0 1 2 8 32>")
```

### fmh()
Sets FM Harmonicity Ratio (timbre).

```javascript
note("c e g b g e")
  .fm(4)
  .fmh("<1 2 1.5 1.61>")
```

### FM Envelope

#### fmattack()
```javascript
note("c e g b g e")
  .fm(4)
  .fmattack("<0 .05 .1 .2>")
```

#### fmdecay()
```javascript
note("c e g b g e")
  .fm(4)
  .fmdecay("<.01 .05 .1 .2>")
  .fmsustain(.4)
```

#### fmsustain()
```javascript
note("c e g b g e")
  .fm(4)
  .fmdecay(.1)
  .fmsustain("<1 .75 .5 0>")
```

#### fmenv()
Sets envelope ramp type: `lin` or `exp`

```javascript
note("c e g b g e")
  .fm(4)
  .fmdecay(.2)
  .fmsustain(0)
  .fmenv("<exp lin>")
```

## Wavetable Synthesis

Custom waveforms loaded as wavetables.

### Using Wavetables

- Prefix sample names with `wt_`
- Use `loopBegin` and `loopEnd` to scan wavetable
- Default set includes 1000+ wavetables from AKWF

```javascript
samples('bubo:waveforms')

note("<[g3,b3,e4]!2 [a3,c3,e4] [b3,d3,f#4]>")
  .n("<1 2 3 4 5 6 7 8 9 10>/2")
  .room(0.5).size(0.9)
  .s('wt_flute')
  .velocity(0.25)
  .often(n => n.ply(2))
  .release(0.125)
  .decay("<0.1 0.25 0.3 0.4>")
  .sustain(0)
  .cutoff(2000)
  .cutoff("<1000 2000 4000>")
  .fast(4)
```

## ZZFX Synth

"Zuper Zmall Zound Zynth" - compact synth and FX engine.

### ZZFX Sound Types

- `z_sawtooth`
- `z_tan`
- `z_noise`
- `z_sine`
- `z_square`

### ZZFX Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| `zrand` | 0-1 | Randomization |
| `attack` | seconds | Envelope attack |
| `decay` | seconds | Envelope decay |
| `sustain` | 0-1 | Envelope sustain level |
| `release` | seconds | Envelope release |
| `curve` | 1-3 | Waveshape |
| `slide` | +/- | Pitch slide |
| `deltaSlide` | number | Pitch slide variation |
| `noise` | 0-1 | Noise amount |
| `zmod` | number | FM speed |
| `zcrush` | 0-1 | Bit crush |
| `zdelay` | 0-1 | Simple delay |
| `pitchJump` | semitones | Pitch change after pitchJumpTime |
| `pitchJumpTime` | seconds | Time before pitchJump |
| `lfo` | Hz | LFO speed (resets slide + pitchJump) |
| `tremolo` | 0-1 | LFO volume modulation |

### ZZFX Example

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

## Synthesis Techniques

### Bass Sounds

```javascript
// Sawtooth bass
note("c2 eb2 f2 g2")
  .s("sawtooth")
  .lpf(800)
  .lpenv(4)
  .lpa(.01)
  .lpd(.1)
  .lps(.5)

// FM bass
note("c2 eb2 f2 g2")
  .s("sine")
  .fm(4)
  .fmh(2)
  .fmdecay(.1)
  .fmsustain(0)
```

### Pad Sounds

```javascript
// Soft pad
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("triangle,sine")
  .attack(.5)
  .release(1)
  .room(.8)
  .gain(.4)

// Bright pad with vibrato
note("<[c3,e3,g3] [d3,f3,a3]>")
  .s("sawtooth")
  .lpf(2000)
  .vib(4)
  .vibmod(0.5)
  .attack(.3)
  .release(.8)
  .room(.6)
```

### Lead Sounds

```javascript
// Square lead
note("c4 e4 g4 b4")
  .s("square")
  .lpf(1500)
  .lpq(5)
  .attack(.01)
  .decay(.1)
  .sustain(.3)

// FM lead
note("c4 e4 g4 b4")
  .s("sine")
  .fm(8)
  .fmh(1.5)
  .fmattack(0)
  .fmdecay(.2)
  .fmsustain(0)
  .delay(.25)
```

### Percussive Sounds

```javascript
// Kick drum
note("c1")
  .s("sine")
  .penv(24)
  .pdecay(.05)
  .decay(.2)
  .sustain(0)

// Snare
sound("white")
  .decay(.08)
  .sustain(0)
  .lpf(8000)
  .hpf(200)

// Hi-hat
sound("white")
  .decay(.04)
  .sustain(0)
  .lpf(12000)
  .hpf(8000)
```

### Experimental Sounds

```javascript
// Noise sweep
sound("white")
  .lpf(sine.range(200, 8000).slow(4))
  .lpq(10)
  .room(.5)

// Granular texture
note("c2")
  .s("sawtooth")
  .partials(randL(50))
  .phases(randL(50))
  .room(.8)

// FM chaos
note("c2 e2 g2")
  .s("sine")
  .fm(sine.range(0, 32).slow(2))
  .fmh(perlin.range(0.5, 4))
```

## Tips for Synthesis

1. **Start Simple**: Begin with basic waveforms
2. **Layer Sounds**: Stack multiple oscillators with `.s("saw,triangle")`
3. **Use Envelopes**: Shape sounds with ADSR
4. **Filter Movement**: Animate filters with `lpenv`, `sine.range()`, etc.
5. **Add Space**: Use reverb and delay for depth
6. **Subtle Vibrato**: Small amounts add life (0.1-0.5 semitones)
7. **FM for Brightness**: Increase `fm` for brighter, more complex timbres
8. **Noise for Texture**: Mix in small amounts of noise
9. **Experiment with Partials**: Create unique timbres
10. **Combine Techniques**: FM + filtering + effects = rich sounds
