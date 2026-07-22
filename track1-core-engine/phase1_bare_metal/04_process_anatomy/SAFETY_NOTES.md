# Module 4: process_anatomy — SAFETY_NOTES.md

**Status: no notable concerns.**

## Primitives used
- Read-only process introspection APIs (`GetProcessMemoryInfo`,
  `GetProcessHandleCount`, `CreateToolhelp32Snapshot`/thread
  enumeration, token/integrity-level queries).
- `OpenProcess()` against a child process this same script spawned,
  using a minimal, explicitly-scoped access mask.

## Why this is safe as built
- Every API used is **read-only introspection** — nothing here writes
  to another process's memory, injects code, suspends/terminates
  threads, or alters another process's security context.
- The only "other process" touched is a child this script itself
  spawns (`python -c "import time; time.sleep(3)"`), inspected with
  the minimum access mask that satisfies the queries
  (`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`) rather than
  `PROCESS_ALL_ACCESS`.
- No targeting of arbitrary system processes, no privilege escalation
  attempted, no persistence.

## Risk if extended
- `OpenProcess()` + `GetProcessMemoryInfo()`/handle enumeration are
  legitimate building blocks of both defensive tooling (process
  monitors, EDR telemetry) and offensive tooling (process
  reconnaissance before injection). This module stops at
  read-only introspection of a self-spawned child; it does not
  demonstrate or enable memory reading of arbitrary process contents,
  writing, or thread manipulation. Worth flagging since `OpenProcess`
  is a name learners will recognize from both contexts.

## Action needed
- None to proceed with Module 5.
