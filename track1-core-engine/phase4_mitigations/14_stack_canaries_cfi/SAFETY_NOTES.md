# Module 14: stack_canaries_cfi — SAFETY_NOTES.md

**Status: contains a REAL, working memory-safety vulnerability (a
genuine stack buffer overflow) — the first in this course. Deliberately
kept non-weaponized: it demonstrates corruption and a controlled crash,
never code execution. Safe as built; the clearest candidate in the
course so far for "this pattern could be extended into something more
sensitive," documented explicitly below.**

## Primitives used
- A genuine, unmitigated C buffer overflow (`strcpy` into a fixed
  16-byte stack buffer with no bounds check).
- GCC's stack protector (`-fstack-protector-all`) as the real-world
  mitigation being evaluated against it.

## Why this is safe as built
- The overflow payload is a **fixed, hardcoded string of the letter
  `A`** (`"A" * 40`) — not shellcode, not a crafted return address, not
  anything designed to redirect execution to attacker-chosen code. When
  the unprotected build's corrupted return address is used, the CPU
  jumps to an address built from repeated `0x41` bytes — landing in
  unmapped memory and crashing immediately (`STATUS_ACCESS_VIOLATION`).
  There is no payload here capable of doing anything beyond that crash.
- No ROP (Return-Oriented Programming) chain, no gadget search, no
  shellcode, no attempt to defeat ASLR/ DEP in combination with this
  bug. This module's `overflow_target.c` is exploitable only in the
  narrowest sense of "can be made to crash in a specific, predictable
  way" — not in the sense of "can be made to run arbitrary code,"
  which this course does not build anywhere.
- Only this module's own compiled binaries are targeted, run locally,
  with a fixed, hardcoded command-line argument — no network exposure,
  no processing of untrusted external input.

## Risk if extended
- **This is a real vulnerability pattern (CWE-121, stack-based buffer
  overflow), genuinely present in the unprotected build.** Extending
  this module's `LONG_INPUT` from a fixed string of `A` characters into
  a carefully constructed byte sequence (a real return address, a NOP
  sled, actual shellcode) would cross from "demonstrates the bug class"
  into "working exploit" — explicitly out of this course's scope per
  the root `ROADMAP.md` ("weaponized/production exploit code" is listed
  as explicitly out of scope). This note exists so that boundary is
  never crossed casually or by incremental extension without deliberate,
  separate review.
- The tutorial's Brain Exercise discusses ROP/return-to-libc
  **conceptually, in prose only** — no gadget-chaining code is written
  anywhere in this module, consistent with the ROADMAP's ban on
  weaponized exploit code.

## Action needed
- None to proceed with Module 15 (which begins Track 2). Any future
  request to make this module's overflow "actually do something" upon
  triggering (beyond a controlled crash) should be treated as a new,
  separate scope decision, not an incremental change to this module.
