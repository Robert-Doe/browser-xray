# Module 35: sandbox_escape_chain — DECISIONS.md

## Reusing Module 9's and Module 10's exact, already-verified mechanisms, rather than inventing a new sandboxing technique
**(c) Convention — the module's entire point.** This course's final
module is deliberately NOT a new technical primitive. Its job is to
prove that real security requires COMBINING independently-built,
independently-verified defenses — which only means something if those
defenses are the genuine ones already proven real in Phase 3, not new
ones built just for this demo.

## Citing Module 14's real buffer overflow as "how code execution would be achieved," without re-detonating it here
**(c) Convention — a deliberate scope boundary.** Module 14 already
built and verified a REAL, working (if deliberately non-weaponized)
stack buffer overflow. Re-running it here would add complexity (this
module would need to spawn a C process, capture a crash, then somehow
continue an "attacker now has code execution" narrative from a crashed
process) without adding any NEW evidence — the interesting, provable
claim for THIS module is what happens AFTER code execution is assumed,
not re-proving code execution is possible at all.

## Switching the second probe action from "read" to "write/tamper," after checking Module 9's own established finding
**(b) External contract, consistency-checked against prior work
before, not after, hitting a bug.** An initial draft tested the
compromised renderer attempting to READ the sensitive file under
Scenario C (token-only). Before treating that as a bug to investigate,
we checked it against Module 9's own DECISIONS.md and tutorial, which
already directly proved (with captured evidence) that Windows'
Mandatory Integrity Control blocks WRITE-up but explicitly does NOT
block read-up on ordinary file objects by default. A read-based test
would have been guaranteed to succeed regardless of the token
restriction, testing nothing meaningful about that defense. Switching
to a WRITE/append action is what actually exercises the real behavior
Module 9 proved — keeping this capstone module's evidence consistent
with, rather than contradicting, the course's own established findings.

## The 2×2 scenario matrix (neither / job-only / token-only / both), rather than just showing "unrestricted" vs. "fully restricted"
**(c) Convention — the module's core teaching structure.** Showing
only the two extremes would prove defenses exist and work together,
but would NOT prove each defense has its own distinct, LIMITED scope.
Testing both single-defense scenarios independently is what produces
the module's sharpest evidence: Job-Object-only leaves file tampering
open, token-only leaves process spawning open — two real, different,
complementary gaps, each closed by a different, real mechanism.

## `flush=True` throughout the orchestrator's own print statements
**(c) Convention — a recurring, now-familiar fix.** The same
child-output-vs-parent-output ordering issue documented in Modules 9
and 10's own `DECISIONS.md` files reappeared here (children inherit the
console and write immediately; this script's own prints are
block-buffered when stdout isn't a live terminal). Applied the
identical, by-now-standard fix.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Reuse Modules 9 & 10's exact real mechanisms | (c) Convention (the module's entire point) | N/A |
| Cite, don't re-detonate, Module 14's buffer overflow | (c) Convention (avoids redundant, complex re-proof) | Yes, re-running it is possible but adds no new evidence |
| Write/tamper instead of read for the file-access probe | (b) Forced — matches Module 9's own already-proven MIC behavior | No, once Module 9's finding is taken as given |
| Full 2×2 scenario matrix | (c) Convention (proves each defense's LIMITED scope, not just "defenses work") | Yes, a two-scenario version is simpler but proves less |
| `flush=True` on all orchestrator prints | (c) Convention (recurring, established fix) | Yes, run in a live terminal and it's unnecessary |

## What We Proved

Running the identical "compromised renderer" probe under four real,
verified process-launch configurations produced exactly the expected
2×2 result:

| Scenario | Job Object | Token | spawn_new_process | tamper_with_file |
|---|---|---|---|---|
| A | off | off | SUCCEEDED | SUCCEEDED |
| B | ON | off | **BLOCKED** | SUCCEEDED |
| C | off | ON | SUCCEEDED | **BLOCKED** |
| D | ON | ON | **BLOCKED** | **BLOCKED** |

This is direct, run-and-observed confirmation of this module's — and
in a real sense, this entire course's — central claim: no single
security mechanism this course built is "the" defense. Module 10's
Job Object stops process creation and nothing else; Module 9's
least-privilege token stops privilege-escalating writes and nothing
else. A process with only one of these applied remains genuinely,
exploitably compromised in the dimension the OTHER mechanism was built
to close. Only Scenario D — both real, independently-verified defenses,
applied together — actually contains a fully compromised process. Real
browser sandboxing looks exactly like Scenario D: several independent,
individually-limited mechanisms, layered, each closing a gap the
others leave open.
