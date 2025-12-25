// {"name": "Wavey Base with Transitions", "tags": ["trance", "base set", "droning dynamic bass", "progressive trance"], "tempo": 130, "description": "Great for a drone-like base to build on"}

samples('github:bubobubobubobubo/dough-waveforms')

setcpm(130/4)

// Drum Set
const bd4 = s("bd:1*4").lpf(300).gain(.7)
const hh8 = s("<- hh>*8").gain(.13).sometimesBy(.05, ply(3))
const sd2 = s("~ white ~ white")
  .clip(.05).lpf(1900).lpenv(-2.0).lpa(.2)
  .room(.4).size(1)
  .gain(.4)

// Droning Orbiting Bass
const droneBass = note("c2*8").s("sawtooth").gain(0.5)
  .lpf(perlin.range(100,1000).slow(8))
  .lpenv(sine.range(-3.0, 4.0).slow(16)).lpa(.1).room(.5).fast(2)
  ._scope()

// Drone Hi (matching bass)
const droneHi = note("c4*8").s("sawtooth")
  .n(run(8))
  .lpf(900).lpenv(sine.range(-3.0, 4.0).slow(16)).lpa(.2)
  .room(.9).size(20)
  .gain(.1)
  //._scope()

const hardLead = note("0*4".layer(x=>x.add("0,2"))).scale("C4:minor").s("sawtooth").n(run(4))
  .lpf(900).lpenv(sine.range(-3.0, 4.0).slow(16)).lpa(.2)
  .room(.9).size(20)
  .sometimesBy(.1, ply("<3 4>"))
  .gain(.1)

// Transitions
const subtleBuild = stack(
  s("white*16").gain(0.1).room(0.6).lpf(sine.range(500, 2000).fast(4)),
  note("c3").s("sine").gain(sine.range(0, 0.3).slow(4)).lpf(sine.range(200, 800).slow(4))
)

const breakdownFade = stack(
  droneHi.gain(sine.range(0.1, 0).slow(2)).room(sine.range(0.9, 1.2).slow(2)),
  s("crash").gain(0.3).room(1)
)

const riserToDrop = stack(
  note("c4*16").s("sawtooth").gain(sine.range(0, 0.4).slow(4)).lpf(sine.range(100, 8000).slow(4)).hpf(200),
  sd2.fast(2).gain(sine.range(0, 0.8).slow(4))
)

const windDown = stack(
  hardLead.gain(sine.range(0.1, 0).slow(4)).room(1.2),
  s("~").gain(0).room(1)  // Silence with reverb tail
)

// Patterns
const pat = {
  intro: droneBass,
  drive: stack(droneBass, bd4),
  foreshadow: stack(droneBass, bd4, hh8, droneHi),
  fakeSilence: stack(droneHi),
  fullOn: stack(droneBass, bd4, hh8, sd2, droneHi, hardLead),
  outro: stack(droneBass, hardLead),
}

// Transitioned Patterns
const introWithEnd = pat.intro.lastOf(15, x => stack(x, s("oh*8").gain(0.2).room(0.5)))
const driveWithEnd = pat.drive.lastOf(7, x => stack(x, s("white*16").gain(0.3).lpf(1500)))
const foreshadowWithEnd = pat.foreshadow.lastOf(15, x => stack(x, hh8.fast(2).gain(0.4)))
const fakeSilenceWithStart = pat.fakeSilence.firstOf(1, x => stack(x, s("white*4").gain(0.2).clip(0.1).room(0.8)))
const fullOnWithEnd = pat.fullOn.lastOf(22, x => stack(x, s("hh*32").gain(sine.range(0.1, 0.7).slow(4))))
const outroWithEnd = pat.outro.lastOf(14, x => stack(x, note("c2").s("sine").gain(sine.range(0.1, 0).slow(2)).room(1.5)))

// Arrangement with inserted transitions
$: arrange(
  [16, pat.intro], 
  //[1, subtleBuild],  // Subtle buildup to drive
  [8, driveWithEnd],
  [2, breakdownFade],  // Fade to foreshadow
  [16, foreshadowWithEnd],
  [1, riserToDrop],  // Riser before silence
  [8, fakeSilenceWithStart],
  [2, riserToDrop],  // Build back up
  [24, fullOnWithEnd],
  [1, windDown],  // Wind down to outro
  [16, outroWithEnd],
)
