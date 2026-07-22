# Module 2: privilege_rings — SAFETY_NOTES.md

**Status: contained dual-use primitive. Safe as built; flagged for
awareness before this pattern is reused/extended in later modules.**

## Primitives used
- `VirtualAlloc(..., PAGE_EXECUTE_READWRITE)` — allocates a
  read+write+execute ("RWX") memory page.
- Hand-written raw x86-64 machine code bytes written into that page.
- Direct execution of that page via a `ctypes.CFUNCTYPE` call.

This is, mechanically, the same primitive shape used by shellcode
loaders and in-memory injection techniques: allocate RWX, write bytes,
jump to them. Flagging it explicitly rather than pretending it's
unrelated to that category.

## Why this is safe as built
- The byte payloads are a **fixed, hardcoded, closed set of four named
  instructions** (`NOP`, `RDTSC`, `CLI`, `HLT`) — not a generic
  "execute arbitrary supplied bytes" facility. There is no code path
  that accepts external/untrusted input as instructions to run.
- Execution targets **only the calling process's own freshly allocated
  page** — no injection into another process, no remote process
  handles opened, no `WriteProcessMemory`/`CreateRemoteThread`-style
  cross-process primitives anywhere in this module.
- The two "privileged" instructions (`CLI`, `HLT`) are chosen
  specifically because the CPU refuses them at Ring 3 by design — the
  demo's entire point is that they **cannot** succeed here, which is
  itself a safety property (there's no path to them "doing damage").
- No network activity, no persistence, no elevation requested or used.

## Risk if extended
- If a future module (or a well-meaning "let's make this more
  general") turned `run_code()` into a helper that accepts **arbitrary
  caller-supplied byte strings** rather than the four fixed, named
  instructions in this file, it would cross from "fixed pedagogical
  demonstration" into "generic native code execution primitive" — at
  that point it deserves fresh, explicit safety review, not an
  inherited pass from this module's approval.
- Modules 13 and 14 (Track 1, Phase 4) deliberately build on this same
  RWX-allocate-and-execute shape, combined with actual memory-safety
  bugs (buffer overflows). Flagging here so that when those modules are
  built, the combination gets reviewed as its own thing rather than
  assumed safe by association with this module.

## Action needed
- None to proceed with Module 3. Revisit this note's "risk if extended"
  section when building Modules 13/14.
