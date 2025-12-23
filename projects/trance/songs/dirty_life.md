# Dirty Life

Trance track featuring building intro, main drop, and chopped variation. Includes transitions for bass drops and builds.

## Intro - 32 Bar Buildup

Use the intro clip to start sparse and build tension:

[Load Dirty Life Intro](../clips/dirty_life_intro.js)

*Transition tip*: At bar 24, fade in kick with `.gain(perlin.range(0,0.9).slow(8))` for smooth entry.

## Main Section - Drop (32 bars)

Full energy with driving bass and arp:

[Load Dirty Life](../clips/dirty_life.js)

*Bass Drop*: To emphasize the drop, boost bass gain: `.gain(1.2)` and add compressor or sidechain simulation via envelope.

## Variation - Chopped Break (16 bars)

Glitchy texture for contrast:

[Load Dirty Life Chopped](../clips/dirty_life_chopped.js)

*Transition*: Chop the pad more aggressively with `.chop(32).fast(2)` leading back to main drop.

## Outro - Fade Out (16 bars)

Combine intro elements with slowing tempo: `slow(2)` on all layers.

*Agent Actions*:
- For builds: Increase `lpf` cutoff gradually with `sine.range(200,2000).slow(16)`
- Bass drops: Layer sub-bass `note("c1").s("sine").lpf(100).gain(1.5)`
- Transitions: Use `segment(8,16)` to switch clips dynamically