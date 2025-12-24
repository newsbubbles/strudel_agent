# Garden Sample Pack

**GitHub**: https://github.com/mot4i/garden  
**Loading**: `samples('github:mot4i/garden')`  
**Creator**: mot4i  
**License**: Free to use, share, and adapt with attribution  
**Support**: https://ko-fi.com/mot4i

## Overview

Garden is a free, thoughtfully curated sample pack designed specifically for live coding environments like Strudel and TidalCycles. Each single-shot sample has been carefully re-amped through select analog gear, bringing warmth, punch, and organic character to every sound.

**Key Features**:
- ✨ Hand-curated selection
- 🎛️ Re-amped through analog gear for warmth
- 🥁 Punchy drums with character
- 🎵 Designed for improvisation and real-time coding
- 📦 Organized by instrument type
- 🆓 Free with attribution

## Loading

```javascript
// Load Garden pack
samples('github:mot4i/garden')

// Use Garden samples
sound("garden_bd garden_sd garden_hh*3")
```

## Sample Categories

### Drums

#### Bass Drums (`garden_bd`)
Punchy, analog-processed kick drums

```javascript
// Basic pattern
sound("garden_bd*4")

// With variations
sound("garden_bd:0 garden_bd:1 garden_bd:2 garden_bd:3")

// Layered with effects
sound("garden_bd*4").lpf(800).gain(1.2)
```

#### Snares (`garden_sd`, `garden_sn`)
Two snare collections with different character

```javascript
// Snare pattern
sound("[~ garden_sd]*2")

// Alternate between collections
sound("[~ <garden_sd garden_sn>]*2")

// Layered snares
stack(
  sound("[~ garden_sd]*2"),
  sound("[~ garden_sn]*2").gain(0.4).hpf(200)
)
```

#### Hi-Hats (`garden_hh`, `garden_oh`)
- `garden_hh` - Closed hi-hats
- `garden_oh` - Open hi-hats

```javascript
// Closed hats
sound("garden_hh*8")

// Mixed open/closed
sound("garden_hh*6 [garden_hh garden_oh]")

// With velocity variation
sound("garden_hh*8").gain(".6 .8 .7 .9 .6 .8 .7 1")
```

#### Cymbals (`garden_cr`)
Crash cymbals

```javascript
// Crash accents
sound("garden_cr").slow(4)

// With reverb
sound("garden_cr").room(0.8).size(0.9).slow(2)
```

#### Toms (`garden_lt`)
Low toms

```javascript
// Tom fills
sound("~ ~ ~ [garden_lt garden_lt garden_lt]")

// Pitched toms
sound("garden_lt").speed("1 1.2 1.5 2")
```

#### Percussion
- `garden_cp` - Claps
- `garden_rim` - Rimshots

```javascript
// Claps on 2 and 4
sound("[~ garden_cp]*2")

// Rimshot pattern
sound("garden_rim*4").gain("1 .7 .8 .6")
```

### Melodic/Tonal

#### Metal Sounds (`metal`)
Metallic percussion and tones

```javascript
// Metallic texture
sound("metal*8").n(irand(8)).gain(0.5)

// Pitched metal
note("c4 e4 g4 b4").s("metal").room(0.5)
```

#### PSR-GX76 (`psr-gx76`)
Samples from Yamaha PSR-GX76 keyboard

```javascript
// Keyboard sounds
sound("psr-gx76").n("<0 1 2 3>")

// Melodic pattern
n("0 2 4 7").s("psr-gx76").scale("C:major")
```

#### ST Sounds (`st`)
Short tones or stabs

```javascript
// Stab pattern
sound("st").n("<0 1 2 1>")
```

### Effects (`fx`)
Sound effects and textures

```javascript
// Texture layer
sound("fx").n(irand(8)).slow(4).room(0.7)

// Accent effects
sound("~ ~ fx ~").n("<0 1 2>")
```

## Complete Sample List

```
fx           - Effects and textures
garden_bd    - Bass drums (analog warmth)
garden_cp    - Claps
garden_cr    - Cymbals
garden_hh    - Hi-hats (closed)
garden_lt    - Low toms
garden_oh    - Open hi-hats
garden_rim   - Rimshots
garden_sd    - Snare drums
garden_sn    - Snare drums (alternate)
metal        - Metallic percussion
psr-gx76     - Yamaha keyboard samples
st           - Short tones/stabs
```

## Usage Examples

### House Beat

```javascript
setcpm(120/4)

// Drums with Garden samples
$: sound("garden_bd*4, [~ garden_sd]*2, garden_hh*8")
   .gain("1 .8 1 .9")  // Groove

// Open hats for accent
$: sound("~ ~ ~ ~ ~ ~ garden_oh ~")
   .gain(0.7)
```

### Techno Pattern

