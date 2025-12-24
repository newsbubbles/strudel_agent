// {"name": "Take 2: Punchy Bass Variation", "tags": ["bass", "fm", "punchy", "modulo"], "tempo": null, "description": "Variation on take_1 with punchier FM basslines for more impact."}
$: sound("bd bd/2 [~ bd] bd").gain(1.0).lpf(200)

$: sound("hh*8 cp*4").room(0.3).gain(0.6).hpf(3000)

// Punchy FM Bass sections
const bassA = note("c1 [eb1 ~ g1] bb1 [~ ab1 g1]").s("fm").lpf(300).fm(4).gain(1.0).hpf(50)
const bassB = note("[c1 eb1] g1 bb1 eb1 [g1 ~]").s("fm").lpf(350).fm(3).gain(1.0).hpf(50)
const bassC = note("c1 eb1 [g1~ bb1] [ab1 g1 eb1]").s("fm").lpf(250).fm(5).gain(1.0).hpf(50).ply(2)

$: arrange([4, bassA], [8, bassB], [4, bassC]).gain(0.9)