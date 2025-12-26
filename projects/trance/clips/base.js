// {"name": "Trance Base", "tags": ["trance", "base", "rolling bass"], "tempo": 138, "description": "A simple base to start any trance song"}
setcps(138/60)

$: sound("bd:4 ~").hpf(60)
  .duckorbit(2).duckattack(0.1).duckdepth(1)
  .gain(0.4)

const s8 = "<[C1:Minor C1:Major E1:Minor E1:Major]@8>"
const s4 = "<[C1:Minor C1:Major E1:Minor E1:Major]@4>"
const s2 = "<[C1:Minor C1:Major E1:Minor E1:Major]@2>"

$: note("0 0 2 0").scale(s8)
  .s("sawtooth")
  .lpf(sine.range(300, 600).slow(8))
  .detune(5)
  .attack(0.005)
  .decay(0.15)
  .sustain(0.3)
  .release(0.1)
  .gain(0.7)
  .orbit(2)
  .room(0.1)
  ._scope()