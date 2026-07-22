# Module 11: site_isolation_model — SAFETY_NOTES.md

**Status: contained dual-use primitive (cross-process memory read).
Safe as built; flagged clearly given real-world sensitivity.**

## Primitives used
- `OpenProcess` + `ReadProcessMemory` — a real, general-purpose
  cross-process memory-reading technique.

## Why this is safe as built
- The target ("victim") process is spawned by this module's own
  orchestrator, in this same demo run, holding a fixed, hardcoded,
  non-sensitive demo string (`ORIGIN_B_SESSION_TOKEN_SECRET`) — not a
  real credential, not another program's actual data, not anything
  belonging to the user or another application on the system.
- The target PID is passed directly and explicitly
  (`sys.argv`) by the orchestrator that spawned it — the attacker probe
  does not search for, enumerate, or guess at PIDs of unrelated
  processes anywhere on the system.
- The read targets one fixed, pre-agreed address — there is no address
  discovery, scanning, or heap-spraying logic here.
- Part B's entire point is demonstrating this technique being
  **blocked** by a real OS mechanism — the module's conclusion is
  defensive ("here's what stops this"), not offensive ("here's how to
  do this against a real target").

## Risk if extended
- **This is the most directly offense-relevant primitive built so far
  in this course.** `OpenProcess`/`ReadProcessMemory` against an
  attacker-chosen PID and a discovered (not pre-shared) address is a
  real building block of credential-dumping and process-injection
  reconnaissance tooling (the same general shape as tools like
  Mimikatz's memory-reading components, at a conceptual level — this
  module implements none of their actual logic). This module's `PID`
  and `ADDRESS` are both supplied cooperatively by its own orchestrator,
  never discovered independently by the "attacker" script. A future
  module or exercise that adds PID enumeration (`CreateToolhelp32Snapshot`,
  already used read-only in Module 4) or address-scanning to this
  probe would cross into materially different, more sensitive
  territory and should get fresh, explicit review before being built.

## Action needed
- None to proceed with Module 12. Flag this note specifically if any
  later module extends `attacker_probe.py`'s technique to target
  processes it did not itself spawn, or to discover addresses rather
  than receive them.
