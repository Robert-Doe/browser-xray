# Module 17: origin_model_sop — SAFETY_NOTES.md

**Status: no notable concerns.**

## Primitives used
- Two loopback-only (`127.0.0.1`) local HTTP servers.
- A same-origin/cross-origin comparison function and two fetch
  wrappers (one deliberately unenforced, one enforcing).

## Why this is safe as built
- Both toy servers bind to `127.0.0.1` only — never reachable from the
  network.
- The "private data" leaked in Part A is a hardcoded, non-sensitive
  demo string (`PRIVATE_SESSION_DATA_FOR_ORIGIN_B_ONLY`) served by this
  module's own script, not real data belonging to any real site or user.
- `naive_fetch()` demonstrates the ABSENCE of a security control for
  teaching purposes, against a target this module itself created and
  controls — it is not pointed at, and cannot reach, any real
  third-party service.

## Risk if extended
- None specific to this module. `naive_fetch()`'s "no origin check"
  behavior is the deliberate negative case the module exists to
  contrast against `sop_enforced_fetch()` — it is not presented as a
  general-purpose tool, and does nothing a real, unmodified `curl` or
  raw socket client couldn't already do against any target.

## Action needed
- None to proceed with Module 18.
