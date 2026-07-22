# Module 33: clickjacking_uxss — DECISIONS.md

## `topmost_layer_at()` never consulting `opacity` when deciding the click target
**(b) External contract — this IS the vulnerability's real mechanism,
not a simplification.** This matches real browser/compositor behavior:
hit-testing (deciding which element receives an input event at a
coordinate) is based on the layer/paint order at that point (Module
24's territory), and is a genuinely SEPARATE concern from how that
layer is visually blended (its opacity). A real browser does not
special-case "don't deliver clicks to nearly-transparent elements" —
doing so would break entirely legitimate uses of low-opacity,
still-interactive UI (fade-in animations, semi-transparent overlays
mid-transition). The vulnerability exploits a genuine, intentional
separation of concerns, not a bug in hit-testing itself.

## Modeling `frame_ancestors_allows()` as a check that happens BEFORE the framed page ever renders
**(c) Convention, matching (b) real specified behavior.** Real
`frame-ancestors` (and its predecessor, `X-Frame-Options`) enforcement
happens when the browser is ABOUT to load a page inside a frame — it
either proceeds with loading or refuses outright. This module's
`frame_ancestors_allows()` returning a plain boolean, checked before
any `Layer` for the framed content is ever constructed in the
clickjacking demo, mirrors that real ordering: the defense removes the
vulnerable page from existing inside the attacker's page at all, rather
than trying to detect a deceptive overlay after the fact (which would
be a much harder, less reliable defense to build).

## UXSS modeled as a MISSING origin check on an already-permitted cross-window access function
**(c) Convention — a deliberate, minimal model of a real, historically
significant bug class.** Real UXSS vulnerabilities have occurred in
real browser engines exactly this way: an internal API that's SUPPOSED
to check origin before returning cross-window data or references
occasionally had a bug (a missed check, an incorrect comparison, a
code path that bypassed the check under specific conditions) that let
it return real data across origins. This module models the simplest
possible version of that shape — a function with an
`enforce_origin_check` flag — specifically to isolate and demonstrate
the CONSEQUENCE of such a bug clearly, not to reproduce any specific
historical CVE's exact mechanism.

## Reusing a plain string-equality `same_origin()` rather than importing Module 17's `Origin`/`same_origin()` directly
**(c) Convention, consistent with this course's per-module
self-containment.** This module's origin comparison need is simpler
than Module 17's (this module already receives clean origin strings,
with no URL-parsing/default-port logic needed), so a minimal local
`same_origin()` was written rather than pulling in Module 17's fuller
`Origin` dataclass and `origin_of()` URL parser — appropriately scoped
to what this module's own demo actually requires.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Hit-testing ignores opacity | (b) Forced — the real mechanism, not a simplification | No |
| `frame-ancestors` checked before the framed page renders | (b)/(c) Forced by real behavior, modeled as a pre-render gate | No |
| UXSS modeled as a missing-check flag on cross-window access | (c) Convention (minimal, real-shaped model) | Yes, a more elaborate historical-CVE reproduction is possible but unnecessary |
| Minimal local `same_origin()` instead of importing Module 17's fuller version | (c) Convention (scoped to actual need) | Yes, importing the fuller version also works |

## What We Proved

1. **Clickjacking**: a nearly-invisible (opacity 0.02) button from
   `bank.example`, positioned exactly over a visible "Play Video"
   button from a different origin, was confirmed to be the ACTUAL
   recipient of a click at that coordinate — the user's visual
   perception and the real click target were genuinely, provably
   different elements from different origins. With
   `frame-ancestors 'none'` applied, the embedding was confirmed
   refused entirely, removing the vulnerable overlay from existing at
   all.
2. **UXSS**: with a simulated missing origin check, a script's
   requesting origin (`https://evil.com`) successfully retrieved
   another origin's (`https://webmail.example`) real document content
   and secret data directly — a violation with nothing to do with any
   bug on the victim site's own part. With the origin check correctly
   enforced, the identical access attempt was blocked outright.

This is direct, run-and-observed confirmation of both of this module's
claims: clickjacking is a real, structural consequence of how
compositing and input-hit-testing are (correctly, deliberately) kept
separate, defended against by preventing the framing itself; and UXSS
is a categorically different, more severe class of vulnerability living
in the browser engine's own origin-enforcement code, not in any
individual website.
