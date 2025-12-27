// {"name": "Register Stateful Function", "tags": ["utility", "stateful", "uzu", "dynamical-systems", "core"], "tempo": null, "description": "Generic uzu-compliant state engine for creating cached discrete dynamical systems indexed by cycle number. Foundation for HMMs, logistic maps, attractors, RNN-like recurrences.", "author": "Strudelmon", "version": "1.0.0", "date": "2025-12-27"}
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