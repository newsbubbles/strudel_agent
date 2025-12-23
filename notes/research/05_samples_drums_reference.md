# Strudel Samples & Drums Reference

**Research Date**: 2025-12-22  
**Source**: https://strudel.cc/learn/samples/

## Default Drum Sounds

### Core Drums

| Sound | Abbreviation | Description |
|-------|--------------|-------------|
| Bass drum / Kick | `bd` | Low frequency drum hit |
| Snare drum | `sd` | Mid-high frequency sharp hit |
| Rimshot | `rim` | Sharp metallic click |
| Clap | `cp` | Hand clap sound |
| Closed hi-hat | `hh` | Short metallic cymbal |
| Open hi-hat | `oh` | Sustained metallic cymbal |
| Crash cymbal | `cr` | Large crash sound |
| Ride cymbal | `rd` | Sustained ride pattern |
| High tom | `ht` | High pitched tom |
| Medium tom | `mt` | Mid pitched tom |
| Low tom | `lt` | Low pitched tom |

### Percussion

| Sound | Abbreviation | Description |
|-------|--------------|-------------|
| Shakers | `sh` | Maracas, cabasas, etc. |
| Cowbell | `cb` | Classic cowbell |
| Tambourine | `tb` | Jingle percussion |
| Other percussion | `perc` | Various percussion |
| Miscellaneous | `misc` | Misc samples |
| Effects | `fx` | Sound effects |

## Drum Machine Banks

Use `.bank()` to select drum machine character:

### Classic Drum Machines

```javascript
// Roland TR-808 (iconic 808 sound)
s("bd sd, hh*8").bank("RolandTR808")

// Roland TR-909 (classic house/techno)
s("bd sd, hh*8").bank("RolandTR909")

// Roland TR-707 (80s digital)
s("bd sd, hh*8").bank("RolandTR707")

// Roland TR-505 (compact 80s)
s("bd sd, hh*8").bank("RolandTR505")

// Akai Linn (80s classic)
s("bd sd, hh*8").bank("AkaiLinn")

// Rhythm Ace (vintage analog)
s("bd sd, hh*8").bank("RhythmAce")

// Visco Space Drum (unique character)
s("bd sd, hh*8").bank("ViscoSpaceDrum")

// Roland Compurhythm 1000
s("bd sd, hh*8").bank("RolandCompurhythm1000")

// Casio RZ-1
s("bd sd, hh*8").bank("CasioRZ1")
```

### Pattern Banks

```javascript
// Alternate between drum machines
s("bd sd, hh*8").bank("<RolandTR808 RolandTR909>")

// Cycle through multiple machines
s("bd*4").bank("<RolandTR808 RolandTR909 RolandTR707 AkaiLinn>")
```

## Sample Selection

### Using Sample Numbers

```javascript
// Direct notation with colon
s("hh:0 hh:1 hh:2 hh:3")

// Using n() function (cleaner)
s("hh*8").n("0 1 2 3 0 1 2 3")

// Pattern sample numbers
s("bd*4").n("<0 1 2 3>")
```

### Sample Variation Patterns

```javascript
// Cycle through samples
s("hh*8").bank("RolandTR909").n("0 1 2 3 4 5 6 7")

// Random-ish variations
s("bd*4").n("0 0 1 0 2 0 1 3")

// Alternating samples
s("sd*4").n("<0 1>")
```

## Non-Drum Samples

### Melodic Samples

```javascript
// Available melodic samples
s("insect")   // Insect sounds
s("wind")     // Wind sounds
s("jazz")     // Jazz samples
s("metal")    // Metallic sounds
s("east")     // Eastern instruments
s("crow")     // Crow sounds
s("casio")    // Casio keyboard
s("space")    // Space sounds
s("numbers")  // Number samples
```

### Using Melodic Samples

```javascript
// Simple pattern
s("jazz*2, insect [crow metal] - -, - space:4 - space:1")

// With sample numbers
n("0 1 [4 2] 3*2").sound("jazz")

// Melodic sequence
n("<0 1 2>").s("casio")
```

## Loading Custom Samples

### From GitHub

```javascript
// Shorthand for GitHub repos
samples('github:tidalcycles/dirt-samples')
s("bd sd bd sd, hh*16")

// Specific branch
samples('github:user/repo/branch')
```

### From URL

```javascript
// Load strudel.json file
samples('https://example.com/samples/strudel.json')

// Custom sample map with base path
samples({
  bassdrum: 'bd/BT0AADA.wav',
  hihat: 'hh27/000_hh27closedhh.wav',
  snaredrum: ['sd/rytm-01-classic.wav', 'sd/rytm-00-hard.wav']
}, 'https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/')

s("bassdrum snaredrum:0 bassdrum snaredrum:1, hihat*16")
```

### Shabda Integration

Query samples from freesound.org:

```javascript
// Load samples from freesound
samples('shabda:bass:4,hihat:4,rimshot:2')

$: n("0 1 2 3").s('bass')
$: n("0 1*2 2 3*2").s('hihat').clip(1)
$: n("~ 0 ~ 1").s('rimshot')
```

### Speech Synthesis

```javascript
// English speech
samples('shabda/speech:the_drum,forever')

// French speech
samples('shabda/speech/fr-FR/m:magnifique')

$: s("the_drum*2").chop(16).speed(rand.range(0.85,1.1))
$: s("forever magnifique").slow(4).late(0.125)
```

