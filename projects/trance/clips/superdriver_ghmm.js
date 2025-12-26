// {"name": "Superdriver GHMM", "tags": ["trance", "hmm", "generative", "supersaw", "full on", "ghmm"], "tempo": 136, "description": "Superdriver with global HMM controlling arp patterns, scales, and filter sweeps", "author": null, "version": "1.1.1", "date": "2025-12-26"}
setcpm(136/4)

// --------------------
// GLOBAL HIDDEN STATE
// --------------------

let globalHiddenStates = []
let globalHiddenIndex = ['groove', 'fill']

let globalHiddenTransitions = {
  'groove': [0.85, 0.15],
  'fill': [0.3, 0.7]
}

// Map global form → local modes
let modeMap = {
  arp: {
    groove: 'stable',
    fill: 'intense'
  },
  filter: {
    groove: 'dark',
    fill: 'bright'
  },
  arrangement: {
    groove: 'spacious',
    fill: 'dense'
  }
}

// --------------------
// LOCAL HMM STATE
// --------------------

let hmmObservedStates = {}

let hmmTables = {
  arp: {
    stable: [
      [[.6, .3, .1], [.4, .5, .1], [.3, .3, .4]]
    ],
    intense: [
      [[.2, .4, .4], [.3, .3, .4], [.4, .3, .3]]
    ]
  },
  filter: {
    dark: [
      [[.7, .2, .1], [.5, .4, .1], [.4, .4, .2]]
    ],
    bright: [
      [[.2, .3, .5], [.3, .3, .4], [.3, .4, .3]]
    ]
  },
  arrangement: {
    spacious: [
      [[.5, .3, .15, .05], [.4, .4, .15, .05], [.3, .4, .2, .1], [.2, .3, .3, .2]]
    ],
    dense: [
      [[.1, .2, .3, .4], [.2, .2, .3, .3], [.2, .3, .3, .2], [.3, .3, .2, .2]]
    ]
  }
}

// --------------------
// SHARED-HIDDEN HMM
// --------------------

const ghmm = register('ghmm', (id, pat) => pat.withHap(hap => {

  if (globalHiddenStates.length === 0) globalHiddenStates = [globalHiddenIndex[0]]
  if (!hmmObservedStates[id]) hmmObservedStates[id] = [0]

  const p = hap.whole.begin.n

  while (globalHiddenStates.length <= p) {

    const prevHidden = globalHiddenStates.at(-1)
    const ht = globalHiddenTransitions[prevHidden]
    let nextHidden = prevHidden
    let acc = 0

    for (let i = 0; i < ht.length; i++) {
      acc += ht[i]
      if (Math.random() < acc) {
        nextHidden = globalHiddenIndex[i]
        break
      }
    }

    globalHiddenStates.push(nextHidden)
  }

  while (hmmObservedStates[id].length <= p) {

    const currentHidden = globalHiddenStates[hmmObservedStates[id].length]
    const localHidden = modeMap[id][currentHidden]
    const prevObs = hmmObservedStates[id].at(-1)
    const table = hmmTables[id][localHidden][0][prevObs]
    let nextObs = prevObs
    let acc = 0

    for (let i = 0; i < table.length; i++) {
      acc += table[i]
      if (Math.random() < acc) {
        nextObs = i
        break
      }
    }

    hmmObservedStates[id].push(nextObs)
  }

  return hap.withValue(() => hmmObservedStates[id][p])
}))

// --------------------
// ACID SHAPE
// --------------------

register('acidenv', (x, p) => p.lpf(100)
  .lpenv(x * 9).lps(.2).lpd(.12)
)

register('superize', (x, p) => p.scale(scala).trans(-24).detune(rand)
  .o(4).acidenv(sine.range(0.2, .9).slow(orbit))
)

const orbit = 32
const scala = "g4:minor"

// --------------------
// HMM-DRIVEN PATTERNS
// --------------------

const arpPatterns = [
  "<0 4 <7 4> <9 <9 7>>>*16",
  "<0 7 4 9>*16",
  "<0 [4 7] 9 [7 4]>*16"
]

