# Module 14: stack_canaries_cfi — DECISIONS.md

## `strcpy` with no length argument, into a fixed `char buf[16]`
**(c) Convention, chosen to be the textbook-simplest real bug.**
This is deliberately the most classic, unambiguous C memory-safety bug
there is — no clever tricks, no edge cases, just a bounds-free copy
into a fixed buffer. The point is to make the BUG itself trivial to
read and verify by inspection, so all the interesting behavior is in
what the mitigation does about it, not in understanding the bug.

## `char buf[16]`, and testing with a 40-byte input
**(c) Convention.** 16 bytes is large enough to hold realistic short
strings without looking contrived, and small enough that a 40-byte
input reliably overflows well past it — including past the saved frame
pointer and return address on a typical x86-64 stack layout — without
needing to hand-tune the overflow length precisely.

## Compiling the SAME source file twice, varying only `-fstack-protector-all` vs. `-fno-stack-protector`
**(c) Convention — the module's central controlled experiment.**
Using one shared source file compiled two different ways (rather than
two different programs) removes any possibility that the observed
difference in behavior comes from anything other than the compiler
flag itself.

## Testing both a SHORT and a LONG input against the protected build
**(c) Convention.** Without the short-input control case, a reader
might wonder whether the stack protector flag itself broke normal
operation. Showing the protected build behave completely normally on
harmless input, and only intervene once a genuine overflow occurs, is
what makes "the canary specifically catches the overflow, not general
program behavior" a demonstrated fact rather than an assumption.

## Reading the real Windows exit codes rather than relying on the printed message alone
**(b) External contract, verified directly.** We captured both the
`stderr` message ("*** stack smashing detected ***") AND the actual
NTSTATUS exit code via PowerShell's `$LASTEXITCODE`
(`0xC0000409`, `STATUS_STACK_BUFFER_OVERRUN` — a real, specific,
Windows-native status code for exactly this failure class, distinct
from the generic `STATUS_ACCESS_VIOLATION` the unprotected build
produces). Confirming both the human-readable message AND the
machine-readable status code gives two independent lines of evidence
for the same claim.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| `strcpy` into a fixed buffer as the bug | (c) Convention (textbook clarity) | Yes — many other unsafe-copy patterns exist |
| 16-byte buffer, 40-byte overflow input | (c) Convention (reliable overflow depth) | Yes, other sizes would also work |
| One source file, two compiler flags | (c) Convention (isolates the true variable) | Yes — two separate files is a weaker design |
| Short-input control case | (c) Convention (rules out "protector breaks everything") | Yes, but a materially weaker proof without it |
| Verify via both message AND NTSTATUS code | (b) Forced by wanting independent confirmation | Yes, message alone would be less rigorous |

## What We Proved

Running `run_canary_demo.py` produced three real, captured results from
the identical vulnerable source file:

1. **Protected build, short input**: completed normally, exit code `0`
   — the stack protector adds no observable behavior when nothing is
   actually wrong.
2. **Protected build, long (overflowing) input**: terminated with
   `*** stack smashing detected ***` and exit code `0xC0000409`
   (`STATUS_STACK_BUFFER_OVERRUN`) — the canary detected the corruption
   and killed the process **before** the corrupted return address was
   ever used.
3. **Unprotected build, identical long input**: ran to completion of
   `vulnerable()`, then crashed on **return**, with exit code
   `0xC0000005` (`STATUS_ACCESS_VIOLATION`) — direct evidence that the
   overflow genuinely corrupted the return address, and that address
   was genuinely used, exactly the outcome the canary in case 2 existed
   to intercept earlier.

This is direct, run-and-observed confirmation of the module's precise
claim: a stack canary catches control-flow hijacking attempts at one
specific checkpoint (right before a function returns) — it doesn't
prevent the overflow from happening, it detects that it happened and
refuses to let the corrupted return address take effect.
