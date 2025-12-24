// {"name": "Suzy", "tags": ["trance", "arps", "rolling bass", ], "tempo": 138, "description": "Suzy just don't quit"}

setcps(138/60)

// 4x4 Bass Kick
$: sound("bd:4 ~").hpf(60)
  .duckorbit(2).duckattack(0.1).duckdepth(1)
  .gain(0.4)

// Traveling Bass Synth
$: note("c1 eb1 f1 g1").s("sawtooth")
  .attack(0.01).decay(0.1)
  .duckorbit(2).duckattack(0.1).duckdepth(1)
  .lpf(300).hpf(100)
  .gain(0.9)

// Closed hi-hats with subtle pan
$: sound("~ <hh:1 hh:1 hh:1 <hh:1 hh:1>>").gain(1.4).hpf(2800)
  .pan(sine.range(-0.2,0.2)).late(0.001)
  .room(.5)
  .gain(.7)

// Evolving nested arpeggio
const arpBase = n("0 [2 4] 7 [7 4] [2 0]").scale("C4:minor").s("sawtooth")
  .lpf(1200).hpf(200).gain(0.3).attack(0.02).decay(0.2).room(0.4)
  .fast(2)

$: arpBase.firstOf(4, x => x.fast(2)) // Speed up first cycle
  .chunk(4, x => x.rev()) // Reverse in second part
  .lastOf(2, x => x.add(12)) // Octave up in last cycles

// Offbeat finger snaps
$: sound("~ cp:1").slow(2)
  .room(0.3).late(0.02)
  .gain(0.4)

// High lead synth with evolving FM
$: note("eb5 g5 bb5 c6").s("square")
  .clip("<.4!4 .3!2 .6!4 1!2>")
  .lpf(1500).hpf(400)
  .gain(0.25).room(0.6)
  .attack(sine.range(0, 0.05).slow(4))
  .decay(perlin.range(0, 0.15)).fm(4).orbit(sine.range(1,3))
  .firstOf(4, x => x.fast(1.5)).chunk(2, x => x.add(12))

// White noise riser for build
$: sound("white")
  .hpf(200).lpf(sine.range(200, 4000).slow(4))
  .gain(perlin.range(0, perlin.range(0.3, 0.5).slow(32)).slow(8)).room(0.9).delay(0.3)
  .struct("~ x ~ ~").firstOf(8, x => x).early(.2)