# Strudel Musical Patterns Library

**Research Date**: 2025-12-22

A collection of proven musical patterns and techniques for live coding with Strudel.

## Drum Patterns

### Basic Beats

#### Four-on-the-Floor (House/Techno)
```javascript
// Classic house beat
$: sound("bd*4, [~ cp]*2, [~ hh]*4").bank("RolandTR909")
```

```javascript
// With open hi-hat accents
$: sound("bd*4, [~ cp]*2, hh*6 [hh oh]").bank("RolandTR909")
```

#### Rock Beat
```javascript
// Basic rock
setcpm(100/4)
$: sound("[bd sd]*2, hh*8").bank("RolandTR505")
```

```javascript
// With variations
setcpm(100/4)
$: sound("bd [~ sd] bd sd, hh*8, ~ ~ oh ~").bank("RolandTR808")
```

#### Breakbeat
```javascript
// Amen break style
setcpm(90/4)
$: sound(`
bd -  -  -  -  -  bd bd,
-  -  sd -  -  -  sd -,
hh hh hh hh hh hh hh hh
`).bank("RolandTR909")
```

```javascript
// With sample variations
setcpm(90/4)
$: sound("bd*2 [~ bd] bd, ~ sd ~ sd:1, hh*8")
  .bank("RolandTR808")
```

#### Hip-Hop
```javascript
// Boom bap
setcpm(85/4)
$: sound(`
bd -  -  -  bd -  -  -,
-  -  sd -  -  -  sd -,
[hh hh] -  hh -  [hh hh] -  hh -
`).bank("AkaiLinn")

// With swing
$: sound("bd ~ ~ ~ bd ~ ~ ~, ~ ~ sd ~ ~ ~ sd ~")
  .late("[0 .01]*4")  // Adds shuffle
  .bank("RolandTR808")
```

### Advanced Drum Patterns

#### 16-Step Sequencer Style
```javascript
setcpm(90/4)
$: sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  -  - ] [-  -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  hh - ],
[-  -  -  - ] [cp -  -  - ] [-  -  -  - ] [cp -  -  - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd]
`).bank("RolandTR808")
```

#### Polyrhythmic Drums
```javascript
// 3 against 4
$: sound("{bd bd bd, sd:2 sd:1 sd:2 sd:1}")

// Layered polyrhythms
$: sound(`
bd*3,
sd*4,
hh*5,
cp*2
`).gain(.7)
```

#### Euclidean Rhythms
```javascript
// Distribute events evenly
$: sound("bd(5,8), sd(3,8), hh(7,8)")
  .bank("RolandTR909")

// With rotation
$: sound("bd(5,8,2), sd(3,8,1), hh(7,8,3)")
```

## Basslines

### Simple Bass Patterns

```javascript
// Root note bass
$: note("<c2 bb1 f2 eb2>")
  .s("sawtooth")
  .lpf(800)

// With rhythm
$: note("<[c2 c3]*4 [bb1 bb2]*4 [f2 f3]*4 [eb2 eb3]*4>")
  .s("sawtooth")
  .lpf(800)

// Octave jumps
$: note("c2 c3 <bb1 bb2> <f2 f3>")
  .s("sawtooth,triangle")
  .lpf(600)
```

### Funky Bass

```javascript
// Syncopated
$: note("c2 ~ [eb2 f2] ~ c2 ~ g2 ~")
  .s("sawtooth")
  .lpf(1000)
  .lpenv(2)
  .decay(.1)
  .sustain(0)

// With slides
$: note("c2@3 eb2, eb2@3 f2, f2@3 g2, g2@3 c3")
  .s("sawtooth")
  .lpf(800)
  .clip(.8)
```

### Walking Bass

```javascript
// Jazz walking bass
$: n("0 2 4 5, 3 5 7 8, 5 7 9 10, 7 9 11 12")
  .scale("C2:major")
  .s("gm_acoustic_bass")
  .slow(2)

// With chromatic approach
$: n("0 2 3 4, 3 5 6 7, 5 7 8 9, 7 9 10 11")
  .scale("C2:major")
  .s("sawtooth")
  .lpf(600)
```

## Melodic Patterns

### Arpeggios

```javascript
// Basic up arpeggio
$: n("0 2 4 7").scale("C4:minor")
  .s("triangle")
  .release(.5)

// Up and down / up and down
$: n("0 2 4 7 4 2").scale("<C2:minor C3:minor C4:minor C3:minor>")
  .s("square")
  .lpf(2000)

