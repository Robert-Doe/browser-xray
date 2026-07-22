# Module 34: side_channel_timing — SAFETY_NOTES.md

**Status: contained, educational demonstration of a real, well-known,
non-weaponized timing side-channel vulnerability class. This is
standard, widely-taught defensive security material (the same lesson
behind "always use constant-time comparison for secrets"). Safe as
built.**

## Primitives used
- `time.perf_counter()` / `time.sleep()` — real timing measurement,
  nothing more.
- A real, working timing-based secret-recovery attack against a
  deliberately vulnerable string-comparison function.

## Why this is safe as built
- **The "secret" is a hardcoded demo string** (`'X7f9Qz2A'`) defined in
  this module's own script — not a real credential, not real user data,
  not anything belonging to a real system.
- **Both the "victim" and "attacker" are plain Python functions in the
  same process** — there is no real network communication, no real
  cross-origin request, no real browser, and no actual timing
  measurement of anything outside this module's own local function
  calls.
- **This is a defensive-security teaching pattern with a long,
  established history** — non-constant-time comparison timing attacks
  are extensively documented in public security research and standard
  curricula specifically so developers learn to use constant-time
  comparison for secrets (as this module's own "AFTER" case
  demonstrates). Nothing about this demonstration exceeds what's
  already widely publicly taught.
- **Not a real CPU-cache/Spectre-class exploit.** This module
  deliberately chose a comparison-timing channel specifically because
  it's reliably reproducible in pure Python (verified directly) and
  fully safe/non-weaponized — no attempt was made to build or approach
  a real speculative-execution exploit.

## Risk if extended
- The one meaningful extension risk: pointing this exact technique at a
  REAL network service's REAL authentication endpoint would be a
  genuine, potentially illegal attack against a system the user doesn't
  own or lack authorization to test — explicitly outside this course's
  scope. Nothing in this module's code sends any real network request;
  it operates entirely on in-process function calls.

## Action needed
- None to proceed with Module 35 (the final module).
