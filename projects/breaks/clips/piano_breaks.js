// {"name": "Classical Breaks Symphony", "tags": ["breaks", "breakbeat", "piano", "dnb", "jungle", "classical", "glitch"], "tempo": 140, "description": "Drum & bass with classical piano composition, chopped amen breaks, extended bass patterns, and glitch effects"}
samples('github:tidalcycles/Dirt-Samples')

setcpm(140/2)

// === BREAKS ===

const amenMain = s("breaks165")
  .loopAt(2)
  .chop(16)
  .gain(.85)
  .cut(1)

const amenVar = s("breaks165")
  .loopAt(2)
  .slice(16, "<[0 2 4 6 8 10 12 14] [1 3 5 7 9 11 13 15] [0 4 8 12 2 6 10 14] [[7 7] 5 3 1 [15 15 15] 13 11 9]>")
  .gain(.85)
  .cut(1)

const amenFast = s("breaks165")
  .loopAt(2)
  .chop(32)
  .gain(.9)
  .cut(1)
  .sometimesBy(.4, ply(2))

const amenGlitch = s("breaks165")
  .loopAt(2)
  .chop(16)
  .gain(.85)
  .cut(1)
  .sometimesBy(.5, ply(3))
  .sometimesBy(.2, x => x.speed("-1"))
  .crush("<16 8 4>")

const amenSparse = s("breaks165")
  .loopAt(2)
  .slice(16, "0 ~ ~ ~ 4 ~ ~ ~ 8 ~ ~ ~ 12 ~ ~ ~")
  .gain(.7)
  .cut(1)

// === BASS ===

const subBass = note(`
  <
    [c1 c1 c1 c1] [c1 c1 g1 c1] [c1 eb1 c1 c1] [c1 c1 g1 ab1]
    [c1 c1 c1 c1] [c1 eb1 f1 g1] [c1 c1 c1 ab1] [c1 g1 f1 eb1]
    [c1 c1 c1 g1] [c1 c1 eb1 c1] [f1 f1 c1 c1] [g1 ab1 g1 f1]
    [c1 eb1 c1 c1] [c1 c1 g1 c1] [ab1 g1 f1 eb1] [c1 c1 c1 c1]
  >
`)
  .s("sine")
  .lpf(100)
  .gain(.6)
  .orbit(1)
  .slow(4)

const reeseBass = note(`
  <
    [c1 c1 c1 c1] [c1 c1 g1 c1] [c1 eb1 c1 c1] [c1 c1 g1 ab1]
    [c1 c1 c1 c1] [c1 eb1 f1 g1] [c1 c1 c1 ab1] [c1 g1 f1 eb1]
    [c1 c1 c1 g1] [c1 c1 eb1 c1] [f1 f1 c1 c1] [g1 ab1 g1 f1]
    [c1 eb1 c1 c1] [c1 c1 g1 c1] [ab1 g1 f1 eb1] [c1 c1 c1 c1]
  >
`)
  .s("sawtooth")
  .lpf(sine.range(200, 600).slow(16))
  .detune("5")
  .gain(.4)
  .orbit(2)
  .slow(4)

// === PIANO - CLASSICAL STYLE ===

const pianoMelody = note(`
  <
    [c5 eb5 g5 c6] [bb4 d5 f5 bb5] [ab4 c5 eb5 ab5] [g4 bb4 d5 g5]
    [f4 ab4 c5 f5] [eb4 g4 bb4 eb5] [d4 f4 ab4 d5] [c4 eb4 g4 c5]
    [g4 bb4 d5 g5] [f4 ab4 c5 f5] [eb4 g4 bb4 eb5] [d4 f4 ab4 d5]
    [c4 eb4 g4 c5] [bb3 d4 f4 bb4] [ab3 c4 eb4 ab4] [g3 bb3 d4 g4]
  >
`)
  .s("piano")
  .velocity("<.65 .7 .6 .75 .8 .65 .7 .72 .68 .75 .7 .65 .8 .7 .65 .6>")
  .release(.8)
  .lpf(12000)
  .room(.35)
  .delay(.15)
  .dfb(.2)
  .gain(.75)
  .slow(8)

