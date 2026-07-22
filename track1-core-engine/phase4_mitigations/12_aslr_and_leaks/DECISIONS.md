# Module 12: aslr_and_leaks — DECISIONS.md

## Letting `VirtualAlloc` choose the address (`lpAddress=None`) instead of pinning it
**(c) Convention — the inverse of Modules 5 and 11's choice, deliberately.**
Those modules pinned a fixed address specifically to remove ASLR as a
variable, so the experiment tested only process isolation. This module
needs the opposite: ASLR must be genuinely active for the demonstration
to mean anything, so `lpAddress=None` lets Windows pick, exactly as it
would for any ordinary allocation.

## A fixed, hardcoded `SECRET_OFFSET = 0x2000` between the diagnostic pointer and the secret
**(c) Convention, modeling a real, common situation.** This offset is
"public" in the demo the same way a real binary's internal layout is
public once reverse-engineered: it's baked into the code, not derived
from anything secret. This models a realistic and common real-world
precondition for this exploitation pattern — many real ASLR-defeating
exploits work exactly this way, using a known, fixed relationship
between a leaked pointer and a separate, targeted structure, obtained
by analyzing the target binary once, ahead of time.

## Simulating the "leak" as a plain, honest debug print rather than a subtler bug
**(c) Convention.** A real information leak might come from something
subtler (an uninitialized memory read, a format-string bug, a
timing/type-confusion side channel). This module deliberately uses the
most legible possible stand-in — a labeled print statement — so the
*consequence* of a leak (ASLR's protection collapsing) is the thing
under test, not the mechanics of any one specific leak vulnerability
class. Realistic leak *mechanisms* are covered separately (Module 34's
side-channel content is a genuinely different, subtler mechanism
producing the same class of consequence).

## Using a genuinely STALE address from a separate, earlier, already-exited process for Part A (rather than a made-up/random guess)
**(c) Convention — chosen to make the "why ASLR helps" claim as strong
as possible.** A purely random guess against a 2⁴⁸-ish address space
would obviously fail and wouldn't teach much beyond "big numbers are
big." Using a *real, correctly-formatted, correctly-offset* address
that was valid for a *different* run of the exact same program is a
much stronger negative case — it shows that even a highly informed,
plausible-looking guess (right program, right offset, a real address
that DID work once) fails against ASLR, because the one thing that
matters (the base) changed between runs.

## `attacker.py` checking `content.startswith(EXPECTED_SECRET)` rather than just checking `ok`
**(c) Convention.** `ReadProcessMemory` succeeding only proves the
target address was *mapped* — it says nothing about whether it
contained anything meaningful. Explicitly checking the bytes read
against the known secret value is what actually distinguishes "we
happened to read some valid-but-irrelevant memory" from "we genuinely
found the secret."

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| ASLR left active (`lpAddress=None`) | (c) Convention (the module's whole point) | N/A |
| Fixed public `SECRET_OFFSET` | (c) Convention (models a realistic precondition) | Yes — a discovered rather than assumed offset is also realistic |
| Plain print as the "leak" | (c) Convention (isolates the consequence from the mechanism) | Yes — Module 34 covers a subtler mechanism separately |
| Stale-but-real address for Part A's negative case | (c) Convention (strongest honest negative case) | Yes — a purely random guess is a weaker, less interesting negative case |
| Verify content, not just read success, in `attacker.py` | (c) Convention (precision) | Yes |

## What We Proved

1. **Part A**: a real, correctly-formatted, correctly-offset address —
   valid for one specific prior run of the exact target program — failed
   against a fresh run of that same program (`ReadProcessMemory` itself
   failed, `GetLastError=299`, indicating the guessed range wasn't even
   validly mapped in the new process). This is direct, captured evidence
   that ASLR's re-randomization between runs defeats reuse of even a
   highly plausible, previously-valid address.
2. **Part B**: the identical attack formula (leaked base + fixed offset),
   applied using THIS run's own freshly-leaked base address, succeeded —
   retrieving the exact real secret value, on the first and only attempt,
   regardless of what random address ASLR had actually chosen for this run.

Together, this is direct, run-and-observed confirmation of the
prerequisite claim: ASLR raises the cost of an exploit by making
addresses unpredictable across runs — but it provides zero protection
once a single real information leak reveals even one address, because
everything else an attacker needs is a fixed, learnable offset away.