const scaleChoices = [
  "g4:minor",
  "g4:phrygian",
  "g4:dorian"
]

const filterLows = [200, 400, 600]
const filterHighs = [600, 900, 1400]

const arpHook = rand.segment(2).ghmm('arp').pick(arpPatterns)
const scalaHMM = rand.segment(4).ghmm('arp').pick(scaleChoices)
const filterLow = rand.segment(2).ghmm('filter').pick(filterLows)
const filterHigh = rand.segment(2).ghmm('filter').pick(filterHighs)

// --------------------
// SUPERSAW & TEXTURE
// --------------------

const superSaw = n(arpHook).s("supersaw").superize(1)

const texture = n(arpHook).s("square").scale(scalaHMM)
  .o(4).lpf(sine.range(filterLow, filterHigh).slow(orbit))
  .room(.4).size(10).gain(.6)

const offTexture = texture.struct("<~ x*4>*4").superize(1)

// --------------------
// DRUMS
// --------------------

const superBD = s("bd:2!4").lpf(sine.range(300, 1600).slow(orbit))
  .duckorbit(4).duckattack(.1).duckdepth(.8)

const superBDHiSweep = superBD.hpf("<1500 1100 900 700 500 300 160 0>!4").duckorbit("<5 5 5 4>!16")
const superBDHi = superBD.hpf(1800).gain(.9).duckorbit(5)

const whiteHH = s("<- white>*8").o(4).clip(.1)
  .delay(.5).gain(.7)

// --------------------
// SWEEPS
// --------------------

const whiteSweep = s("white!4").att(.4).o(6).gain(.1)
const longSweepDown = s("white*16").o(5)
  .hpf(sine.range(2400, 300).slow(4)).lpf(3300).sustain(1)
  .gain(.1)

// --------------------
// PATTERN ELEMENTS
// --------------------

const pat = {
  intro: superSaw,
  driver: stack(superSaw, superBDHiSweep),
  fakeSilence: stack(texture, whiteSweep, superBDHi),
  feliz: stack(superSaw, superBD, whiteHH, offTexture),
  fakeOutro: stack(superSaw, superBDHi)
}

// --------------------
// ARRANGEMENT STRUCTURES
// --------------------

const arrangement0 = [
  [16, pat.intro],
  [8, pat.driver],
  [4, pat.fakeSilence],
  [16, pat.feliz],
  [4, pat.fakeOutro]
]

const arrangement1 = [
  [8, pat.intro],
  [4, pat.driver],
  [8, pat.feliz],
  [2, pat.fakeSilence],
  [8, pat.driver],
  [2, pat.fakeOutro]
]

const arrangement2 = [
  [4, pat.intro],
  [2, pat.driver],
  [4, pat.feliz],
  [2, pat.driver],
  [4, pat.feliz],
  [2, pat.fakeSilence],
  [2, pat.fakeOutro]
]

const arrangement3 = [
  [12, pat.intro],
  [12, pat.driver],
  [8, pat.fakeSilence],
  [24, pat.feliz],
  [8, pat.fakeOutro]
]

const arrangementChoices = [arrangement0, arrangement1, arrangement2, arrangement3]

let selectedIdx = 0
let arrangementState = []

const pickArrangement = () => {
  if (arrangementState.length === 0) {
    arrangementState = [0]
    selectedIdx = 0
  } else {
    const currentHidden = globalHiddenStates.length > 0 ? globalHiddenStates.at(-1) : 'groove'
    const localHidden = modeMap.arrangement[currentHidden]
    const prevObs = arrangementState.at(-1)
    const table = hmmTables.arrangement[localHidden][0][prevObs]
    
    let nextObs = prevObs
    let acc = 0
    
    for (let i = 0; i < table.length; i++) {
      acc += table[i]
      if (Math.random() < acc) {
        nextObs = i
        break
      }
    }
    
    arrangementState.push(nextObs)
    selectedIdx = nextObs
  }
  
  return arrangementChoices[selectedIdx]
}

$: arrange(...pickArrangement())._pianoroll()