# Module 9: least_privilege_tokens — SAFETY_NOTES.md

**Status: no notable concerns — this module's entire technique is a
privilege-REDUCING primitive, which is the safe direction.**

## Primitives used
- `DuplicateTokenEx` / `SetTokenInformation` to create a copy of the
  calling process's own token with a LOWERED integrity level.
- `CreateProcessAsUser` to spawn a child process running under that
  reduced token.

## Why this is safe as built
- The token operations in this module only ever **remove** capability
  relative to the calling process — never grant, escalate, or
  impersonate a different, more privileged account. Raising integrity
  requires `SeRelabelPrivilege`, which this module never attempts to
  use or acquire.
- The only token ever duplicated is **this process's own** — no
  impersonation of another user or logon session occurs anywhere.
- The file operations tested are a plain, non-sensitive demo file
  created and deleted by this module's own script.

## Risk if extended
- `CreateProcessAsUser` combined with a token obtained by OTHER means
  (e.g. `LogonUser` with credentials, or a token stolen/duplicated from
  a different, more-privileged process) is a real, well-known
  privilege-escalation building block in offensive tooling. This module
  deliberately stays on the narrow, safe side of that line: it only
  ever duplicates its own token and only ever lowers it. A generalized
  "spawn a process as an arbitrary token" helper would need fresh
  review — this module's `run_with_token()` is not that; it does not
  take arbitrary caller-supplied tokens from outside this file's own
  `make_token_at_integrity()`.

## Action needed
- None to proceed with Module 10.
