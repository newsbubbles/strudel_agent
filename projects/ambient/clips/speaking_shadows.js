// {"name": "Speaking Shadows", "tags": ["ambient", "chaos", "adventure-time", "glitch", "weird", "melodic", "dissonant", "organic"], "tempo": 75, "description": "Chaotic ambient with wobbling voices that emerge like jump scares then settle into strange speech - beautiful dissonance meets structured harmony", "author": null, "version": "1.0.0", "date": "2025-12-26"}
setcpm(75/4)

samples('github:tidalcycles/dirt-samples')

const weirdBass = note("<c1 f1 ab1 eb1>")
  .s("square")
  .slow(4)
  .lpf(sine.range(200, 600).slow(7))
  .distort(0.3)
  .gain(0.8)
  .room(0.4)

const glitchMelody = note("<<c5 [c5 g5]> <eb5 [eb5 bb5]> <f5 [f5 c6]> <ab4 [ab4 eb5]>>")
  .s("glockenspiel")
  .slow(2)
  .sometimes(x => x.speed(rand.range(0.8, 1.2)))
  .delay(rand.range(0.3, 0.8))
  .delaytime("<0.25 0.375 0.5>")
  .room(0.9)
  .gain(0.6)
  .pan(rand)

const chaosPad = note("[c3,eb3,g3,bb3]")
  .s("<sawtooth square triangle>")
  .slow(8)
  .lpf(perlin.range(400, 1200).slow(11))
  .attack(rand.range(1, 3))
  .release(rand.range(2, 5))
  .room(0.7)
  .gain(sine.range(0.4, 0.7).slow(13))
  .pan(cosine.range(0.2, 0.8).slow(9))

const strangePerc = s("<alphabet:3 alphabet:7 ~ alphabet:11>")
  .speed(rand.range(1.5, 3))
  .delay(0.6)
  .room(0.8)
  .gain(0.5)
  .pan(rand)

const wobbleOrgan = note("<c4 eb4 f4 ab4>")
  .s("triangle")
  .slow(4)
  .lpf(sine.range(600, 2000).slow(5))
  .vib("<3 5 7>")
  .vibmod(sine.range(0.3, 0.8).slow(6))
  .room(0.6)
  .gain(0.5)
  .pan(sine.range(0.3, 0.7).slow(7))

const dreamKick = s("bd")
  .slow(2)
  .sometimes(x => x.speed(0.7))
  .lpf(400)
  .room(0.5)
  .gain(0.7)

const frame1 = stack(weirdBass, chaosPad)
const frame2 = stack(weirdBass, chaosPad, glitchMelody)
const frame3 = stack(weirdBass, chaosPad, glitchMelody, strangePerc)
const frame4 = stack(weirdBass, chaosPad, glitchMelody, wobbleOrgan, dreamKick)
const frame5 = stack(chaosPad, glitchMelody, wobbleOrgan, strangePerc)

$: arrange(
  [4, frame1],
  [4, frame2],
  [8, frame3],
  [8, frame4],
  [4, frame5]
)._scope()._pianoroll()