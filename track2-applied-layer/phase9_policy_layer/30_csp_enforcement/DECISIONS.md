# Module 30: csp_enforcement — DECISIONS.md

## Splitting the header on `;` then on whitespace, matching Module 16/21's parsing style
**(c) Convention.** A CSP header is genuinely this simple structurally
— directive name, then space-separated sources, semicolon-separated
directives. Reusing the same "split on a clear delimiter, strip
whitespace" approach this course has used for HTTP headers (Module 16)
and CSS declarations (Module 21) is consistent, not a new technique
invented for this module.

## Only implementing the blanket `'unsafe-inline'` keyword, not nonces or hashes
**(c) Convention — a deliberate, named scope boundary.** Real CSP
supports `'nonce-<value>'` and `'sha256-<hash>'` source expressions,
which allow SPECIFIC inline scripts (matching a per-request nonce or a
script's exact content hash) without allowing all inline scripts the
way `'unsafe-inline'` does. This is real, important, additional
precision modern CSP deployments rely on — implementing it would
require this module's script loader to compute/compare hashes or track
per-request nonces, which is out of this module's scope. The blanket
keyword is enough to demonstrate the core "checked before execution"
claim.

## Checking `script-src` with a fallback to `default-src`
**(b) External contract.** This is real, specified CSP fallback
behavior — if a page doesn't declare a specific `script-src` directive,
`default-src` governs scripts (and other resource types) instead.
Implementing this fallback, rather than only checking `script-src`
directly, avoids silently misrepresenting a real policy that relies on
`default-src` alone.

## ADDENDUM — a real bug caught later, while building Module 32
**(b) External contract, corrected after discovery.** The original
version of `check_script()` computed
`sources = policy.get("script-src", policy.get("default-src", []))` —
which silently treated "no CSP header sent at all" (an EMPTY policy
dict) the same as "a `script-src` directive explicitly present but set
to an empty/`'none'`-equivalent list," both collapsing to
`sources = []`, both then rejected as blocked. This directly
contradicted this module's OWN documented tutorial claim ("no CSP
header means everything is allowed by default") — a real inconsistency
between the code and its own docs, caught only when Module 32 exercised
this exact "no CSP header" case directly and got `False` (blocked)
where `True` (allowed) was expected. Fixed by explicitly checking
`"script-src" in policy` / `"default-src" in policy` before falling
back to "no directive present at all → unrestricted," rather than
using `dict.get()`'s default-value behavior to paper over the
distinction. This module's own demo (which always supplies a
`script-src` directive) was never affected by the bug; it was real and
latent until Module 32 hit it directly. Kept here, dated after the
original entries above, as an honest record of when and how it was
found.

## Comparing both the full origin (with port) and a no-port form against source expressions
**(b) External contract.** CSP source expressions are commonly written
without an explicit port (`https://cdn.trusted.com` implicitly means
the scheme's default port). Since this module's own `origin_of()`
always includes an explicit port (matching Module 17/18's origin
model), comparing against BOTH forms is necessary to correctly match
real-world CSP policies that omit the port, which is the overwhelmingly
common way CSP headers are actually written in practice.

## The demo splitting results into `executed` vs. `blocked` lists, rather than just printing pass/fail per line
**(c) Convention.** Explicitly partitioning scripts into "reached
execution" and "blocked before ever executing" makes the module's core
claim — CSP is checked BEFORE execution, not as an after-the-fact
filter on already-run content — visible as a structural fact about the
demo's own control flow, not just something asserted in prose.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Header parsing style matches Modules 16/21 | (c) Convention (consistency, not novelty) | Yes, but consistency has real value |
| Only `'unsafe-inline'`, no nonce/hash support | (c) Convention (named scope boundary) | Yes — nonce/hash support is a natural, real extension |
| `default-src` fallback for `script-src` | (b) Forced — real, specified CSP fallback behavior | No |
| Compare both full-origin and no-port source forms | (b) Forced — matches how CSP policies are commonly written | No |
| Explicit executed/blocked partitioning in the demo | (c) Convention (makes the core claim structurally visible) | Yes, a simpler pass/fail log also works, less clearly |

## What We Proved

Running one real, parsed CSP policy against four representative
`<script>` tags produced exactly the expected enforcement outcome:

1. **An inline script** (standing in for XSS-injected code) was
   **BLOCKED** — no `'unsafe-inline'` in the policy's `script-src`.
2. **A same-origin script** (`/app.js`) was **ALLOWED** — matched by
   `'self'`.
3. **An explicitly listed third-party CDN script** was **ALLOWED** —
   matched by its exact origin in the policy.
4. **An unlisted third-party script** was **BLOCKED** — matched by
   nothing in the policy.

Critically, the demo's own control flow shows this decision happening
BEFORE any notion of "running" the script exists at all — blocked
entries never reach the `executed` list, exactly mirroring how a real
browser's CSP enforcement gates script execution as a precondition,
not a post-hoc content filter applied to already-executed code.
