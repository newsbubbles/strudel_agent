// {"name": "Take 2: Step Sequencer Drums", "tags": ["drums", "step-sequencer", "rolandtr808", "progression"], "tempo": null, "description": "Variation on take_1 with nicer drum progression using step sequencer style and RolandTR808 bank."}
setcpm(90/4)

$: sound(`
[-  -  oh - ] [-  -  -  - ] [-  -  -  - ] [-  -  -  - ],
[hh hh -  - ] [hh -  hh - ] [hh -  hh - ] [hh -  hh - ],
[-  -  -  - ] [cp -  -  - ] [-  -  -  - ] [cp -  -  - ],
[bd -  -  - ] [-  -  -  bd] [-  -  bd - ] [-  -  -  bd]
`).bank("RolandTR808")

// Bass sections from take_1
const bassA = note("c1 [eb1 ~ g1] bb1 [~ ab1 g1]").s("sawtooth").lpf(500)
const bassB = note("[c1 eb1] g1 bb1 eb1 [g1 ~]").s("sawtooth").lpf(600)
const bassC = note("c1 eb1 [g1~ bb1] [ab1 g1 eb1]").s("sawtooth").lpf(400).ply(2)

$: arrange([4, bassA], [8, bassB], [4, bassC]).s("sawtooth").dist(0.3).gain(0.8)