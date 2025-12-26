// {"name": "Rain Complete", "tags": ["ambient", "rain", "texture", "atmosphere"], "tempo": 60, "description": "Complete rain effect with continuous atmosphere and individual drops", "author": null, "version": "1.0.0", "date": "2025-12-26"}
setcpm(60/4)

// Rain atmosphere (continuous)
$: s("white@8")
  .lpf(perlin.range(800, 3000).slow(8))
  .hpf(perlin.range(200, 600).slow(6))
  .gain(perlin.range(0.3, 0.6).slow(4))
  .pan(perlin.range(-0.7, 0.7).slow(5))
  .room(0.7)
  .size(0.9)
  .gain(.4)

// Individual rain drops
$: s("crackle").gain(perlin.range(0.5, 2).slow(16))
  .lpf(perlin.range(2000, 3000).slow(64))
  .density(perlin.range(0, .1).slow(32))
  .room(0.6)
  ._scope()