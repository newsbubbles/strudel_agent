samples('github:tidalcycles/Dirt-Samples') // Load Dirt-Samples for fx

// Kick - driving 4/4 with subtle delay
$: sound("bd*4").gain(0.9).room(0.1).delay(0.1)

// Hi-hats - open and closed with phaser
$: sound("hh*8").gain(0.4).hpf(3000).late(0.01).phaser(0.5)
$: sound("oh*2").gain(0.3).lpf(8000).tremolo(4)

// Bassline - deep sub with sidechain
$: note("c1 eb1 f1 g1").s("sawtooth").lpf(200).gain(0.7).attack(0.05).decay(0.2)

// Arp - uplifting with delay and phaser
$: note("c4 <eb4 g4> [bb4 g4] <f4 ab4>").s("triangle").lpf(1200).gain(0.6).fast(4).delay(0.25).phaser(0.3)

// Pad - atmospheric with chorus-like delay
$: note("c3 [eb3 g3] <f3 ab3> bb3").s("sawtooth").lpf(600).room(0.8).delay("0.3:0.25:0.4").gain(0.4)

// White noise sweep - building riser
$: sound("noise").gain(0.3).hpf(sine.range(100,8000)).lpf(12000).slow(4).room(0.6)