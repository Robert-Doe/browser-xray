# Module 13: dep_nx_w_xor_x — SAFETY_NOTES.md

**Status: contained dual-use primitive (raw machine code construction
and execution, in C this time). Same category of concern as Module 2,
now with an actual, real, non-Python-mediated crash. Safe as built.**

## Primitives used
- Hand-assembled x86-64 machine code bytes, written into both
  non-executable (`malloc`) and executable (`VirtualAlloc` +
  `PAGE_EXECUTE_READWRITE`) memory, then executed via a function-pointer
  cast.

## Why this is safe as built
- The payload is a **fixed, hardcoded six bytes** (`mov eax, 42; ret`)
  — a complete, closed, harmless function. There is no path anywhere
  in either program that accepts external or untrusted bytes as
  "code to run."
- Both programs operate entirely within their own process's own
  memory — no cross-process writes, no injection into another process,
  no network activity, no file access beyond compiling from local
  source.
- `dep_violation.exe`'s crash is expected, intentional, and contained
  — the OS terminates the single offending process; nothing else on
  the system is affected.

## Risk if extended
- Same category of note as Module 2's `SAFETY_NOTES.md`: this is,
  mechanically, the same "construct bytes, mark memory executable
  (or not), jump to it" shape used by real shellcode loaders. It
  remains safe here because the byte payload is fixed and non-generic.
  A future module or exercise that generalized either program into "run
  caller-supplied bytes" would need fresh, explicit review — neither
  program here does that.
- Module 14 (stack_canaries_cfi) will build directly on this module's C
  toolchain and go further, deliberately writing PAST the end of a
  buffer (a real stack-based buffer overflow) to demonstrate canary
  detection. That module gets its own safety review; noting the
  connection here since it's a direct continuation of this module's
  approach.

## Action needed
- None to proceed with Module 14.
