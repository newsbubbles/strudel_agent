// {"name": "Rain Simulation", "tags": ["ambient", "rain", "texture", "noise"], "tempo": 60, "description": "Atmospheric rain texture using white noise and filtering", "author": null, "version": "1.0.0", "date": "2025-12-26"}
setcpm(60/4)

$: s("white")
  .lpf(perlin.range(800, 3000).slow(8))
  .hpf(perlin.range(200, 600).slow(6))
  .gain(perlin.range(0.3, 0.6).slow(4))
  .pan(perlin.range(-0.7, 0.7).slow(5))
  .room(0.7)
  .size(0.9)
  ._scope()