```javascript
setcpm(128/4)

// Driving kick
$: sound("garden_bd*4")
   .lpf(1200)
   .gain(1.1)

// Offbeat claps
$: sound("[~ garden_cp]*2")
   .room(0.3)

// Fast hats
$: sound("garden_hh*16")
   .gain(".5 .6 .7 .8 .5 .6 .7 .9")
   .hpf(8000)
```

### Ambient Texture

```javascript
setcpm(60/4)

// Sparse drums
$: sound("garden_bd ~ ~ ~, ~ ~ ~ garden_sd")
   .room(0.8)
   .slow(2)

// Metallic atmosphere
$: sound("metal*4")
   .n(irand(8))
   .gain(0.3)
   .room(0.9)
   .delay(0.5)
   .slow(4)

// Cymbal wash
$: sound("garden_cr")
   .room(0.95)
   .size(0.9)
   .gain(0.4)
   .slow(8)
```

### Hip-Hop Beat

```javascript
setcpm(85/4)

// Boom-bap drums
$: sound(`
garden_bd -  -  -  garden_bd -  -  -,
-         -  garden_sd -  -  -  garden_sd -,
garden_hh garden_hh garden_hh garden_hh garden_hh garden_hh garden_hh garden_hh
`).late("[0 .01]*4")  // Swing

// Rimshot accents
$: sound("~ garden_rim ~ ~ ~ garden_rim ~ ~")
   .gain(0.6)
```

### Layering Garden with Other Packs

```javascript
// Garden kicks + 808 sub
stack(
  sound("garden_bd*4"),
  sound("808bd*4").gain(0.5).lpf(200)  // Sub layer
)

// Garden snare + reverb tail
stack(
  sound("[~ garden_sd]*2"),
  sound("[~ garden_sd]*2").gain(0.3).room(0.9).delay(0.25)
)
```

## Character & Sound Design

### Analog Warmth
Garden samples are re-amped through analog gear, giving them:
- Natural saturation
- Harmonic richness
- Organic character
- Warmth and depth

```javascript
// Emphasize warmth with gentle filtering
sound("garden_bd*4")
  .lpf(2000)
  .lpenv(1.5)
  .clip(0.8)  // Slight saturation
```

### Punch
Samples are designed for impact:

```javascript
// Maximize punch
sound("garden_bd garden_sd")
  .gain(1.2)
  .shape(0.3)  // Add bite
```

### Nuance
Multiple variations per instrument:

```javascript
// Cycle through variations for realism
sound("garden_hh*8").n("0 1 2 1 0 1 3 1")
```

## Live Coding Tips

### Start Simple

```javascript
// Begin with Garden drums
sound("garden_bd garden_sd")
```

### Build Gradually

```javascript
// Add layers one at a time
$: sound("garden_bd*4")
$: sound("[~ garden_sd]*2")
$: sound("garden_hh*8")
$: sound("~ ~ ~ garden_oh")
```

### Use Variables

```javascript
// Save patterns
let drums = sound("garden_bd*4, [~ garden_sd]*2, garden_hh*8")
let perc = sound("garden_rim*4").gain(0.5)

$: drums
$: perc
```

### Experiment with Effects

```javascript
// Garden sounds take effects well
sound("garden_bd*4")
  .lpf(sine.range(400, 2000).slow(4))  // Filter sweep
  .room(0.3)
  .distort(0.5)
```

## Tags

`drums`, `percussion`, `analog`, `warm`, `curated`, `punchy`, `live-coding`, `free`, `attribution`, `diy`, `re-amped`, `organic`

## License & Attribution

**License**: Free to use, share, and adapt  
**Attribution**: Please credit mot4i  
**Support**: Consider supporting the creator at https://ko-fi.com/mot4i

### Usage in Projects

```javascript
// Add attribution in your code comments:
/*
 * Using Garden sample pack by mot4i
 * https://github.com/mot4i/garden
 * Support: https://ko-fi.com/mot4i
 */

samples('github:mot4i/garden')
```

## Comparison with Dirt-Samples

| Feature | Garden | Dirt-Samples |
|---------|--------|-------------|
| Size | Focused | Comprehensive |
| Character | Analog warmth | Variable |
| Curation | Hand-picked | Community collection |
| License | Clear (free w/ attribution) | Unknown/mixed |
| Best For | Warm, punchy drums | Variety and experimentation |

## See Also

- [Dirt-Samples](01_dirt_samples.md) - Comprehensive TidalCycles library
- [Clean-Breaks](03_clean_breaks.md) - Licensed drum breaks
- [Creator's Ko-fi](https://ko-fi.com/mot4i) - Support the creator

---

**Last Updated**: 2025-12-22  
**Status**: Complete reference  
**Creator**: mot4i  
**Support**: https://ko-fi.com/mot4i
