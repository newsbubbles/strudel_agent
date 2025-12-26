// {"name": "Layered Pads", "tags": ["ambient", "pad", "texture", "drone", "minimal"], "tempo": 60, "description": "Multi-layer pad foundation with wind texture and sub bass", "author": null, "version": "1.0.0", "date": "2025-12-26"}
setcpm(60/4)

samples('github:tidalcycles/dirt-samples')

const pad1 = note("c2 eb2 g2 bb2")
  .s("sawtooth")
  .slow(8)
  .lpf(400)
  .attack(4).release(6)
  .room(0.8).size(0.9)
  .gain(0.6)

const pad2 = note("eb3 g3 bb3")
  .s("square")
  .slow(12)
  .lpf(600)
  .attack(3).release(5)
  .room(0.7)
  .gain(0.5)
  .pan(sine.range(0.3, 0.7).slow(16))

const texture = s("wind:0")
  .chop(8)
  .slow(4)
  .lpf(800)
  .room(0.6)
  .gain(0.4)

const subBass = note("c1")
  .s("sine")
  .slow(2)
  .gain(0.8)

$: stack(
  pad1,
  pad2, 
  texture,
  subBass
)._scope()