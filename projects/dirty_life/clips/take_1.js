// Dirty Kick
$: sound("bd bd/2 [~ bd] bd").gain(1.0).lpf(200)

// Gritty Hats
$: sound("hh*8 cp*4").room(0.3).gain(0.6).hpf(3000)

// Funky Raw Bass with Variations
// Define bass groups: A (groovy syncopation), B (driving path), C (complex funk)
const bassA = note("c1 [eb1 ~ g1] bb1 [~ ab1 g1]").s("sawtooth").lpf(500)
const bassB = note("[c1 eb1] g1 bb1 eb1 [g1 ~]").s("sawtooth").lpf(600)
const bassC = note("c1 eb1 [g1~ bb1] [ab1 g1 eb1]").s("sawtooth").lpf(400).ply(2)

// Choose path: <A B C> cycles through; replace with single var for fixed
$: note("<c1 [eb1 ~ g1] bb1 [~ ab1 g1] [c1 eb1] g1 bb1 eb1 [g1 ~] c1 eb1 [g1~ bb1] [ab1 g1 eb1]>").s("sawtooth").lpf("<500 600 400>").dist(0.3).gain(0.8)

// Or arrange sections: [4, bassA], [8, bassB], [4, bassC] for A (4 cycles) -> B (8) -> C (4)
$: arrange([4, bassA], [8, bassB], [4, bassC]).s("sawtooth").dist(0.3).gain(0.8)