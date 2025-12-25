// {"name": "Wavey Base", "tags": ["trance", "base set", "droning dynamic bass", "progressive trance"], "tempo": 130, "description": "Great for a drone-like base to build on"}

samples('github:bubobubobubobubo/dough-waveforms')

setcpm(130/4)

// Drum Set
const bd4 = s("bd:1*4").lpf(300).gain(.7)
const hh8 = s("<- hh>*8").gain(.13).sometimesBy(.05, ply(3))
const sd2 = s("- white - white")
  .clip(.05).lpf(1900).lpenv(-2.0).lpa(.2)
  .room(.4).size(1)
  .gain(.4)

// Droning Orbiting Bass
const droneBass = note("c2*8").s("wt_dbass").n(run(8))
  .lpf(perlin.range(100,1000).slow(8))
  .lpenv(sine.range(-3.0, 4.0).slow(16)).lpa(.1).room(.5).fast(2)
  //._scope()

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


// Patterns
const pat = {
  intro: droneBass,
  drive: stack(droneBass, bd4),
  foreshadow: stack(droneBass, bd4, hh8, droneHi),
  fakeSilence: stack(droneHi),
  fullOn: stack(droneBass, bd4, hh8, sd2, droneHi, hardLead),
  outro: stack(droneBass, hardLead),
}

// Arrangement
$: arrange(
  [16, pat.intro], 
  [8, pat.drive],
  [16, pat.foreshadow],
  [8, pat.fakeSilence],
  [24, pat.fullOn],
  [8, pat.outro],
)