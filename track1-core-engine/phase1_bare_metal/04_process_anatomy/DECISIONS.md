# Module 4: process_anatomy — DECISIONS.md

## `process_anatomy.py`

### Using `pywin32` (`win32api`, `win32process`, `win32security`) instead of raw `ctypes` throughout
**(c) Convention.** Modules 1–3 deliberately used raw `ctypes` to make
every ABI detail visible. Here, for the pieces pywin32 already wraps
correctly and safely (`GetProcessMemoryInfo`, token/SID handling), we
use it rather than re-declaring more structs — the teaching point of
this module is "what a process is made of," not "how to bind more
Win32 structs," which Modules 1–3 already covered thoroughly. Where
pywin32 has no wrapper (thread enumeration, handle count), we still
drop to `ctypes` directly, so the module doesn't hide the boundary
entirely.

### `CreateToolhelp32Snapshot` + manual `Thread32First`/`Thread32Next` filtering, instead of a direct "thread count" API
**(b) External contract.** There is no single Win32 call that directly
returns "how many threads does PID X have" — the only supported way is
to snapshot *every* thread on the entire system and filter by
`th32OwnerProcessID` yourself. This is Microsoft's own API shape, not
a roundabout choice we made.

### `ConvertSidToStringSid()` + parsing the trailing RID, instead of `GetSidSubAuthority`
**(c) Convention, chosen after `GetSidSubAuthority` turned out not to
be exposed by this pywin32 version.** We verified this directly (see
`06 Run It`) rather than assuming pywin32's coverage. The string form
(`S-1-16-8192`) is a standard, well-documented SID text representation
where the final dash-separated number is exactly the sub-authority /
integrity RID we need — parsing it is a legitimate, if slightly
indirect, way to reach the same value.

### The `names` dict mapping RID → human-readable integrity level
**(c) Convention.** These names (`Low`, `Medium`, `High`, `System`,
...) are Microsoft's own documented labels for these RID values, but
choosing to build a lookup dict for readability — rather than printing
the raw RID and making the reader memorize the mapping — was our call,
made for the same "presentation-friendly" reasoning behind this
course's Python-first tooling choice.

---

## `inspect_child_process.py`

### `PROCESS_QUERY_INFORMATION | PROCESS_VM_READ` as the requested access mask
**(c) Convention, informed by (b) external contract.** These two access
rights are Microsoft-defined constants (we don't get to invent new
ones), but choosing this specific *combination*, rather than requesting
`PROCESS_ALL_ACCESS`, is deliberate: it's the minimum set of rights
that actually satisfies everything this script queries
(`GetProcessMemoryInfo`, our thread/handle helpers, token queries).
Requesting only what's needed is itself a small, concrete preview of
the least-privilege principle Module 9 builds on directly.

### `time.sleep(0.3)` after spawning the child before querying it
**(c) Convention — a real race condition, handled pragmatically.**
There is a brief window between `Popen()` returning and the child
process finishing its own startup (loading the Python interpreter,
etc.) during which some queries could behave oddly (e.g., thread count
mid-startup). A fixed short sleep is a simple, if inelegant, way to
avoid flakiness in a teaching demo; a production-grade version might
instead poll for a specific readiness signal.

### Reusing `count_threads`, `handle_count`, `integrity_level` from `process_anatomy.py` via import
**(c) Convention.** Keeping one implementation of each query function
avoids two copies drifting out of sync, and reinforces the module's
actual point: these functions work identically whether you're
inspecting yourself or another process — only the *handle you start
with* differs (`GetCurrentProcess()`'s pseudo-handle vs. a real
`OpenProcess()` handle).

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| pywin32 for memory/token, ctypes for threads/handles | (c) Convention (scope focus) | Yes — all-ctypes was Modules 1–3's style |
| Toolhelp32 snapshot-and-filter for thread count | (b) Forced — no direct Win32 API | No |
| SID string parsing for integrity RID | (c) Convention (verified workaround) | Yes, if a newer pywin32 exposed `GetSidSubAuthority` |
| Minimal access mask (`QUERY_INFORMATION \| VM_READ`) | (c) Convention (least-privilege preview) | Yes — `PROCESS_ALL_ACCESS` would also work here |
| Fixed `sleep(0.3)` before inspecting child | (c) Convention (pragmatic, not robust) | Yes — a readiness-signal approach is more correct |
| Shared query functions via import | (c) Convention (avoid duplication/drift) | Yes |

## What We Proved

1. **`process_anatomy.py`**: for a live process, thread count, open
   handle count, working-set memory, and security-context integrity
   level are all independently queryable, kernel-tracked facts — not
   something inferred or assumed. Together with Module 1's proof about
   virtual address spaces, this directly confirms the Prerequisite 4
   claim: a process is a PCB (identity + security context + handle
   table) plus an address space plus N threads, and every one of those
   pieces is real and separately inspectable.
2. **`inspect_child_process.py`**: the identical query functions,
   pointed at a genuinely different process, returned that *other*
   process's real data — but only after explicitly obtaining a handle
   via `OpenProcess()` with named rights. This confirms process anatomy
   is kernel-tracked state reachable by any suitably privileged process,
   not private self-knowledge — and that reaching it always requires
   the explicit handle-with-rights mechanism from Prerequisite 5, never
   a bare PID.
