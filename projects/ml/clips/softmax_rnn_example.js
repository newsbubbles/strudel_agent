// {"name": "Softmax RNN Example", "tags": ["example", "stateful", "rnn", "softmax", "ml", "vector"], "tempo": null, "description": "Tiny RNN-ish example using vector recurrence with softmax. Demonstrates linear algebra style state progression.", "author": "Strudelmon", "version": "1.0.0", "date": "2025-12-27"}
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

function softmax(v) {
  const e = v.map(Math.exp)
  const s = e.reduce((a,b) => a+b, 0)
  return e.map(x => x/s)
}

const softmaxStep = (v) => {
  const W = [
    [1.2, -0.4],
    [0.3,  0.8]
  ]
  const z = [
    W[0][0]*v[0] + W[0][1]*v[1],
    W[1][0]*v[0] + W[1][1]*v[1]
  ]
  return softmax(z)
}

const soft = registerStateful(
  'soft',
  [0.5, 0.5],
  softmaxStep
)

$: s(
  soft('vec', rand)
    .map(v => (Math.random() < v[0] ? 0 : 1))
    .pick(["bd", "sd"])
).fast(8).gain(0.7)._scope()