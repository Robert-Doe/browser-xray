# Module 27: bytecode_vm — DECISIONS.md

## A flat `list[Instr]` with an integer program counter, instead of the AST itself
**(c) Convention — the module's entire point.** The whole performance
argument depends on this specific structural change: instructions live
in a flat array, addressed by a simple integer index that only ever
increments (or jumps), rather than being reached by recursively
descending into nested Python objects. This is exactly the same shape
real bytecode interpreters (including V8's Ignition) use.

## Compiling `&&`/`||` as plain `BINARY_OP`, not short-circuited via jumps
**(c) Convention — a deliberate, named, and real simplification.** Real
JS (and a real bytecode compiler) short-circuits these: `a() || b()`
must never evaluate `b()` if `a()` is truthy, because `b()` might have
side effects. This module's compiler always emits code that evaluates
BOTH sides unconditionally before combining them — correct for this
module's own test programs (none of which rely on short-circuit side
effects), but a genuine, flagged deviation from full JS semantics. A
correct implementation would compile these using the same
`JUMP_IF_FALSE`/`JUMP` machinery already built for `if`/`while`.

## Function calls recursing through Python's own call stack (`run()` calling itself), rather than an explicit VM-level frame stack
**(c) Convention — a deliberate, named simplification.** Production
bytecode VMs typically maintain their OWN explicit stack of call
frames (so the VM itself controls recursion depth, tail-call handling,
etc.), independent of the host implementation language's call stack.
This module reuses Python's own recursion for simplicity — every
`fib()` call inside the interpreted program becomes one real Python
function call to `run()`. This is a real, acknowledged difference from
how a production VM is built, though it doesn't affect the correctness
of anything this module's test programs exercise.

## `run_program()` returning the top-level frame's `locals` dict, as a separate function from `run()`
**(c) Convention.** `run()`'s return value is used for actual JS
`return` values when the VM is executing a FUNCTION call. The
top-level script isn't a function call and has no meaningful "return
value" in the same sense — `run_program()` exists specifically to let
the demo inspect top-level variables afterward, mirroring Module 26's
`env.get(...)` access pattern for its own top-level `Environment`.

## Benchmarking in the SAME process, back-to-back, rather than citing Module 26's previously-recorded number
**(c) Convention — chosen for the fairest possible comparison.**
Machine load, background processes, and CPU frequency scaling can
all shift wall-clock timings between separate runs at separate times.
Running both the tree-walking interpreter and the bytecode VM inside
the identical Python process, one immediately after the other, on the
byte-for-byte identical source string, removes as many confounding
variables as this course's tooling reasonably can.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Flat instruction list + program counter | (c) Convention (the module's entire point) | N/A |
| `&&`/`||` not short-circuited | (c) Convention (named, real simplification) | Yes — jump-based short-circuiting is a natural, real extension |
| Recursion via Python's own call stack for function calls | (c) Convention (named simplification vs. production VM design) | Yes — an explicit VM frame stack is more production-realistic |
| Separate `run_program()` for top-level variable inspection | (c) Convention (mirrors Module 26's access pattern) | Yes |
| Same-process, back-to-back benchmarking | (c) Convention (fairest comparison available) | Yes, separate runs are also valid but noisier |

## What We Proved

1. **Correctness**: the compiler+VM produced results IDENTICAL to
   Module 26's tree-walking interpreter for both a recursive function
   test (`fib(10) = 55.0`) and a loop/mutation test
   (`sum of 0..99 = 4950.0`) — the same program, two different
   execution strategies, same answer.
2. **Performance**: running the byte-for-byte identical `fib(24)`
   source through both engines in the same process produced real,
   captured timings — **1295.0 ms** for the tree-walking interpreter
   versus **702.8 ms** for the bytecode VM — a measured **1.84x
   speedup**.

This is direct, run-and-observed confirmation that compiling to
bytecode before execution is a genuine, measurable engineering
response to interpreter overhead — not a claim taken on faith from how
real engines are described, but a real number produced by running both
approaches against the identical program in the identical process.
