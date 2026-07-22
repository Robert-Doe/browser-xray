# Module 26: tree_walking_interpreter — DECISIONS.md

## `isinstance` dispatch over AST node types, re-checked on every visit
**(c) Convention — this IS the thing being measured.** A
tree-walking interpreter's defining, unavoidable characteristic is
that it never precomputes "what kind of node is this" once and
remembers — it re-asks that question, via a chain of `isinstance`
checks, every single time execution reaches that node, including every
one of ~150,000 times `fib(24)` revisits the same handful of AST
nodes. This isn't an inefficiency we accidentally introduced; it's the
literal definition of what makes an interpreter a "tree-walking" one,
and Module 27's benchmark exists specifically to quantify its cost.

## `ReturnSignal`, a Python exception, used to implement JS `return`
**(c) Convention — a standard, real implementation technique.** JS
`return` needs to unwind out of however many nested blocks/ifs/whiles
it's inside, immediately, back to the function call boundary. Python's
own exception mechanism already does exactly this kind of stack
unwinding — reusing it (rather than threading a "did we return yet"
flag through every single statement-execution function) is a common,
legitimate technique real tree-walking interpreters use, not a hack.

## `Environment` as an explicit, linked chain of scopes (not just a single dict)
**(b) External contract.** Real JS scoping is genuinely chained —
looking up a variable checks the current scope, then its enclosing
scope, and so on outward, and a closure captures a REFERENCE to its
defining scope, not a copy. `JSFunction` storing `closure` (the
`Environment` active at the moment the function was DEFINED) and
`call_function` creating each call's new environment as a CHILD of
that closure is what makes real closure behavior — a function
remembering variables from its defining scope even after that scope's
own statement has finished running — actually work.

## Blocks (`BlockStatement`) NOT creating their own child scope
**(c) Convention — a deliberate, named, and REAL simplification.**
This matches how JS's `var` behaves (function-scoped, not
block-scoped) but does NOT match how `let`/`const` actually behave in
real JS (block-scoped — a `let` declared inside an `if` block is
genuinely invisible outside it). Implementing correct `let`/`const`
block-scoping would require blocks to create and discard their own
child `Environment`, which this module deliberately does not do, to
keep the interpreter's scope model simple. This is flagged explicitly
here and in the tutorial rather than silently producing behavior that
looks like modern JS but isn't quite.

## `apply_operator` implementing `+` via Python's own `+` operator directly
**(b) External contract, with a real, useful coincidence.** Python's
`+` already does the right thing for both "number + number" and
"string + string" (JS's most common `+` behaviors) without extra code
— we didn't have to write separate numeric-addition and
string-concatenation branches. This is a genuine, accurate match for
common cases, though real JS's full `+` semantics (implicit
type coercion between strings and numbers, e.g. `"5" + 3` producing
`"53"`) are NOT reproduced here, since our lexer/parser never produces
mixed-type arithmetic in the test programs this module runs.

## `fib(24)` (not a larger or smaller N) as the benchmark
**(c) Convention.** Chosen empirically: small enough to complete in a
few seconds (verified directly — 1614.8 ms captured), large enough
(~150,000 recursive calls) to make the real per-node dispatch overhead
clearly measurable rather than dominated by fixed startup cost.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Re-dispatching via `isinstance` on every visit | (c) Convention (the literal definition of tree-walking, and the thing being measured) | N/A |
| `ReturnSignal` exception for `return` | (c) Convention (standard, real technique) | Yes, a flag-threading approach also works, more verbose |
| Explicit linked-chain `Environment` | (b) Forced — matches real JS scoping/closure semantics | No |
| Blocks share their parent's scope (no `let` block-scoping) | (c) Convention (deliberate, flagged simplification) | Yes — real block-scoping is a natural, real extension |
| `+` via Python's native `+` | (b) Forced/convenient — matches common JS `+` cases directly | Partially — full JS coercion rules are a further extension |
| `fib(24)` as the benchmark size | (c) Convention (empirically balanced) | Yes, any sufficiently large N works |

## What We Proved

1. **Correctness**: recursion (`fib(10) = 55`), loops with mutation
   (`sum of 0..99 = 4950`), string concatenation
   (`"hello " + "world" = 'hello world'`), and logical operators
   (`!false && (1 < 2) = True`) all evaluated to the correct real
   results via direct AST evaluation.
2. **Performance baseline**: `fib(24)`, requiring roughly 150,000
   recursive calls and correspondingly many re-visits of the same small
   set of AST nodes, took **1614.8 ms** of real, measured wall-clock
   time on this machine, running the identical Python interpreter
   process used throughout this course.

This is direct, run-and-observed confirmation both that direct AST
evaluation correctly implements real language semantics, and that it
has a real, non-trivial, precisely measured performance cost — the
exact number Module 27's bytecode VM will be benchmarked against,
running the byte-for-byte identical program.
