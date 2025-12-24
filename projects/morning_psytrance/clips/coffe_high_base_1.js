//Morning Trance: Coffee High Bases 1
setcps(145/240)

// Drums
$: sound("bd:1*4").gain(0.9) // bd 1 on default set is more trancey
$: sound("hh*8").gain(0.3).pan(sine.range(-0.5,0.5))

// Mid lead
$: note("[bb1 c2 c3 eb2]*4")
  .s("sawtooth")
  .fm(4).orbit(2)
  .attack(0.01).decay(0.2)
  .lpf(400).hpf(150).gain(0.8)
  .room(0.7).delay(.5)

// High lead
$: note("eb5 ~ [eb3,g3]")
  .s("square")
  .fm(4).orbit(2)
  .attack(0.1).decay(0.06)
  .distort(2)
  .lpf(400).hpf(150).gain(0.2)
  .room(0.7).delay(.5)