// {"name": "Dirty Life Intro - 32 Bar Build", "tags": ["trance", "intro", "buildup"], "tempo": null, "description": "Sparse intro building tension over 32 bars: starts with pad and noise sweep, adds bass and arp gradually, full drums at end"}

// Pad - atmospheric wash starting sparse
note("c3 eb3 g3 bb3").s("sawtooth").lpf(200).room(1).delay("0.5").gain(0.2).slow(8)

// White noise sweep - slow build
sound("noise").gain(0.1).hpf(sine.range(50,2000).slow(16)).lpf(4000).slow(32).room(0.9)

// Bass - enter after 8 bars
note("c1 eb1 ~ ~ ~ f1 g1 ~ ~ ~").s("sawtooth").lpf(150).gain(0.4).attack(0.1).slow(4)

// Arp - enter after 16 bars, building
note("~ ~ c4 <eb4 g4> [bb4 g4] <f4 ab4> ~ ~ ~ ~").s("triangle").lpf(800).gain(0.3).fast(2).delay(0.3).slow(2)

// Drums fade in at 24 bars
sound("bd*4").gain(0).fast(1).segment(24,8).gain(0.9).room(0.1)
sound("hh*8").gain(0).fast(1).segment(24,8).gain(0.4).hpf(3000).late(0.01)

// Final bars tease the full pattern
note("c3 [eb3 g3] <f3 ab3> bb3").s("sawtooth").lpf(400).room(0.8).gain(0.2).segment(28,4)