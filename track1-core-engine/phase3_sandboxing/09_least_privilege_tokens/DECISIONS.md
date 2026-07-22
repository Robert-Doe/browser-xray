# Module 9: least_privilege_tokens — DECISIONS.md

## `low_integrity_token.py`

### Duplicating the CALLING process's own token, rather than a different account's
**(b) External contract, deliberately exploited.** Windows requires
`SeAssignPrimaryTokenPrivilege` and `SeIncreaseQuotaPrivilege` to call
`CreateProcessAsUser` with an arbitrary token — rights an ordinary,
non-elevated, non-service process does not hold. But Windows makes a
documented special case: when the token supplied is a duplicate of the
**calling process's own token**, those privilege checks are bypassed,
because you're not impersonating anyone — you already had every right
that token holds, and you're only ever narrowing it. This module
relies on that specific, real allowance; we verified it works from an
ordinary non-elevated shell before writing any of this documentation
(see `06 Run It`).

### `SE_GROUP_INTEGRITY = 0x00000020` hardcoded rather than via `win32con`
**(b) External contract, worked around after discovery.** This
constant is defined in Microsoft's `WinNT.h`; the installed pywin32
build's `win32con` module does not expose it (we hit an
`AttributeError` testing this directly). Rather than adding a new
dependency, we hardcoded the documented numeric value with a comment
explaining its origin — a real, verified workaround, not a guess.

### Only ever lowering integrity, never raising it
**(a) Forced by the platform.** Raising a token's integrity level
requires `SeRelabelPrivilege`, which ordinary user accounts do not
hold. This module's entire technique works specifically because
*lowering* your own token's integrity is always permitted with no
special privilege — this is not a limitation we designed around, it's
the actual security property that makes least-privilege delegation
possible for ordinary applications (including real sandboxed browsers)
without needing elevation or a broker service.

### `run_with_token()` inherits the console rather than capturing output
**(c) Convention.** Capturing a spawned process's stdout via a pipe
requires setting up `STARTUPINFO` with redirected handles and
`bInheritHandles=True`, plus careful handle-closing to avoid deadlocks.
Since this module's point is about *file access success/failure*, not
about output capture mechanics (already covered pragmatically by
`subprocess` in earlier modules), letting the child write directly to
the inherited console was the simpler, sufficient choice here.

### Adding `flush=True` to every parent `print()` call
**(c) Convention — fixed after a real, observed bug.** Running this
script with stdout redirected (as our own verification tooling does)
initially printed every child process's output BEFORE any of the
parent's own status lines, even though the parent's prints happen
first in program order. The cause: Python block-buffers stdout by
default when it isn't a real interactive terminal, so the parent's
prints sat in a buffer while each child (writing directly to the
inherited console handle) appeared immediately. `flush=True` on the
parent's prints was the fix, verified by re-running and confirming the
correct interleaved order — this is documented here, not silently
patched, because it's a real, transferable gotcha ("my print statements
are out of order relative to a spawned process's output") future
debugging is likely to hit again.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Duplicate own token rather than impersonate another account | (b) Forced/exploited real Windows exemption | No — this is what makes the whole technique work unprivileged |
| Hardcoded `SE_GROUP_INTEGRITY` | (b) Forced by a pywin32 coverage gap, verified directly | Yes, with a different binding/library |
| Only lower integrity, never raise | (a) Forced — `SeRelabelPrivilege` required to raise | No |
| Inherited console instead of captured output | (c) Convention (simplicity) | Yes — pipe redirection is more complex, not needed here |
| `flush=True` on parent prints | (c) Convention (fix for a real observed bug) | N/A — needed for correct ordering |

## What We Proved

Running `run_least_privilege_demo.py` against one ordinary file, with
one Windows user account, produced three real, captured results:

1. A **Low-integrity** child process **could still read** the file
   (`READ OK`) — confirming that Mandatory Integrity Control's default
   policy is "no write up," not "no access at all," a real and
   commonly-misunderstood distinction.
2. The **same** Low-integrity child, attempting to **write** to the
   identical file, was **denied** (`WRITE FAILED: PermissionError`) —
   with no code changes, no different file, no different user account.
3. A **Medium-integrity** (unrestricted, same as the parent) child
   **could write** to the same file successfully (`WRITE OK`) — the
   control that confirms the write failure in (2) was specifically
   caused by the integrity level, not some unrelated environmental
   factor (a locked file, a missing permission elsewhere, etc.).

This is direct, run-and-observed confirmation of the module's claim: a
process's OS-level rights can be reduced below its parent's, purely via
the token it's launched with — the exact mechanism Chromium's original
Windows sandbox used to keep a compromised renderer from writing to the
filesystem, without needing a different user account or elevated broker
service to enforce it.
