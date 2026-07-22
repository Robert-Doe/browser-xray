# Module 11: site_isolation_model — DECISIONS.md

## Building Part A to succeed (a working cross-process memory read), not just Part B's refusal
**(c) Convention — the module's central, deliberate teaching choice.**
It would have been easy to build only the "restricted" case and let
the reader assume process separation alone was always the reason
cross-origin reads fail. We built the unrestricted case FIRST and
verified it actually succeeds (see `06 Run It`), specifically because
that result is surprising and important: it directly contradicts a
plausible but wrong mental model ("processes are isolated, so nothing
can read another process's memory"). Showing the successful read is
what makes Part B's refusal meaningful, rather than assumed.

## Reusing `PINNED_ADDRESS = 0x0000300000000000` (Module 5's technique) instead of a dynamic/leaked address
**(c) Convention.** This module is not about address discovery (that's
adjacent to Module 12's ASLR/info-leak content and Module 34's
side-channel content) — it's about whether a *known* address in another
process can be reached at all. Using a fixed, pre-agreed address (the
"attacker" is handed it directly via `sys.argv`) removes address
discovery as a variable, isolating the module's actual claim.

## Duplicating Module 9's low-integrity token helper into this module's own directory
**(c) Convention, consistent with this course's per-module
self-containment.** Every module in this course is runnable from its
own directory alone (see, e.g., Module 8's `ipc_protocol.py` living
inside that module rather than a shared `common/` package). Importing
across module directories would break that property for a marginal
reduction in duplicated code, so `integrity_token.py` here is a
deliberate, small copy of Module 9's logic — the tutorial cites Module
9 directly for the full explanation rather than re-teaching it.

## `attacker_probe.py` reporting `GetLastError` on both the OpenProcess success and failure paths
**(c) Convention.** Printing the raw Win32 error code even on the
success path (`GetLastError=0`) makes Part A and Part B's output
directly, visually comparable line-for-line — the reader can see
exactly one number change (`0` → `5`, `ERROR_ACCESS_DENIED`) between an
otherwise identical operation.

## Part B uses only an integrity-level difference, not a full AppContainer or restricted-token sandbox
**(c) Convention — a deliberately scoped, honest simplification.** Real
Chromium's actual cross-renderer protection is stronger and more
layered than a bare integrity-level gap (it combines restricted
tokens, Job Objects, and on modern Windows, AppContainer isolation with
per-renderer distinct SIDs). This module isolates and proves the
*specific, real* mechanism ("no read up" on process/thread kernel
objects under Mandatory Integrity Control) that a bare integrity
difference alone provides — accurately scoped as one real contributing
layer, not oversold as the entire mechanism. The tutorial's Limits
section says this explicitly.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Build Part A to genuinely succeed first | (c) Convention (the module's core teaching move) | N/A — this is the point |
| Fixed, pre-shared pinned address | (c) Convention (isolates the claim from address-discovery) | Yes — a "found" address would conflate two different lessons |
| Duplicate Module 9's token helper locally | (c) Convention (per-module self-containment) | Yes — a shared library would reduce duplication at the cost of that property |
| Print `GetLastError` on both paths | (c) Convention (comparability) | Yes |
| Only integrity-level separation, not full sandbox | (c) Convention (honest, scoped claim) | Yes — a fuller sandbox demo is possible but conflates multiple mechanisms |

## What We Proved

1. **Part A**: an unrestricted, same-integrity "origin A" process
   successfully used only ordinary, documented Win32 APIs
   (`OpenProcess` + `ReadProcessMemory`) to read a known secret directly
   out of "origin B" renderer's private memory — real, captured proof
   that OS process separation alone (Module 5) does not prevent a
   deliberate, sufficiently-privileged cross-process read.
2. **Part B**: the identical attempt, with the attacker forced to a
   LOW integrity token (Module 9's technique) against a victim left at
   the OS default (Medium), failed at the very first step —
   `OpenProcess` itself was refused with `ERROR_ACCESS_DENIED` — because
   Windows' Mandatory Integrity Control enforces "no read up"
   specifically for process and thread kernel objects, unlike the
   generic file objects Module 9 tested.

Together, this is direct, run-and-observed evidence for the real,
precise claim Site Isolation depends on: putting different origins in
different OS processes only becomes a meaningful security boundary when
combined with an actual privilege/trust difference between those
processes — process separation by itself is necessary but not
sufficient.