## Pitched Samples

### Specifying Sample Pitch

```javascript
samples({
  'gtr': 'gtr/0001_cleanC.wav',
  'moog': { 'g3': 'moog/005_Mighty%20Moog%20G3.wav' }
}, 'github:tidalcycles/dirt-samples')

note("g3 [bb3 c4] <g4 f4 eb4 f3>@2")
  .s("gtr,moog").clip(1).gain(.5)
```

### Multiple Pitch Regions

```javascript
samples({
  'moog': {
    'g2': 'moog/004_Mighty%20Moog%20G2.wav',
    'g3': 'moog/005_Mighty%20Moog%20G3.wav',
    'g4': 'moog/006_Mighty%20Moog%20G4.wav'
  }
}, 'github:tidalcycles/dirt-samples')

note("g2!2 <bb2 c3>!2, <c4@3 [<eb4 bb3> g4 f4]>")
  .s('moog').clip(1).gain(.5)
```

## Sample Manipulation

### begin() - Skip Beginning
**Range**: 0-1 (fraction of sample)

```javascript
samples({ rave: 'rave/AREUREADY.wav' }, 'github:tidalcycles/dirt-samples')
s("rave").begin("<0 .25 .5 .75>").fast(2)
```

### end() - Cut End
**Range**: 0-1 (fraction of sample)

```javascript
s("bd*2, oh*4").end("<.1 .2 .5 1>").fast(2)
```

### loop() - Loop Sample
**Range**: 0 or 1

```javascript
s("casio").loop(1)
```

### loopBegin() / loopb()
**Range**: 0-1 (loop start point)

```javascript
s("space").loop(1).loopBegin("<0 .125 .25>")
```

### loopEnd() / loope()
**Range**: 0-1 (loop end point)

```javascript
s("space").loop(1).loopEnd("<1 .75 .5 .25>")
```

### cut()
Stops playing sample when another in same group plays

**Range**: Cut group number

```javascript
s("[oh hh]*4").cut(1)  // Hi-hats cut each other
```

### speed()
Changes playback speed and pitch

**Range**: Any number (negative = reverse)

```javascript
s("bd*6").speed("1 2 4 1 -2 -4")
speed("1 1.5*2 [2 1.1]").s("piano").clip(1)
```

## Advanced Sample Techniques

### chop() - Slice Sample
Cuts sample into equal parts

```javascript
samples({ rhodes: 'https://cdn.freesound.org/previews/132/132051_316502-lq.mp3' })
s("rhodes")
  .chop(4)      // Cut into 4 parts
  .rev()        // Reverse order
  .loopAt(2)    // Fit into 2 cycles
```

### striate() - Progressive Slicing
Cuts sample into parts, triggering progressive portions

```javascript
s("numbers:0 numbers:1 numbers:2").striate(6).slow(3)
```

### slice() - Trigger Slices
Chops and triggers specific slices

```javascript
samples('github:tidalcycles/dirt-samples')
s("breaks165")
  .slice(8, "0 1 <2 2*2> 3 [4 0] 5 6 7")
  .every(3, rev)
  .slow(0.75)

// Using specific positions
s("breaks125").fit()
  .slice([0,.25,.5,.75], "0 1 1 <2 3>")
```

### splice() - Slice with Speed Matching
Like slice, but matches playback speed to step duration

```javascript
samples('github:tidalcycles/dirt-samples')
s("breaks165").splice(8, "0 1 [2 3 0]@2 3 0@2 7")
```

### scrub() - Tape Scrubbing
Scrub through audio like a tape loop

```javascript
samples('github:switchangel/pad')
s("swpad:0").scrub("{0.1!2 .25@3 0.7!2 <0.8:1.5>}%8")

samples('github:yaxu/clean-breaks/main')
s("amen/4").fit().scrub("{0@3 0@2 4@3}%8".div(16))
```

### loopAt() - Fit to Cycles
Makes sample fit given number of cycles by changing speed

```javascript
samples({ rhodes: 'https://cdn.freesound.org/previews/132/132051_316502-lq.mp3' })
s("rhodes").loopAt(2)  // Fit to 2 cycles
```

### fit() - Fit to Event Duration
Makes sample fit its event duration

```javascript
samples({ rhodes: 'https://cdn.freesound.org/previews/132/132051_316502-lq.mp3' })
s("rhodes/2").fit()  // Fit to event
```

## Classic Drum Patterns

### Four-on-the-Floor (House)
```javascript
sound("bd*4, [~ cp]*2, [~ hh]*4").bank("RolandTR909")
```

### Basic Rock Beat
```javascript
setcpm(100/4)
sound("[bd sd]*2, hh*8").bank("RolandTR505")
```

### Breakbeat
```javascript
setcpm(90/4)
sound(`
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd],
[-  -  -  - ] [cp -  -  - ] [-  -  -  - ] [cp -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  hh - ],
[-  -  oh - ] [-  -  -  - ] [-  -  -  - ] [-  -  oh:1 - ]
`).bank("RolandTR808")
```

### "We Will Rock You" Pattern
```javascript
setcpm(81/2)
sound("bd*2 cp").bank("RolandTR707")
```

## Utility Functions

### soundAlias()
Creates custom aliases for sounds

```javascript
soundAlias('RolandTR808_bd', 'kick')
s("kick")  // Now plays RolandTR808_bd
```