const pianoChords = note(`
  <
    [c3,eb3,g3,c4] ~ [bb2,d3,f3,bb3] ~
    [ab2,c3,eb3,ab3] ~ [g2,bb2,d3,g3] ~
    [f2,ab2,c3,f3] ~ [eb2,g2,bb2,eb3] ~
    [d2,f2,ab2,d3] ~ [c2,eb2,g2,c3] ~
  >
`)
  .s("piano")
  .velocity("<.5 ~ .55 ~ .52 ~ .58 ~ .5 ~ .54 ~ .56 ~ .6 ~>")
  .release(1.2)
  .room(.4)
  .gain(.65)
  .slow(4)

const pianoAccents = note("~ ~ <[c6,eb6,g6] [f6,ab6,c7]> ~")
  .s("piano")
  .velocity(.85)
  .release(.6)
  .lpf(10000)
  .room(.3)
  .gain(.6)
  .slow(2)

// === SNARE LAYERING ===

const snareLayer = s("~ sd ~ sd")
  .gain(.4)
  .lpf(8000)
  .room(.2)

// === ATMOSPHERE ===

const pad = note("<c3 d3 c3 f3>")
  .s("sine,triangle")
  .slow(4)
  .lpf(sine.range(300, 700).slow(32))
  .attack(1.5)
  .decay(2)
  .gain(.25)
  .room(.8)
  .orbit(3)

const crackle = s("cr:4").slow(8).gain(.15).lpf(4000)

// === TRANSITIONS ===

const riser = s("white")
  .lpf(sine.range(1000, 12000).slow(4))
  .hpf(sine.range(200, 2000).slow(4))
  .gain(sine.range(.2, .7).slow(4))

const crashHit = s("~ ~ ~ cr:0")
  .gain(.6)
  .room(.5)
  .slow(4)

const fillRoll = s("~ ~ ~ [sd*8]")
  .gain("<.4 .5 .6 .7 .5 .6 .7 .8>")
  .slow(8)

// === SECTIONS ===

const intro = stack(
  amenMain,
  subBass,
  crackle
)

const verse = stack(
  amenMain,
  subBass,
  reeseBass.gain(.3),
  pianoMelody.gain(.5),
  pianoChords.gain(.5),
  crackle
)

const chorus = stack(
  amenVar,
  subBass,
  reeseBass,
  pianoMelody,
  pianoChords,
  pianoAccents,
  snareLayer,
  pad.gain(.2),
  crackle
)

const drop = stack(
  amenFast,
  subBass,
  reeseBass,
  pianoMelody,
  pianoChords,
  pianoAccents,
  snareLayer,
  pad.gain(.2),
  crackle,
  crashHit
)

const dropGlitch = stack(
  amenGlitch,
  subBass,
  reeseBass.gain(.5),
  pianoMelody.crush(8),
  pianoChords,
  snareLayer.sometimesBy(.3, ply(2)),
  pad.gain(.15),
  crackle
)

const breakdown = stack(
  amenSparse,
  pianoMelody.gain(.9),
  pianoChords.gain(.7),
  pad.gain(.4),
  crackle.gain(.25)
)

const build = stack(
  s("breaks165").loopAt(2).chop("<16 32 64>").gain(.8).cut(1),
  s("~!6 [hh*16]").slow(8).gain(.5),
  subBass.gain(.5),
  pianoMelody.lpf(sine.range(12000, 400).slow(4)),
  riser,
  fillRoll
)

// === ARRANGEMENT ===
$: arrange(
  [8, intro],
  [16, verse],
  [16, chorus],
  [8, breakdown],
  [4, build],
  [1, s("~")],
  [16, drop],
  [8, dropGlitch],
  [8, verse],
  [8, breakdown]
)._scope()

// === MASTERING ===
all(x => x
  .compressor("-12:4:5:0.01:0.15")
  .postgain(1.15)
  .hpf(25)
  .lpf(17000)
  .clip(0.95)
)