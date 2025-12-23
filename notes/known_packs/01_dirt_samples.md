# Dirt-Samples Pack

**GitHub**: https://github.com/tidalcycles/Dirt-Samples  
**Loading**: `samples('github:tidalcycles/Dirt-Samples')`  
**Creator**: TidalCycles community  
**License**: Mixed/Unknown provenance (use with caution for commercial work)

## Overview

Dirt-Samples is the canonical sample library for TidalCycles and Strudel. It contains 100+ sample categories covering drums, breaks, synths, effects, and field recordings. This is the default sample pack loaded in most Strudel environments.

**Note**: The provenance of many samples in Dirt-Samples is unknown. For properly licensed samples, see [Clean-Samples](https://github.com/tidalcycles/Clean-Samples).

## Loading

```javascript
// Usually pre-loaded in Strudel, but can be explicitly loaded:
samples('github:tidalcycles/Dirt-Samples')

// Or from raw GitHub URL:
samples('https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/')
```

## Sample Categories

### Drum Machines

#### Roland TR-808
- `808` - Complete TR-808 kit
- `808bd` - Bass drums
- `808cy` - Cymbals  
- `808hc` - Hand claps
- `808ht` - High toms
- `808lc` - Low congas
- `808lt` - Low toms
- `808mc` - Mid congas
- `808mt` - Mid toms
- `808oh` - Open hi-hats
- `808sd` - Snare drums

**Usage**:
```javascript
sound("808bd*4, 808sd*2, 808oh*8")
```

#### Roland TR-909
- `909` - Complete TR-909 kit

**Usage**:
```javascript
sound("909*4, [~ 909:1]*2, 909:2*8")
```

#### Other Drum Machines
- `dr55` - Boss DR-55 drum machine
- `drumtraks` - Sequential Circuits DrumTraks
- `casio` - Casio keyboard drums

### Generic Drums

- `bd` - Bass drums (multiple variations)
- `sd` - Snare drums
- `cp` - Claps
- `hh` - Hi-hats (closed)
- `oh` - Open hi-hats
- `lt` - Low toms
- `mt` - Mid toms  
- `ht` - High toms
- `cr` - Crash cymbals
- `cb` - Cowbells
- `cc` - Closed hi-hats
- `co` - Conga sequence

**Usage**:
```javascript
// Generic drum pattern
sound("bd*4, [~ sd]*2, hh*8")

// With sample variations
sound("bd:0 bd:1 bd:2 bd:3")
```

### Drum Breaks

- `amencutup` - Amen break sliced (iconic jungle break)
- `breaks125` - 125 BPM breaks
- `breaks152` - 152 BPM breaks
- `breaks157` - 157 BPM breaks
- `breaks165` - 165 BPM breaks

**Usage**:
```javascript
// Play amen break slices
s("amencutup").n("0 1 2 3 4 5 6 7").slow(2)

// Randomize amen
s("amencutup").n(irand(16)).fast(2)

// 125 BPM break
s("breaks125:0").loopAt(2)
```

### Bass

- `bass` - Generic bass hits
- `bass0`, `bass1`, `bass2`, `bass3` - Bass variations
- `bassdm` - Bass drum
- `bassfoo` - Bass samples
- `clubkick` - Club kick drums

**Usage**:
```javascript
// Bass pattern
s("bass").n("0 2 4 5").lpf(400)

// Pitched bass
note("c2 eb2 f2 g2").s("bass1")
```

### Melodic/Tuned

- `arpy` - Tuned arpeggio samples (single hits of tuned instruments)
- `arp` - Arpeggios
- `casio` - Casio keyboard

**Usage**:
```javascript
// Arpeggiated melody
n("0 2 4 7").s("arpy").scale("C:minor")

// Casio tones
s("casio").n("<0 1 2 3>")
```

### Effects & Textures

- `glitch` - Glitch sounds
- `glitch2` - More glitch
- `fm` - FM synthesis samples
- `dist` - Distorted sounds
- `bleep` - Bleeps
- `blip` - Blips
- `click` - Clicks
- `clak` - Clacks
- `flick` - Flicks

**Usage**:
```javascript
// Glitchy texture
s("glitch*8").n(irand(8)).gain(0.6)

// FM tones
s("fm").n("0 3 7 12").fast(2)
```

### Vocal/Speech

- `diphone` - Speech synthesis
- `diphone2` - More diphones
- `alphabet` - Letter sounds

**Usage**:
```javascript
// Speech synthesis
s("diphone").n("0 1 2 3").slow(2)
```

### Percussion

- `tabla` - Tabla drums
- `can` - Can hits
- `bottle` - Bottle percussion
- `coins` - Coin sounds
- `glasstap` - Glass taps

### Nature/Field Recordings

- `birds` - Bird sounds
- `birds3` - More birds
- `crow` - Crow calls
- `breath` - Breathing
- `bubble` - Bubbles
- `fire` - Fire sounds

**Usage**:
```javascript
// Ambient birds
s("birds").n("<0 1 2>").slow(4).room(0.9)
```

### Electronic/Synth

- `electro1` - Electro sounds
- `feel` - Synth feels
- `feelfx` - Feel effects
- `future` - Futuristic sounds
- `cosmicg` - Cosmic sounds

### Experimental/Misc

- `circus` - Circus sounds
- `control` - Control samples
- `dork2`, `dorkbot` - Experimental
- `east` - Eastern sounds
- `fest` - Festival sounds
- `gab`, `gabba`, `gabbaloud`, `gabbalouder` - Gabber kicks
- `alex`, `ade`, `ades2`, `ades3`, `ades4` - Named collections
- `armora`, `auto`, `baa`, `baa2` - Misc samples
- `battles`, `bend`, `bev`, `bin`, `blue` - Misc samples
- `chin`, `d`, `db`, `dr`, `dr2`, `dr_few` - Misc drums
- `e`, `em2`, `erk`, `f`, `foo` - Misc samples

## Complete List (100+ Categories)

Here's the full alphabetical list:

```
808, 808bd, 808cy, 808hc, 808ht, 808lc, 808lt, 808mc, 808mt, 808oh, 808sd,
909, ab, ade, ades2, ades3, ades4, alex, alphabet, amencutup, armora, arp,
arpy, auto, baa, baa2, bass, bass0, bass1, bass2, bass3, bassdm, bassfoo,
battles, bd, bend, bev, bin, birds, birds3, bleep, blip, blue, bottle,
breaks125, breaks152, breaks157, breaks165, breath, bubble, can, casio, cb,
cc, chin, circus, clak, click, clubkick, co, coins, control, cosmicg, cp,
cr, crow, d, db, diphone, diphone2, dist, dork2, dorkbot, dr, dr2, dr55,
dr_few, drum, drumtraks, e, east, electro1, em2, erk, f, feel, feelfx,
fest, fire, flick, fm, foo, future, gab, gabba, gabbaloud, gabbalouder,
glasstp, glitch, glitch2, (and more...)
```

## Usage Patterns

### Basic Drum Pattern

```javascript
// Four-on-the-floor house
sound("bd*4, [~ cp]*2, hh*8")
```

### Sample Variations

```javascript
// Cycle through kick variations
sound("bd:0 bd:1 bd:2 bd:3")

// Random selection
sound("bd").n(irand(8))
```

### Breaks and Loops

```javascript
// Amen break
s("amencutup").n("0 1 2 3 4 5 6 7").slow(2)

// Shuffled amen
s("amencutup").n(shuffle(8))

// Pitched breaks
s("breaks125:0").loopAt(2).speed("<1 1.5 0.75>")
```

### Melodic Usage

```javascript
// Arpy melody
n("0 2 4 7 9").s("arpy").scale("C:minor:pentatonic")

// Bass line
note("c2 eb2 f2 g2").s("bass1").lpf(600)
```

### Layering

```javascript
// Layer 808 with generic drums
stack(
  sound("808bd*4"),
  sound("bd*4").gain(0.3),  // Layer for thickness
  sound("808oh*8").gain(0.6)
)
```

## Tags

`drums`, `breaks`, `synths`, `fx`, `classic`, `comprehensive`, `tidalcycles`, `default`, `808`, `909`, `amen`, `field-recording`, `experimental`

## Notes

### Provenance Warning
Many samples in Dirt-Samples have unknown origins. For commercial use or projects requiring clear licensing:
- Use [Clean-Samples](https://github.com/tidalcycles/Clean-Samples) instead
- Create your own samples
- Source samples with clear licenses

### Performance
Dirt-Samples is large (100+ categories). If you only need specific sounds, consider:
- Using smaller, focused packs
- Loading only what you need
- Using synthesis instead of samples where possible

### Sample Count
Most categories contain 8-16 variations, accessible with `:n` notation:
```javascript
sound("bd:0 bd:1 bd:2")  // First 3 bass drums
```

## See Also

- [Clean-Samples](https://github.com/tidalcycles/Clean-Samples) - Properly licensed alternative
- [Clean-Breaks](03_clean_breaks.md) - Licensed drum breaks
- [TidalCycles Documentation](https://tidalcycles.org/)

---

**Last Updated**: 2025-12-22  
**Status**: Complete reference
