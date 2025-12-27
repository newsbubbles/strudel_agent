// {"name": "Hidden Markov Breaks - Gated Lead", "tags": ["hmm", "breaks", "bass", "generative", "lead", "gated"], "tempo": 160, "description": "HMM-driven breakbeat with filtered bass and gated lead using dual HMM controls for texture and rhythm", "author": "Strudelmon", "version": "1.0.0", "date": "2025-12-26"}
setcpm(160/4)

let hmmHiddenStates = {};
let hmmObservedStates = {};
let hiddenTransitions = {
  'drums': {
    'groove': [0.7, 0.3],
    'fill': [0.4, 0.6]
  },
  'chords': {
    'stable': [0.8, 0.2],
    'transition': [0.3, 0.7]
  },
  'texture': {
    'sparse': [0.6, 0.4],
    'dense': [0.3, 0.7]
  },
  'gate': {
    'active': [0.7, 0.3],
    'changing': [0.4, 0.6]
  }
};
let hmmTables = {
  'drums': {
    'groove': [
      [[0, .2, .8], [.3, 0, .7], [.9, .1, 0]]
    ],
    'fill': [
      [[.1, .4, .5], [.4, .2, .4], [.5, .3, .2]]
    ]
  },
  'chords': {
    'stable': [
      [[.2, .2, .4, .2], [.5, .3, .2, .1], [0, .2, .7, .1], [.7, .1, .1, .1]]
    ],
    'transition': [
      [[.1, .3, .3, .3], [.3, .2, .3, .2], [.2, .2, .4, .2], [.3, .3, .2, .2]]
    ]
  },
  'texture': {
    'sparse': [
      [[.6, .3, .1], [.4, .4, .2], [.5, .3, .2]]
    ],
    'dense': [
      [[.2, .4, .4], [.3, .3, .4], [.2, .5, .3]]
    ]
  },
  'gate': {
    'active': [
      [[.3, .4, .2, .1], [.2, .5, .2, .1], [.1, .3, .4, .2], [.2, .2, .3, .3]]
    ],
    'changing': [
      [[.2, .3, .3, .2], [.3, .2, .3, .2], [.2, .3, .2, .3], [.3, .2, .2, .3]]
    ]
  }
};
let hiddenIndex = {
  'drums': ['groove', 'fill'],
  'chords': ['stable', 'transition'],
  'texture': ['sparse', 'dense'],
  'gate': ['active', 'changing']
};

const hmm = register('hmm', (id, pat) => pat.withHap(hap => {

  if (!hmmHiddenStates[id]) hmmHiddenStates[id] = [hiddenIndex[id][0]]
  if (!hmmObservedStates[id]) hmmObservedStates[id] = [0]

  const p = hap.whole.begin.n

  while (hmmObservedStates[id].length <= p) {

    const prevHidden = hmmHiddenStates[id].at(-1)
    const ht = hiddenTransitions[id][prevHidden]
    let nextHidden = prevHidden
    let acc = 0

    for (let i = 0; i < ht.length; i++) {
      acc += ht[i]
      if (Math.random() < acc) {
        nextHidden = hiddenIndex[id][i]
        break
      }
    }

    hmmHiddenStates[id].push(nextHidden)

    const prevObs = hmmObservedStates[id].at(-1)
    const table = hmmTables[id][nextHidden][0][prevObs]
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

const breaks = s(rand.segment(1)
  .hmm('drums').pick(["<bd:3 bd:2>","<sd:5 sd:2>","hh"])).fast(8)
  .duckorbit(2).duckattack(.01).duckdepth(.7)
  .gain(.4)

const bass = note(rand.late(.2).segment(2).hmm('chords').pick(["E1","C2","F1","A2"])).fast(2)
  .s("sawtooth").orbit(2)
  .lpf(sine.range(200,800).slow(8))
  .gain(.6)
  .room(.4)

const lead = note("e5 [g5 a5] ~ c6 ~ [a5 f5] e5 ~")
  .s("square")
  .slow(2)
  .lpf(rand.segment(2).hmm('texture').pick([1200, 1800, 2400]))
  .hpf(rand.segment(2).hmm('texture').pick([400, 600, 800]))
  .attack(rand.segment(2).hmm('texture').pick([0.01, 0.05, 0.1]))
  .decay(0.2)
  .delay(0.5)
  .delaytime(0.375)
  .room(0.7)
  .gain("<.0 .4 .2 .8>")
  .pan(perlin.range(0.3, 0.7))
  .mask(rand.segment(4).hmm('gate').pick(["0", "1", "1 0", "0 1"]))

$: breaks
$: bass
$: lead._pianoroll()._scope()