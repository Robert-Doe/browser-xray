# Module 10: syscall_filtering — DECISIONS.md

## Choosing Job Objects (`JOB_OBJECT_LIMIT_ACTIVE_PROCESS`) over Win32k System Call Disable
**(c) Convention — chosen after a real, documented dead end.** The
Windows-native mechanism closest to Linux's seccomp-bpf is actually
`UpdateProcThreadAttribute` with
`PROC_THREAD_ATTRIBUTE_MITIGATION_POLICY` and the
`PROCESS_CREATION_MITIGATION_POLICY_WIN32K_SYSTEM_CALL_DISABLE_ALWAYS_ON`
flag — this is the real mechanism Chromium's Windows sandbox uses to
block an entire renderer process from ever making Win32k.sys (GUI
subsystem) syscalls. We built it first: correct struct layouts, correct
attribute IDs (verified against `PROCESS_MITIGATION_POLICY` enum
ordering), correct `EXTENDED_STARTUPINFO_PRESENT` process creation.
Every API call reported success (`CreateProcessW` returned `TRUE`,
`UpdateProcThreadAttribute` returned `TRUE`). But directly querying the
resulting process's actual policy via `GetProcessMitigationPolicy`
(itself verified correct against a known-good case: default DEP status
on a plain 64-bit process, which read back exactly as expected) showed
the Win32k policy flag was **never actually applied** — and a real
win32k-heavy test (window class registration + window creation)
succeeded inside the "restricted" child, confirming the policy plainly
wasn't in effect, not just unreported.

We did not chase this further into undocumented territory (possible
causes include Windows-build-specific behavior, an unmet precondition,
or an attribute-list transfer subtlety we didn't isolate). Per this
course's non-negotiable rule — never assert a behavior that wasn't
verified by actually running it — we did not write a module claiming
Win32k lockdown works based on API return codes alone, once direct
verification contradicted them. We pivoted to Windows Job Objects
instead, which are: (1) an equally real, equally Chromium-relevant
sandboxing primitive (Chromium's sandbox `JobLevel` restrictions use
exactly `JOB_OBJECT_LIMIT_ACTIVE_PROCESS` and related limits), (2) far
more mature, stable, and widely-relied-upon API surface, and (3)
something we verified end-to-end, including the negative case, before
writing a single word of tutorial content.

## `JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 1` as the specific restriction demonstrated
**(c) Convention.** Job Objects support many simultaneous limits
(memory, CPU time, UI restrictions, process count). We chose the active
process count limit specifically because it produces an unambiguous,
easily-explained failure (`ERROR_NOT_ENOUGH_QUOTA`) at the exact moment
of an attempted `CreateProcess` call, and because "stop a compromised
renderer from spawning a shell" is a real, well-known, high-value
sandboxing goal that maps directly onto this one limit.

## `CREATE_SUSPENDED` + `AssignProcessToJobObject` + `ResumeThread`, rather than assigning after the process starts running
**(c) Convention, chosen for correctness, not just style.** If the
child process were allowed to start running before being assigned to
the restrictive job, it could -- in principle, depending on timing --
attempt its own child-spawn before the restriction was in place, which
would make Part B's result timing-dependent and unreliable. Creating
the process suspended, assigning it to the job while it cannot yet
execute any of its own code, and only then resuming it guarantees the
restriction is in effect for 100% of the child's execution, with no
race window.

## Using a dict, not a tuple, for `SetInformationJobObject`
**(b) External contract, discovered empirically.** Our first attempt
passed a tuple mirroring the C struct's field order (a pattern that
worked for several other pywin32 APIs elsewhere in this course) and
failed immediately with `TypeError: argument 3 must be dict, not
dict`. Querying the *current* (default, all-zero) limit info via
`QueryInformationJobObject` first, inspecting its actual returned
shape, and modifying that same dict in place before setting it back
was the fix — verified directly, not guessed from documentation alone.

## `probe_spawn_child.py` catching only `OSError`
**(c) Convention.** `subprocess.run`'s failure to launch a process
(as opposed to the launched process itself failing) surfaces as an
`OSError` (specifically, on Windows, wrapping the `WinError`) — this is
the correct, specific exception type for "the OS refused to create the
process," distinct from, say, the child process running and exiting
with a nonzero code, which would not raise at all.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Job Objects over Win32k System Call Disable | (c) Convention, forced by a verified real dead end | Win32k lockdown remains a real mechanism; not reliably reproducible here |
| `ActiveProcessLimit = 1` as the specific demonstrated limit | (c) Convention | Yes — other Job Object limits also demonstrate OS-level enforcement |
| `CREATE_SUSPENDED` before job assignment | (c) Convention (eliminates a real race window) | Yes, with weaker timing guarantees |
| Dict-based `SetInformationJobObject` calls | (b) Forced by pywin32's actual binding shape | No, once pywin32 is the chosen library |
| Catch `OSError` specifically in the probe | (c) Convention (precise exception semantics) | Yes, a broader `except Exception` also works, less precisely |

## What We Proved

1. **Part A**: `probe_spawn_child.py`, run with no restriction, spawned
   its own child process successfully — the ordinary, unrestricted case.
2. **Part B**: the exact same script, exact same Python interpreter,
   exact same `subprocess.run` call — placed inside a Job Object with
   `ActiveProcessLimit=1` — had its process-creation attempt refused
   outright by the OS (`WinError 1816`, "Not enough quota is available
   to process this command"), with no exception-handling trickery or
   special code inside the probe itself needed to produce that failure.

This is direct, run-and-observed confirmation that an OS-enforced
restriction can block an entire category of operation (here: process
creation) regardless of what code inside the restricted process
attempts — the process's own code has no way to opt out or work around
it, because the refusal happens in the kernel, at the moment of the
`CreateProcess` syscall itself, before any new process exists. This is
the real mechanism a Chromium-style Windows sandbox uses to stop a
compromised renderer from spawning a shell.
