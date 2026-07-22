# Module 12: aslr_and_leaks — SAFETY_NOTES.md

**Status: contained dual-use primitive (info-leak + cross-process
read, chained). Safe as built; this is the clearest "toy exploit
chain" in the course so far — flagged accordingly.**

## Primitives used
- A simulated information leak (a plain, labeled debug print — not a
  real memory-disclosure bug).
- `OpenProcess` + `ReadProcessMemory` (Module 11's technique), reused
  here to complete the demonstration end-to-end.

## Why this is safe as built
- The "leak" is not a real vulnerability — it's a deliberate, labeled
  print statement standing in for one, entirely contained within this
  module's own toy program. No real bug class (uninitialized memory,
  format string, etc.) is implemented or exploited.
- The target process, its PID, and its secret are all produced by this
  module's own orchestrator in the same run — the attacker script never
  targets, scans for, or discovers processes/addresses outside what
  this demo itself set up.
- The "secret" is a hardcoded, non-sensitive demo string, not real data.
- The offset (`SECRET_OFFSET`) is hardcoded and shared between the
  "vulnerable" and "attacker" scripts as known, cooperative demo
  configuration — not discovered through any reverse-engineering
  process this module performs.

## Risk if extended
- This module demonstrates a genuine, real-world-accurate *pattern*
  (leak an address, compute a target via a known offset, read it) that
  is precisely how real ASLR-bypass exploitation works. Nothing here
  is a working exploit against any real target — the offset is
  hardcoded cooperative configuration, not discovered. A future
  exercise that added automatic offset discovery (e.g., pattern-scanning
  a process's memory to find a target without being told the offset)
  would be a meaningfully different, more sensitive capability and
  should get its own explicit review.

## Action needed
- None to proceed with Module 13.
