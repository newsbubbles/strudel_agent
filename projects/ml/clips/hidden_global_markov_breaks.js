// {"name": "Hidden Global Markov Breaks", "tags": ["hmm", "breaks", "bass", "generative", "global"], "tempo": 160, "description": "HMM-driven breakbeat with global shared hidden state between drums and bass", "author": null, "version": "1.1.0", "date": "2025-12-26"}
setcpm(160/4)

// --------------------
// GLOBAL HIDDEN STATE
// --------------------

let globalHidden = ['low']
let globalIndex = ['low', 'high']

let globalTransitions = {
  low:  [0.92, 0.08],
  high: [0.25, 0.75]
}

// Map global form → local modes
let modeMap = {
  drums: {
    low: 'groove',
    high: 'fill'
  },
  chords: {
    low: 'stable',
    high: 'transition'
  }
}

// --------------------
// LOCAL HMM STATE
// --------------------

let hmmObservedStates = {}

let hmmTables = {
  drums: {
    groove: [
      [[0, .2, .8], [.3, 0, .7], [.9, .1, 0]]
    ],
    fill: [
      [[.1, .4, .5], [.4, .2, .4], [.5, .3, .2]]
    ]
  },
  chords: {
    stable: [
      [[.2, .2, .4, .2], [.5, .3, .2, .1], [0, .2, .7, .1], [.7, .1, .1, .1]]
    ],
    transition: [
      [[.1, .3, .3, .3], [.3, .2, .3, .2], [.2, .2, .4, .2], [.3, .3, .2, .2]]
    ]
  }
}

// --------------------
// SHARED-HIDDEN HMM
// --------------------

const hmm = register('hmm', (id, pat) => pat.withHap(hap => {

  if (!hmmObservedStates[id]) hmmObservedStates[id] = [0]

  const p = hap.whole.begin.n

  while (hmmObservedStates[id].length <= p) {

    // ---- advance GLOBAL hidden state ----
    const prevGlobal = globalHidden.at(-1)
    const gt = globalTransitions[prevGlobal]

    let nextGlobal = prevGlobal
    let acc = 0

    for (let i = 0; i < gt.length; i++) {
      acc += gt[i]
      if (Math.random() < acc) {
        nextGlobal = globalIndex[i]
        break
      }
    }

    globalHidden.push(nextGlobal)

    // ---- local emission based on global state ----
    const localHidden = modeMap[id][nextGlobal]
    const prevObs = hmmObservedStates[id].at(-1)
    const table = hmmTables[id][localHidden][0][prevObs]

    let nextObs = prevObs
    acc = 0

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
// DRUMS
// --------------------

$: s(
  rand.segment(1)
    .hmm('drums')
    .pick(["<bd:3 bd:2>", "<sd:5 sd:2>", "hh"])
).fast(8)
 .duckorbit(2)
 .duckattack(.01)
 .duckdepth(.7)
 .gain(.4)

// --------------------
// CHORD / BASS VOICE
// --------------------

$: note(
  rand.late(.2)
    .segment(2)
    .hmm('chords')
    .pick(["E1","C2","F1","A2"])
).fast(2)
 .sound("sawtooth")
 .detune(-.1)
 .lpf(
   rand.segment(2)
     .hmm('chords')
     .pick([2000,3000,400,800])
 ).slow(4)
 .phaser(
   rand.segment(2)
     .hmm('chords')
     .pick([2,3,4,8])
 ).fast(2)
 .o(2)
 .gain(1)
 ._scope()