# Module 1: mem_addressing — DECISIONS.md

Line-by-line / unit-by-unit rationale for every non-obvious choice in
`addr_dump.py` and `prove_aslr_illusion.py`. Every choice below is tagged:

- **(a) FORCED — hardware/platform/spec.** Not actually a choice; get it
  wrong and the program is simply incorrect.
- **(b) FORCED — external contract.** Dictated by an API, file format,
  protocol, or implementation-specific documented behavior we depend on.
- **(c) CONVENTION.** Our call, made for safety/clarity. A different,
  equally correct choice existed.

---

## `addr_dump.py`

### `MEMORY_BASIC_INFORMATION` field order and types
```python
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ...]
```
**(b) External contract.** This must byte-for-byte match the real
`MEMORY_BASIC_INFORMATION` struct defined in Windows' `WinNT.h`. ctypes
has no way to know the real Win32 layout — we are hand-declaring the
other side of a binary contract. Reorder or mistype a field and every
value read after the mistake silently becomes garbage; there is no
runtime check that would catch this for you.

### The `__alignment1` / `__alignment2` padding fields
**(a) Forced by platform.** The x64 C ABI requires 8-byte-sized fields
(pointers, `size_t`) to start on 8-byte boundaries. `AllocationProtect`
is a 4-byte `DWORD` immediately followed by an 8-byte `RegionSize` in
the real struct — the compiler that built `kernel32.dll` inserted 4
bytes of padding there to satisfy that alignment rule, whether it wanted
to or not. We aren't choosing to add padding; we're declaring the
padding the ABI already forces to exist, so our ctypes struct's total
size and field offsets match the real one.

### Explicit `argtypes` / `restype` on `VirtualQuery`
```python
kernel32.VirtualQuery.argtypes = [...]
kernel32.VirtualQuery.restype = ctypes.c_size_t
```
**(b) External contract, with a (c) convention layered on top.** ctypes
defaults an undeclared function's return type to a 32-bit `c_int`. On a
64-bit process, `VirtualQuery`'s real return type is `SIZE_T` (64-bit).
Leaving `restype` undeclared would silently truncate return values —
this has bitten real ctypes code before. Declaring both `argtypes` and
`restype` explicitly is technically optional (ctypes would still *run*
without it), which makes doing so a **convention** — but it's a
convention chosen specifically to eliminate a known, real class of
silent-truncation bugs, not an arbitrary style preference.

### Using `id(obj)` as "the address"
**(b) External contract — and a scoped one.** The Python *language
specification* only guarantees `id()` returns a value unique and
constant for an object's lifetime — it never promises that value is a
memory address. **CPython specifically** documents `id()` as returning
the object's memory address as an implementation detail. We are relying
on CPython's implementation contract, not the language spec — this
module's claims do not port to PyPy or other Python implementations
without re-verification, and the tutorial says so explicitly.

### Using a large int (`999_983 + 1`) instead of a small literal
**(c) Convention.** CPython pre-allocates and interns integers from
-5 to 256 as long-lived singletons shared across the whole process.
Using a small int like `5` would print the address of a singleton that
existed before this run's "fresh allocation" ever happened, which would
quietly defeat the entire experiment. A large, non-cached value forces
a genuine heap allocation local to this run.

### `sys.platform != "win32"` guard raising `SystemExit`
**(c) Convention.** `VirtualQuery` is a Windows-only API — there is no
silent cross-platform fallback here by design, per this course's
Windows-native-primary architecture decision (see root `ROADMAP.md`).
Failing loudly and immediately, rather than trying to shim in a
Linux `/proc/self/maps` equivalent inline, keeps this module's claims
scoped to what it actually tested.

---

## `prove_aslr_illusion.py`

### Parsing `addr_dump.py`'s stdout with a regex instead of a machine format
**(c) Convention.** A `--json` output mode on `addr_dump.py` would be
more robust to parse. We chose plain, human-readable text instead
because a learner is meant to *run addr_dump.py directly* first and
read it themselves — optimizing its output for a downstream parser
would have made the primary, standalone artifact worse for the reader
it's actually for. The regex coupling this creates is a deliberately
accepted tradeoff, not an oversight.

### `subprocess.run(..., check=True)`
**(c) Convention.** If `addr_dump.py` fails (e.g., run on non-Windows),
we want the proof script to crash loudly with the real traceback rather
than silently proceeding with empty output and printing a misleading
"proof."

### `sys.executable` rather than the string `"python"`
**(b) External contract, functionally forced.** This machine has two
separate Python installations (a Microsoft Store 3.12 and an Anaconda
3.11) resolving differently for the `python` vs `pip` commands. Using
the literal string `"python"` would let the subprocess silently resolve
to *whichever interpreter happens to be first on PATH at run time* —
not necessarily the one currently executing this script, and not
necessarily one with the same behavior. `sys.executable` is the only
way to guarantee the child process is running the identical interpreter
as the parent, which matters because CPython's exact small-int caching
and memory allocator behavior is itself implementation/version-specific.

### Comparing the *relative offset* between two objects across runs
**(c) Convention — this is the module's actual teaching payload.**
Nothing forces this comparison; it's the deliberate analytical step that
turns "the addresses looked different" into "the base moved but the
allocator's internal relative layout didn't," which is the precise,
falsifiable claim this module exists to prove.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Struct field layout matches WinNT.h exactly | (a) Forced — platform ABI | No |
| Padding fields present | (a) Forced — platform ABI | No |
| Explicit `argtypes`/`restype` | (b) contract / (c) convention | Yes, but reintroduces a known truncation bug class |
| Rely on CPython's `id()`-is-address behavior | (b) External contract (implementation-specific) | Not on this course's stated toolchain (Python 3.12 CPython) |
| Non-cached large int for "fresh" object | (c) Convention | Yes — any value outside -5..256 works equally |
| Windows-only, hard fail elsewhere | (c) Convention | Yes — could shim `/proc/self/maps` on Linux |
| Text output over JSON | (c) Convention | Yes — JSON would ease parsing, cost readability |
| `sys.executable` over `"python"` | (b) Functionally forced by this machine's dual-install reality | No, given the environment |
| Diff relative offsets, not just absolutes | (c) Convention (the module's core teaching move) | N/A — this is the point |

## What We Proved

Running `addr_dump.py` twice as two independent OS processes and
diffing the output produced real, captured evidence that:

1. **Every printed address differed between the two runs** — the same
   Python objects, allocated the same way, landed at different virtual
   addresses each time the process started fresh.
2. **The relative offset between two objects allocated back-to-back in
   the same run was identical across both runs** (195536 bytes in our
   captured run) — proving the *allocator's* internal layout logic is
   deterministic, while only the *base* it's anchored to moves.
3. **`VirtualQuery` successfully described a real page** for every
   address queried (`PAGE_READWRITE`, `MEM_COMMIT`, `MEM_PRIVATE`) —
   proving that permission/state metadata is a genuine, queryable
   property of the page itself, addressable through the OS, and not
   something our program invented or assumed.

Together this is direct, run-and-observed evidence for the prerequisite
claim: a virtual address is a per-run, per-process assignment translated
by the OS/MMU — never a fixed physical location.
