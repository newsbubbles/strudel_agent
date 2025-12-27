// {"name": "HMM Stateful Example", "tags": ["example", "stateful", "hmm", "markov", "probabilistic"], "tempo": null, "description": "Simple Hidden Markov Model using registerStateful. Same engine, different step function pattern.", "author": "Strudelmon", "version": "1.0.0", "date": "2025-12-27"}
const STATE = {}

function getState(scope, n, init, stepFn, ctx) {
  if (!STATE[scope]) STATE[scope] = [init]
  const arr = STATE[scope]
  while (arr.length <= n) {
    const k = arr.length - 1
    arr.push(stepFn(arr[k], ctx, k))
  }
  return arr[n]
}

function registerStateful(name, init, stepFn) {
  return register(name, (scope, pat) =>
    pat.withHap(hap => {
      const n = hap.whole.begin.n
      const ctx = {
        n,
        read: (otherScope, otherInit, otherStep) =>
          getState(otherScope, n, otherInit, otherStep, ctx)
      }
      const value = getState(scope, n, init, stepFn, ctx)
      return hap.withValue(() => value)
    })
  )
}

const hmmStep = (prev, ctx) => {
  const table = [
    [0.7, 0.3],
    [0.4, 0.6]
  ]
  return Math.random() < table[prev][0] ? 0 : 1
}

const hmm = registerStateful('hmm', 0, hmmStep)

$: s(
  hmm('state', rand.segment(4)).pick(["bd", "sd"])
).fast(4).gain(0.7)

$: note(
  hmm('melody', rand.segment(2)).pick(["c4", "e4"])
).s("triangle").decay(0.3).gain(0.5)._pianoroll()