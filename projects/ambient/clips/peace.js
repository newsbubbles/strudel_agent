// {"name": "Peace", "tags": ["ambient", "pad", "rain", "layered", "peaceful"], "tempo": 60, "description": "Three-layer ambient pad with rain texture - warm, spacious, grounding", "author": null, "version": "1.0.3", "date": "2025-12-26"}
setcpm(60/4)

// Layer 1: Body (warm mid-range)
const padBody = note("<[c3,e3,g3] [a2,c3,e3]>")
  .s("sawtooth")
  .attack(1.5).release(2.5)
  .lpf(800)
  .gain(0.5)

// Layer 2: Air (bright, airy texture)
const padAir = note("<[c4,e4,g4] [a3,c4,e4]>")
  .s("triangle")
  .attack(2).release(3)
  .lpf(3000)
  .chorus(0.5)
  .gain(0.3)

// Layer 3: Sub (low grounding)
const padSub = note("<c2 a1>")
  .s("sine")
  .attack(2).release(3)
  .lpf(200)
  .gain(0.4)

const threeLayerPad = stack(padBody, padAir, padSub)
  .slow(2)
  .attack(.4)
  .sustain(1)
  .room(0.9)
  .size(20)
  .gain(sine.range(.1,.3).slow(2))

$: threeLayerPad

// Rain atmosphere (continuous)
$: s("white@8")
  .lpf(perlin.range(800, 3000).slow(8))
  .hpf(perlin.range(200, 600).slow(6))
  .gain(perlin.range(0.3, 0.6).slow(4))
  .pan(perlin.range(-0.7, 0.7).slow(5))
  .room(0.7)
  .size(0.9)
  .gain(.4)

// Individual rain drops
$: s("crackle").gain(perlin.range(0.5, 2).slow(16))
  .lpf(perlin.range(2000, 3000).slow(64))
  .density(perlin.range(0, .1).slow(32))
  .room(0.6)
  ._scope()