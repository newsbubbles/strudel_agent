// {"name": "Logistic Map Example", "tags": ["example", "stateful", "chaos", "dynamical-systems", "math"], "tempo": null, "description": "Classic logistic map x_{n+1} = r * x_n * (1 - x_n) using registerStateful. Demonstrates simplest discrete dynamical system.", "author": "Strudelmon", "version": "1.0.0", "date": "2025-12-27"}
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

const logistic = registerStateful(
  'logistic',
  0.2,
  (x, ctx) => 3.8 * x * (1 - x)
)

$: note(
  logistic('log', rand).range(40, 80)
).fast(4).s("sine").decay(0.2).gain(0.6)._pianoroll()