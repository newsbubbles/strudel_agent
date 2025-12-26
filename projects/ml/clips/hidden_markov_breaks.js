// {"name": "Hidden Markov Breaks", "tags": ["hmm", "breaks", "bass", "generative"], "tempo": 150, "description": "HMM-driven breakbeat with ducking and filtered bass", "author": null, "version": "1.0.2", "date": "2025-12-26"}
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
  }
};
let hiddenIndex = {
  'drums': ['groove', 'fill'],
  'chords': ['stable', 'transition']
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

$: s(rand.segment(1)
  .hmm('drums').pick(["<bd:3 bd:2>","<sd:5 sd:2>","hh"])).fast(8)
  .duckorbit(2).duckattack(.01).duckdepth(.7)
  .gain(.4)

$: note(rand.late(.2).segment(2).hmm('chords').pick(["E1","C2","F1","A2"])).fast(2)
  .sound("sawtooth").detune(-.1)
  .lpf(rand.segment(2).hmm('chords').pick([2000,3000,400,800])).slow(4)
  .phaser(rand.segment(2).hmm('chords').pick([2,3,4,8])).fast(2)
  .o(2)
  .gain(1)
  ._scope()