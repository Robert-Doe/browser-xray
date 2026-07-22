# Module 32: xss_csrf_on_toy_browser — DECISIONS.md

## Reusing Module 19/20's real tokenizer/DOM builder to prove the XSS injection, rather than just asserting it
**(c) Convention — the module's central teaching decision.** It would
be easy to simply claim "unsanitized input becomes a script tag."
Instead, this module's vulnerable `render_comment_page_VULNERABLE()`
output is fed through this course's OWN, already-built-and-verified
HTML tokenizer and tree constructor, and the resulting DOM is inspected
directly for a real `<script>` element. This makes the injection's
structural reality a demonstrated fact about this course's own prior
work, not a new claim taken on faith.

## A real bug this module's testing caught in Module 30's `check_script()`
**(b) External contract, corrected after discovery — see Module 30's
own `DECISIONS.md` addendum for the full account.** Building this
module's "BEFORE: no CSP header" case directly exercised a code path
Module 30's own demo never had reason to hit — an empty policy dict —
and it surfaced a genuine logic bug (an empty policy was incorrectly
treated as "block everything" rather than "no restriction at all").
Fixed at the source (Module 30's own file), not just patched locally in
this module's copy, since the bug was real and would have affected any
future use of that function, not just this one.

## `render_comment_page_VULNERABLE()`'s name spelling out the vulnerability explicitly
**(c) Convention.** Naming it plainly, in capital letters, in the one
function that has an actual security bug, is deliberate — this course
builds real vulnerable code exactly once, on purpose, for teaching, and
the naming makes that unmistakable rather than something a reader might
mistake for an accidental oversight elsewhere in the codebase.

## The CSRF attack modeled as an auto-submitting, hidden top-level-navigation POST form
**(b) External contract.** This is the real, classic CSRF shape — not
a simplified stand-in. A form's `action` attribute pointing
cross-site, combined with JavaScript calling `.submit()` on page load,
genuinely causes the VICTIM's browser to make a real, top-level POST
navigation to the target — carrying whatever cookies the browser's own
SameSite rules (Module 29, reused directly here) decide belong on that
request. This module doesn't invent a new attack shape; it reproduces
the textbook one.

## The toy bank server checking ONLY a session cookie, with no CSRF token
**(c) Convention — a deliberate, named vulnerability, not an
oversight.** Real, hardened servers defend against CSRF with a
SECOND, independent mechanism beyond cookies (a CSRF token embedded in
the legitimate form, checked server-side, that a cross-site attacker
cannot obtain). This module's toy server deliberately omits that
defense specifically to isolate and demonstrate the COOKIE-side of the
picture (SameSite) in isolation — a real production system should
layer both defenses, not rely on SameSite alone.

---

## Decisions We Made

| Decision | Category | Could it have gone another way? |
|---|---|---|
| Feed the XSS payload through the real tokenizer/DOM builder | (c) Convention (grounds the claim in this course's own verified work) | Yes, asserting it is weaker but faster |
| Fix the Module 30 bug at its source, not just locally | (c) Convention (correctness over convenience) | No — patching only the local copy would leave the real bug live |
| Explicit `_VULNERABLE` naming | (c) Convention (unmistakable intent) | Yes, understated naming is possible but less clear |
| Auto-submitting top-level POST form for CSRF | (b) Forced — the real, classic CSRF vector | No |
| No CSRF token in the toy bank server | (c) Convention (isolates the cookie/SameSite mechanism specifically) | Yes — a real server should have both defenses |

## What We Proved

1. **XSS**: a comment containing `<script>fetch(...document.cookie)</script>`,
   inserted into a page via naive string concatenation, was shown to
   produce a REAL `<script>` element in this course's own, previously
   built DOM tree — not merely inert text. With no CSP header, that
   script was confirmed ALLOWED to run. With a real CSP policy
   (`script-src 'self'`, no `'unsafe-inline'`) applied, the identical
   injected script was confirmed BLOCKED.
2. **CSRF**: an auto-submitting cross-site form targeting a toy bank's
   `/transfer` endpoint, with the victim's session cookie set to
   `SameSite=None`, successfully attached that cookie and completed a
   real, unauthorized `$500` transfer. With the identical cookie
   instead set to `SameSite=Lax`, the identical cross-site POST carried
   NO cookies at all, and the server correctly rejected the request.

Both halves directly, run-and-observedly confirm this module's central
claim: a real attack succeeds against this course's own toy stack until
the specific defensive module (Module 30's CSP, Module 29's SameSite)
is actually wired in — and fails immediately once it is, with no other
change to the attack itself.
