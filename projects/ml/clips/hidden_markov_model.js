// {"name": "Hidden Markov Model", "tags": ["hmm", "generative", "algorithm", "utility"], "tempo": 120, "description": "HMM implementation with state transitions and observation tables", "author": null, "version": "1.0.0", "date": "2025-12-26"}
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