// Complex arpeggio
$: n("<[0 2 4 7]*2 [0 3 5 8]*2>")
  .scale("C4:minor")
  .s("sawtooth")
  .lpf(1500)
  .delay(.25)
```

### Sequences

```javascript
// Pentatonic sequence
$: n("0 2 3 5 7 5 3 2").scale("C4:minor:pentatonic")
  .s("piano")
  .room(.3)

// With rhythm variation
$: n("0 [2 3] 5 [7 5] 3 2")
  .scale("C4:minor:pentatonic")
  .s("gm_xylophone")

// Octave jumps
$: n("0 7 12 7 0 -5 0 7")
  .scale("C3:minor")
  .s("sawtooth")
  .lpf(2000)
```

### Generative Melodies

```javascript
// Random Bassline
$: n(irand(8)).struct("x x*2 x x*3").scale("C1:minor:pentatonic")
  .s("sawtooth").fm(3).orbit(2)
  .room(.5).duckorbit(2).duckattack("<0.06 <0 0.1 0 0.15> 0.08>").duckdepth(1)

// Bass accompanying lead following same random pattern
$: n(irand(8)).struct("x <x*2 x*3> x <x*3 x*2>").scale("C5:minor:pentatonic")
  .s("square").gain(0.3).orbit(2)
  .delay(.5).room(.8).size(4).duckorbit(2).duckattack("<0.06 <0 0.1 0 0.15> 0.08>").duckdepth(1)

// Constrained randomness
$: n("<0 2 4> <[0 2] [3 5]> <[4 7] [5 8]>")
  .scale("C4:minor")
  .s("piano")

// With probability
$: n("0 [2|3|4] [5|7] [7|9|11]")
  .scale("C4:minor")
  .s("piano")
```

## Chord Progressions

### Basic Progressions

```javascript
// I-IV-V-I
$: chord("<C F G C>")
  .voicing()
  .s("piano")
  .room(.5)

// ii-V-I (jazz)
$: chord("<Dm7 G7 C^7>")
  .voicing()
  .s("gm_electric_piano")

// I-vi-IV-V (pop)
$: chord("<C Am F G>")
  .voicing()
  .s("sawtooth")
  .lpf(2000)
  .room(.4)
```

### Complex Progressions

```javascript
// Modal interchange
$: chord("<C^7 Fm7 C^7 Ab^7>")
  .voicing()
  .s("gm_epiano1")
  .phaser(4)
  .room(.5)

// With rhythm
$: chord("<[C^7 C^7] [Dm7 Dm7] [Em7 Em7] [F^7 F^7]>")
  .voicing()
  .s("piano")
  .gain("<1 .8 .9 .7>")

// Stacked voicings
$: chord("<Bbm9 Fm9>/4")
  .offset(-1)
  .voicing()
  .s("gm_epiano1:1")
  .phaser(4)
  .room(.5)
```

## Rhythmic Techniques

### Polymeters

```javascript
// Different cycle lengths
$: sound("bd*4").fast(1)      // 4/4
$: sound("sd*3").fast(1)      // 3/4 over 4/4
$: sound("hh*5").fast(1)      // 5/4 over 4/4
```

### Phasing

```javascript
// Steve Reich style
$: note("c e g c").s("piano")
$: note("c e g c").s("piano").late(.01)
$: note("c e g c").s("piano").late(.02)
```

### Swing/Shuffle

```javascript
// Using elongation
$: n("<[4@2 4] [5@2 5] [6@2 6] [5@2 5]>*2")
  .scale("C2:mixolydian")
  .s("gm_acoustic_bass")

// Using late()
$: sound("hh*8")
  .late("0 .01 0 .01 0 .01 0 .01")
```

## Pattern Transformations

### Using rev()

```javascript
// Reverse melody
$: n("0 2 4 6").scale("C4:minor")
  .s("piano")
  .rev()

// Alternating reverse
$: n("0 2 4 6").scale("C4:minor")
  .s("piano")
  .every(2, rev)
```

### Using jux()

```javascript
// Stereo reverse
$: n("0 1 [4 3] 2").sound("jazz")
  .jux(rev)

// Stereo speed variation
$: sound("bd sd hh cp")
  .jux(fast(2))

// Stereo pitch shift
$: n("0 2 4 6").scale("C4:minor")
  .s("piano")
  .jux(x => x.add(7))
```

### Using off()

```javascript
// Echo with harmony
$: n("0 [4 <3 2>] <2 3> [~ 1]")
  .off(1/16, x => x.add(4))  // Add fourth above
  .scale("C5:minor")
  .s("triangle")

