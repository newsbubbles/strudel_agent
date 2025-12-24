// {"name": "Trance Base", "tags": ["trance", "base", "rolling bass"], "tempo": 138, "description": "A simple base to start any trance song"}

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

