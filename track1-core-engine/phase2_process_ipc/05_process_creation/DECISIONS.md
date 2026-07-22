# Module 5: process_creation — DECISIONS.md

## `mem_pin.py`

### Passing a non-NULL `lpAddress` to `VirtualAlloc`
**(b) External contract.** `VirtualAlloc`'s documented behavior is:
if `lpAddress` is `NULL`, the system chooses the address; if
`lpAddress` is non-NULL, the system attempts to allocate at that exact
address (rounded to allocation granularity) and **fails outright** if
that range isn't free — it will not silently substitute a different
address. This exact/fail behavior, not a convention we invented, is
what makes it possible to force two processes to agree on a number in
advance.

### The specific value `0x0000200000000000` (32 TB)
**(c) Convention.** Any mutually-agreed, available address would prove
the same point. We verified several candidates directly (see
`06 Run It`) and picked a high, unusual address specifically because
ordinary process startup — the loader, the default heap, the initial
stack, loaded DLLs — has no reason to ever land anywhere near it,
making an exact-address request reliably succeed run after run rather
than occasionally colliding with something ASLR happened to place
there.

### Raising `RuntimeError` if the OS grants a different address than requested
**(c) Convention — a correctness guard, not a formality.** If this ever
fired, the whole experiment's premise (both processes using the
*identical* address) would be silently false, and every result after
it would be meaningless. Failing loudly here was a deliberate choice
over letting a mismatched-address run produce a misleadingly "successful"
looking result.

### `ctypes.string_at` / `ctypes.memmove` for reading and writing the pinned buffer
**(c) Convention.** These are ctypes' standard, minimal-boilerplate
functions for raw memory access by address — chosen over, e.g., casting
to a `ctypes` array type, because the module's point is about the
address itself, not about typed memory views.

---

## `child_writes_same_address.py` and `parent_writes.py`

### Reading the pinned address BEFORE writing, in the child
**(c) Convention — this is the experiment's actual control.** Without
this step, "the child wrote its own value" wouldn't distinguish between
"the address was genuinely private to the child" and "the address
happened to already contain something unrelated." Reading first and
finding all-zero bytes — freshly `MEM_COMMIT`ted pages are documented
by Microsoft to be zero-initialized — positively rules out the
child inheriting or seeing the parent's data at that address.

### Parent re-reads its OWN copy AFTER the child has run and exited
**(c) Convention — the experiment's actual payoff.** This is the step
that would catch a failure of process isolation, if one existed: if the
child's write had somehow reached the parent's physical memory (e.g.
if the two processes were actually sharing that page), the parent's
final read would show the child's string instead of its own. It didn't.

### `subprocess.run(..., check=True)` rather than `Popen`
**(c) Convention.** The parent's proof depends on the child having
fully completed its write *before* the parent re-reads its own memory.
`subprocess.run` blocks until the child exits, which is exactly the
ordering guarantee this experiment needs; `check=True` additionally
ensures a child-side crash surfaces loudly rather than the parent
silently reading its own unmodified value and (correctly, but for the
wrong reason) reporting "unchanged."

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Non-NULL `lpAddress` forces exact-or-fail allocation | (b) Forced — documented `VirtualAlloc` behavior | No |
| Address value `0x200000000000` | (c) Convention (verified, unusual, reliable) | Yes — any mutually free address works |
| Hard failure if granted address ≠ requested | (c) Convention (correctness guard) | Yes, but would weaken the proof |
| Child reads before writing (control step) | (c) Convention (the experiment's control) | N/A — this is the point |
| Parent re-reads after child exits | (c) Convention (the experiment's payoff) | N/A — this is the point |
| `subprocess.run(check=True)` over `Popen` | (c) Convention (ordering + failure visibility) | Yes, with weaker guarantees |

## What We Proved

Running `parent_writes.py` produced real, captured evidence that:

1. Two **completely independent processes** each successfully claimed
   the identical virtual address `0x200000000000`.
2. The child, reading that address **before writing anything**, saw
   only zero bytes — never the parent's string — even though the
   parent had already written its value there moments earlier, at the
   identical numeric address.
3. After the child wrote its own value and exited, the parent re-read
   its own copy at that same address and found its **original value,
   completely unchanged**.

This is direct, run-and-observed confirmation that spawning a process
(via `subprocess`, which under the hood uses Windows'
`CreateProcess`) creates a genuinely separate address space — not a
shared one, not a copy-then-diverge-eventually one. The numeric
address was identical; the physical reality behind it, in each
process, was not.
