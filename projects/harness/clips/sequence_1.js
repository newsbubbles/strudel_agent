// Off Bass (yeah off beat, weird)
const offbass = stack(
  note("2 2 2 ~ 2 2 2 ~ 2 4 1 ~").scale("C3:major").s("square").fm(4).orbit(2).attack(0.05).decay(0),
  note("2 2 2 ~ 2 2 2 ~ 2 4 1 ~").scale("C1:major").s("square").fm(4).orbit(2).attack(0.05).decay(0.04)
)

// Mid Range juxtaposed creepy repeater
const midcreep = note("<[6 6 4 4] [7 7 5 5]>").scale("C2:major").s("sawtooth")
  .fm(8).orbit(2)
  .attack(0.05).decay(0.2)
  .phaser(0.2)
  .gain(1.2)

// +ocatve Hilight with a smooth attack and tremolo
const hilight = note("6@3 ~").scale("C4:major").s("triangle")
  .fm(4).orbit(4)
  .attack(.1)
  .tremsync(4)

const beats1 = sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  -  - ] [-  -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  hh - ],
[-  -  -  - ] [-  -  -  - ] [sd:1 -  -  - ] [-  -  -  - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd]
`).bank("RolandTR808").gain(1.4)

const rollbass = note("2@8").scale("C1:major").s("sawtooth")
  .attack(.5)
  .gain(1.2)

// Frame Stacks
const frame1 = offbass
const frame2 = stack(offbass, midcreep)
const frame3 = stack(offbass, midcreep, hilight)
const frame4 = stack(offbass, midcreep, hilight, beats1)
const frame5 = stack(offbass, midcreep, hilight, beats1, rollbass)

// Frame Sequence
$: arrange([4, frame1], [4, frame2], [8, frame3], [8, frame4], [16, frame5])
  ._scope()  ._pianoroll()