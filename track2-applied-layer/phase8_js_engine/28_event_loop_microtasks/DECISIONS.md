# Module 28: event_loop_microtasks — DECISIONS.md

## Two separate `deque` queues (macrotasks, microtasks), not one shared queue with priority tagging
**(b) External contract.** This is the real, specified shape of the
browser/Node event loop — macrotasks and microtasks are genuinely
different queues with a different draining rule (macrotasks: one at a
time; microtasks: fully drained, every time), not the same queue
sorted by a priority field. Modeling them as one queue with priorities
would obscure the actual rule this module exists to prove: the FULL
DRAIN behavior, not just "microtasks go first."

## `_drain_microtasks()` using a `while self.microtasks:` loop, re-checking the queue every iteration
**(b) External contract — this is the exact mechanism the "promise 3"
test case depends on.** Using `while` (re-checking the queue's current
state every loop) rather than, say, iterating a fixed-length snapshot
of the queue taken at the start, is what correctly picks up "promise
3" — a microtask queued from INSIDE "promise 2" while draining is
already in progress. A snapshot-based loop would have missed it
entirely and left it to run later than real JS actually runs it.

## Callbacks as plain Python callables, queued via this module's own explicit API, rather than interpreting real `Promise`/`setTimeout` JS syntax
**(c) Convention — a deliberate, named scope boundary.** This module's
claim is about the SCHEDULING mechanism (two queues, one draining rule)
independent of any particular language's syntax for triggering it.
Modeling `setTimeout`/`Promise.resolve().then()` as direct
`queue_macrotask`/`queue_microtask` calls keeps the demo focused on the
scheduler itself, rather than requiring this course's toy JS engine
(Modules 25-27) to first implement a real `Promise` object and a real
`setTimeout` built-in, which is real, additional complexity out of
this module's scope.

## The demo script itself performs "synchronous" logging directly (not via `queue_macrotask`), before calling `loop.run()`
**(b) External contract.** This mirrors a real, important fact about
the event loop: the CURRENTLY EXECUTING script's own top-level code is
not itself a queued task — it runs immediately, to completion, before
the event loop even starts processing its queues. Modeling the
"synchronous" lines as direct Python statements (not queued callbacks)
before `loop.run()` is called is what makes `"script end"` correctly
appear before ANY queued task, matching real JS.

## Asserting the exact expected order as a literal list, rather than checking only a few key relationships
**(c) Convention.** A partial check (e.g., "does promise 1 come before
setTimeout 1?") would prove a weaker claim. Comparing the ENTIRE
captured log against the full expected sequence, including which
specific microtask discovered mid-drain (`promise 3`) lands exactly
where real JS puts it, is the strongest, most falsifiable version of
this module's claim we could build.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Two separate queues, not one shared priority queue | (b) Forced — matches the real, specified event loop shape | No |
| `while self.microtasks:` re-checking each iteration | (b) Forced — required for the mid-drain "promise 3" case | No |
| Plain callables via explicit queue API, not real Promise/setTimeout syntax | (c) Convention (isolates the scheduler from language syntax) | Yes — implementing real Promise semantics is a natural, larger extension |
| Synchronous lines run directly, not queued, before `loop.run()` | (b) Forced — matches real "script runs to completion first" behavior | No |
| Full literal-list comparison against expected order | (c) Convention (strongest, most falsifiable check) | Yes, a partial check is weaker but still valid |

## What We Proved

Running one real, deliberately tricky scenario — two macrotasks, two
initial microtasks, and one microtask (`promise 3`) queued from inside
another microtask while the queue was still draining — through this
module's event loop produced an execution order that matched real,
well-known JS behavior EXACTLY, verified as a full list comparison:

```
sync: script start, sync: script end,
microtask: promise 1, microtask: promise 2, microtask: promise 3,
macrotask: setTimeout 1, macrotask: setTimeout 2
```

This is direct, run-and-observed confirmation that JS's concurrency
model is single-threaded, cooperative scheduling via two distinctly-
draining queues — not real parallelism, and not a vague "microtasks
are faster" folk rule, but a precise, mechanically-derived ordering
that this module's `EventLoop` reproduces exactly, including the subtle
case of a microtask discovering more work for itself mid-drain.
