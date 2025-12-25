// {"name": "Shimmer", "tags": ["trance", "supersaw", "epic", "arranged"], "tempo": 136, "description": "Epic supersaw lead with nested melody changeups and arranged movement"}
setcpm(136/4)

register('pluckenv', (x, p) => p.lpf(400)
  .lpenv(x * 12).lps(.15).lpd(.08)
)

register('shimmer', (x, p) => p.scale(scala).trans(-12).detune(rand.range(0, x))
  .o(3).room(.7).delay(.3)
)

const orbit = 32
const epicLead = "<[0 4 7 <11 9>] [2 5 <9 7> 12] [4 7 11 [14 <16 14>]] [5 9 <12 14> [16 <19 17>]]>*4"
const scala = "d4:minor"

const supersawLead = n(epicLead).s("supersaw").scale(scala)
  .o(5)
  .lpf(sine.range(1200, 3200).slow(orbit))
  .detune(.2)
  .gain(.7)
  .room(.4)

const padLayer = n(epicLead).s("sawtooth").scale(scala)
  .o(2).lpf(sine.range(400, 1200).slow(orbit))
  .room(.6).size(8).gain(.5).attack(.3)

const shimmerPad = padLayer.struct("<~ x*2>*4").shimmer(8)

const driveBD = s("bd:1!4").lpf(sine.range(500, 1800).slow(orbit))
  .duckorbit(3).duckattack(.08).duckdepth(.7)

const driveBDSweep = driveBD.hpf("<1200 900 600 400 200 100 50 0>!4").duckorbit("<4 4 4 3>!16")
const driveBDClean = driveBD.hpf(1600).gain(.85).duckorbit(4)

const metallicHH = s("<- cp:2>*8").o(3).clip(.08)
  .delay(.4).gain(.65).hpf(2000)

const noiseRise = s("white!4").att(.6).o(5).gain(.12)
const filterSweep = s("white*16").o(4)
  .hpf(sine.range(1800, 400).slow(4)).lpf(2800).sustain(.9)
  .gain(.12)

const pat = {
  opening: supersawLead,
  charge: stack(supersawLead, driveBDSweep),
  breath: stack(padLayer, noiseRise, driveBDClean),
  rush: stack(supersawLead, driveBD, metallicHH, shimmerPad),
  release: stack(supersawLead, driveBDClean)
}

$: arrange(
  [16, pat.opening],
  [8, pat.charge],
  [4, pat.breath],
  [16, pat.rush],
  [4, pat.release]
)._pianoroll()