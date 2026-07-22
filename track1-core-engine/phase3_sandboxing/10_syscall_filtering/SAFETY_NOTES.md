# Module 10: syscall_filtering — SAFETY_NOTES.md

**Status: no notable concerns.**

## Primitives used
- Windows Job Objects (`CreateJobObject`, `SetInformationJobObject`,
  `AssignProcessToJobObject`) restricting a process's active-process count.
- `CREATE_SUSPENDED` process creation, later resumed via `ResumeThread`.

## Why this is safe as built
- Job Objects are a standard, defensive Windows containment primitive
  — the same mechanism real sandboxes (including Chromium's) use to
  *restrict* processes, not to escalate or evade anything.
- All processes involved are spawned by this module's own scripts, run
  the same non-elevated user account, and do nothing beyond printing a
  status line.
- No attempt is made to bypass or defeat the Job Object restriction —
  the module's entire point is that it succeeds at containing the
  child, and it demonstrates that directly and honestly.

## Risk if extended
- None specific to this module. Job Object active-process limits are
  purely restrictive; there is no natural "more dangerous" extension of
  this specific technique.

## A note on process (not this module's safety, but methodology)
- This module's `DECISIONS.md` documents an earlier approach (Win32k
  System Call Disable via `UpdateProcThreadAttribute`) that was built,
  tested, found not to work as claimed by Microsoft's documented API
  contract in this environment, and deliberately abandoned rather than
  documented as working. Recorded here only to note: no unverified
  mitigation-bypass or evasion technique was carried forward from that
  investigation into the final module.

## Action needed
- None to proceed with Module 11.