// Delayed variation
$: sound("bd sd [~ bd] sd")
  .off(1/8, x => x.speed(1.5))

// Complex delay network
$: n("0 <2 1> 4 6")
  .scale("C4:minor")
  .s("piano")
  .off(1/16, x => x.add(7))
  .off(1/8, x => x.add(12))
```

### Using add()

```javascript
// Transposition
$: note("c2 [eb3,g3]")
  .add("<0 <1 -1>>")
  .s("gm_acoustic_bass")

// Chord building
$: n("0 [2 4] <3 5> [~ <4 1>]")
  .add("<0 [0,2,4]>")  // Add chord tones
  .scale("C5:minor")
  .s("gm_xylophone")
```

## Complete Musical Examples

### Minimal Techno

```javascript
setcpm(126/4)

$: sound("bd*4").bank("RolandTR909")

$: sound("~ cp ~ cp").bank("RolandTR909")
   .gain(.8)

$: sound("hh*8").bank("RolandTR909")
   .gain("<.6 .8>")
   .n("0 1 2 1")

$: note("<c2 c2 bb1 f2>*4")
   .s("sawtooth")
   .lpf(sine.range(400, 1200).slow(8))
   .lpq(10)
   .gain(.5)
   .room(.2)
```

### Ambient Pad

```javascript
setcpm(30/4)

$: note("<[c2,e2,g2] [d2,f2,a2] [e2,g2,b2] [f2,a2,c3]>")
   .s("sawtooth,triangle")
   .attack(2)
   .release(3)
   .lpf(1500)
   .vib(3)
   .vibmod(0.3)
   .room(.9)
   .gain(.3)

$: note("<c4 d4 e4 f4>")
   .s("sine")
   .delay(.5)
   .room(.8)
   .gain(.2)
   .slow(4)
```

### Jazz Comping

```javascript
setcpm(120/4)

$: chord("<Dm7 G7 C^7 A7>")
   .voicing()
   .s("gm_electric_piano")
   .gain("~ .8 ~ .9 ~ .7 ~ 1")
   .room(.4)

$: n("<0 2 4 5 7 9 11 12>".slow(2))
   .scale("C3:major")
   .s("gm_acoustic_bass")
   .clip(.8)

$: sound("~ rim ~ rim")
   .bank("RolandTR707")
   .gain(.6)

$: sound("hh*4")
   .bank("RolandTR707")
   .n("<0 1 2 1>")
   .gain(".4 .7 .5 .8")
```

### Dub Techno

```javascript
setcpm(120/4)

$: sound("bd*4")
   .bank("RolandTR909")
   .delay(.4)
   .delayfeedback(.7)

$: sound("~ cp")
   .bank("RolandTR909")
   .delay(.5)
   .room(.6)

$: sound("hh*8")
   .bank("RolandTR909")
   .n("<0 1 2 3>")
   .gain("<.4 .6>")

$: note("<c2 bb1 f2 eb2>*2")
   .s("sawtooth")
   .lpf(800)
   .delay(.5)
   .delaytime(".25 .375")
   .delayfeedback(.6)
   .room(.7)
   .gain(.4)

$: chord("<C7 Bb7 F7 Eb7>")
   .voicing()
   .s("sawtooth")
   .lpf(2000)
   .delay(.5)
   .room(.8)
   .gain(.2)
   .slow(2)
```

### Breakcore

```javascript
setcpm(180/4)

samples('github:tidalcycles/dirt-samples')

$: s("breaks165")
   .slice(8, "0 1 <2 2*2> 3 [4 0] 5 6 7")
   .every(3, rev)
   .slow(0.75)
   .gain(.8)

$: note("<c2 eb2 f2 g2>*4")
   .s("sawtooth")
   .lpf(600)
   .distort(2)
   .gain(.5)

$: sound("bd*4")
   .bank("RolandTR909")
   .gain("<1 .8 .9 .7>")
```

## Tips for Creating Patterns

1. **Start with rhythm**: Build drums first, then add melodic elements
2. **Layer gradually**: Add one element at a time
3. **Use space**: Rests are as important as notes
4. **Vary dynamics**: Use `.gain()` patterns for expression
5. **Add movement**: Animate filters, panning, effects
6. **Create contrast**: Alternate between busy and sparse sections
7. **Use randomness**: But constrain it musically
8. **Think in cycles**: Patterns that resolve over 2, 4, or 8 cycles
9. **Experiment with time**: Use `.slow()`, `.fast()`, `.every()`
10. **Save variations**: Store patterns in variables for easy recall
