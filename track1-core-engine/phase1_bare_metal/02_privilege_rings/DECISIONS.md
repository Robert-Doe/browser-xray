# Module 2: privilege_rings — DECISIONS.md

## `privileged_instr_child.py` and `ring_boundary_probe.py`

### Choosing CLI (0xFA) and HLT (0xF4) as the "privileged" test instructions
**(c) Convention**, sitting on top of an **(a) forced fact**: *which*
instructions the x86-64 architecture defines as privileged is entirely
Intel/AMD's ISA specification — not our choice (see next entry). But
*which* privileged instructions to demonstrate with was ours to pick.
We chose CLI and HLT specifically because they're single-byte, and if
something went unexpectedly wrong and they *did* execute, their effects
(interrupts disabled, CPU halted) are locally contained and recoverable
by the OS scheduler — unlike, say, an instruction that rewrites control
register CR0 and could put the CPU into an inconsistent state. Safety
of the demo itself was the deciding factor.

### The raw byte values (`0xFA`, `0xF4`, `0x90`, `0x0F 0x31`)
**(a) Forced by hardware/spec.** These are not symbolic mnemonics we
get to assign — they are literally the byte encodings x86-64 CPUs
decode as CLI, HLT, NOP, and RDTSC, defined in Intel's own instruction
set reference. Get a single bit wrong and you've encoded a different
instruction entirely (or an invalid one).

### Appending `0xC3` (RET) after every test instruction
**(c) Convention, chosen for safety.** If an instruction we expected to
fault somehow didn't, execution would otherwise fall through into
whatever bytes happen to sit in memory immediately after our buffer —
undefined, dangerous behavior. A RET guarantees that in the "unexpected
success" case, control returns cleanly to the calling Python frame
instead.

### `PAGE_EXECUTE_READWRITE` for the test page, written to and executed
**(c) Convention — a deliberate scope decision.** Using a single RWX
page is the simplest way to write code and immediately run it. It is
*not* representative of production-safe practice — real DEP/W^X
enforcement is specifically about refusing to execute writable pages,
and that exact enforcement is this course's own Module 13. Using RWX
here is a deliberate choice to keep Module 2 testing exactly one
variable (privilege rings) without accidentally also tripping the DEP
boundary Module 13 hasn't taught yet. Building this module with a
stricter write-then-`VirtualProtect`-to-RX pattern was considered and
rejected as unnecessary complexity for what this specific module needs
to prove.

### Catching `OSError` around the foreign function call
**(b) External contract — a verified, not assumed, CPython behavior.**
We did not know in advance exactly what would happen when a hardware
exception fires inside a ctypes-called function; we ran it and observed
directly (see `06 Run It` in the tutorial): CPython's `ctypes` module
wraps every foreign-function call on Windows in a real SEH (Structured
Exception Handling) frame, and converts specific hardware exception
codes into a Python `OSError` with a fixed message
(`"exception: privileged instruction"` for `STATUS_PRIVILEGED_INSTRUCTION`).
This is documented CPython/`ctypes` behavior on Windows, not something
we invented — we depend on it, and the tutorial is explicit that this
is *CPython's* safety net, not a general property of "calling machine
code from anywhere."

### Keeping `privileged_instr_child.py` as an *uncaught* companion script
**(c) Convention.** `ring_boundary_probe.py` catches the fault to build
a clean comparison table. `privileged_instr_child.py` deliberately does
**not** catch it, so a learner also sees the raw, unhandled form: a
real Python traceback ending in `OSError: exception: privileged
instruction`, and a nonzero process exit code. Showing both forms
prevents a false impression that "ctypes always protects you" — the
protection is opt-in (you have to `try`/`except`), not automatic.

### `VirtualFree` in a `finally` block
**(c) Convention.** Not calling it wouldn't break the demo — the OS
reclaims all of a process's memory when it exits regardless — but
leaking a page per iteration is bad hygiene, and `finally` guarantees
cleanup runs even on the fault path.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| CLI/HLT as the privileged instructions | (c) convention, atop (a) forced ISA fact | Yes — other privileged instructions exist |
| Exact byte encodings | (a) Forced — x86-64 ISA | No |
| Trailing RET after each test instruction | (c) Convention (safety) | Yes, but riskier without it |
| RWX page instead of write-then-protect-to-RX | (c) Convention (scope isolation from Module 13) | Yes, deliberately simplified here |
| Rely on ctypes' SEH→OSError translation | (b) Verified external/implementation contract | No — this is what CPython actually does on Windows |
| Provide both caught and uncaught versions | (c) Convention (pedagogical contrast) | Yes |
| `VirtualFree` in `finally` | (c) Convention (hygiene) | Yes |

## What We Proved

Running `ring_boundary_probe.py` against four real, hand-encoded x86-64
instructions produced a captured, four-row result table:

- **NOP** and **RDTSC** — ordinary Ring 3-legal instructions — both
  executed and returned normally (`OK`).
- **CLI** and **HLT** — instructions the x86-64 architecture itself
  defines as privileged — both faulted immediately
  (`exception: privileged instruction`), every single run, with no code
  of ours doing anything to "cause" that beyond simply executing the
  instruction.

This is direct, run-and-observed evidence that Ring 3 code cannot
execute a privileged instruction — not because the OS politely
declines, but because the CPU hardware itself refuses at the instant
of execution, before the instruction has any effect. `privileged_instr_child.py`
additionally shows what this looks like *without* a safety net: an
unhandled `OSError` and a nonzero exit code, proving the fault is real
and fatal by default, not merely a soft warning.
