# Module 26: tree_walking_interpreter — SAFETY_NOTES.md

**Status: contained, first module in the course that actually EXECUTES
parsed code. Safe as built; flagged since "execute untrusted code" is
inherently a sensitive capability class.**

## Primitives used
- A real, working interpreter that executes an AST — meaning, unlike
  Module 25, this module's code actually RUNS the input program.

## Why this is safe as built
- Only a small, closed, hand-implemented language subset is
  executable (arithmetic, string concatenation, control flow, function
  calls within this interpreter's own semantics) — there is no access
  to the filesystem, network, environment variables, or the host
  Python process's own capabilities from within the interpreted
  language. A program run through this interpreter cannot open a file,
  make a network call, or import a Python module; those capabilities
  simply don't exist anywhere in `evaluate`/`execute_statement`.
- All executed programs are fixed, hardcoded source strings defined in
  this module's own demo script — there is no code path that executes
  externally-supplied or user-provided source.

## Risk if extended
- The moment ANY built-in function is added that reaches outside the
  interpreter's own sandboxed semantics (e.g. a hypothetical
  `readFile()` or `fetch()` builtin), this module's safety posture
  changes completely and would need fresh review. Nothing here does
  that today — `call_function` only ever invokes `JSFunction` objects
  defined entirely within the interpreted language itself.
- This module is also the natural place a future exercise might be
  tempted to add a "run arbitrary JS the user provides" feature; doing
  so against genuinely untrusted input (as opposed to this module's own
  fixed demo programs) would deserve its own explicit review at that
  time.

## Action needed
- None to proceed with Module 27.
