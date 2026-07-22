# Module 34: side_channel_timing — DECISIONS.md

## A non-constant-time STRING COMPARISON timing channel, rather than attempting a real CPU-cache (Flush+Reload) or speculative-execution (Spectre) channel
**(c) Convention — a deliberate choice made after directly testing the
alternative and finding it unreliable.** We first tried to build a
genuine CPU-cache-timing side channel in Python (touching a "warm" vs.
"cold" memory chunk and timing the difference). Testing it directly
(see the module's build history) showed no reliable, measurable signal
at all — Python's own interpreter overhead (bytecode dispatch, function
call overhead, GC) operates at a scale that swamps real L1/L2 cache
timing differences, which live at the nanosecond scale. Rather than
present an unreliable or fabricated result, we deliberately chose a
DIFFERENT, real, well-documented timing side-channel class —
non-constant-time comparison — that we verified produces a strong,
completely reliable signal in pure Python. This is a real, historically
significant vulnerability class in its own right (timing attacks
against password/HMAC/token verification are real, documented,
CVE-worthy bugs), not a lesser substitute for Spectre.

## `PER_CHARACTER_DELAY = 0.0002` seconds injected into BOTH the vulnerable and fixed comparison functions
**(c) Convention, and an honest, disclosed choice.** A bare
character-by-character Python comparison with no injected delay is
fast enough that Python-level timing (`time.perf_counter()`, subject to
OS scheduling granularity and interpreter overhead) could not reliably
distinguish a 1-character-correct guess from a 2-character-correct
guess — we did not attempt to claim otherwise. Adding a small, fixed,
EQUAL per-character delay to both functions models a realistic
real-world scenario (a per-character verification step that does real
work, such as a hash update) and is what makes the demonstrated signal
large enough to be reliably, repeatably measurable — without changing
which function is vulnerable (the vulnerability is EARLY EXIT on
mismatch, not the delay itself, which is identical in both functions).

## `_time_guess()` taking the MINIMUM over several repetitions, not the average
**(b) External contract — a real, standard technique.** Minimum-of-N is
the standard noise-reduction approach used in real timing-attack
research and tooling, because OS scheduling, garbage collection pauses,
and other system noise can only ever ADD delay to a measurement, never
subtract from the true minimum achievable time for that operation.
Averaging would let occasional noise spikes distort the signal;
taking the minimum consistently recovers the "best case" (least noisy)
timing for each guess.

## Recovering the secret ONE CHARACTER AT A TIME, trying every character in a fixed charset at each position
**(b) External contract.** This is the real, standard structure of
this entire vulnerability class in practice: an early-exit comparison
leaks information ONE CHARACTER (or byte) AT A TIME specifically
because the comparison function returns as soon as the FIRST mismatch
is found — meaning only the length of the correct PREFIX affects
timing, which is exactly what makes character-by-character (rather
than whole-guess) recovery both possible and dramatically more
efficient than brute-forcing the entire secret at once.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Non-constant-time comparison channel, not CPU-cache timing | (c) Convention, chosen after testing the alternative failed | Yes, given C-level tooling instead of pure Python |
| Injected, disclosed per-character delay in both functions | (c) Convention (honest, necessary for a reliable Python-level signal) | Yes, with lower-level timing tools this wouldn't be needed |
| Minimum-of-N repetitions for noise reduction | (b) Forced — standard, real technique | No |
| Character-by-character recovery | (b) Forced — matches how early-exit comparison actually leaks information | No |

## What We Proved

1. **The vulnerable comparison (`naive_compare`)**: the timing attack
   recovered the FULL, EXACT 8-character secret token
   (`'X7f9Qz2A'`), matching perfectly, using ONLY wall-clock timing
   measurements — never once reading the secret's actual value.
2. **The fixed comparison (`constant_time_compare`)**: the IDENTICAL
   attack, given the identical number of guesses and identical effort,
   recovered a completely wrong, effectively random 8-character string
   — the timing signal was gone.

This is direct, run-and-observed confirmation of this module's central,
precise claim: a real information leak can exist entirely within the
TIMING dimension, completely independent of whether the Same-Origin
Policy (Module 17) or process-level site isolation (Module 11) are
working correctly — because neither of those policies was ever designed
to hide how long an operation takes, only what data a response
contains. This is exactly the category of concern that motivated real
browsers to treat Site Isolation as a defense against Spectre-class
timing attacks specifically at the PROCESS boundary (physically
separating memory, closing off an entire class of cache-timing
measurement) rather than relying on script-level content checks alone.
