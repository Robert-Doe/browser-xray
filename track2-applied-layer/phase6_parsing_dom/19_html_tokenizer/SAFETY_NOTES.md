# Module 19: html_tokenizer — SAFETY_NOTES.md

**Status: no notable concerns.**

## Primitives used
- A pure, in-memory string-processing state machine — no file I/O, no
  network access, no code execution of any kind.

## Why this is safe as built
- The tokenizer only ever reads its input string and produces a list of
  plain dataclass token objects. There is no `eval`, no dynamic code
  generation, and no mechanism by which malformed or adversarial HTML
  input could cause anything beyond a (bounded, finite) token stream or
  a Python exception on truly pathological input.
- All test inputs are small, fixed, hardcoded strings defined in this
  module's own demo script.

## Risk if extended
- None specific to this module. A hand-rolled parser fed genuinely
  adversarial, fuzzed input could in principle have unbounded-loop or
  performance edge cases (as any parser can) — this module does not
  claim to be hardened against adversarial input, only to correctly
  demonstrate the spec's defined recovery behavior for the malformed
  cases it explicitly tests.

## Action needed
- None to proceed with Module 20.
