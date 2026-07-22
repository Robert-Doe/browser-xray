# Module 13: dep_nx_w_xor_x — DECISIONS.md

## Using C for the two target programs, Python for the orchestrator
**(c) Convention, per this course's stated tools policy.** This is the
first module where the point being proven — what the CPU does when a
process jumps into non-executable memory — genuinely requires raw
machine code and a language with no runtime standing between the
program and that memory. Python could allocate the memory (as earlier
modules did via `ctypes`), but writing the actual "jump into this
buffer" as a first-class, minimal, inspectable operation is clearer and
more honest in six lines of C than through several layers of `ctypes`
function-pointer plumbing. The orchestration (compiling, running,
reporting) stays in Python, consistent with every other module.

## The hand-assembled bytes `B8 2A 00 00 00 C3` (`mov eax, 42; ret`)
**(a) Forced by the x86-64 instruction encoding.** These are not
symbolic — they are the literal byte encoding of a minimal, complete,
valid function. Returning a specific, checkable value (42, not just
"some code that doesn't crash") is what lets `dep_legitimate_jit.c`
prove it didn't just avoid crashing, but genuinely *executed* the
intended code and got the intended result.

## `malloc()` for the violating buffer, `VirtualAlloc(..., PAGE_EXECUTE_READWRITE)` for the legitimate one
**(b) External contract.** `malloc` is documented and guaranteed to
return memory suitable for data, never guaranteed executable — on
Windows this is backed by the process heap, which is READ+WRITE, never
EXECUTE. `VirtualAlloc` with an explicit `PAGE_EXECUTE_READWRITE`
protection flag is the documented, sanctioned way to request memory the
OS agrees, in advance, may be executed — this is not a workaround, it's
the API's own intended purpose (real JIT compilers use exactly this).

## Compiling with `-O0` (no optimization)
**(c) Convention.** A more aggressive optimization level could, in
principle, let the compiler reorder, inline, or otherwise transform
code in ways that obscure the direct correspondence between the C
source and what's actually being tested. `-O0` keeps the compiled
behavior as close as possible to a literal reading of the source.

## The `PATH` fix in `run_dep_demo.py` (`_BUILD_ENV`)
**(b) External contract, discovered empirically.** Invoking
`gcc.exe` by its full absolute path, without its own containing
directory (`mingw64\bin`) also present on `PATH`, failed silently
(`returncode=1`, no stderr) when tested directly. This MSYS2 packaging
of `gcc.exe` locates its own helper executables (`cc1.exe`,
`collect2.exe`, `ld.exe`) via `PATH` lookup rather than purely via a
path relative to its own location. We verified the fix directly (adding
`mingw64\bin` to the subprocess's `PATH`) before relying on it, rather
than assuming a full path alone would be sufficient.

## `os.path.abspath(exe)` when launching the compiled `.exe` files
**(b) External contract, discovered empirically.** `subprocess.run`
on Windows uses `CreateProcess` directly, which — unlike a shell —
does not search the current working directory for a bare relative
filename like `"dep_violation.exe"`; this raised a real
`FileNotFoundError` during testing. Windows shells like `cmd.exe`
add that convenience; the raw Win32 API does not. Using an explicit
absolute path removed the ambiguity.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| C for the target programs, Python for orchestration | (c) Convention (this course's tools policy) | Yes — a pure-ctypes version is possible but less direct |
| `mov eax, 42; ret` as the payload | (a) Forced — real x86-64 encoding | No, though a different return value would work equally |
| `malloc` vs. `VirtualAlloc(PAGE_EXECUTE_READWRITE)` | (b) Forced — documented memory-permission contracts | No |
| `-O0` compilation | (c) Convention (source/behavior correspondence) | Yes |
| PATH fix for invoking gcc | (b) Forced by this specific gcc packaging, verified directly | No, once this toolchain is the one installed |
| Absolute path for launching compiled exes | (b) Forced by `CreateProcess` semantics | No |

## What We Proved

Built and ran both C programs, with real, captured Windows-native
results:

1. **`dep_violation.exe`**: jumping into identical, valid machine code
   placed in ordinary `malloc`'d heap memory was killed by the OS with
   exit code `0xC0000005` (`STATUS_ACCESS_VIOLATION`) — confirmed both
   via direct execution and via `$LASTEXITCODE` in PowerShell, matching
   the real Windows-native NTSTATUS for this exact class of fault.
2. **`dep_legitimate_jit.exe`**: the identical machine code bytes,
   placed instead in memory explicitly requested as
   `PAGE_EXECUTE_READWRITE`, executed successfully and returned the
   correct, checkable value (`42`), with a clean exit code of `0`.

This is direct, run-and-observed confirmation of DEP/W^X's real,
absolute guarantee: it is not a heuristic or a "usually blocks this" —
identical bytes, identical jump-into-buffer logic, and the sole
determining factor was whether the OS had been explicitly told, in
advance, that this specific page was allowed to contain executable
code.
