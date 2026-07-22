# Module 32: xss_csrf_on_toy_browser — SAFETY_NOTES.md

**Status: contained, educational demonstration of two real,
well-known web vulnerability classes (XSS, CSRF) against this course's
own toy stack. This is precisely the kind of defensive security
education this course exists to provide. Safe as built; documented
carefully given the subject matter.**

## Primitives used
- A deliberately vulnerable toy HTML-rendering function
  (string-concatenation XSS).
- A real `<script>` payload demonstrating data exfiltration intent
  (`fetch(...+document.cookie)`), never actually executed by anything
  in this module.
- A toy CSRF scenario (auto-submitting form + cookie jar) against a toy
  bank server, entirely self-contained.

## Why this is safe as built
- **Nothing here targets a real system.** Every "server" (the comment
  page renderer, the toy bank) is a Python object defined in this
  module's own scripts, with fake data (`$1000` balance, a hardcoded
  fake session token). No real website, real user, or real
  infrastructure is touched, scanned, or referenced by domain name
  anywhere in this module.
- **The XSS payload is never executed.** The `fetch(...)` JavaScript
  text is treated purely as DATA throughout this module — parsed into
  a DOM text node, read as a string, and passed to a CSP checker that
  decides ALLOWED/BLOCKED. At no point does this module's Python code
  (or any JS engine built in this course) actually evaluate or run that
  JavaScript string. It is inert content demonstrating a real
  vulnerability class, not a functioning payload.
- **The CSRF demo sends no real network requests.** The "attack" is a
  fully in-memory function call (`bank.handle_transfer_request(...)`)
  against a Python object in the same process — there is no HTTP
  request, no real form submission, no real browser involved anywhere.
- This module's entire second half of each demonstration (CSP enabled,
  SameSite=Lax) shows the DEFENSE working — the narrative arc is
  explicitly "here is the vulnerability, and here is the real fix,"
  consistent with defensive security education.

## Risk if extended
- This module is the most natural point in the course where a request
  to "make the attack actually work against a real site" might arise.
  That would be a fundamentally different, unauthorized activity,
  explicitly outside this course's scope (per the root `ROADMAP.md`'s
  "explicitly out of scope" list: weaponized/production exploit code).
  Nothing in this module's code is structured to make that extension
  easy or implied — the "bank," "victim," and "attacker" are all
  labels on local Python objects, not network-addressable endpoints.

## Action needed
- None to proceed with Module 33. This module's pattern (real
  vulnerability demonstrated against the course's own toy stack, then
  the specific real defense shown closing it) is the template Modules
  33-35 will continue to follow.
