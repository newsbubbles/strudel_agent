setcpm(140/4)


let boidStates = {}

register('boidsArp', (id, pat, cfg = {}) =>
  pat.withHap(hap => {

    const {
      count = 6,
      center = 60,
      spread = 12,
      cohesion = 0.02,
      separation = 0.05,
      alignment = 0.03,
      speed = 0.2,
      scale = [0,2,3,5,7,10],
    } = cfg

    // init per-id
    if (!boidStates[id]) {
      boidStates[id] = Array.from({ length: count }, () => ({
        pos: center + (Math.random() - 0.5) * spread,
        vel: (Math.random() - 0.5) * speed
      }))
    }

    const boids = boidStates[id]

    // update ONCE per cycle
    const step = hap.whole.begin.n
    if (boids._lastStep !== step) {
      boids._lastStep = step

      boids.forEach((b, i) => {
        let avgPos = 0, avgVel = 0, sep = 0

        boids.forEach((o, j) => {
          if (i === j) return
          avgPos += o.pos
          avgVel += o.vel
          const d = b.pos - o.pos
          if (Math.abs(d) < 1) sep += d
        })

        avgPos /= boids.length
        avgVel /= boids.length

        b.vel +=
          (avgPos - b.pos) * cohesion +
          sep * separation +
          (avgVel - b.vel) * alignment

        b.pos += b.vel

        if (b.pos < center - spread || b.pos > center + spread)
          b.vel *= -1
      })
    }

    // choose boid by event value
    const v =
    typeof hap.value === "number"
        ? hap.value
        : Math.random()

    const i = Math.floor(
        Math.abs(v) * boids.length
    ) % boids.length

    const b = boids[i]

    // quantize
    const note = ((Math.round(b.pos) % 12) + 12) % 12
    const octave = Math.floor(b.pos / 12)
    const q = scale.reduce((a,n) =>
      Math.abs(n - note) < Math.abs(a - note) ? n : a
    )

    return hap.withValue(octave * 12 + q)
  })
)

// Superize for supersaw effect
register('superize', (x, p) => p.scale(scala).trans(-24).detune(rand)
  .o(4).acidenv(sine.range(0.2, .9).slow(orbit))
)

const orbit = 32
const arpHook = "<0 4 <7 4> <9 <9 7>>>*16"
const scala = "g4:minor"

// Arpy Supersaw
const superSaw = n(arpHook).s("supersaw").superize(1)

$: superSaw.boidsArp('arp1', { spread: 24 })

$: n(rand.segment(1)
   .boidsArp('arp1', { spread: 24 }))
   .pick(["c","d","f","g","a"])
   .s("supersaw")
   .fast(8)
