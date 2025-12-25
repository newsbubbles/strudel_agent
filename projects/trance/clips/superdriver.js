// {"name": "Superdriver", "tags": ["trance", "base set", "supersaw", "full on"], "tempo": 136, "description": "Use for big rising energy"}

setcpm(136/4)

// Acid Shape
register('acidenv', (x, p) => p.lpf(100)
  .lpenv(x * 9).lps(.2).lpd(.12)
)

// Superize for supersaw effect
register('superize', (x, p) => p.scale(scala).trans(-24).detune(rand)
  .o(4).acidenv(sine.range(0.2, .9).slow(orbit))
)

const orbit = 32
const arpHook = "<0 4 <7 4> <9 <9 7>>>*16"
const scala = "g4:minor"

// Arpy Supersaw
const superSaw = n(arpHook).s("supersaw").superize(1) 

// Lead texture
const texture = n(arpHook).s("square").scale(scala)
  .o(4).lpf(sine.range(200, 900).slow(orbit))
  .room(.4).size(10).gain(.6)

// Off texture for post buildup
const offTexture = texture.struct("<~ x*4>*4").superize(1)

// BD with slow orbit low pass filter to match supersaw
const superBD = s("bd:2!4").lpf(sine.range(300, 1600).slow(orbit))
  .duckorbit(4).duckattack(.1).duckdepth(.8)

// BD variations
const superBDHiSweep = superBD.hpf("<1500 1100 900 700 500 300 160 0>!4").duckorbit("<5 5 5 4>!16")
const superBDHi = superBD.hpf(1800).gain(.9).duckorbit(5)

// High Hats
const whiteHH = s("<- white>*8").o(4).clip(.1)
  .delay(.5).gain(.7)

// Sweep effects
const whiteSweep = s("white!4").att(.4).o(6).gain(.1)
const longSweepDown = s("white*16").o(5)
  .hpf(sine.range(2400, 300).slow(4)).lpf(3300).sustain(1)
  .gain(.1)

// Patterns
const pat = {
  intro: superSaw,
  driver: stack(superSaw, superBDHiSweep),
  fakeSilence: stack(texture, whiteSweep, superBDHi),
  feliz: stack(superSaw, superBD, whiteHH, offTexture),
  fakeOutro: stack(superSaw, superBDHi)
}

// Arrangement
$: arrange(
  [16, pat.intro],
  [8, pat.driver],
  [4, pat.fakeSilence],
  [16, pat.feliz],
  [4, pat.fakeOutro],
  
)._pianoroll()

