// {"name": "Minecraft 1", "tags": ["ambient", "minecraft", "piano", "bells", "arranged", "peaceful"], "tempo": 60, "description": "Minecraft-inspired ambient arrangement with piano, bells, pads and wind texture", "author": "Strudelmon", "version": "1.0.0", "date": "2025-12-27"}
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

const piano = note("<<c4 [c4 eb4]> <eb4 [eb4 g4]> <g4 [g4 bb4]> ~ <bb4 [bb4 g4]> ~ <g4 [g4 eb4]> <eb4 [eb4 c4]>>")
  .s("piano")
  .slow(4)
  .velocity(0.6)
  .room(0.9).size(0.9)
  .delay(0.6).delaytime(0.375)
  .gain(0.8)
  .release(4)

const bellMelody = note("~ <g5 [g5 c6]> ~ ~ <c5 [c5 eb5]> ~ ~ <eb5 [eb5 g5]> ~ ~ ~ <bb4 [bb4 eb5]> ~ ~ ~ ~")
  .s("glockenspiel")
  .slow(2)
  .velocity(0.5)
  .room(0.95)
  .delay(0.7).delaytime(0.5)
  .gain(0.6)
  .release(3)

const deepPiano = note("c2 ~ ~ ~ eb2 ~ ~ ~ g2 ~ ~ ~ bb2 ~ ~ ~")
  .s("piano")
  .slow(4)
  .velocity(0.5)
  .lpf(600)
  .room(0.8)
  .gain(0.7)
  .release(6)

const frame1 = stack(pad1, subBass, texture)
const frame2 = stack(pad1, pad2, subBass, texture, deepPiano)
const frame3 = stack(pad1, pad2, subBass, texture, piano)
const frame4 = stack(pad1, pad2, subBass, texture, piano, bellMelody)
const frame5 = stack(pad2, texture, piano, bellMelody)

$: arrange(
  [8, frame1],
  [8, frame2],
  [8, frame3],
  [16, frame4],
  [4, frame5]
)._scope()._pianoroll()