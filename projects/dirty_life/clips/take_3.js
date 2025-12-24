setcps(86.6/4)

// Drum variations for progressive build: simple groove -> adding layers -> climactic fill
const drumsSimple = sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  -  - ] [-  -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  hh - ],
[-  -  -  - ] [cp -  -  - ] [-  -  -  - ] [cp -  -  - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd]
`).bank("RolandTR808").compressor(0.5)._punchcard()

const drumsBuilding = sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  oh - ] [-  -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  <hh oh:1 hh> - ],
[-  -  -  - ] [cp -  -  - ] [-  -  cp - ] [cp -  -  - ],
[-  -  -  - ] [-  -  -  - ] [-  -  sd - ] [sd -  sd - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd]
`).bank("RolandTR808").compressor(0.6)._punchcard()

const drumsFill = sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  oh - ] [-  -  <oh oh oh> - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh*3 -  <hh oh:1 hh*2> - ],
[-  -  -  - ] [cp -  -  - ] [-  -  cp - ] [<cp cp cp> -  - ],
[-  -  -  - ] [-  -  -  - ] [-  -  sd - ] [<sd sd sd sd> -  sd - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  bd <bd bd bd*4> - ]
`).bank("RolandTR808").compressor(0.7)._punchcard()

// Arrange drums over 16 bars: 8 bars simple, 6 building, 2 fill
$: arrange([7, drumsSimple], [1, drumsBuilding], [4, drumsFill])._punchcard()

// Funky Raw Bass with Variations
// Define bass groups: A (groovy syncopation), B (driving path), C (complex funk)
const bassA = note("c1 [eb1 ~ g1] bb1 [~ ab1 g1]").s("sawtooth").lpf(500)
const bassB = note("[c1 eb1] g1 bb1 eb1 [g1 ~]").s("sawtooth").lpf(600)
const bassC = note("c1 eb1 [g1~ bb1] [ab1 g1 eb1]").s("sawtooth").lpf(400).ply(2)

// Mid bass: <A B C> cycles through
$: note("<c1 [eb1 ~ g1] bb1 [~ ab1 g1] [c1 eb1] g1 bb1 eb1 [g1 ~] c1 eb1 [g1~ bb1] [ab1 g1 eb1]>")
  .s("square").octave(1).phaser("<2 4 2 4 2 8 2 4>")
  .lpf("<500 600 400>").dist(0.3).gain(0.8)
  ._scope()

// Or arrange sections: [4, bassA], [8, bassB], [4, bassC] for A (4 cycles) -> B (8) -> C (4)
$: arrange([4, bassA], [8, bassB], [4, bassC]).s("sawtooth").dist(0.3).gain(0.8)

// Piano layer: punchier hits with sharp envelope, compression, and dynamic gain
$: note("<c3 eb3 g3 bb3> ~ <eb3 g3 bb3 c4> ~")
  .s("piano")
  .attack(0.01).decay(0.05).sustain(0.4).release(1)
  .gain("<1 0.6 0.8>").hpf(150).compressor("0.4:3:0.1:0.01:0.1")
  .room(0.6).delay(0.2).lpf(1800)
  .gain(0.7)

// Arpeggiated piano variation: sometimes on, breaking chords into fast up/down sequences
$: note("<[c3 eb3 g3 bb3]/4 [eb3 g3 bb3 d4]/4>")
  .sometimes(x => x)
  .s("piano")
  .attack(0.01).decay(0.03).sustain(0.3).release(0.8)
  .gain("<0.9 0.5>").hpf(200).compressor("0.3:4:0.05:0.01:0.1")
  .room(0.5).delay(0.15).lpf(2000).gain(0.5)